# Project Summary: TinyERP Service Order Analysis & Local DB

## Objective
The primary goal is to extract detailed service order data from TinyERP via its API v3 and store it in a local, robust database (PostgreSQL). This database will serve as a foundation for analysis, reporting (dashboards), CRM integration, and other applications, with the capability to be containerized using Docker in the future.

## Constraints & Key Information
- **API Rate Limit:** TinyERP API has a limit of 120 requests per minute (60 GET, 60 PUT).
- **Data Volume:** Target is to extract and maintain ~31,000+ service orders, with daily updates.
- **Data Structure:** The database must handle relationships (Orders, Contacts, Addresses, etc.) and allow for custom categorization fields.
- **Relevant Fields:** A comprehensive list of fields to extract from the API is documented in `docs/conhecimento.txt`. Specific attention needed for `equipamentoSerie` and `marcadores`.
- **Service Order Statuses:** Various statuses exist (e.g., Finalizada, Em andamento, Aprovada).
- **Documentation:** API documentation is available in the `/docs` folder (`Tiny_API_Documentation.md`, `doc_TinyAPI_v3.md`).
- **Unicode:** Data must be handled correctly (UTF-8) to preserve special characters and accents.

## Progress So Far
- **Authentication:** Successfully authenticated with the TinyERP API using OAuth 2.0 (`src/tiny_auth_server.py`, `tiny_token.json`).
- **Initial Data Fetch:** Scripts (`src/get_orders.py`, `src/get_orders_post.py`, `src/get_orders_v3.py`, `src/fetch_orders_april.py`) developed to fetch service orders.
- **Basic Order List:** Successfully retrieved a list of the latest 10 service orders (`latest_10_orders.json`).
- **Detailed Order Fetch:** Script `src/get_orders_v3.py` successfully fetches detailed data for specific order IDs using `GET /ordem-servico/{idOrdemServico}` and saves to `detailed_10_orders.json`.
- **API Field Investigation:**
    - Confirmed `equipamentoSerie` is in the API response schema but returned empty in tests.
    - Confirmed `marcadores` is *not* in the standard response schema for `GET /ordem-servico/{idOrdemServico}`.
    - Generated a report (`report_tiny_support.txt`) for Tiny ERP support regarding these field issues.
- **Knowledge Base:** Created `docs/conhecimento.txt` to document project details, API fields, and statuses.
- **Version Control:** Initialized a Git repository in the project directory.
- **Database Setup (Local PostgreSQL):**
    - Installed PostgreSQL using Homebrew.
    - Started the PostgreSQL service.
    - Created the `tiny_os_data` database.
    - Installed `psycopg2-binary` Python dependency.
    - Defined the database schema in `db/schema.sql` and created the tables.
    - Created `src/db_utils.py` for database connection handling.
    - Created `src/process_data.py` with logic to read JSON data and insert/update into the database.
- **Data Import:** Successfully extracted 120 finalized service orders from April 2025 using `src/fetch_orders_april.py` and saved to `orders_april_finalizadas.json`. These orders were then successfully processed and inserted into the PostgreSQL database using `src/process_data.py`.
- **Web Interface Data Display:** Successfully configured the web interface (`web_interface/`) to connect to and display April service orders from the Supabase PostgreSQL database.

## Current Plan & Next Steps

1.  **Full Extraction & Database Completion:**
    *   Modify the script to capture all service orders from 2013 to today to complete the database.
    *   Adapt scripts to handle API pagination and rate limits to fetch *all* 31k+ orders.
    *   Set up a mechanism (e.g., `cron`) for daily data updates.
    *   **Data Recovery Implementation (May 2025):**
        * Created `recuperar_dados_completos.py` to fetch complete order details from TinyERP API for specified date ranges (01/01/2024 to 08/05/2025).
        * Implemented batched processing to handle large volumes of data while respecting API rate limits.
        * Added protection against data corruption by using the "safe" mode which prevents NULL values from overwriting existing data.
        * Implemented structured JSON logging for better observability and troubleshooting.
        * Integrated with `process_data_with_tags.py` to update the database while preserving existing markers.
        * Improved error handling to continue processing despite individual API call failures.
