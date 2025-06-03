# Plan for WhatsApp Chat History Database Integration

## 1. Overview

This document outlines a comprehensive plan to integrate WhatsApp chat history data from the `organized_whatsapp_chats` folder into the existing database, with a focus on preserving data integrity and initially processing only the 2025 chat data. This integration will enhance the customer service database by providing access to conversation history linked to service orders.

## 2. Prerequisite: TinyERP Contact Synchronization

Before integrating chat history, we need to ensure all contacts from TinyERP are available in our database to maximize matching success.

### Contact Extraction and Synchronization Process

1. **Extract Complete Contact List from TinyERP API**
   - Create a script `src/sync_contacts_from_tiny.py` that:
     - Uses the TinyERP API v3 endpoint `/contatos` with pagination
     - Implements retries and respects API rate limits
     - Fetches all contacts regardless of status
     - Stores the API responses as backup JSON files

2. **Database Operations for Contact Sync**
   ```python
   def sync_contacts_from_tiny():
       """
       Synchronizes contacts from TinyERP API to local database.
       """
       conn = get_db_connection()
       try:
           # Pagination variables
           page_size = 100
           offset = 0
           total_synced = 0
           new_contacts = 0
           updated_contacts = 0
           
           while True:
               # Fetch contacts with pagination
               contacts = fetch_contacts_from_api(limit=page_size, offset=offset)
               if not contacts or len(contacts) == 0:
                   break
               
               # Process each contact
               for contact in contacts:
                   contact_id = contact.get('id')
                   if not contact_id:
                       continue
                       
                   # Check if contact already exists
                   cur = conn.cursor()
                   cur.execute("SELECT id FROM contatos WHERE id = %s", (contact_id,))
                   exists = cur.fetchone()
                   
                   # Extract contact details
                   nome = contact.get('nome')
                   codigo = contact.get('codigo')
                   fantasia = contact.get('fantasia')
                   tipo_pessoa = contact.get('tipo')[:1] if contact.get('tipo') else None
                   cpf_cnpj = contact.get('cpf_cnpj')
                   inscricao_estadual = contact.get('ie')
                   rg = contact.get('rg')
                   telefone = contact.get('fone')
                   celular = contact.get('celular')
                   email = contact.get('email')
                   
                   if exists:
                       # Update existing contact
                       cur.execute("""
                           UPDATE contatos 
                           SET nome = %s, codigo = %s, fantasia = %s, 
                               tipo_pessoa = %s, cpf_cnpj = %s, inscricao_estadual = %s,
                               rg = %s, telefone = %s, celular = %s, email = %s
                           WHERE id = %s
                       """, (nome, codigo, fantasia, tipo_pessoa, cpf_cnpj, 
                             inscricao_estadual, rg, telefone, celular, email, contact_id))
                       updated_contacts += 1
                   else:
                       # Insert new contact
                       cur.execute("""
                           INSERT INTO contatos 
                           (id, nome, codigo, fantasia, tipo_pessoa, cpf_cnpj, 
                           inscricao_estadual, rg, telefone, celular, email)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                       """, (contact_id, nome, codigo, fantasia, tipo_pessoa, 
                             cpf_cnpj, inscricao_estadual, rg, telefone, celular, email))
                       new_contacts += 1
               
               # Commit batch
               conn.commit()
               total_synced += len(contacts)
               log_json("INFO", f"Processed {len(contacts)} contacts", 
                       offset=offset, total_synced=total_synced)
               
               # Move to next page
               offset += page_size
               
               # Respect API rate limits
               time.sleep(1)
           
           # Log final statistics
           log_json("INFO", "Contact synchronization complete", 
                   total_synced=total_synced,
                   new_contacts=new_contacts,
                   updated_contacts=updated_contacts)
           
       except Exception as e:
           conn.rollback()
           log_json("ERROR", f"Error synchronizing contacts: {e}")
       finally:
           close_db_connection(conn)
   ```

