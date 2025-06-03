#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to synchronize contacts from TinyERP API into the local database.
This script prioritizes preserving existing data and only adds new contacts.
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
import psycopg2
import re
from db_utils import get_db_connection, close_db_connection

# Configuration
API_BASE_URL = "https://api.tiny.com.br/public-api/v3"
TOKEN_FILE = "tiny_token.json"
BACKUP_DIR = "backup_contacts"
MAX_RETRIES = 3
BATCH_SIZE = 100
DELAY_BETWEEN_REQUESTS = 1  # seconds

def log_json(level, message, **kwargs):
    """Structured JSON logging function."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": message,
        **kwargs
    }
    print(json.dumps(log_entry, ensure_ascii=False))

def get_api_token():
    """Read the API token from token file."""
    try:
        with open(TOKEN_FILE, 'r') as f:
            token_data = json.load(f)
            return token_data.get('access_token')
    except Exception as e:
        log_json("ERROR", f"Failed to read API token: {e}")
        return None

def fetch_contacts_from_api(limit=BATCH_SIZE, offset=0):
    """
    Fetch contacts from TinyERP API with pagination.
    Returns the list of contacts or None on error.
    """
    token = get_api_token()
    if not token:
        log_json("ERROR", "No API token available")
        return None
    
    endpoint = f"{API_BASE_URL}/contatos"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    params = {
        "limit": limit,
        "offset": offset
    }
    
    # Implement retry logic
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            data = response.json()
            
            # Backup the raw response
            save_backup_response(data, offset)
            
            # Extract contacts from the response
            # Note: Adjust this based on the actual API response structure
            if 'itens' in data:
                return data['itens']
            else:
                log_json("WARNING", "Unexpected API response format", data=data)
                return []
                
        except requests.exceptions.RequestException as e:
            log_json("ERROR", f"API request failed (attempt {attempt+1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                # Exponential backoff
                wait_time = (2 ** attempt) * DELAY_BETWEEN_REQUESTS
                log_json("INFO", f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                log_json("ERROR", "Max retries exceeded, giving up.")
                return None
    
    return None

def save_backup_response(data, offset):
    """Save the API response as a backup file."""
    try:
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{BACKUP_DIR}/contacts_response_offset_{offset}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        log_json("DEBUG", f"Saved API response backup to {filename}")
    except Exception as e:
        log_json("WARNING", f"Failed to save API response backup: {e}")

def normalize_phone_right_to_left(phone):
    """
    Normalize phone number by keeping only digits and analyzing from right to left.
    Returns the normalized phone or None if not valid.
    """
    if not phone:
        return None
        
    # Remove all non-digit characters
    digits_only = re.sub(r'[^0-9]', '', phone)
    
    # Handle empty or too short numbers
    if not digits_only or len(digits_only) < 8:
        return None
        
    # Return the rightmost digits (most significant for matching)
    return digits_only

def find_contact_by_phone(cur, phone):
    """
    Find a contact by phone number using right-to-left matching.
    Returns contact_id if found, None otherwise.
    """
    if not phone:
        return None
        
    normalized_phone = normalize_phone_right_to_left(phone)
    if not normalized_phone:
        return None
    
    # Try different lengths from right to left (8, 9, 10, 11 digits)
    for digits in [8, 9, 10, 11]:
        if len(normalized_phone) >= digits:
            # Get rightmost N digits
            phone_suffix = normalized_phone[-digits:]
            
            # Try both telefone and celular fields with LIKE pattern matching
            pattern = f"%{phone_suffix}"
            cur.execute("""
                SELECT id FROM contatos 
                WHERE telefone LIKE %s OR celular LIKE %s
                LIMIT 2
            """, (pattern, pattern))
            
            results = cur.fetchall()
            if len(results) == 1:  # Unique match found
                return results[0][0]
    
    return None

def sync_contacts_from_tiny(dry_run=False):
    """
    Synchronize contacts from TinyERP API to local database.
    If dry_run is True, no changes will be made to the database.
    """
    conn = get_db_connection()
    if not conn:
        log_json("ERROR", "Failed to connect to database")
        return
    
    try:
        # Pagination variables
        offset = 0
        total_synced = 0
        new_contacts = 0
        updated_contacts = 0
        skipped_contacts = 0
        
        log_json("INFO", f"Starting contact synchronization (dry_run={dry_run})")
        
        while True:
            # Fetch contacts from API
            contacts = fetch_contacts_from_api(limit=BATCH_SIZE, offset=offset)
            if not contacts:
                if offset == 0:
                    log_json("ERROR", "Failed to fetch any contacts from API")
                break
                
            if len(contacts) == 0:
                log_json("INFO", "No more contacts to process")
                break
                
            log_json("INFO", f"Processing {len(contacts)} contacts (offset={offset})")
            
            for contact in contacts:
                # Extract contact ID and basic info
                contact_id = contact.get('id')
                if not contact_id:
                    log_json("WARNING", "Contact missing ID, skipping", contact=contact)
                    skipped_contacts += 1
                    continue
                
                # Required fields
                nome = contact.get('nome')
                if not nome:
                    log_json("WARNING", f"Contact {contact_id} missing name, skipping")
                    skipped_contacts += 1
                    continue
                
                # Extract other contact details
                codigo = contact.get('codigo')
                fantasia = contact.get('fantasia')
                tipo_pessoa = contact.get('tipo')[:1] if contact.get('tipo') else None
                cpf_cnpj = contact.get('cpf_cnpj')
                inscricao_estadual = contact.get('ie')
                rg = contact.get('rg')
                telefone = contact.get('fone')
                celular = contact.get('celular')
                email = contact.get('email')
                
                # Check if contact exists
                cur = conn.cursor()
                cur.execute("SELECT id FROM contatos WHERE id = %s", (contact_id,))
                exists = cur.fetchone()
                
                if exists:
                    if dry_run:
                        log_json("INFO", f"[DRY RUN] Would update existing contact {contact_id}: {nome}")
                    else:
                        # Update existing contact preserving any null fields
                        update_fields = []
                        update_values = []
                        
                        # Check each field and only update if value exists
                        fields_to_check = [
                            ("nome", nome),
                            ("codigo", codigo),
                            ("fantasia", fantasia),
                            ("tipo_pessoa", tipo_pessoa),
                            ("cpf_cnpj", cpf_cnpj),
                            ("inscricao_estadual", inscricao_estadual),
                            ("rg", rg),
                            ("telefone", telefone),
                            ("celular", celular),
                            ("email", email)
                        ]
                        
                        for field, value in fields_to_check:
                            if value is not None:
                                update_fields.append(f"{field} = %s")
                                update_values.append(value)
                        
                        # Only update if there are fields to update
                        if update_fields:
                            query = f"UPDATE contatos SET {', '.join(update_fields)} WHERE id = %s"
                            cur.execute(query, update_values + [contact_id])
                            updated_contacts += 1
                        else:
                            skipped_contacts += 1
                else:
                    # Check if contact exists with similar phone
                    existing_id = None
                    if telefone or celular:
                        for phone in [telefone, celular]:
                            if phone:
                                existing_id = find_contact_by_phone(cur, phone)
                                if existing_id:
                                    log_json("INFO", f"Found contact with matching phone: API ID={contact_id}, DB ID={existing_id}")
                                    break
                    
                    if existing_id:
                        # Contact exists with different ID, update if needed
                        if dry_run:
                            log_json("INFO", f"[DRY RUN] Would update phone-matched contact {existing_id}: {nome}")
                        else:
                            # Similar update logic as above
                            update_fields = []
                            update_values = []
                            
                            for field, value in fields_to_check:
                                if value is not None:
                                    update_fields.append(f"{field} = %s")
                                    update_values.append(value)
                            
                            if update_fields:
                                query = f"UPDATE contatos SET {', '.join(update_fields)} WHERE id = %s"
                                cur.execute(query, update_values + [existing_id])
                                updated_contacts += 1
                            else:
                                skipped_contacts += 1
                    else:
                        # Insert new contact
                        if dry_run:
                            log_json("INFO", f"[DRY RUN] Would add new contact {contact_id}: {nome}")
                        else:
                            cur.execute("""
                                INSERT INTO contatos 
                                (id, nome, codigo, fantasia, tipo_pessoa, cpf_cnpj, 
                                inscricao_estadual, rg, telefone, celular, email)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (contact_id, nome, codigo, fantasia, tipo_pessoa, 
                                 cpf_cnpj, inscricao_estadual, rg, telefone, celular, email))
                            new_contacts += 1
            
            # Commit batch if not dry run
            if not dry_run:
                conn.commit()
                
            total_synced += len(contacts)
            log_json("INFO", f"Processed {len(contacts)} contacts", 
                    total_synced=total_synced,
                    new_contacts=new_contacts,
                    updated_contacts=updated_contacts,
                    skipped_contacts=skipped_contacts)
            
            # Move to next page
            offset += BATCH_SIZE
            
            # Respect API rate limits
            time.sleep(DELAY_BETWEEN_REQUESTS)
        
        # Final statistics
        log_json("INFO", "Contact synchronization complete", 
                total_synced=total_synced,
                new_contacts=new_contacts,
                updated_contacts=updated_contacts,
                skipped_contacts=skipped_contacts)
        
    except Exception as e:
        if not dry_run:
            conn.rollback()
        log_json("ERROR", f"Error synchronizing contacts: {e}")
    finally:
        close_db_connection(conn)

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Synchronize contacts from TinyERP API to local database')
    parser.add_argument('--dry-run', action='store_true', help='Simulate operations without modifying the database')
    args = parser.parse_args()
    
    sync_contacts_from_tiny(dry_run=args.dry_run)

if __name__ == "__main__":
    main()