2.  **Optimize Report Access Interface:**
    *   Optimize the web interface for efficient access and display of the full report data.
3.  **Dockerization:**
    *   Create `Dockerfile` for the Python application.
    *   Create `docker-compose.yml` to manage the Python app and PostgreSQL containers.
4.  **Address `marcadores` and `equipamentoSerie`:**
    *   Follow up on the support ticket with Tiny ERP regarding the API issues with these fields.
    *   Once a solution is available, update the extraction and processing scripts to correctly handle this data.

## Web Interface Implementation (Supabase Backend)

5.  **Web Interface Development:**
    *   **Purpose:** Create a web interface to view, filter, and customize the display of service orders, connecting directly to the Supabase PostgreSQL database.
    *   **Backend:** **Supabase PostgreSQL Database** (replaces local Flask backend).
        *   Database schema replicated and initial data populated.
        *   Row Level Security (RLS) configured for read access.
        *   Frontend will interact directly with the Supabase API.
    *   **Frontend:** Use Vite + TypeScript + Tailwind CSS located in the `web_interface/` directory.
        *   `@supabase/supabase-js` client library installed and configured.
        *   Implemented data fetching and filtering logic using Supabase query methods.
        *   Implemented column selection using Supabase's `.select()` method.
        *   UI for filter inputs, column selection (checkboxes/multi-select), and dynamic data table rendering is in place.
        *   **Recent Improvements (July 2025):**
            *   Redesigned column selection UI to use buttons for better visualization.
            *   Configured table columns to update immediately upon column selection changes.
            *   Added functionality for users to adjust table column widths by dragging headers.
            *   Implemented column reordering with drag-and-drop functionality (May 2025).
            *   Added column configuration persistence using localStorage (May 2025).
            *   Fixed data mapping for customer phone numbers to correctly display the 'celular' field (May 2025).
            *   Implemented proper retrieval and display of service order markers (May 2025).
            *   Ensured 'ID' column is not displayed and 'Número OS' is always visible.
            *   Added new date filter options: 'This Month', 'This Year', and 'Last Year' (May 2025).
            *   Changed default date filter from 'Today' to 'Last Week' for better usability (May 2025).
    *   **Build Tool:** Vite for frontend development and build process.

---

## [Error Log] Frontend Environment Issue (April/May 2025)

### Problem
Persistent error: **"npm error could not determine executable to run"** when running `npx tailwindcss init -p` in `web_interface`, even after cleaning and reinstalling dependencies.

### Troubleshooting Steps Attempted
1. Verified Node.js and npm installation (Node v22.14.0, npm v10.9.2).
2. Checked PATH and nvm configuration.
3. Cleaned npm cache.
4. Deleted and reinstalled node_modules and package-lock.json.
5. Reinstalled tailwindcss locally and globally.
6. Confirmed tailwindcss is present in package.json but not in node_modules/.bin.
7. Global tailwindcss binary not found in PATH after global install.
8. `npm bin -g` not recognized; `which tailwindcss` returns not found.
9. npx cannot find the executable to run.

---

## [API Integration Issues] Tiny API Data Processing Challenges (May 2025)

### Problem 1: Campos 'orcar' e 'orcado' incompatíveis com o banco de dados
Os campos 'orcar' e 'orcado' da API Tiny vêm como valores booleanos (true/false), mas o banco de dados os define como CHAR(1). Isso causa o erro "value too long for type character(1)" quando o PostgreSQL tenta inserir a string "true" ou "false" em um campo que aceita apenas um caractere.

### Solução implementada
- Removemos completamente os campos 'orcar' e 'orcado' das queries SQL de inserção/atualização
- Esses campos não são necessários para as operações do sistema, então podem ser ignorados sem impacto na funcionalidade

### Problem 2: Estrutura de resposta diferente para ordens antigas (2014-2016)
As ordens de serviço mais antigas (especialmente de 2014) têm uma estrutura de resposta diferente na API Tiny, causando erros "Empty or invalid order data" quando o script tenta acessar os dados no caminho esperado.