3. **Phone Number Normalization**
   - Create a script to update existing contacts with normalized phone numbers
   - Add new columns to store normalized versions of both `telefone` and `celular`
   ```sql
   ALTER TABLE contatos 
   ADD COLUMN telefone_normalizado VARCHAR(20),
   ADD COLUMN celular_normalizado VARCHAR(20);
   
   CREATE INDEX idx_contatos_telefone_norm ON contatos(telefone_normalizado);
   CREATE INDEX idx_contatos_celular_norm ON contatos(celular_normalizado);
   ```
   
   - Update these fields with a script that applies consistent formatting for matching
   ```python
   def normalize_phone_number(phone):
       """Remove all non-numeric characters and ensure consistent format."""
       if not phone:
           return None
       return re.sub(r'[^0-9]', '', phone)[-11:] # Keep just last 11 digits at most
       
   def update_normalized_phone_fields():
       """Update normalized phone fields for all contacts."""
       conn = get_db_connection()
       try:
           cur = conn.cursor()
           
           # Get all contacts
           cur.execute("SELECT id, telefone, celular FROM contatos")
           contacts = cur.fetchall()
           
           for contact_id, telefone, celular in contacts:
               telefone_norm = normalize_phone_number(telefone)
               celular_norm = normalize_phone_number(celular)
               
               cur.execute("""
                   UPDATE contatos 
                   SET telefone_normalizado = %s, celular_normalizado = %s
                   WHERE id = %s
               """, (telefone_norm, celular_norm, contact_id))
               
           conn.commit()
           log_json("INFO", f"Updated normalized phone fields for {len(contacts)} contacts")
           
       except Exception as e:
           conn.rollback()
           log_json("ERROR", f"Error updating normalized phone fields: {e}")
       finally:
           close_db_connection(conn)
   ```

4. **Verification and Validation**
   - Run database queries to check contact completeness
   - Verify phone number formats and variations
   - Generate statistics on contact coverage compared to service orders

## 3. Current State Analysis

### Database Structure
The current database is organized around service orders (`ordens_servico`) and contacts (`contatos`), with no existing tables for chat history. The main connection points will be:

- `contatos`: Contains customer information including phone numbers that can link to chat files
- `ordens_servico`: Service orders that are often referenced in chat filenames (e.g., "OS 30415")

### Chat Data Structure
The `organized_whatsapp_chats` folder contains:
- Hierarchical organization by year and month
- Files named following a pattern: "WhatsApp - YYYY-MM-DD HH MM SS - [Customer Name/Phone].txt"
- Many files include service order numbers in the filename
- Message content includes timestamps, sender information, and conversation flow
- Some files have 2025 timestamps in filenames but may contain conversations from earlier years

## 4. Database Schema Extension

We need to create additional tables to store chat history without modifying existing tables:

```sql
-- Table for WhatsApp Chat Files
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_chat_contato
        FOREIGN KEY (id_contato)
        REFERENCES contatos (id),
    CONSTRAINT fk_chat_ordem
        FOREIGN KEY (id_ordem_servico)
        REFERENCES ordens_servico (id)
);

-- Table for Individual Chat Messages
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
);

-- Table for Customer Chat Summaries
CREATE TABLE IF NOT EXISTS customer_chat_summaries (
    id SERIAL PRIMARY KEY,
    id_contato INTEGER,
    last_interaction_date TIMESTAMP,
    communication_frequency VARCHAR(20), -- 'frequent', 'regular', 'occasional', 'rare'
    common_topics TEXT[],
    sentiment_analysis VARCHAR(20), -- 'positive', 'neutral', 'negative'
    summary TEXT,
    
    CONSTRAINT fk_chat_summary_contato
        FOREIGN KEY (id_contato)
        REFERENCES contatos (id)
);

-- Index for performance
CREATE INDEX idx_chat_files_phone ON chat_files(phone_number);
CREATE INDEX idx_chat_files_os ON chat_files(reference_os);
CREATE INDEX idx_chat_messages_timestamp ON chat_messages(message_timestamp);
```

## 5. Implementation Plan

### Phase 1: Database Schema Setup (Safety First)

1. **Create Database Backup**
   ```bash
   python src/backup_database.py
   ```

2. **Run Schema Migration Script**
   - Create a new script `src/create_chat_tables.py` that:
     - Connects to the database
     - Checks if tables already exist (to avoid errors)
     - Creates the new tables with proper constraints
     - Logs all operations

### Phase 2: File Indexing and Contact/Order Link Discovery

1. **Create File Indexer Tool**
   - Develop a script `src/index_chat_files.py` that:
     - Walks through the `organized_whatsapp_chats/2025` directory
     - Parses filenames to extract dates, phone numbers, and potential OS references
     - Performs verification to ensure the file metadata is valid
     - Populates the `chat_files` table without parsing message content yet
     - Implements dry-run mode for safety testing

