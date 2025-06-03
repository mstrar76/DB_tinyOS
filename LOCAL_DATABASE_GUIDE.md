# Local Database Guide

This guide explains how to set up and use both local and remote PostgreSQL databases for the TinyOS project.

## Connection Options

### 1. Local Supabase Database (Default Development)

- **Host**: `localhost`
- **Port**: `54322`
- **Database**: `postgres`
- **Username**: `postgres`
- **Password**: `postgres` (default Supabase local password)
- **SSL Mode**: `disable`

### 2. Remote Supabase Database (Production)

- **Host**: `db.urvdgztmmnyopbbijinj.supabase.co`
- **Port**: `5432`
- **Database**: `postgres`
- **Username**: `postgres`
- **Password**: `joqxir-qawsat-3hevWo`
- **SSL Mode**: `require`

### 3. Standard Local PostgreSQL (Alternative)

- **Host**: `localhost`
- **Port**: `5432` (standard PostgreSQL port)
- **Database**: `tinyos_local` (or your chosen name)
- **Username**: `tinyos_user` (or your chosen user)
- **Password**: `your_password`
- **SSL Mode**: `disable`

## Setting Up Environments

### Configure Environment Variables

Create or update the `.env` file in the project root directory with the appropriate connection details:

#### For Local Supabase Development:
```
DB_HOST=localhost
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_PORT=54322

# Frontend variables (for web_interface)
VITE_SUPABASE_URL=http://localhost:54321
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVydmRnenRtbW55b3BiYmlqaW5qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU5NDY5ODAsImV4cCI6MjA2MTUyMjk4MH0.PhaqBk5FN3v-eXbiiHDBG2NzC-hbNG3uOkQoLgy9Y-U
```

#### For Remote Supabase Production:
```
DB_HOST=db.urvdgztmmnyopbbijinj.supabase.co
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=joqxir-qawsat-3hevWo
DB_PORT=5432

# Frontend variables (for web_interface)
VITE_SUPABASE_URL=https://urvdgztmmnyopbbijinj.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVydmRnenRtbW55b3BiYmlqaW5qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU5NDY5ODAsImV4cCI6MjA2MTUyMjk4MH0.PhaqBk5FN3v-eXbiiHDBG2NzC-hbNG3uOkQoLgy9Y-U
```

#### For Standard Local PostgreSQL:
```
DB_HOST=localhost
DB_NAME=tinyos_local
DB_USER=tinyos_user
DB_PASSWORD=your_password
DB_PORT=5432

# Frontend variables (use Supabase API or set up a local proxy)
VITE_SUPABASE_URL=http://localhost:3000/api
VITE_SUPABASE_ANON_KEY=local_development_key
```

### Setting Up a Standard Local PostgreSQL Database

If you want to use a standard PostgreSQL installation instead of Supabase:

1. **Install PostgreSQL**:
   ```bash
   # macOS
   brew install postgresql
   brew services start postgresql
   
   # Ubuntu/Debian
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   sudo systemctl start postgresql
   ```

2. **Create Database and User**:
   ```bash
   # Login as postgres user
   sudo -u postgres psql
   
   # In PostgreSQL prompt
   CREATE DATABASE tinyos_local;
   CREATE USER tinyos_user WITH ENCRYPTED PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE tinyos_local TO tinyos_user;
   \q
   ```

3. **Initialize Schema**:
   ```bash
   psql -h localhost -p 5432 -U tinyos_user -d tinyos_local -f db/schema.sql
   ```

## Connection Strings and Code Examples

### PostgreSQL Connection String

```
# Local Supabase
postgresql://postgres:postgres@localhost:54322/postgres

# Remote Supabase
postgresql://postgres:joqxir-qawsat-3hevWo@db.urvdgztmmnyopbbijinj.supabase.co:5432/postgres

# Standard Local
postgresql://tinyos_user:your_password@localhost:5432/tinyos_local
```

### Python (psycopg2)

The project automatically uses the connection details from your `.env` file:

```python
import psycopg2
from src.db_utils import get_db_connection

# Using the utility function
conn = get_db_connection()

# Direct connection
host = os.environ.get("DB_HOST", "localhost")
database = os.environ.get("DB_NAME", "postgres")
user = os.environ.get("DB_USER", "postgres")
password = os.environ.get("DB_PASSWORD", "postgres")
port = os.environ.get("DB_PORT", "54322")

conn = psycopg2.connect(
    host=host,
    database=database,
    user=user,
    password=password,
    port=port
)
```