### Solução implementada
- Modificamos o script para tentar diferentes estruturas de resposta:
  - Diretamente em `ordemServico`
  - Dentro de `retorno.ordemServico`
  - Dentro de `dados`
  - Na raiz da resposta (se contiver campos esperados)
- Adicionamos logging das chaves da estrutura de resposta para diagnóstico
- Implementamos validação mais robusta verificando explicitamente a presença do campo `id`

Essas adaptações permitem processar ordens de serviço de diferentes períodos (2014-2023) apesar das mudanças na estrutura da API ao longo do tempo.

### Analysis
- The issue is likely due to a misconfiguration or corruption in npm, nvm, or Node.js installation, or a problem with how binaries are linked on this system.
- The problem persists across both local and global installs, and even after full cleanups.

### Recommendations & Next Steps
- Consider switching to a stable LTS Node.js version (e.g., Node 20.x) using nvm.
- Reinstall Node.js and npm completely to ensure a clean environment.
- Ensure the global npm bin directory is in your PATH.
- Consult npm/nvm documentation for fixing global/local binary linking issues.
- If the problem persists, seek help on Stack Overflow or npm GitHub issues with the full error log.

---

*(Note: The npm/tailwindcss environment issue was resolved in April 2025. Refer to this log only if similar issues arise in the future.)*

## Database Backup Strategy (May 2025)

1. **Automated Backup Solution:**
   * Implemented `backup_database_direct.py` script that creates reliable SQL backups of the entire database.
   * Uses direct SQL connection with psycopg2 to avoid PostgreSQL version compatibility issues.
   * Creates timestamped backups in the `backup_db/` directory for easy recovery.
   * Includes all schemas, tables, primary keys, foreign key constraints, and data.
   * Implements structured JSON logging in compliance with project standards, including timestamps, severity levels, service names, and correlation IDs.
   * Validates environment variables for secure credential handling - never hardcodes sensitive information.
   * Handles errors gracefully with comprehensive exception handling and detailed logging.

## Current Priorities (May 2025)

1. **Enhanced Web Interface Features:**
   * Implement marker addition and removal for service orders.
   * Develop a dedicated view for detailed service order information.
   * Add print/export functionality for service order reports.
   * Implement user authentication and authorization for Supabase access.

2.  **Data Integration:**
   * Develop and implement automated synchronization between TinyERP and Supabase databases.
   * Create views or materialized views for common reporting scenarios.

3. **Performance Optimization:**
   * Implement server-side pagination for larger datasets.
   * Optimize queries for faster response times.
   * Add caching mechanisms for frequently accessed data.

## Documentação Técnica do Sistema

### Estrutura do Banco de Dados

#### Tabelas e Relações

1. **ordens_servico** (Tabela Principal)
   * **Chave Primária**: `id` (INTEGER)
   * **Campos Principais**: 
     * `numero_ordem_servico` (VARCHAR) - Identificador visível para o usuário
     * `situacao` (VARCHAR) - Código da situação da OS (ex: "3" para Finalizada)
     * `data_emissao`, `data_prevista`, `data_conclusao` - Campos de data
     * `total_servicos`, `total_ordem_servico`, `total_pecas` - Valores numéricos
     * `equipamento`, `equipamento_serie` - Informações do equipamento
     * `descricao_problema`, `observacoes`, `observacoes_internas` - Campos de texto
     * `linha_dispositivo`, `tipo_servico`, `origem_cliente` - Campos personalizados
   * **Chaves Estrangeiras**:
     * `id_contato` → `contatos.id` (cliente)
     * `id_vendedor` → `contatos.id` (técnico/vendedor)
     * `id_categoria_os` → `categorias_os.id`
     * `id_forma_pagamento` → `formas_pagamento.id`

2. **contatos**
   * **Chave Primária**: `id` (INTEGER)
   * **Campos Principais**: `nome`, `fantasia`, `tipo_pessoa`, `cpf_cnpj`, `telefone`, `celular`, `email`
   * **Chaves Estrangeiras**: `id_endereco` → `enderecos.id`