2. **Comprehensive Contact Linking Process**
   - Develop a script `src/link_chats_to_contacts.py` that:
     - Prioritizes linking every chat to a contact ID for efficient querying
     - Implements a multi-stage matching algorithm:
       - Stage 1: Exact phone number matching with the `celular` field in `contatos`
       - Stage 2: Normalized phone number matching (removing special characters, country codes)
       - Stage 3: Secondary phone matching with the `telefone` field in `contatos`
       - Stage 4: Name-based matching for chats with customer names (using fuzzy matching with threshold)
     - Creates a detailed matching report showing confidence levels
     - Flags ambiguous matches for manual review
     - Records the matching method used for each link in a new field
     - Uses a caching mechanism to speed up repeated matches of the same number/name
     - Updates the `chat_files` table with discovered contact IDs
     - Implements a manual override feature for correcting mismatches

3. **Service Order Linking Process**
   - Develop a script `src/link_chats_to_orders.py` that:
     - Identifies service order references in chat filenames (like "OS 30415")
     - Double-checks these references against the `ordens_servico` table
     - For chats with both contact ID and timeframe but no explicit OS reference:
       - Searches for service orders for that customer within the chat timeframe
       - Proposes potential matches based on temporal proximity
     - Updates the `chat_files` table with confirmed service order IDs
     - Produces a report of linked and unlinked conversations

### Phase 3: Message Content Processing

1. **Message Parser Tool**
   - Create a script `src/parse_chat_messages.py` that:
     - Reads each chat file from the `chat_files` table
     - Parses the message format to extract:
       - Message timestamps
       - Sender information (customer or staff)
       - Message content
       - Reply references
     - Performs validation on parsed content
     - Inserts valid messages into the `chat_messages` table
     - Implements batch processing with transaction support

2. **Verification and Correction Process**
   - Implement a verification script that:
     - Counts messages per file for sanity checks
     - Validates timestamps and ordering
     - Produces exception reports for manual review
     - Provides tools to fix common parsing issues

### Phase 4: Customer Summary Generation

1. **Develop Summary Generator**
   - Create a script `src/generate_chat_summaries.py` that:
     - Processes chat history for each customer
     - Identifies communication patterns and frequency
     - Extracts common topics and issues
     - Generates concise summaries for customer service context
     - Populates the `customer_chat_summaries` table

## 6. Execution Strategy with Data Protection

### Safety Measures

1. **Database Protection**
   - Run all operations with explicit transactions
   - Implement dry-run mode for all scripts
   - Create daily backups during the migration period
   - Set up verification checkpoints between phases

2. **Rate Limiting and Batching**
   - Process files in small batches (50-100 at a time)
   - Add delays between batch processing
   - Implement pause/resume functionality for long-running processes

3. **Logging and Monitoring**
   - Create detailed logs with JSON formatting
   - Log each file's processing status and outcome
   - Set up monitoring to detect processing issues early

### Contact Linking Priority and Strategy

Since efficiently connecting chat histories to contacts is a key priority, we'll implement a comprehensive approach:

1. **Schema Enhancement**
   - Add fields to track matching method and confidence score
   ```sql
   ALTER TABLE chat_files 
   ADD COLUMN match_method VARCHAR(20),
   ADD COLUMN match_confidence FLOAT,
   ADD COLUMN order_match_method VARCHAR(20);
   ```

2. **Multi-level Matching Algorithm**
   - Follow a cascading approach to maximize contact matching:
     1. **Direct phone matching**: Exact match with `celular` field
     2. **Normalized phone matching**: Remove formatting/country codes
     3. **Secondary phone matching**: Check `telefone` field
     4. **Name-based matching**: Use fuzzy matching with names
     5. **Equipment-based matching**: Match based on device mentions

3. **Match Quality Reporting**
   - Generate reports showing match distribution by type and confidence
   - Flag ambiguous matches for manual review
   - Create a report of unmatched chats for further analysis

4. **Manual Override Interface**
   - Design a simple interface (or SQL scripts) to allow admin review
   - Enable correcting mismatched contacts
   - Document the manual verification process

5. **Optimization for Performance**
   - Cache contact information for repeated matching
   - Use precomputed normalization of phone numbers
   - Implement batch processing for name matching

### Execution Plan for 2025 Data Only

1. **Initial Test Run**
   - Select a small sample of 20-30 files from 2025/01
   - Run the full process with verbose logging
   - Manually verify the results
   - Address any issues before proceeding