### Node.js (pg)

```javascript
const { Pool } = require('pg');

const pool = new Pool({
  user: process.env.DB_USER || 'postgres',
  host: process.env.DB_HOST || 'localhost',
  database: process.env.DB_NAME || 'postgres',
  password: process.env.DB_PASSWORD || 'postgres',
  port: process.env.DB_PORT || 54322,
});
```

## Database Schema

### Tables Overview

1. **categorias_os** - Service order categories
2. **contatos** - Contacts information
3. **enderecos** - Addresses
4. **formas_pagamento** - Payment methods
5. **marcadores** - Tags/markers for service orders
6. **ordem_servico_marcadores** - Junction table for order tags
7. **ordens_servico** - Main service orders table

### Key Tables Structure

#### ordens_servico (Main table)

- **id** (integer) - Primary Key
- **numero_ordem_servico** (varchar) - Service order number
- **situacao** (varchar) - Order status
- **data_emissao** (date) - Issue date
- **data_prevista** (timestamp) - Expected completion date
- **data_conclusao** (date) - Completion date
- **total_servicos** (numeric) - Total services amount
- **total_ordem_servico** (numeric) - Total order amount
- **total_pecas** (numeric) - Total parts amount
- **equipamento** (varchar) - Equipment name
- **equipamento_serie** (varchar) - Equipment serial number
- **descricao_problema** (text) - Problem description
- **observacoes** (text) - General observations
- **observacoes_internas** (text) - Internal notes
- **orcar** (char) - Needs quote (S/N)
- **orcado** (char) - Quoted (S/N)
- **alq_comissao** (numeric) - Commission percentage
- **vlr_comissao** (numeric) - Commission value
- **desconto** (numeric) - Discount amount
- **id_lista_preco** (integer) - Price list ID
- **tecnico** (varchar) - Technician name
- **id_contato** (integer) - Contact ID (foreign key)
- **id_vendedor** (integer) - Seller ID (foreign key to contatos)
- **id_categoria_os** (integer) - Category ID (foreign key)
- **id_forma_pagamento** (integer) - Payment method ID (foreign key)
- **id_conta_contabil** (integer) - Accounting account ID
- **data_extracao** (timestamp) - Extraction timestamp
- **linha_dispositivo** (varchar) - Device line
- **tipo_servico** (varchar) - Service type
- **origem_cliente** (varchar) - Customer origin

*For complete schema details, refer to `db/schema.sql`*

## Command-line Database Access

### Connect to Database

```bash
# Local Supabase
psql -h localhost -p 54322 -U postgres -d postgres

# Remote Supabase
psql -h db.urvdgztmmnyopbbijinj.supabase.co -p 5432 -U postgres -d postgres

# Standard Local PostgreSQL
psql -h localhost -p 5432 -U tinyos_user -d tinyos_local
```

### Common psql Commands

```
\dt             # List all tables
\d table_name   # Describe table structure
\q              # Quit psql
\?              # Help with psql commands
```

## Example Queries

### Get All Service Orders with Contact Information

```sql
SELECT os.*, c.nome as nome_cliente, c.email, c.telefone
FROM ordens_servico os
JOIN contatos c ON os.id_contato = c.id
ORDER BY os.data_emissao DESC
LIMIT 100;
```

### Get Service Orders with Specific Markers

```sql
SELECT os.*, c.nome as cliente, m.nome as marcador
FROM ordens_servico os
JOIN contatos c ON os.id_contato = c.id
JOIN ordem_servico_marcadores osm ON os.id = osm.ordem_servico_id
JOIN marcadores m ON osm.marcador_id = m.id
WHERE m.nome IN ('Urgente', 'Garantia')
ORDER BY os.data_emissao DESC;
```

### Get Payment Method Distribution

```sql
SELECT 
    fp.nome as forma_pagamento,
    COUNT(*) as total_ordens,
    SUM(os.total_ordem_servico) as valor_total
FROM ordens_servico os
JOIN formas_pagamento fp ON os.id_forma_pagamento = fp.id
GROUP BY fp.nome
ORDER BY valor_total DESC;
```

### Find Orders with Null Contacts

```sql
SELECT id, numero_ordem_servico, data_emissao, situacao, equipamento
FROM ordens_servico
WHERE id_contato IS NULL;
```

