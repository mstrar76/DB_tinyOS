#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to index January 2025 WhatsApp chat files in the database.
This is a simplified version for initial testing.
"""

import os
import sys
import json
import re
from datetime import datetime
import psycopg2
from db_utils import get_db_connection, close_db_connection

# Configuration
CHATS_DIR = "organized_whatsapp_chats/2025/01"  # Focus only on January 2025
BATCH_SIZE = 50

def log_json(level, message, **kwargs):
    """Structured JSON logging function."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": message,
        **kwargs
    }
    print(json.dumps(log_entry, ensure_ascii=False))

def extract_filename_data(filename):
    """
    Parse a WhatsApp chat filename to extract metadata.
    Returns a dictionary with extracted data or None if parsing fails.
    """
    try:
        # Parse filename components - format: "WhatsApp - YYYY-MM-DD HH MM SS - Customer.txt"
        match = re.match(r"WhatsApp - (\d{4}-\d{2}-\d{2}) (\d{2}) (\d{2}) (\d{2}) - (.+)\.txt", filename)
        if not match:
            return None
            
        date_str, hour, minute, second, name_or_phone = match.groups()
        
        # Extract phone if present (various formats)
        phone_match = re.search(r'(?:\+\d{1,3}\s?)?(?:\(\d{2,3}\)\s?)?(?:\d{2,3}[\s.-]?\d{4,5}[\s.-]?\d{4}|\d{10,11})', name_or_phone)
        phone = phone_match.group(0).strip() if phone_match else None
        
        # Extract OS reference if present (format: OS#, OS #, OS:#, etc.)
        os_match = re.search(r'OS\s*[:#]?\s*(\d+)', name_or_phone, re.IGNORECASE)
        reference_os = os_match.group(1) if os_match else None
        
        # Create datetime object for full timestamp
        hour, minute, second = int(hour), int(minute), int(second)
        timestamp = f"{date_str} {hour:02d}:{minute:02d}:{second:02d}"
        
        return {
            "file_date": date_str,
            "timestamp": timestamp,
            "name_or_phone": name_or_phone,
            "phone_number": phone,
            "reference_os": reference_os
        }
    except Exception as e:
        log_json("WARNING", f"Error parsing filename {filename}: {e}")
        return None

def file_already_indexed(conn, file_path):
    """Check if a file is already indexed in the database."""
    cur = conn.cursor()
    cur.execute("SELECT id FROM chat_files WHERE file_path = %s", (file_path,))
    result = cur.fetchone()
    return result is not None

def index_chat_files(dry_run=False):
    """
    Index January 2025 chat files in the database.
    If dry_run is True, no changes will be made to the database.
    """
    conn = get_db_connection()
    if not conn:
        log_json("ERROR", "Failed to connect to database")
        return
    
    try:
        indexed_count = 0
        skipped_count = 0
        error_count = 0
        
        if not os.path.exists(CHATS_DIR):
            log_json("ERROR", f"Chat directory {CHATS_DIR} does not exist")
            return
            
        # Get list of files
        files = []
        for file in os.listdir(CHATS_DIR):
            if file.startswith("WhatsApp") and file.endswith(".txt"):
                files.append(file)
        
        total_files = len(files)
        log_json("INFO", f"Found {total_files} chat files in {CHATS_DIR}")
        
        # Process in batches
        batch_files = []
        for file in files:
            file_path = os.path.join(CHATS_DIR, file)
            
            # Check if file is already indexed
            if file_already_indexed(conn, file_path):
                log_json("DEBUG", f"File already indexed, skipping: {file_path}")
                skipped_count += 1
                continue
            
            # Parse filename components
            file_data = extract_filename_data(file)
            if not file_data:
                log_json("WARNING", f"Could not parse filename, skipping: {file}")
                error_count += 1
                continue
            
            # Add to batch
            batch_files.append({
                "filename": file,
                "file_path": file_path,
                "file_date": file_data["file_date"],
                "phone_number": file_data["phone_number"],
                "customer_name": file_data["name_or_phone"],
                "reference_os": file_data["reference_os"]
            })
            
            # Process batch if it reaches the batch size
            if len(batch_files) >= BATCH_SIZE:
                process_batch(conn, batch_files, dry_run)
                indexed_count += len(batch_files)
                batch_files = []
                
                log_json("INFO", f"Processed batch of {BATCH_SIZE} files", 
                        indexed=indexed_count, skipped=skipped_count, errors=error_count)
        
        # Process remaining files
        if batch_files:
            process_batch(conn, batch_files, dry_run)
            indexed_count += len(batch_files)
        
        log_json("INFO", "Chat file indexing complete", 
                indexed=indexed_count, skipped=skipped_count, errors=error_count,
                total_files=total_files)
        
    except Exception as e:
        if not dry_run:
            conn.rollback()
        log_json("ERROR", f"Error indexing chat files: {e}")
    finally:
        close_db_connection(conn)

def process_batch(conn, batch_files, dry_run):
    """Process a batch of files by inserting them into the database."""
    if dry_run:
        for file in batch_files:
            log_json("INFO", f"[DRY RUN] Would index file: {file['filename']}", 
                    file_date=file['file_date'],
                    phone=file['phone_number'],
                    os_ref=file['reference_os'])
        return
    
    # Insert files into database
    cur = conn.cursor()
    for file in batch_files:
        try:
            cur.execute("""
                INSERT INTO chat_files
                (filename, file_path, file_date, phone_number, customer_name, reference_os, processing_status)
                VALUES (%s, %s, %s, %s, %s, %s, 'pending')
                RETURNING id
            """, (
                file['filename'], 
                file['file_path'], 
                file['file_date'], 
                file['phone_number'], 
                file['customer_name'], 
                file['reference_os']
            ))
            file_id = cur.fetchone()[0]
            
            log_json("DEBUG", f"Indexed chat file (ID: {file_id}): {file['filename']}")
        except Exception as e:
            log_json("ERROR", f"Error indexing file {file['filename']}: {e}")
            # Continue with other files in batch
    
    # Commit the batch
    conn.commit()

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Index January 2025 WhatsApp chat files')
    parser.add_argument('--dry-run', action='store_true', help='Simulate operations without modifying the database')
    args = parser.parse_args()
    
    index_chat_files(dry_run=args.dry_run)

if __name__ == "__main__":
    main()