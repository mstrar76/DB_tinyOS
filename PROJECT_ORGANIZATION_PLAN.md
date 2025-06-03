# Project Organization Plan

This document outlines a plan to reorganize the project directory structure to improve maintainability and organization.

## Proposed Directory Structure

```
DB_tinyOS/
├── .env                       # Environment variables
├── .gitignore                 # Git ignore file
├── README.md                  # Project documentation
├── CLAUDE.md                  # Claude AI instructions
├── LOCAL_DATABASE_GUIDE.md    # Local database setup guide
│
├── api_docs/                  # API documentation
│   └── Tiny_API_Documentation.md
│
├── data/                      # Organized data directory
│   ├── extracted/             # Final extracted data
│   │   ├── monthly/           # Monthly order data
│   │   └── complete/          # Complete datasets
│   │
│   ├── temp/                  # Temporary data files
│   │   └── batch_processing/  # Batch processing files
│   │
│   ├── raw/                   # Raw API responses
│   │   └── order_details/     # Individual order details
│   │
│   └── exports/               # CSV and other exports
│
├── db/                        # Database files
│   ├── schema.sql             # Database schema
│   └── migrations/            # Database migrations
│
├── backup_db/                 # Database backups
│
├── logs/                      # Application logs
│   ├── backups/               # Backup logs
│   ├── api/                   # API call logs
│   ├── extraction/            # Data extraction logs
│   └── processing/            # Data processing logs
│
├── src/                       # Source code
│   ├── extraction/            # Data extraction scripts
│   ├── processing/            # Data processing scripts
│   ├── utilities/             # Utility functions
│   └── old/                   # Old scripts (for reference)
│
├── web_api/                   # Flask API backend
│
├── web_interface/             # Frontend application
│
├── docs/                      # Project documentation
│
└── notebooks/                 # Jupyter notebooks (optional)
```

## Migration Plan

### 1. Create New Directory Structure

```bash
# Create main data directories
mkdir -p data/extracted/monthly
mkdir -p data/extracted/complete
mkdir -p data/temp/batch_processing
mkdir -p data/raw/order_details
mkdir -p data/exports

# Create log directories
mkdir -p logs/backups
mkdir -p logs/api
mkdir -p logs/extraction
mkdir -p logs/processing

# Create source code directories
mkdir -p src/extraction
mkdir -p src/processing
mkdir -p src/utilities
mkdir -p src/old

# Create API docs directory
mkdir -p api_docs

# Create notebooks directory (optional)
mkdir -p notebooks
```

### 2. Move Files to New Locations

#### Data Files:

1. Move order marker files:
   ```bash
   mv all_orders_with_markers_*.json data/extracted/monthly/
   ```

2. Move temporary batch files:
   ```bash
   mv temp_all_orders_batch_details_*.json data/temp/batch_processing/
   mv temp/batch_*.json data/temp/batch_processing/
   ```

3. Move extracted data files:
   ```bash
   mv stracted_data/*.json data/extracted/
   # Move complete datasets
   mv data/extracted/ordens_20240101_a_20250508_completo.json data/extracted/complete/
   mv data/extracted/orders_2024_01_01_a_2025_05_08_with_tags.json data/extracted/complete/
   ```

4. Move individual order details:
   ```bash
   mv order_api_responses/*.json data/raw/order_details/
   ```

5. Move CSV exports:
   ```bash
   mv *.csv data/exports/
   ```

#### Logs:

1. Move API logs:
   ```bash
   mv tiny_auth.log logs/api/
   ```

2. Move extraction logs:
   ```bash
   mv *_extraction.log logs/extraction/
   ```

3. Move backup logs:
   ```bash
   mv logs/backup_*.log logs/backups/
   ```

4. Move other logs:
   ```bash
   mv logs/fetch_*.log logs/extraction/
   mv logs/save_*.log logs/processing/
   mv logs/verify_*.log logs/processing/
   ```

#### Source Code:

1. Organize scripts by purpose:
   ```bash
   # Extraction scripts
   mv src/get_*.py src/fetch_*.py src/extraction/
   
   # Processing scripts
   mv src/process_*.py src/processing/
   
   # Utility scripts
   mv src/db_utils.py src/backup_*.py src/utilities/
   
   # Old scripts
   mv src/old_extraction_scripts/* src/old/
   ```

#### Documentation:

1. Move API documentation:
   ```bash
   mv docs/Tiny_API_Documentation.md docs/doc_TinyAPI_v3.md api_docs/
   ```

### 3. Update Import References

After moving files, you'll need to update import statements in Python files to reflect the new directory structure. This will require carefully reviewing each file.

### 4. Update .gitignore

Update the .gitignore file to reflect the new directory structure:

```
# Environment variables
.env

# Temporary files
data/temp/

# Large data files
data/extracted/complete/*.json

# Logs
logs/**/*.log

# Database backups
backup_db/*.dump
backup_db/*.sql

# IDE and system files
.DS_Store
.vscode/
__pycache__/
*.pyc
```

## Benefits of New Structure

1. **Separation of Concerns**: Clear distinction between different types of data and code
2. **Improved Organization**: Structured directories for different file types
3. **Better Maintainability**: Easier to locate files and understand their purpose
4. **Reduced Root Directory Clutter**: Fewer files in the project root
5. **Clear Data Flow**: Better understanding of data pipeline through directory structure
6. **Easier Backup Management**: Organized backup and log files
7. **Simplified Git Management**: Better control over what gets committed to version control

## Implementation Notes

- Implement changes incrementally to avoid disruption to existing workflows
- Test thoroughly after each major change to ensure functionality is preserved
- Consider creating a script to automate parts of the migration process
- Document any changes to file paths or import statements for future reference