## Backup and Restore

### Create Backup

The project includes scripts for backing up the database:

```bash
# Using project scripts
python src/backup_database.py
python src/backup_database_direct.py

# Manual backup commands
# For Supabase (local)
PGPASSWORD=postgres pg_dump -h localhost -p 54322 -U postgres -d postgres -Fc -f backup_file.dump

# For Supabase (remote)
PGPASSWORD=joqxir-qawsat-3hevWo pg_dump -h db.urvdgztmmnyopbbijinj.supabase.co -p 5432 -U postgres -d postgres -Fc -f backup_file.dump

# For SQL format backup
PGPASSWORD=postgres pg_dump -h localhost -p 54322 -U postgres -d postgres -F p -f backup_file.sql
```

### Restore Backup

```bash
# For custom format backups (.dump)
pg_restore -h localhost -p 54322 -U postgres -d postgres backup_file.dump

# For SQL format backups (.sql)
psql -h localhost -p 54322 -U postgres -d postgres < backup_file.sql
```

## Troubleshooting

### Connection Issues

1. **Verify Environment Variables**:
   ```bash
   # Print environment variables
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('DB_HOST'), os.getenv('DB_PORT'), os.getenv('DB_USER'))"
   ```

2. **Test Direct Connection**:
   ```bash
   psql -h localhost -p 54322 -U postgres -d postgres -c "SELECT 1;"
   ```

3. **Check if Service is Running**:
   ```bash
   # For Supabase local
   docker ps | grep postgres
   
   # For standard PostgreSQL
   # macOS
   brew services list
   
   # Ubuntu/Debian
   sudo systemctl status postgresql
   ```

### Data Issues

1. **Check Order Counts**:
   ```sql
   SELECT COUNT(*) FROM ordens_servico;
   ```

2. **Check for Orders with Missing Contact Information**:
   ```sql
   SELECT COUNT(*) FROM ordens_servico WHERE id_contato IS NULL;
   ```

3. **Verify the Latest Data Extraction**:
   ```sql
   SELECT MAX(data_extracao) FROM ordens_servico;
   ```

### Performance Issues

1. **Check for Missing Indexes**:
   ```sql
   SELECT
     relname as table_name,
     seq_scan,
     seq_tup_read,
     idx_scan,
     idx_tup_fetch
   FROM
     pg_stat_user_tables
   ORDER BY
     seq_scan DESC;
   ```

2. **Identify Slow Queries**:
   Enable query logging in PostgreSQL to identify slow queries.

## Best Practices

1. **Always Use Environment Variables**:
   Never hardcode database credentials in your code.

2. **Create Regular Backups**:
   Schedule automatic backups using the backup scripts.

3. **Use Transactions for Data Processing**:
   Wrap data import and processing in transactions to ensure data integrity.

4. **Validate Data Before Import**:
   Always validate API data before importing into the database.

5. **Handle NULL Values Properly**:
   Use the "safe" mode in processing scripts to avoid overwriting existing data with NULL values.

6. **Regularly Monitor Database Size**:
   Large databases can cause performance issues.

## Web Interface Integration

The web interface connects to the database through Supabase. To use it with different database configurations:

1. **Update the .env file in the web_interface directory**:
   ```
   # For Supabase remote
   VITE_SUPABASE_URL=https://urvdgztmmnyopbbijinj.supabase.co
   VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVydmRnenRtbW55b3BiYmlqaW5qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU5NDY5ODAsImV4cCI6MjA2MTUyMjk4MH0.PhaqBk5FN3v-eXbiiHDBG2NzC-hbNG3uOkQoLgy9Y-U
   
   # For Supabase local
   VITE_SUPABASE_URL=http://localhost:54321
   VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVydmRnenRtbW55b3BiYmlqaW5qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU5NDY5ODAsImV4cCI6MjA2MTUyMjk4MH0.PhaqBk5FN3v-eXbiiHDBG2NzC-hbNG3uOkQoLgy9Y-U
   ```

2. **Start the Web Interface**:
   ```bash
   cd web_interface
   npm run dev
   ```

3. **Start the Backend API**:
   ```bash
   cd web_api
   python app.py
   ```

## References

For more information, refer to:
- [Project Documentation](docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Supabase Documentation](https://supabase.com/docs)
- [TinyERP API Documentation](docs/Tiny_API_Documentation.md)