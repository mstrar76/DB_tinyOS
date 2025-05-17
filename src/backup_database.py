#!/usr/bin/env python3
"""
Database Backup Script for TinyOS

This script creates a backup of the PostgreSQL database used by TinyOS.
It follows project guidelines for structured logging and security.
"""

import os
import sys
import json
import logging
import datetime
import subprocess
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
    Create a backup of the PostgreSQL database using pg_dump.
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
    backup_filename = f"db_backup_{timestamp}.dump"
    backup_path = backup_dir / backup_filename
    
    # Build the pg_dump command using SQL format instead of custom format
    # This is more compatible across different PostgreSQL versions
    # Note: We use environment variables for the password instead of command line
    # to avoid exposing it in process lists
    pg_env = os.environ.copy()
    pg_env["PGPASSWORD"] = db_password
    
    # Change file extension for SQL format
    backup_path = backup_path.with_suffix('.sql')
    
    pg_dump_cmd = [
        "pg_dump",
        "-h", db_host,
        "-p", db_port,
        "-U", db_user,
        "-F", "p",  # Plain text SQL format (more compatible)
        "--no-owner", # Skip ownership commands for better portability
        "--no-acl",   # Skip access privilege commands
        "-f", str(backup_path),
        db_name
    ]
    
    logger.info(f"Starting database backup to {backup_filename}", 
                extra={"backup_file": str(backup_path), "db_name": db_name})
    
    try:
        # Execute the pg_dump command
        process = subprocess.run(
            pg_dump_cmd,
            env=pg_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False  # We'll handle errors ourselves
        )
        
        if process.returncode == 0:
            # Calculate backup size
            backup_size_bytes = backup_path.stat().st_size
            backup_size_mb = backup_size_bytes / (1024 * 1024)
            
            logger.info(
                f"Database backup completed successfully", 
                extra={
                    "backup_file": str(backup_path),
                    "size_bytes": backup_size_bytes,
                    "size_mb": round(backup_size_mb, 2),
                    "duration_seconds": process.stderr.count("sec") # Rough estimate from pg_dump output
                }
            )
            return True
        else:
            logger.error(
                f"Database backup failed with exit code {process.returncode}",
                extra={
                    "error": process.stderr,
                    "command": " ".join(pg_dump_cmd),
                    "detailed_error": process.stderr
                }
            )
            # Print detailed error for immediate troubleshooting
            print(f"\nDetailed error output:\n{process.stderr}")
            return False
            
    except Exception as e:
        logger.error(
            f"Exception during database backup: {str(e)}",
            extra={"exception_type": type(e).__name__}
        )
        return False

if __name__ == "__main__":
    logger.info("Database backup process started")
    success = backup_database()
    exit_code = 0 if success else 1
    logger.info(f"Database backup process completed with status: {'success' if success else 'failure'}")
    sys.exit(exit_code)
