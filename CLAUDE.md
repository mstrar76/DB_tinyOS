# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project extracts and synchronizes service order data from the TinyERP API into a local PostgreSQL database for analysis and reporting. It consists of data extraction scripts, database utilities, and a web interface for viewing and filtering service orders.

## Command Reference

### Database Operations

```bash
# Connect to the local PostgreSQL database
psql -h localhost -p 54322 -U postgres -d postgres

# Run database backup script
python src/backup_database.py

# Alternative direct backup method
python src/backup_database_direct.py

# Restore a database backup
pg_restore -h localhost -p 54322 -U postgres -d postgres backup_db/db_backup_YYYYMMDD_HHMMSS.dump
```

### Data Extraction and Processing

```bash
# Process data from JSON file and insert/update database
# Modes: safe (default), complete, append
python src/process_data_with_tags.py <path_to_json_file> --modo=safe|complete|append

# Simulate processing without modifying database
python src/process_data_with_tags.py <path_to_json_file> --dry-run

# Fetch orders from the TinyERP API
python src/get_orders_v3.py

# Fetch all orders with markers
python src/fetch_all_orders_with_markers.py

# Fetch orders in specific date range
python src/fetch_orders_test_range.py <start_date> <end_date>

# Check for orders with null contacts
python src/listar_ordens_contatos_nulos.py

# Verify orders without contact information
python src/verificar_ordens_sem_contato.py
```

### Web Interface

```bash
# Start the Flask API backend
cd web_api
python app.py

# Start the web interface development server
cd web_interface
npm run dev
```

## Architecture

### System Components

1. **API Integration Layer**
   - Scripts in `src/` connect to TinyERP API v3
   - Authentication handled by `tiny_auth_server.py` and `tiny_auth_debug.py`
   - Token stored in `tiny_token.json`

2. **Data Processing Layer**
   - Scripts parse API responses and transform data
   - `process_data_with_tags.py` handles database insertion/updates
   - Robust error handling and logging implemented

3. **Database Layer**
   - PostgreSQL database (schema in `db/schema.sql`)
   - Tables for service orders, contacts, categories, payment methods, etc.
   - Connection utilities in `src/db_utils.py`

4. **Web Interface**
   - Flask backend in `web_api/`
   - Frontend in `web_interface/` (Vite, TypeScript, Tailwind CSS)
   - Direct connection to PostgreSQL database

### Data Flow

1. **Extraction**: Scripts fetch service order data from TinyERP API
2. **Processing**: JSON data is parsed, validated, and transformed
3. **Storage**: Processed data is stored in PostgreSQL database
4. **Presentation**: Web interface queries database and displays data

## Database Schema

The database consists of the following main tables:

- `ordens_servico`: Service orders (main table)
- `contatos`: Customer and vendor contacts
- `enderecos`: Addresses
- `categorias_os`: Service order categories
- `formas_pagamento`: Payment methods
- `marcadores`: Tags/markers for service orders
- `ordem_servico_marcadores`: Junction table for order tags

Refer to `db/schema.sql` for the complete schema definition.

## API Configuration

The project connects to the TinyERP API v3. Authentication is handled via OAuth 2.0, with the token stored in `tiny_token.json`. 

Key API endpoints used:
- `GET /ordem-servico`: List service orders
- `GET /ordem-servico/{id}`: Get details for a specific service order
- `GET /contatos`: List contacts

The API has rate limits (120 requests per minute), which the scripts respect by implementing pauses between requests.

## Environment Setup

The project requires:

1. **PostgreSQL** (local or via Supabase)
   - Connection details in `.env` file or environment variables
   - Variables: DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT

2. **Python Dependencies**
   - psycopg2-binary: PostgreSQL connector
   - flask: Web API backend
   - flask-cors: CORS handling
   - python-dotenv: Environment variable loading
   - requests: HTTP client

3. **Node.js/npm** (for web interface)
   - Dependencies listed in `web_interface/package.json`

## Best Practices

1. **Error Handling**: All API calls and database operations should include robust error handling
2. **Logging**: Use structured JSON logging as implemented in existing scripts
3. **Database Operations**: Always validate data before inserting/updating
4. **Rate Limiting**: Respect the TinyERP API rate limits (use pauses between requests)
5. **Backup**: Create database backups before large operations

## Development Guidelines

1. **Data Validation**: Always validate data received from the API before processing
2. **Safe Updates**: Use "safe" mode by default to avoid overwriting data with NULL values
3. **Efficiency**: Batch database operations when possible
4. **Documentation**: Document any new fields or API endpoints
5. **Security**: Never hardcode credentials; use environment variables

## Current Challenges

1. **API Limitations**: Some fields (like 'equipamentoSerie') may not be returned correctly by the API
2. **Data Integrity**: Need to handle contacts that don't exist in the database
3. **Performance**: Large datasets require optimized processing
4. **Synchronization**: Keeping local database in sync with TinyERP

Refer to `memory/project_summary.md` and `memory/planejamento_sync_db_tinyOS.md` for more detailed information about the project status and plans.