3. **enderecos**
   * **Chave Primária**: `id` (SERIAL)
   * **Campos Principais**: `endereco`, `numero`, `complemento`, `bairro`, `municipio`, `cep`, `uf`, `pais`

4. **categorias_os**
   * **Chave Primária**: `id` (INTEGER)
   * **Campos Principais**: `descricao`

5. **formas_pagamento**
   * **Chave Primária**: `id` (INTEGER)
   * **Campos Principais**: `nome`

6. **marcadores**
   * **Chave Primária**: `id` (SERIAL)
   * **Campos Principais**: `nome` (UNIQUE)

7. **ordem_servico_marcadores** (Tabela de Junção)
   * **Chave Primária Composta**: (`id_ordem_servico`, `id_marcador`)
   * **Chaves Estrangeiras**:
     * `id_ordem_servico` → `ordens_servico.id`
     * `id_marcador` → `marcadores.id`

#### Diagrama de Relacionamento

```
+----------------+      +------------+      +--------------+
|                |      |            |      |              |
| categorias_os  |      | marcadores |      | formas_pagto |
|                |      |            |      |              |
+-------+--------+      +-----+------+      +------+-------+
        |                     |                    |
        |                     |                    |
        v                     |                    v
+-------+-------------------+ |  +----------------+--+
|                           | |  |                   |
| ordens_servico +----------+-+--+                   |
|                |          |    |                   |
+----------------+          |    +-------------------+
        ^                   v
        |           +-------+------+
        |           |              |
        +-----------+ os_marcadores|
                    |              |
                    +--------------+
        ^                    
        |                    
+-------+--------+    +-------------+
|                |    |             |
| contatos       +---->  enderecos  |
|                |    |             |
+----------------+    +-------------+
```

### Endpoints da API TinyERP

#### Base URL
```
https://api.tiny.com.br/public-api/v3
```

#### Autenticação
Todos os endpoints exigem autenticação via Bearer Token:
```
Authorization: Bearer {access_token}
```
O token é armazenado no arquivo `tiny_token.json` (não versionado no git).

#### Endpoints Principais

1. **Listar Ordens de Serviço**
   * **URL**: `/ordem-servico`
   * **Método**: GET
   * **Parâmetros**:
     * `situacao` - Status da OS (ex: "3" para Finalizada)
     * `dataInicialEmissao` - Data inicial (formato YYYY-MM-DD)
     * `dataFinalEmissao` - Data final (formato YYYY-MM-DD)
     * `limit` - Número máximo de resultados (padrão: 100)
     * `offset` - Deslocamento para paginação
   * **Resposta**: Lista com múltiplas ordens de serviço com informações básicas e marcadores
   * **Usado em**: `recuperar_dados_completos.py`, `fetch_historical_orders.py`, `update_orders_with_tags.py`

2. **Obter Detalhes de Ordem de Serviço**
   * **URL**: `/ordem-servico/{order_id}`
   * **Método**: GET
   * **Parâmetros**: Nenhum (id na URL)
   * **Resposta**: Dados detalhados de uma ordem de serviço específica
   * **Observações**: Este endpoint não retorna marcadores, que devem ser obtidos via endpoint de listagem
   * **Usado em**: `recuperar_dados_completos.py`, `get_orders_v3.py`, `fetch_historical_orders.py`

#### Limitações e Desafios Conhecidos

1. **Campo `equipamentoSerie`**:
   * Presente no schema da API, mas retorna vazio em testes
   * Suporte TinyERP consultado via ticket
   * Soluções de contorno implementadas para preservar dados existentes

2. **Campo `marcadores`**:
   * Não disponível diretamente no endpoint de detalhes da OS
   * Solução: Obter via endpoint de listagem e mesclar com dados detalhados
   * Implementado em `recuperar_dados_completos.py` e scripts relacionados

3. **Limitação de Taxa**:
   * API limitada a 120 requisições por minuto (60 GET, 60 PUT)
   * Scripts implementam pausa de 1 segundo entre requisições
   * Processamento em lotes para evitar limites de memória e taxa

4. **Erros de Autorização**:
   * Erros 401 ocasionais em algumas OˢS específicas
   * Scripts implementam tratamento de erro para continuar o processamento