2. **Full 2025 Processing**
   - Process all files from 2025 (currently only January)
   - Run file indexing
   - Run link discovery
   - Run message parsing
   - Generate preliminary summaries

3. **Validation and Quality Assurance**
   - Develop validation queries to check data integrity
   - Provide report on linking success rates
   - Manual spot-checking of processed chats
   - Create list of potential improvements

## 7. Future Extensions

1. **Web Interface Integration**
   - Add chat history tab to service order view
   - Enable searching through chat history
   - Display customer summaries on contact views

2. **Automated Summary Updates**
   - Set up periodic jobs to update summaries as new chats are added
   - Improve summary generation with more sophisticated NLP techniques

3. **Historical Data Processing**
   - Extend processing to earlier years (2024, 2023, etc.)
   - Implement incremental updates for efficiency

## 8. Implementation Timeline

| Phase | Task | Estimated Duration | Dependencies |
|-------|------|-------------------|--------------|
| 0 | TinyERP Contact Sync | 2 days | None - prerequisite task |
| 1 | Database Schema Setup | 1 day | Database backup |
| 2 | File Indexer Development | 2 days | Schema setup |
| 2 | Link Discovery Implementation | 3 days | File indexing |
| 3 | Message Parser Development | 4 days | Link discovery |
| 3 | Verification & Correction | 2 days | Message parsing |
| 4 | Summary Generator | 3 days | Complete message processing |
| - | Testing & Validation | 3 days | All components |

## 9. Sample Scripts and Implementation Details

### File Indexer (Pseudo-code)

