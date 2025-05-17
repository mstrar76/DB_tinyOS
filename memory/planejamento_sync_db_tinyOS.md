# Planejamento Estratégico para Sincronização e Cache de OS do Tiny

## 1. Situação atual (resumo rápido)

| Camada | Implementação proposta | Pontos fortes | Limitações / riscos |
| ------ | --------------------- | ------------- | ------------------- |
| **Carga histórica** | Scripts ad-hoc (`fetch_historical_orders_2014_2016.py` etc.) | Traz todo o backlog | Não guarda _checkpoint_, executa serialmente, pode estourar _rate-limit_, token refresh duplicado |
| **Sincronismo contínuo** | `sync_orders_cache.py` + `schedule_sync_job.py` (1× h) | Simples, idempotente, só atualiza o necessário, registra `data_conclusao`, logs estruturados | - Busca sempre “últimos 30 dias”, logo ordens antigas que mudem depois de 30 d não seriam detectadas<br>- Não mantém histórico de trocas de status<br>- Dependência de processo Python em loop (“schedule”) |
| **Observabilidade** | Logs JSON locais | Fácil de grepar | Falta consolidação central, métricas/alertas |
| **Segurança & Token** | Lê `tiny_token.json`, refresh espalhado | Fácil | Falta expir-at, renovação proativa, vault/secret-manager |

---

## 2. Hipóteses e variações

1. **Granularidade de sincronismo**  
   ‑ Talvez 1 h seja muito; se a OS muda de “Em atendimento” → “Finalizada” em minutos, relatar em quase-tempo-real pode ser útil (ex.: 5 min).  
   ‑ Mas _rate-limit_ da Tiny é ~ n req/min → fazer *pull* agressivo pode bloquear.

2. **Estratégia _delta-pull_**  
   Se a API expõe `updatedAfter`/`dataAlteracao`, podemos puxar “tudo que mudou desde o último sync”, reduzindo chamadas.

3. **Histórico de status**  
   Guardar só o status atual perde auditoria. Criar tabela `ordem_status_history(id_os, status_antigo, status_novo, changed_at)` com trigger ou na própria lógica.

4. **Orquestração**  
   ‑ `schedule` é simples mas não lida com falhas do processo.  
   ‑ Alternativas:  
     • `cron` + script idempotente;  
     • APScheduler (em memória mas robusto);  
     • Celery Beat / Airflow se já existir stack;  
     • systemd service + timer.

5. **Paralelismo**  
   ‑ Para carga histórica ou grandes períodos, usar `concurrent.futures.ThreadPoolExecutor` ou *asyncio* → acelerar mantendo _back-off_.

6. **Checkpoint / resume**  
   ‑ Registrar em tabela “sync_checkpoint” últimos IDs ou `updated_at` processados → retomada segura após falha.

7. **Pooling & batch-upsert**  
   ‑ Hoje é 1 update/insert por OS. Usar `psycopg2.extras.execute_batch` ou COPY para lotes.

8. **Token management**  
   ‑ Unificar refresh numa lib (`tiny_auth.py`) que:  
     • armazena `expires_at`;  
     • renova 5 min antes;  
     • salva no Redis/DB para múltiplos workers.

9. **Logs**  
   ‑ Encaminhar JSON para Loki/Elastic via `HTTPHandler` ou fluent-bit.  
   ‑ Adicionar métricas Prometheus (`orders_synced_total`, `status_changes_total`).

10. **Tratamento de erros idempotente**  
    ‑ Re-filas de ordens falhadas para nova tentativa.  
    ‑ Circuit-breaker se > N erros consecutivos.

11. **Tabela dedicada a finalizações**  
    Se relatórios precisarem apenas de “quando finalizou”, derivar `view` ou trigger que preenche `data_conclusao` no `history`.

---

## 3. Novo planejamento sugerido (MVP → Evolução)

### Fase 0 – Refatoração utilitária (2 ~ 3 h)
- `tiny_api.py`
  - `TinyClient.get_orders(situacao, updated_after, page…)`
  - `TinyClient.get_order(id)`
  - `TinyClient.refresh_token()`
- `db_repo.py`
  - Funções de _upsert_ em lote, pooling.

### Fase 1 – Sincronismo incremental confiável (6 ~ 8 h)
1. Tabela `sync_metadata(chave text primary key, valor text)`  
   ‑ `ultima_execucao_orders` (timestamp).
