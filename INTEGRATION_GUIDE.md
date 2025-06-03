# Guia de Integração - DB_tinyOS

## 🎯 Resumo Executivo

O projeto DB_tinyOS é um **sistema de integração completo** entre a API TinyERP v3 e PostgreSQL, oferecendo sincronização automatizada de ordens de serviço, interface web para visualização e análise de dados, com capacidade para processar mais de 31.000 registros.

## 🏗️ Arquitetura do Sistema

### Componentes Principais

```
TinyERP API → Autenticação → Extração → Processamento → PostgreSQL → Interface Web
     ↓            ↓             ↓           ↓            ↓           ↓
OAuth 2.0    Token Refresh   Rate Limit   Validação   Backup    Visualização
```

### 1. **Camada de Autenticação**
- **Scripts**: `src/auth/tiny_auth_server.py`, `src/auth/tiny_auth_debug.py`
- **Token**: Armazenado em `tiny_token.json` (duração: 4h, refresh: 1 dia)
- **Configuração**: OAuth 2.0 com CLIENT_ID e CLIENT_SECRET

### 2. **Camada de Extração**
- **Localização**: `src/extraction/`
- **Limite de API**: 120 requisições/minuto (respeitado com sleep(1))
- **Scripts principais**:
  - `fetch_all_orders_with_markers.py` - Carga completa com marcadores
  - `fetch_pending_and_recent_orders.py` - Atualizações incrementais
  - `get_orders_v3.py` - Extração básica de detalhes

### 3. **Camada de Processamento**
- **Localização**: `src/processing/`
- **Script principal**: `process_data_with_tags.py`
- **Modos de operação**:
  - `safe`: Preserva dados existentes (padrão)
  - `complete`: Sobrescreve todos os dados
  - `append`: Apenas adiciona novos registros

### 4. **Banco de Dados**
- **Schema**: `db/schema.sql`
- **Conexão**: `src/utilities/db_utils.py`
- **Backup**: `src/utilities/backup_database_direct.py`

### 5. **Interface Web**
- **Backend**: `web_api/app.py` (Flask)
- **Frontend**: `web_interface/` (Vite + TypeScript + Tailwind)
- **Conexão**: Supabase PostgreSQL

## 📊 Mapeamento de Tabelas

### Principais Tabelas (Schema: `db/schema.sql`)

#### `ordens_servico` (Tabela Principal)
```sql
id INTEGER PRIMARY KEY                    -- ID único da ordem
numero_ordem_servico VARCHAR(50)          -- Número visível da OS
situacao VARCHAR(10)                      -- Status (1-5, códigos numéricos)
data_emissao DATE                         -- Data de criação
data_conclusao DATE                       -- Data de finalização
total_ordem_servico NUMERIC(10,2)        -- Valor total
equipamento VARCHAR(255)                  -- Nome do equipamento
equipamento_serie VARCHAR(255)           -- Série (campo problemático)
descricao_problema TEXT                   -- Descrição do problema
linha_dispositivo VARCHAR(50)            -- Campo customizado
tipo_servico VARCHAR(100)                -- Campo customizado
origem_cliente VARCHAR(50)               -- Extraído dos marcadores
```

#### `contatos` (Clientes e Técnicos)
```sql
id INTEGER PRIMARY KEY
nome VARCHAR(255)
telefone VARCHAR(20)
celular VARCHAR(20)
email VARCHAR(255)
```

#### `marcadores` (Tags/Categorias)
```sql
id SERIAL PRIMARY KEY
nome VARCHAR(255) UNIQUE
```

#### `ordem_servico_marcadores` (Relacionamento N:N)
```sql
ordem_servico_id INTEGER
marcador_id INTEGER
```

### Relacionamentos
- `ordens_servico.id_contato` → `contatos.id` (cliente)
- `ordens_servico.id_vendedor` → `contatos.id` (técnico)
- `ordem_servico_marcadores` conecta ordens e marcadores

## 🔌 Mapeamento de Endpoints da API

### Base URL: `https://api.tiny.com.br/public-api/v3`

#### 1. **Listagem de Ordens** (Com Marcadores)
```
GET /ordem-servico
Parâmetros:
- situacao: Status da OS (1-5)
- dataInicialEmissao: YYYY-MM-DD
- dataFinalEmissao: YYYY-MM-DD
- limit: 100 (padrão)
- offset: 0 (paginação)

Retorna: Lista com marcadores incluídos
Usado em: fetch_all_orders_with_markers.py
```

#### 2. **Detalhes da Ordem** (Sem Marcadores)
```
GET /ordem-servico/{id}
Parâmetros: ID na URL

Retorna: Dados completos da ordem (SEM marcadores)
Usado em: get_orders_v3.py, fetch_pending_and_recent_orders.py
```

#### 3. **Autenticação**
```
POST https://accounts.tiny.com.br/realms/tiny/protocol/openid-connect/token
Parâmetros: grant_type, client_id, client_secret, code/refresh_token

Retorna: access_token, refresh_token, expires_in
Usado em: tiny_auth_server.py
```

## ⚠️ Processos de Exceção e Casos Especiais

### 1. **Extração de Marcadores**
**Problema**: Endpoint de detalhes (`/ordem-servico/{id}`) NÃO retorna marcadores.

**Solução**:
```python
# 1. Buscar lista com marcadores
orders_with_markers = get_orders_list(start_date, end_date)

# 2. Buscar detalhes individuais
for order_id in order_ids:
    details = get_order_details(order_id)
    
# 3. Mesclar marcadores com detalhes
merged_data = merge_markers_with_details(orders_with_markers, details)
```