```python
def index_chat_files(directory, dry_run=True):
    """
    Scan directory recursively for chat files and index them in the database.
    """
    conn = get_db_connection()
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.startswith("WhatsApp") and file.endswith(".txt"):
                    file_path = os.path.join(root, file)
                    
                    # Parse filename components
                    match = re.match(r"WhatsApp - (\d{4}-\d{2}-\d{2}) (\d{2}) (\d{2}) (\d{2}) - (.+)\.txt", file)
                    if match:
                        date_str, hour, minute, second, name_or_phone = match.groups()
                        
                        # Extract phone if present
                        phone_match = re.search(r'\+\d{1,3} \d{2} \d{4,5}-\d{4}', name_or_phone)
                        phone = phone_match.group(0) if phone_match else None
                        
                        # Extract OS reference if present
                        os_match = re.search(r'OS[:\s]+(\d+)', name_or_phone, re.IGNORECASE)
                        os_ref = os_match.group(1) if os_match else None
                        
                        # Log for verification
                        log_json("INFO", f"Processing chat file", 
                                filename=file, 
                                date=date_str,
                                phone=phone,
                                os_ref=os_ref)
                        
                        if not dry_run:
                            # Insert into database
                            cur = conn.cursor()
                            cur.execute("""
                                INSERT INTO chat_files
                                (filename, file_path, file_date, phone_number, customer_name, reference_os, processing_status)
                                VALUES (%s, %s, %s, %s, %s, %s, 'pending')
                                RETURNING id
                            """, (file, file_path, date_str, phone, name_or_phone, os_ref))
                            file_id = cur.fetchone()[0]
                            conn.commit()
                            log_json("INFO", f"Indexed chat file", file_id=file_id)
                    else:
                        log_json("WARNING", f"Could not parse filename", filename=file)
    except Exception as e:
        conn.rollback()
        log_json("ERROR", f"Error indexing chat files: {e}")
    finally:
        close_db_connection(conn)


def link_chats_to_contacts(dry_run=True):
    """
    Links WhatsApp chat files to contacts in the database using multiple matching strategies.
    """
    conn = get_db_connection()
    try:
        # Get chat files that don't have contact IDs yet
        cur = conn.cursor()
        cur.execute("""
            SELECT id, phone_number, customer_name, reference_os 
            FROM chat_files 
            WHERE id_contato IS NULL AND processing_status = 'pending'
        """)
        chat_files = cur.fetchall()
        
        # Statistics for reporting
        match_stats = {
            'exact_phone': 0,
            'normalized_phone': 0,
            'secondary_phone': 0,
            'name_match': 0,
            'unmatched': 0
        }
        
        for file_id, phone, customer_name, os_ref in chat_files:
            contact_id = None
            match_type = None
            confidence = 0.0
            
            # Stage 1: Exact phone match with celular field
            if phone:
                cur.execute("SELECT id FROM contatos WHERE celular = %s LIMIT 1", (phone,))
                result = cur.fetchone()
                if result:
                    contact_id = result[0]
                    match_type = 'exact_phone'
                    confidence = 1.0
                    match_stats['exact_phone'] += 1
                    
                    log_json("INFO", "Found exact phone match", 
                            file_id=file_id, contact_id=contact_id, phone=phone)
                else:
                    # Stage 2: Normalized phone matching
                    normalized_phone = re.sub(r'[^0-9]', '', phone)
                    # Try with different length patterns (last 8 digits, last 9 digits, etc.)
                    for digits in [8, 9, 10, 11]:
                        if len(normalized_phone) >= digits:
                            pattern = f"%{normalized_phone[-digits:]}"
                            cur.execute("""
                                SELECT id, celular FROM contatos 
                                WHERE celular LIKE %s OR celular LIKE %s
                                LIMIT 2
                            """, (pattern, phone + '%'))
                            results = cur.fetchall()
                            
                            if len(results) == 1:  # Unique match
                                contact_id = results[0][0]
                                match_type = 'normalized_phone'
                                confidence = 0.9
                                match_stats['normalized_phone'] += 1
                                break
            
            # Stage 3: Try telefone field if still no match
            if not contact_id and phone:
                cur.execute("SELECT id FROM contatos WHERE telefone = %s LIMIT 1", (phone,))
                result = cur.fetchone()
                if result:
                    contact_id = result[0]
                    match_type = 'secondary_phone'
                    confidence = 0.8
                    match_stats['secondary_phone'] += 1
            
            # Stage 4: Name-based matching for contacts with customer names
            if not contact_id and customer_name:
                # Skip if it's just a phone number in the customer name field
                if not re.match(r'^[\d\+\(\)\-\s]+$', customer_name):
                    # Extract potential name (remove OS reference, etc.)
                    name_parts = re.sub(r'OS\s*\d+', '', customer_name).strip()
                    name_parts = re.sub(r'\s+', ' ', name_parts)
                    
                    cur.execute("SELECT id, nome, fantasia FROM contatos")
                    contacts = cur.fetchall()
                    
                    best_match = None
                    best_score = 0.7  # Minimum threshold
                    
                    for c_id, nome, fantasia in contacts:
                        # Try both nome and fantasia fields
                        for field in [nome, fantasia]:
                            if field:
                                # Use fuzzy matching with Levenshtein distance
                                ratio = difflib.SequenceMatcher(None, name_parts.lower(), field.lower()).ratio()
                                if ratio > best_score:
                                    best_score = ratio
                                    best_match = c_id
                    
                    if best_match:
                        contact_id = best_match
                        match_type = 'name_match'
                        confidence = best_score
                        match_stats['name_match'] += 1
            
            # Update database with match results
            if contact_id and not dry_run:
                cur.execute("""
                    UPDATE chat_files 
                    SET id_contato = %s, match_method = %s, match_confidence = %s 
                    WHERE id = %s
                """, (contact_id, match_type, confidence, file_id))
                conn.commit()
                
                log_json("INFO", f"Updated chat file with contact link", 
                        file_id=file_id, contact_id=contact_id, 
                        method=match_type, confidence=confidence)
            else:
                match_stats['unmatched'] += 1
                log_json("WARNING", f"No contact match found", 
                        file_id=file_id, phone=phone, name=customer_name)
        
        # Log summary statistics
        log_json("INFO", "Contact matching complete", 
                total_processed=len(chat_files),
                stats=match_stats)
                
    except Exception as e:
        conn.rollback()
        log_json("ERROR", f"Error linking chats to contacts: {e}")
    finally:
        close_db_connection(conn)


def link_chats_to_orders(dry_run=True):
    """
    Links WhatsApp chat files to service orders based on references and temporal proximity.
    """
    conn = get_db_connection()
    try:
        # Get chat files that have either a reference_os or a contact_id but no id_ordem_servico yet
        cur = conn.cursor()
        cur.execute("""
            SELECT id, reference_os, id_contato, file_date, customer_name
            FROM chat_files 
            WHERE id_ordem_servico IS NULL 
            AND (reference_os IS NOT NULL OR id_contato IS NOT NULL)
        """)
        chat_files = cur.fetchall()
        
        # Statistics for reporting
        match_stats = {
            'direct_os_ref': 0,
            'temporal_match': 0,
            'unmatched': 0
        }
        
        for file_id, reference_os, contact_id, file_date, customer_name in chat_files:
            order_id = None
            match_type = None
            
            # Direct OS reference matching
            if reference_os:
                # First try exact match on id
                cur.execute("SELECT id FROM ordens_servico WHERE id = %s", (reference_os,))
                result = cur.fetchone()
                
                # Then try match on numero_ordem_servico
                if not result:
                    cur.execute("SELECT id FROM ordens_servico WHERE numero_ordem_servico = %s", (reference_os,))
                    result = cur.fetchone()
                
                if result:
                    order_id = result[0]
                    match_type = 'direct_os_ref'
                    match_stats['direct_os_ref'] += 1
                    
                    log_json("INFO", "Found direct OS reference match", 
                            file_id=file_id, order_id=order_id, reference=reference_os)
            
            # Temporal matching for chats with contact_id but no direct OS reference
            if not order_id and contact_id and file_date:
                # Look for orders within a window of time (±30 days)
                file_date_obj = datetime.strptime(file_date, '%Y-%m-%d')
                date_from = (file_date_obj - timedelta(days=15)).strftime('%Y-%m-%d')
                date_to = (file_date_obj + timedelta(days=15)).strftime('%Y-%m-%d')
                
                cur.execute("""
                    SELECT id, numero_ordem_servico, data_emissao, equipamento
                    FROM ordens_servico 
                    WHERE id_contato = %s 
                    AND data_emissao BETWEEN %s AND %s
                    ORDER BY ABS(DATE_PART('day', data_emissao - %s::date))
                """, (contact_id, date_from, date_to, file_date))
                
                results = cur.fetchall()
                if results:
                    # If there's just one order in timeframe, use it
                    if len(results) == 1:
                        order_id = results[0][0]
                        match_type = 'temporal_match'
                        match_stats['temporal_match'] += 1
                    else:
                        # Check for equipment mentioned in chat name
                        if customer_name:
                            for o_id, numero, data, equipamento in results:
                                if equipamento and equipamento.lower() in customer_name.lower():
                                    order_id = o_id
                                    match_type = 'equipment_match'
                                    break
                            
                            # If still no match, use the closest one by date
                            if not order_id:
                                order_id = results[0][0]  # First is closest by date due to ORDER BY
                                match_type = 'temporal_match'
                                match_stats['temporal_match'] += 1
                
            # Update database with match results
            if order_id and not dry_run:
                cur.execute("""
                    UPDATE chat_files 
                    SET id_ordem_servico = %s, order_match_method = %s 
                    WHERE id = %s
                """, (order_id, match_type, file_id))
                conn.commit()
                
                log_json("INFO", f"Updated chat file with order link", 
                        file_id=file_id, order_id=order_id, method=match_type)
            else:
                match_stats['unmatched'] += 1
                log_json("WARNING", f"No order match found", 
                        file_id=file_id, reference_os=reference_os, contact_id=contact_id)
        
        # Log summary statistics
        log_json("INFO", "Order matching complete", 
                total_processed=len(chat_files),
                stats=match_stats)
                
    except Exception as e:
        conn.rollback()
        log_json("ERROR", f"Error linking chats to orders: {e}")
    finally:
        close_db_connection(conn)
```