2. Script `sync_orders.py`  
   - Calcula `updated_after = ultima_execucao_orders`.  
   - Faz *pull* paginado **por status** OU única rota se a Tiny permitir filtro de alteração.  
   - Usa `execute_batch` para _upsert_.  
   - Atualiza `sync_metadata`.
3. Registrar cada mudança de status em `ordem_status_history`.
4. Expor métrica Prometheus com `prometheus_client`.

### Fase 2 – Orquestração resiliente (2 ~ 3 h)
- Empacotar em contêiner Docker.  
- Usar `cron` no host ou **systemd timer** (`OnUnitActiveSec=15min; Restart=on-failure`).  
- Healthcheck (`python -m sync_orders --health`) retorna 0/1.

### Fase 3 – Carga histórica paralela (opcional, 4 ~ 6 h)
- Script `historical_loader.py` que aceita range de anos/meses;  
- Multi-thread para 5 chamadas paralelas;  
- Usa checkpoint por mês em `sync_metadata` para retomar;  
- Respeita _rate-limit_ com `tenacity` + back-off.

### Fase 4 – Observabilidade & alerta (2 ~ 4 h)
- ‑ Logs JSON → Loki; dashboards.  
- ‑ Prometheus alerts (p95 latency, falhas de token).  
- ‑ Sentry para exceções Python (chave no `.env`).

### Fase 5 – Hardening & performance (ongoing)
- Índices em `ordens_servico(situacao, data_emissao)`.
- Verificar VACUUM / autovacuum.
- Adicionar testes unitários (pytest + VCR.py para mock de API).

---

## 4. Decisão rápida (caso queira algo menor)

Se o objetivo imediato é **só** registrar `data_conclusao` de forma mais robusta:

1. **Adicionar histórico de status** (uma migration simples).  
2. Alterar `sync_orders_cache.py` para buscar **todas as ordens não-finalizadas** + `updated_after` dos últimos 7 d — passa a ser 15 min/30 min.  
3. Substituir lib `schedule` por `cron` (menos dependência).  

Isso resolve 90 % dos casos sem grande reestruturação.

---

## 5. Próximos passos recomendados

1. Executar verificação inicial de integridade para identificar ordens faltantes ou desatualizadas.
2. Confirme se a API Tiny possui campo "dataAlteracao" ou similar → decide _delta-pull_.  
3. Escolha mecanismo de orquestração (cron vs systemd vs Celery).  
4. Defina SLA de atualização (minutos? horas?) para calibrar frequência.  
5. Implementar `sync_metadata` + _delta-pull_ + history table (fase 1).  
6. Migrar scripts históricos para loader paralelo com checkpoint.  

Caso esteja de acordo, seguimos detalhando a **Fase 0.5 (Verificação de integridade)** e **Fase 1 (Sync incremental + history)** com suas migrations.

## 6. Detalhamento da verificação de integridade

### Tabela para rastreamento de falhas

```sql
CREATE TABLE IF NOT EXISTS import_failures (
    id_ordem INTEGER PRIMARY KEY,
    primeira_tentativa TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultima_tentativa TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    erro TEXT,
    tentativas INTEGER DEFAULT 1,
    resolvido BOOLEAN DEFAULT FALSE,
    dados_api JSONB -- Armazena a resposta da API para debug
);

CREATE INDEX IF NOT EXISTS idx_import_failures_resolvido ON import_failures(resolvido);
CREATE INDEX IF NOT EXISTS idx_import_failures_tentativas ON import_failures(tentativas);
```

### Algoritmo de verificação de integridade

1. Para cada status possível (1-5):
   - Obter lista completa de IDs de ordens da API Tiny
   - Comparar com ordens existentes no banco
   - Para cada ordem faltante:
     - Tentar importar com tratamento de erro robusto
     - Se falhar, registrar na tabela `import_failures`
   - Para cada ordem com status diferente:
     - Atualizar status e registrar na tabela `ordem_status_history`

2. Estratégia de retry para falhas:
   - Backoff exponencial (30s, 2min, 8min, etc.)
   - Limite máximo de tentativas (ex: 5)
   - Após limite, manter na tabela mas marcar para verificação manual

3. Relatório de integridade:
   - Total de ordens na API vs banco
   - Ordens faltantes recuperadas
   - Ordens com falha persistente
   - Ordens com status desatualizado
   - Tempo de execução e estatísticas de API
