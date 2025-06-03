# DB_tinyOS - TinyERP API Integration System

Complete integration system for synchronizing TinyERP service orders with PostgreSQL database, featuring automated data extraction, processing, and a web interface for visualization and analysis.

## 🚀 Quick Start

**📖 NEW USERS: Start with the [Integration Guide](INTEGRATION_GUIDE.md)**

For comprehensive setup instructions, API documentation, and integration into external applications, please read the **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** first.

## 🎯 What This Project Does

- **Automated TinyERP API Integration**: Syncs 31,000+ service orders via TinyERP API v3
- **PostgreSQL Database**: Structured storage with complete schema and relationships  
- **Web Interface**: Filter, view, and analyze service orders with custom columns
- **Data Processing**: Handles markers, contact management, and legacy data structures
- **Ready for Integration**: Documented for import into external applications

## 📁 Project Structure

```
DB_tinyOS/
├── 📖 INTEGRATION_GUIDE.md          # 👈 START HERE - Complete integration guide
├── 📖 LOCAL_DATABASE_GUIDE.md       # Database setup and configuration
├── 📖 CLAUDE.md                     # Command reference and development guide
├── src/                             # Python source code
│   ├── extraction/                  # TinyERP API data extraction
│   ├── processing/                  # Data validation and database operations  
│   ├── utilities/                   # Helper functions and tools
│   ├── auth/                        # OAuth authentication
│   └── old/                         # Legacy/deprecated scripts
├── data/                            # Data files (organized by type)
│   ├── extracted/                   # Processed JSON data
│   ├── raw/                         # Raw API responses
│   └── exports/                     # CSV exports and reports
├── web_api/                         # Flask backend API
├── web_interface/                   # Frontend (Vite + TypeScript + Tailwind)
├── api_docs/                        # TinyERP API documentation
├── db/                              # Database schema and migrations
└── memory/                          # Project documentation and planning
```

## 📋 Key Documentation Files

- **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** - Complete setup and integration guide
- **[LOCAL_DATABASE_GUIDE.md](LOCAL_DATABASE_GUIDE.md)** - Database configuration  
- **[CLAUDE.md](CLAUDE.md)** - Command reference and development guidelines

## ⚡ Quick Setup (Web Interface Only)

> **Note**: For complete setup including TinyERP API integration, see [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)

### Prerequisites

- Python 3.8+ with dependencies: `pip install psycopg2-binary flask flask-cors python-dotenv`
- Node.js 16+ with npm
- PostgreSQL database with service order data (see [LOCAL_DATABASE_GUIDE.md](LOCAL_DATABASE_GUIDE.md))

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

## 🔧 Advanced Usage & Integration

### For TinyERP API Integration
- **Automated Sync**: Set up automated data synchronization from TinyERP
- **Data Processing**: Handle markers, contacts, and legacy data structures  
- **Authentication**: OAuth 2.0 setup with TinyERP API v3
- **Exception Handling**: Process problematic fields and data inconsistencies

See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for complete instructions.

### For External Application Integration
The project includes comprehensive documentation for importing into other applications:
- Complete API endpoint mapping
- Database schema with relationships
- Error handling processes
- Docker-ready structure

## 📡 API Endpoints

- `GET /api/orders`: Fetches service orders with filtering.
  - **Query Parameters**:
    - `columns`: Comma-separated list of columns to include in the result
    - `start_date`: Start date for filtering (YYYY-MM-DD)
    - `end_date`: End date for filtering (YYYY-MM-DD)
    - `status`: Filter by status
    - Additional field-specific filters (e.g., `tecnico=John`, `numero_ordem_servico=123`)

## 🤝 Contributing

See [CLAUDE.md](CLAUDE.md) for development guidelines and command reference.

## 📄 License

This project is configured for TinyERP API v3 integration. Ensure you have proper TinyERP API access and credentials.
