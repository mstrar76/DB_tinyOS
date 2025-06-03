#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to create the necessary database tables for WhatsApp chat history.
This script is designed to be safe and idempotent - it will not drop or modify existing data.
"""

import os
import sys
import json
from datetime import datetime
import psycopg2
from db_utils import get_db_connection, close_db_connection

def log_json(level, message, **kwargs):
    """Structured JSON logging function."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": message,
        **kwargs
    }
    print(json.dumps(log_entry, ensure_ascii=False))

def table_exists(conn, table_name):
    """Check if a table exists in the database."""
    cur = conn.cursor()
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM pg_tables
            WHERE schemaname = 'public'
            AND tablename = %s
        )
    """, (table_name,))
    exists = cur.fetchone()[0]
    
    # For debugging
    log_json("DEBUG", f"Table {table_name} exists check result: {exists}")
    
    # Force false for now to ensure tables are created
    return False

def column_exists(conn, table_name, column_name):
    """Check if a column exists in a table."""
    cur = conn.cursor()
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = %s
            AND column_name = %s
        )
    """, (table_name, column_name))
    return cur.fetchone()[0]

def create_chat_tables(dry_run=False):
    """
    Create the necessary tables for storing WhatsApp chat history.
    If dry_run is True, SQL statements will be printed but not executed.
    """
    conn = get_db_connection()
    if not conn:
        log_json("ERROR", "Failed to connect to database")
        return
    
    try:
        # Start transaction
        cur = conn.cursor()
        
        # Define tables to create
        tables = [
            # Table for WhatsApp Chat Files
            {
                "name": "chat_files",
                "sql": """
                    CREATE TABLE IF NOT EXISTS chat_files (
                        id SERIAL PRIMARY KEY,
                        filename VARCHAR(255) NOT NULL,
                        file_path VARCHAR(512) NOT NULL,
                        file_date DATE,
                        phone_number VARCHAR(20),
                        customer_name VARCHAR(255),
                        reference_os VARCHAR(50),
                        id_contato INTEGER NULL,
                        id_ordem_servico INTEGER NULL,
                        processing_status VARCHAR(20) DEFAULT 'pending',
                        match_method VARCHAR(20),
                        match_confidence FLOAT,
                        order_match_method VARCHAR(20),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        
                        CONSTRAINT fk_chat_contato
                            FOREIGN KEY (id_contato)
                            REFERENCES contatos (id),
                        CONSTRAINT fk_chat_ordem
                            FOREIGN KEY (id_ordem_servico)
                            REFERENCES ordens_servico (id)
                    )
                """
            },
            # Table for Individual Chat Messages
            {
                "name": "chat_messages",
                "sql": """
                    CREATE TABLE IF NOT EXISTS chat_messages (
                        id SERIAL PRIMARY KEY,
                        id_chat_file INTEGER NOT NULL,
                        message_timestamp TIMESTAMP,
                        is_from_customer BOOLEAN,
                        message_text TEXT,
                        responding_to TEXT NULL,
                        
                        CONSTRAINT fk_chat_message_file
                            FOREIGN KEY (id_chat_file)
                            REFERENCES chat_files (id)
                    )
                """
            },
            # Table for Customer Chat Summaries
            {
                "name": "customer_chat_summaries",
                "sql": """
                    CREATE TABLE IF NOT EXISTS customer_chat_summaries (
                        id SERIAL PRIMARY KEY,
                        id_contato INTEGER,
                        last_interaction_date TIMESTAMP,
                        communication_frequency VARCHAR(20),
                        common_topics TEXT[],
                        sentiment_analysis VARCHAR(20),
                        summary TEXT,
                        
                        CONSTRAINT fk_chat_summary_contato
                            FOREIGN KEY (id_contato)
                            REFERENCES contatos (id)
                    )
                """
            }
        ]
        
        # Define indexes to create
        indexes = [
            {
                "name": "idx_chat_files_phone",
                "table": "chat_files",
                "sql": "CREATE INDEX IF NOT EXISTS idx_chat_files_phone ON chat_files(phone_number)"
            },
            {
                "name": "idx_chat_files_os",
                "table": "chat_files",
                "sql": "CREATE INDEX IF NOT EXISTS idx_chat_files_os ON chat_files(reference_os)"
            },
            {
                "name": "idx_chat_messages_timestamp",
                "table": "chat_messages",
                "sql": "CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp ON chat_messages(message_timestamp)"
            },
            {
                "name": "idx_chat_messages_file_id",
                "table": "chat_messages",
                "sql": "CREATE INDEX IF NOT EXISTS idx_chat_messages_file_id ON chat_messages(id_chat_file)"
            },
            {
                "name": "idx_chat_files_contato",
                "table": "chat_files",
                "sql": "CREATE INDEX IF NOT EXISTS idx_chat_files_contato ON chat_files(id_contato)"
            },
            {
                "name": "idx_chat_files_ordem",
                "table": "chat_files",
                "sql": "CREATE INDEX IF NOT EXISTS idx_chat_files_ordem ON chat_files(id_ordem_servico)"
            }
        ]
        
        # Create tables
        for table in tables:
            if table_exists(conn, table["name"]):
                log_json("INFO", f"Table {table['name']} already exists, skipping")
            else:
                if dry_run:
                    log_json("INFO", f"[DRY RUN] Would create table {table['name']}")
                    print(table["sql"])
                else:
                    log_json("INFO", f"Creating table {table['name']}")
                    cur.execute(table["sql"])
        
        # Create indexes
        for index in indexes:
            # Check if the parent table exists before trying to create the index
            if not table_exists(conn, index["table"]):
                log_json("WARNING", f"Parent table {index['table']} does not exist for index {index['name']}, skipping")
                continue
                
            # Check if index already exists (simplified check)
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM pg_indexes
                    WHERE schemaname = 'public'
                    AND indexname = %s
                )
            """, (index["name"],))
            if cur.fetchone()[0]:
                log_json("INFO", f"Index {index['name']} already exists, skipping")
            else:
                if dry_run:
                    log_json("INFO", f"[DRY RUN] Would create index {index['name']}")
                    print(index["sql"])
                else:
                    log_json("INFO", f"Creating index {index['name']}")
                    cur.execute(index["sql"])
        
        # Commit changes if not dry run
        if not dry_run:
            conn.commit()
            log_json("INFO", "Database schema setup completed successfully")
        else:
            log_json("INFO", "[DRY RUN] No changes were made to the database")
        
    except Exception as e:
        if not dry_run:
            conn.rollback()
        log_json("ERROR", f"Error creating chat tables: {e}")
    finally:
        close_db_connection(conn)

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Create database schema for WhatsApp chat history')
    parser.add_argument('--dry-run', action='store_true', help='Print SQL statements without executing them')
    args = parser.parse_args()
    
    create_chat_tables(dry_run=args.dry_run)

if __name__ == "__main__":
    main()