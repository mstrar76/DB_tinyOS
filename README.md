# TinyERP Service Order Web Interface

This web interface allows you to view and filter service orders from the TinyERP database. It provides filtering capabilities by date, status, and other fields, as well as customization of displayed columns.

## Project Structure

- `web_api/`: Flask backend that connects to the PostgreSQL database and provides the API.
- `web_interface/`: Frontend built with Vite, TypeScript, and Tailwind CSS.

## Setup and Running

### Prerequisites

- Python 3.6+ with Flask and psycopg2-binary installed
- Node.js 14+ with npm
- PostgreSQL database with service order data (created by the data extraction scripts)

### Backend Setup

1. Configure the database connection settings in `web_api/app.py`:

```python
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_NAME = os.environ.get("DB_NAME", "tiny_os_data") # This should match your database name
DB_USER = os.environ.get("DB_USER", "your_db_user") # Replace with your actual username
DB_PASSWORD = os.environ.get("DB_PASSWORD", "your_db_password") # Replace with your actual password
DB_PORT = os.environ.get("DB_PORT", "5432")
```

2. Start the Flask backend:

```bash
cd web_api
python app.py
```

The API will run on `http://localhost:5000`.

### Frontend Setup

1. Start the Vite development server:

```bash
cd web_interface
npm run dev
```

The interface will be available at `http://localhost:5173` or another port if 5173 is in use.

## Features

- **Filter Service Orders**:
  - By date (today, last week, last month, or custom date range)
  - By status (e.g., Em andamento, Finalizada, Aprovada)
  - By additional fields (e.g., order number, technician, equipment)

- **Customize Columns**:
  - Select which columns to display
  - Columns are dynamically added/removed from the table

- **Data Display**:
  - Service orders are displayed in a responsive table
  - Data formatted appropriately (dates, currency values, etc.)

## API Endpoints

- `GET /api/orders`: Fetches service orders with filtering.
  - **Query Parameters**:
    - `columns`: Comma-separated list of columns to include in the result
    - `start_date`: Start date for filtering (YYYY-MM-DD)
    - `end_date`: End date for filtering (YYYY-MM-DD)
    - `status`: Filter by status
    - Additional field-specific filters (e.g., `tecnico=John`, `numero_ordem_servico=123`)
