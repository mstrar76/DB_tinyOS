#!/usr/bin/env python3
"""
Database Backup Script for TinyOS using direct SQL connection

This script creates a backup of the PostgreSQL database used by TinyOS
by directly connecting to the database and exporting data to SQL files.
It follows project guidelines for structured logging and security.
"""

import os
import sys
import json
import logging
import datetime
import psycopg2
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure structured JSON logging
class JsonFormatter(logging.Formatter):
    """Format logs as JSON for better observability and analysis."""
    
    def format(self, record):
        log_record = {
            "timestamp": datetime.datetime.now().isoformat(),
            "level": record.levelname,
            "service": "database_backup",
            "correlation_id": f"backup-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            "message": record.getMessage(),
        }
        
        # Add exception info if available
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        # Add any extra attributes
        if hasattr(record, "extra"):
            log_record.update(record.extra)
            
        return json.dumps(log_record)

# Set up logger
logger = logging.getLogger("backup_service")
logger.setLevel(logging.INFO)

# Console handler with JSON formatter
console_handler = logging.StreamHandler()
console_handler.setFormatter(JsonFormatter())
logger.addHandler(console_handler)

# File handler for persistent logs
log_dir = Path("/Users/marcelo/Projetos/DB_tinyOS/logs")
log_dir.mkdir(exist_ok=True)
file_handler = logging.FileHandler(log_dir / f"backup_{datetime.datetime.now().strftime('%Y%m%d')}.log")
file_handler.setFormatter(JsonFormatter())
logger.addHandler(file_handler)