### Implementation Details for Message Parser

The message parser will need to handle the specific format observed in WhatsApp exports:

1. Messages are separated by a line of dashes (----)
2. Each message has a header with sender and timestamp
3. Some messages are responses to previous messages
4. System notifications are present

By developing a robust parser, we can accurately extract the conversational flow and make it queryable in the database.

## 10. Verification and Testing Plan

1. **Validation Queries**
   - Confirm all 2025 files were indexed
   - Verify correct contact linking
   - Check message count per chat file
   - Ensure timestamp ordering is correct

2. **Manual Review Sample Criteria**
   - Review 10% of processed files or 20 files, whichever is greater
   - Focus on files with OS references
   - Include files with both phone numbers and named customers
   - Review any files with parsing warnings or errors

## 11. Risk Mitigation

| Risk | Mitigation Strategy |
|------|---------------------|
| Database corruption | Multiple backups, transactions, incremental approach |
| Incorrect contact linking | Conservative matching, verification reports, manual review options |
| Performance issues with large files | Batch processing, progress tracking, resume capability |
| Format inconsistencies in chat files | Robust parsing with exception handling, detailed logging |
| Data privacy concerns | Ensure proper access controls on new tables |

By following this well-structured approach, we can safely integrate the WhatsApp chat history into the database without compromising existing data, while providing valuable insights into customer interactions.