**Scripts Relevantes**:
- `src/extraction/fetch_all_orders_with_markers.py`
- `src/processing/update_orders_with_tags.py`

### 2. **Campo `equipamentoSerie`**
**Problema**: Campo existe no schema mas retorna vazio na API.

**Solução**: Modo "safe" preserva valores existentes quando API retorna NULL.

**Script**: `src/processing/process_data_with_tags.py` (modo safe)

### 3. **Estruturas Legadas (2014-2016)**
**Problema**: Ordens antigas têm estrutura de resposta diferente.

**Solução**: Tentativa de múltiplas estruturas:
```python
def extract_order_data(response):
    # Tenta diferentes caminhos
    if 'ordemServico' in response:
        return response['ordemServico']
    elif 'retorno' in response and 'ordemServico' in response['retorno']:
        return response['retorno']['ordemServico']
    elif 'dados' in response:
        return response['dados']
    else:
        return response  # Tenta raiz
```

### 4. **Campos Incompatíveis**
**Problema**: `orcar`/`orcado` são boolean na API mas CHAR(1) no BD.

**Solução**: Campos removidos do processamento (não essenciais).

### 5. **Erros 401 (Token Expirado)**
**Solução**: Refresh automático implementado em todos os scripts.

```python
def refresh_token_if_needed(response):
    if response.status_code == 401:
        refresh_access_token()
        return True  # Retry
    return False
```

## 🔄 Fluxo de Sincronização Automatizada

### Carga Inicial
```bash
# 1. Executar uma vez para histórico completo
python src/extraction/fetch_all_orders_with_markers.py

# 2. Processar dados extraídos
python src/processing/process_data_with_tags.py data/extracted/complete/all_orders.json --modo=complete
```

### Atualização Diária (Cron)
```bash
# Sincronização diária às 3h
0 3 * * * cd /path/to/project && python src/extraction/fetch_pending_and_recent_orders.py && python src/processing/process_data_with_tags.py data/extracted/daily_update.json --modo=safe
```

### Backup Semanal
```bash
# Backup domingo à meia-noite
0 0 * * 0 cd /path/to/project && python src/utilities/backup_database_direct.py
```

## 📁 Arquivos de Referência Essenciais

### Documentação Técnica
- **Schema do BD**: `db/schema.sql`
- **Conexão DB**: `src/utilities/db_utils.py`
- **Guia do Banco**: `LOCAL_DATABASE_GUIDE.md`

### Configuração da API
- **Documentação**: `api_docs/Tiny_API_Documentation.md`, `api_docs/doc_TinyAPI_v3.md`
- **Detalhes de Integração**: `memory/api_tinyerp_detalhes.md`
- **Casos Especiais**: `docs/conhecimento.txt`

### Planejamento e Arquitetura
- **Sumário do Projeto**: `memory/project_summary.md`
- **Planejamento de Sync**: `memory/planejamento_sync_db_tinyOS.md`
- **Organização**: `PROJECT_ORGANIZATION_PLAN.md`

### Scripts de Referência
- **Extração Principal**: `src/extraction/fetch_all_orders_with_markers.py`
- **Processamento**: `src/processing/process_data_with_tags.py`
- **Autenticação**: `src/auth/tiny_auth_server.py`
- **Backup**: `src/utilities/backup_database_direct.py`

### Configuração de Ambiente
- **Comandos**: `CLAUDE.md`
- **Estrutura**: `REORGANIZATION_SUMMARY.md`
- **Interface Web**: `README.md`

## 🚀 Setup para Nova Integração

### 1. Dependências
```bash
pip install psycopg2-binary requests python-dotenv flask flask-cors
```

### 2. Configuração (.env)
```bash
# Database
DB_HOST=localhost
DB_PORT=54322
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_password

# TinyERP API
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret

# Supabase (opcional)
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_anon_key
```

### 3. Inicialização do Banco
```bash
psql -h localhost -p 54322 -U postgres -d postgres -f db/schema.sql
```

### 4. Primeira Autenticação
```bash
python src/auth/tiny_auth_server.py
```

### 5. Teste de Extração
```bash
python src/extraction/get_orders_v3.py
```

## 📈 Monitoramento e Logs

### Sistema de Logs Estruturados
- **Formato**: JSON com timestamp, level, service, correlation_id
- **Localização**: `logs/` (organizados por tipo)
- **Exemplo**:
```json
{
  "timestamp": "2025-02-06T10:30:00",
  "level": "INFO",
  "service": "data_extraction",
  "correlation_id": "abc-123",
  "message": "Processadas 150 ordens com sucesso",
  "orders_processed": 150
}
```

### Métricas Importantes
- Taxa de sucesso das requisições API
- Tempo de processamento por lote
- Ordens com falha de importação
- Status do token de autenticação

## 🔧 Solução de Problemas

### Problemas Comuns
1. **Token expirado**: Verificar logs e executar refresh
2. **Marcadores ausentes**: Usar script de atualização de tags
3. **Dados inconsistentes**: Executar em modo "safe"
4. **Performance lenta**: Verificar índices do banco

### Comandos de Diagnóstico
```bash
# Verificar conexão DB
python -c "from src.utilities.db_utils import get_db_connection; print('OK' if get_db_connection() else 'ERRO')"

# Contar ordens no banco
psql -h localhost -p 54322 -U postgres -d postgres -c "SELECT COUNT(*) FROM ordens_servico;"

# Verificar token
python -c "import json; print(json.load(open('tiny_token.json'))['expires_at'])"
```

---

**Último Update**: Fevereiro 2025  
**Versão**: 1.0  
**Compatibilidade**: TinyERP API v3, PostgreSQL 12+, Python 3.8+