def backup_database():
    """
    Create a backup of the PostgreSQL database using direct SQL connection.
    Uses environment variables for credentials and never hardcodes sensitive information.
    """
    # Get database credentials from environment variables
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    
    # Validate environment variables
    missing_vars = []
    for var_name, var_value in [
        ("DB_HOST", db_host),
        ("DB_PORT", db_port),
        ("DB_NAME", db_name),
        ("DB_USER", db_user),
        ("DB_PASSWORD", db_password)
    ]:
        if not var_value:
            missing_vars.append(var_name)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    # Create backup directory if it doesn't exist
    backup_dir = Path("/Users/marcelo/Projetos/DB_tinyOS/backup_db")
    backup_dir.mkdir(exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"db_backup_{timestamp}.sql"
    backup_path = backup_dir / backup_filename
    
    logger.info(f"Starting database backup to {backup_filename}", 
                extra={"backup_file": str(backup_path), "db_name": db_name})
    
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password
        )
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Get a list of all tables in the database
        cursor.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
            ORDER BY table_schema, table_name
        """)
        
        tables = cursor.fetchall()
        
        # Open the backup file for writing
        with open(backup_path, 'w') as f:
            # Write header
            f.write(f"-- Database backup of {db_name}\n")
            f.write(f"-- Generated on {datetime.datetime.now().isoformat()}\n\n")
            
            # For each table, export schema and data
            for schema, table in tables:
                logger.info(f"Backing up table {schema}.{table}")
                
                # Get table schema
                cursor.execute(f"""
                    SELECT 
                        column_name, 
                        data_type, 
                        character_maximum_length,
                        column_default, 
                        is_nullable
                    FROM 
                        information_schema.columns 
                    WHERE 
                        table_schema = %s AND 
                        table_name = %s
                    ORDER BY 
                        ordinal_position
                """, (schema, table))
                
                columns = cursor.fetchall()
                
                # Write CREATE TABLE statement
                f.write(f"-- Table: {schema}.{table}\n")
                f.write(f"CREATE TABLE IF NOT EXISTS {schema}.{table} (\n")
                
                column_defs = []
                for col_name, col_type, col_length, col_default, col_nullable in columns:
                    type_str = col_type
                    if col_length:
                        type_str += f"({col_length})"
                    
                    nullable_str = "NULL" if col_nullable == "YES" else "NOT NULL"
                    default_str = f" DEFAULT {col_default}" if col_default else ""
                    
                    column_defs.append(f"    {col_name} {type_str} {nullable_str}{default_str}")
                
                f.write(",\n".join(column_defs))
                f.write("\n);\n\n")
                
                # Get primary key information
                cursor.execute(f"""
                    SELECT 
                        tc.constraint_name, 
                        kcu.column_name
                    FROM 
                        information_schema.table_constraints AS tc
                        JOIN information_schema.key_column_usage AS kcu
                          ON tc.constraint_name = kcu.constraint_name
                          AND tc.table_schema = kcu.table_schema
                    WHERE 
                        tc.constraint_type = 'PRIMARY KEY' AND
                        tc.table_schema = %s AND
                        tc.table_name = %s
                    ORDER BY 
                        kcu.ordinal_position
                """, (schema, table))
                
                pk_columns = [col[1] for col in cursor.fetchall()]
                
                if pk_columns:
                    f.write(f"ALTER TABLE {schema}.{table} ADD PRIMARY KEY ({', '.join(pk_columns)});\n\n")
                
                # Get data from the table
                cursor.execute(f'SELECT * FROM {schema}."{table}"')
                rows = cursor.fetchall()
                
                if rows:
                    # Get column names for INSERT statement
                    column_names = [col[0] for col in columns]
                    
                    # Write INSERT statements
                    f.write(f"-- Data for table {schema}.{table}\n")
                    
                    for row in rows:
                        values = []
                        for val in row:
                            if val is None:
                                values.append("NULL")
                            elif isinstance(val, (int, float)):
                                values.append(str(val))
                            elif isinstance(val, datetime.datetime):
                                values.append(f"'{val.isoformat()}'")
                            elif isinstance(val, (datetime.date, datetime.time)):
                                values.append(f"'{val}'")
                            elif isinstance(val, bool):
                                values.append("TRUE" if val else "FALSE")
                            else:
                                # Escape single quotes in string values
                                val_str = str(val).replace("'", "''")
                                values.append(f"'{val_str}'")
                        
                        f.write(f"INSERT INTO {schema}.{table} ({', '.join(column_names)}) VALUES ({', '.join(values)});\n")
                    
                    f.write("\n")
            
            # Get foreign key constraints
            cursor.execute("""
                SELECT
                    tc.table_schema, 
                    tc.table_name, 
                    tc.constraint_name, 
                    kcu.column_name, 
                    ccu.table_schema AS foreign_table_schema,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name 
                FROM 
                    information_schema.table_constraints AS tc 
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                      AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                      AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                ORDER BY tc.table_schema, tc.table_name
            """)
            
            fk_constraints = cursor.fetchall()
            
            if fk_constraints:
                f.write("-- Foreign key constraints\n")
                for schema, table, constraint, column, f_schema, f_table, f_column in fk_constraints:
                    f.write(f"ALTER TABLE {schema}.{table} ADD CONSTRAINT {constraint} ")
                    f.write(f"FOREIGN KEY ({column}) REFERENCES {f_schema}.{f_table} ({f_column});\n")
                
                f.write("\n")
        
        # Close the database connection
        cursor.close()
        conn.close()
        
        # Calculate backup size
        backup_size_bytes = backup_path.stat().st_size
        backup_size_mb = backup_size_bytes / (1024 * 1024)
        
        logger.info(
            f"Database backup completed successfully", 
            extra={
                "backup_file": str(backup_path),
                "size_bytes": backup_size_bytes,
                "size_mb": round(backup_size_mb, 2),
                "tables_count": len(tables)
            }
        )
        return True
        
    except Exception as e:
        logger.error(
            f"Exception during database backup: {str(e)}",
            extra={"exception_type": type(e).__name__}
        )
        # Print detailed error for immediate troubleshooting
        print(f"\nDetailed error output:\n{str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Database backup process started")
    success = backup_database()
    exit_code = 0 if success else 1
    logger.info(f"Database backup process completed with status: {'success' if success else 'failure'}")
    sys.exit(exit_code)
