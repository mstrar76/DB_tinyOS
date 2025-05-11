import requests
import json
import time
from db_utils import get_db_connection, close_db_connection
from datetime import datetime
import os

API_BASE = "https://api.tiny.com.br/public-api/v3"
TOKEN_FILE = "tiny_token.json"
TINY_ACCOUNTS_TOKEN_URL = "https://accounts.tiny.com.br/realms/tiny/protocol/openid-connect/token"

def get_access_token():
    """Reads the access token from the token file."""
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("access_token")
    except FileNotFoundError:
        print(f"Error: {TOKEN_FILE} not found. Please run the authentication script first.")
        return None
    except Exception as e:
        print(f"Error reading {TOKEN_FILE}: {e}")
        return None

def get_refresh_token():
    """Reads the refresh token from the token file."""
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("refresh_token")
    except FileNotFoundError:
        print(f"Error: {TOKEN_FILE} not found. Cannot refresh token.")
        return None
    except Exception as e:
        print(f"Error reading {TOKEN_FILE} for refresh token: {e}")
        return None

def save_tokens(tokens_data):
    """Saves the new tokens data to the token file."""
    try:
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump(tokens_data, f, indent=2)
        print(f"Tokens successfully saved to {TOKEN_FILE}")
    except Exception as e:
        print(f"Error saving tokens to {TOKEN_FILE}: {e}")

def refresh_access_token():
    """Refreshes the access token using the refresh token."""
    refresh_token = get_refresh_token()
    if not refresh_token:
        print("No refresh token available. Cannot refresh.")
        return None

    # Assuming client_id and client_secret are available as environment variables
    client_id = os.environ.get("TINY_CLIENT_ID")
    client_secret = os.environ.get("TINY_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("TINY_CLIENT_ID or TINY_CLIENT_SECRET environment variables not set. Cannot refresh token.")
        return None

    payload = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token
    }

    try:
        print("Attempting to refresh access token...")
        response = requests.post(TINY_ACCOUNTS_TOKEN_URL, data=payload)
        response.raise_for_status() # Raise an exception for HTTP errors

        tokens_data = response.json()
        save_tokens(tokens_data)
        print("Access token refreshed successfully.")
        return tokens_data.get("access_token")

    except requests.exceptions.RequestException as e:
        print(f"Error refreshing access token: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during token refresh: {e}")
        return None


def parse_numeric(value_str):
    """Safely parses a string to a float, handling None, empty strings, and commas."""
    if value_str is None or value_str == "":
        return None
    try:
        return float(str(value_str).replace(',', '.'))
    except ValueError:
        # print(f"Warning: Could not convert '{value_str}' to numeric.") # Avoid excessive printing
        return None

def process_and_save_order(cursor, order_data):
    """Processes a single order's data and inserts/updates it into the database."""
    try:
        # --- Data Extraction and Cleaning for related tables (contatos, enderecos) ---
        contact_data = order_data.get("contato") or {}
        address_data = contact_data.get("endereco") or {}

        # Process Enderecos first (UPSERT based on content)
        address_id = None
        if address_data:
            endereco = address_data.get("endereco")
            numero = address_data.get("numero")
            complemento = address_data.get("complemento")
            bairro = address_data.get("bairro")
            municipio = address_data.get("municipio")
            cep = address_data.get("cep")
            uf = address_data.get("uf")
            pais = address_data.get("pais")

            cursor.execute("""
                SELECT id FROM enderecos
                WHERE endereco = %s AND numero = %s AND complemento = %s AND bairro = %s
                AND municipio = %s AND cep = %s AND uf = %s AND pais = %s;
            """, (endereco, numero, complemento, bairro, municipio, cep, uf, pais))
            existing_address = cursor.fetchone()

            if existing_address:
                address_id = existing_address[0]
            else:
                cursor.execute("""
                    INSERT INTO enderecos (endereco, numero, complemento, bairro, municipio, cep, uf, pais)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """, (endereco, numero, complemento, bairro, municipio, cep, uf, pais))
                address_id = cursor.fetchone()[0]

        # Process Contatos (UPSERT based on API ID)
        contact_id = contact_data.get("id")
        if contact_id:
            nome_contato = contact_data.get("nome")
            codigo_contato = contact_data.get("codigo")
            fantasia_contato = contact_data.get("fantasia")
            tipo_pessoa_contato = contact_data.get("tipoPessoa")
            cpf_cnpj_contato = contact_data.get("cpfCnpj")
            inscricao_estadual_contato = contact_data.get("inscricaoEstadual")
            rg_contato = contact_data.get("rg")
            telefone_contato = contact_data.get("telefone")
            celular_contato = contact_data.get("celular")
            email_contato = contact_data.get("email")

            upsert_contact_sql = """
                INSERT INTO contatos (
                    id, nome, codigo, fantasia, tipo_pessoa, cpf_cnpj,
                    inscricao_estadual, rg, telefone, celular, email, id_endereco
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (id) DO UPDATE SET
                    nome = EXCLUDED.nome,
                    codigo = EXCLUDED.codigo,
                    fantasia = EXCLUDED.fantasia,
                    tipo_pessoa = EXCLUDED.tipo_pessoa,
                    cpf_cnpj = EXCLUDED.cpf_cnpj,
                    inscricao_estadual = EXCLUDED.inscricao_estadual,
                    rg = EXCLUDED.rg,
                    telefone = EXCLUDED.telefone,
                    celular = EXCLUDED.celular,
                    email = EXCLUDED.email,
                    id_endereco = EXCLUDED.id_endereco;
            """
            cursor.execute(upsert_contact_sql, (
                contact_id, nome_contato, codigo_contato, fantasia_contato,
                tipo_pessoa_contato, cpf_cnpj_contato, inscricao_estadual_contato,
                rg_contato, telefone_contato, celular_contato, email_contato, address_id
            ))
        else:
            contact_id = None

        # --- Data Extraction and Cleaning for ordens_servico ---
        order_id = order_data.get("id")
        if order_id is None:
            print(f"Skipping order due to missing ID: {order_data}")
            return # Skip this order

        numero_ordem_servico = order_data.get("numeroOrdemServico")
        situacao_str = order_data.get("situacao", "")
        situacao = situacao_str.split(" - ")[0] if " - " in situacao_str else situacao_str

        data_emissao_str = order_data.get("data")
        data_emissao = data_emissao_str if data_emissao_str and data_emissao_str != '0000-00-00' else None

        data_prevista_str = order_data.get("dataPrevista")
        data_prevista = data_prevista_str if data_prevista_str and not data_prevista_str.startswith('0000-00-00') else None

        data_conclusao_str = order_data.get("dataConclusao")
        data_conclusao = data_conclusao_str if data_conclusao_str and data_conclusao_str != '0000-00-00' else None

        total_servicos = parse_numeric(order_data.get("totalServicos"))
        total_ordem_servico = parse_numeric(order_data.get("totalOrdemServico"))
        total_pecas = parse_numeric(order_data.get("totalPecas"))
        alq_comissao = parse_numeric(order_data.get("alqComissao"))
        vlr_comissao = parse_numeric(order_data.get("vlrComissao"))
        desconto = parse_numeric(order_data.get("desconto"))

        equipamento = order_data.get("equipamento")
        equipamento_serie = order_data.get("equipamentoSerie") if order_data.get("equipamentoSerie") != "" else None
        descricao_problema = order_data.get("descricaoProblema")
        observacoes = order_data.get("observacoes")
        observacoes_internas = order_data.get("observacoesInternas")
        orcar = order_data.get("orcar")
        orcado = order_data.get("orcado")
        id_lista_preco = order_data.get("idListaPreco") if order_data.get("idListaPreco") != 0 else None
        tecnico = order_data.get("tecnico")
        id_conta_contabil = order_data.get("idContaContabil") if order_data.get("idContaContabil") != 0 else None

        vendedor_data = order_data.get("vendedor") or {}
        id_vendedor = vendedor_data.get("id")
        categoria_data = order_data.get("categoria") or {}
        id_categoria_os = categoria_data.get("id")
        categoria_descricao = categoria_data.get("descricao")
        # Upsert categoria_os if id and descricao are present
        if id_categoria_os and categoria_descricao:
            upsert_categoria_sql = """
                INSERT INTO categorias_os (id, descricao)
                VALUES (%s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    descricao = EXCLUDED.descricao;
            """
            cursor.execute(upsert_categoria_sql, (id_categoria_os, categoria_descricao))
        forma_pagamento_data = order_data.get("formaPagamento") or {}
        id_forma_pagamento = forma_pagamento_data.get("id")
        forma_pagamento_nome = forma_pagamento_data.get("nome")
        # Upsert forma_pagamento if id and nome are present
        if id_forma_pagamento and forma_pagamento_nome is not None:
            upsert_forma_pagamento_sql = """
                INSERT INTO formas_pagamento (id, nome)
                VALUES (%s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    nome = EXCLUDED.nome;
            """
            cursor.execute(upsert_forma_pagamento_sql, (id_forma_pagamento, forma_pagamento_nome))

        # --- Custom Field Mapping ---
        linha_dispositivo = None
        equipamento_lower = equipamento.lower() if equipamento else ""
        if "iphone" in equipamento_lower:
            linha_dispositivo = "iphone"
        elif "mac" in equipamento_lower:
            linha_dispositivo = "mac"
        elif "ipad" in equipamento_lower:
            linha_dispositivo = "ipad"
        elif "apple watch" in equipamento_lower:
            linha_dispositivo = "apple_watch"
        else:
            linha_dispositivo = "outros"

        tipo_servico = None
        problema_lower = descricao_problema.lower() if descricao_problema else ""
        if "tela" in problema_lower:
            tipo_servico = "troca_tela"
        elif "bateria" in problema_lower:
            tipo_servico = "troca_bateria"
        elif "placa" in problema_lower:
            tipo_servico = "reparo_placa"
        elif "vidro traseira" in problema_lower or "lente camera" in problema_lower:
            tipo_servico = "troca_vidro_traseiro"
        elif "flex" in problema_lower or "carcaça" in problema_lower:
             tipo_servico = "outros_perifericos"
        else:
            tipo_servico = "outros"

        origem_cliente = None # This will be handled later when processing markers

        # --- Database Insertion/Update for ordens_servico ---
        upsert_sql = """
            INSERT INTO ordens_servico (
                id, numero_ordem_servico, situacao, data_emissao, data_prevista,
                data_conclusao, total_servicos, total_ordem_servico, total_pecas,
                equipamento, equipamento_serie, descricao_problema, observacoes,
                observacoes_internas, orcar, orcado, alq_comissao, vlr_comissao,
                desconto, id_lista_preco, tecnico, id_contato, id_vendedor,
                id_categoria_os, id_forma_pagamento, id_conta_contabil,
                linha_dispositivo, tipo_servico, origem_cliente
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (id) DO UPDATE SET
                numero_ordem_servico = EXCLUDED.numero_ordem_servico,
                situacao = EXCLUDED.situacao,
                data_emissao = EXCLUDED.data_emissao,
                data_prevista = EXCLUDED.data_prevista,
                data_conclusao = EXCLUDED.data_conclusao,
                total_servicos = EXCLUDED.total_servicos,
                total_ordem_servico = EXCLUDED.total_ordem_servico,
                total_pecas = EXCLUDED.total_pecas,
                equipamento = EXCLUDED.equipamento,
                equipamento_serie = EXCLUDED.equipamento_serie,
                descricao_problema = EXCLUDED.descricao_problema,
                observacoes = EXCLUDED.observacoes,
                observacoes_internas = EXCLUDED.observacoes_internas,
                orcar = EXCLUDED.orcar,
                orcado = EXCLUDED.orcado,
                alq_comissao = EXCLUDED.alq_comissao,
                vlr_comissao = EXCLUDED.vlr_comissao,
                desconto = EXCLUDED.desconto,
                id_lista_preco = EXCLUDED.id_lista_preco,
                tecnico = EXCLUDED.tecnico,
                id_contato = EXCLUDED.id_contato,
                id_vendedor = EXCLUDED.id_vendedor,
                id_categoria_os = EXCLUDED.id_categoria_os,
                id_forma_pagamento = EXCLUDED.id_forma_pagamento,
                id_conta_contabil = EXCLUDED.id_conta_contabil,
                linha_dispositivo = EXCLUDED.linha_dispositivo,
                tipo_servico = EXCLUDED.tipo_servico,
                origem_cliente = EXCLUDED.origem_cliente,
                data_extracao = CURRENT_TIMESTAMP;

        """
        cursor.execute(upsert_sql, (
            order_id, numero_ordem_servico, situacao, data_emissao, data_prevista,
            data_conclusao, total_servicos, total_ordem_servico, total_pecas,
            equipamento, equipamento_serie, descricao_problema, observacoes,
            observacoes_internas, orcar, orcado, alq_comissao, vlr_comissao,
            desconto, id_lista_preco, tecnico, contact_id, id_vendedor,
            id_categoria_os, id_forma_pagamento, id_conta_contabil,
            linha_dispositivo, tipo_servico, origem_cliente
        ))
        # Note: commit is handled outside this function for batch processing

    except Exception as e:
        print(f"Error processing Order ID {order_data.get('id', 'N/A')}: {e}")
        # Note: rollback is handled outside this function for batch processing
        raise # Re-raise to signal failure for batch handling

def fetch_and_process_orders(token, conn, cursor):
    """Fetches order IDs and details, then processes and saves them to the database."""
    headers = {"Authorization": f"Bearer {token}"}
    start_year = 2013
    end_year = 2025
    batch_size = 50 # Process and commit in batches

    # Iterate through years and months in reverse, in 3-month chunks
    # Start from March 2025 and go back to January 2013
    current_year = 2025
    current_month = 3 # Start from March 2025

    while current_year >= 2013:
        # Determine the end date of the current 3-month period
        end_month = current_month
        end_year = current_year

        # Determine the start date of the current 3-month period
        start_month = current_month - 2
        start_year = current_year
        if start_month < 1:
            start_month += 12
            start_year -= 1

        # Handle the very first period if it starts before 2013
        if start_year < 2013:
            start_year = 2013
            start_month = 1

        data_inicial = f"{start_year}-{start_month:02d}-01"

        # Calculate the last day of the end month
        if end_month == 12:
             last_day = (time.mktime((end_year + 1, 1, 1, 0, 0, 0, 0, 0, 0)) - 1)
        else:
             last_day = (time.mktime((end_year, end_month + 1, 1, 0, 0, 0, 0, 0, 0)) - 1)
        data_final = time.strftime("%Y-%m-%d", time.localtime(last_day))

        # Skip April 2025 if it falls within this period (shouldn't with 3-month chunks starting Mar 2025)
        # Added a check just in case the logic is adjusted or for safety.
        if start_year <= 2025 <= end_year and 4 in range(start_month, end_month + 1):
             if start_year == 2025 and start_month <= 4 and end_month >= 4:
                 print(f"Skipping April 2025 as per request.")
                 # Adjust the date range to exclude April 2025 if it's the only month in the period
                 if start_month == 4 and end_month == 4:
                     # This case should be skipped entirely by the outer loop logic, but added for robustness
                     current_month -= 3
                     if current_month < 1:
                         current_month += 12
                         current_year -= 1
                     continue
                 elif start_month == 4:
                     # If the period starts in April, start from May instead
                     data_inicial = f"{year}-05-01"
                     print(f"Adjusting period to exclude April 2025: {data_inicial} to {data_final}")
                 elif end_month == 4:
                     # If the period ends in April, end in March instead
                     data_final = f"{year}-03-31"
                     print(f"Adjusting period to exclude April 2025: {data_inicial} to {data_final}")
                 # If April is in the middle, the current logic doesn't split the period.
                 # For simplicity, we'll skip the entire 3-month period if April 2025 is included.
                 # A more complex approach would split the period around April.
                 # Given the requirement is only to exclude April 2025, and we are iterating backwards in 3-month chunks,
                 # starting from March 2025, April 2025 will not be included in any 3-month chunk.
                 # The initial check `if year == 2025 and month == 4:` in the previous month-by-month loop was sufficient.
                 # I will remove the complex April exclusion logic here and rely on the iteration logic.

        # Re-evaluate the April 2025 skip based on the 3-month period
        # If the period is Jan-Mar 2025, we process it.
        # If the period is Apr-Jun 2025, we would skip it (but our loop ends at Mar 2025).
        # If the period spans April 2025 (e.g., Mar-May 2025), we would need more complex logic to split.
        # Given the requirement is *only* to exclude April 2025, and our loop ends at March 2025,
        # the only month we need to explicitly skip is April 2025 itself if the loop structure included it.
        # Since we are iterating backwards in 3-month chunks ending at March 2025, April 2025 is not included.
        # The previous explicit check for `year == 2025 and month == 4:` is no longer necessary with this iteration logic.

        print(f"Fetching orders for {data_inicial} to {data_final}...")

        params = {
            "situacao": "3",  # Finalizada
            "dataInicialEmissao": data_inicial,
            "dataFinalEmissao": data_final,
            "limit": 100, # API limit per page
            "offset": 0
        }

        month_order_ids = [] # Renamed to period_order_ids for clarity
        while True:
            resp = requests.get(f"{API_BASE}/ordem-servico", headers=headers, params=params)
            
            # Check for 401 and refresh token
            if resp.status_code == 401:
                print("Received 401 Unauthorized. Attempting to refresh token...")
                new_token = refresh_access_token()
                if new_token:
                    headers["Authorization"] = f"Bearer {new_token}"
                    print("Token refreshed. Retrying the last request...")
                    resp = requests.get(f"{API_BASE}/ordem-servico", headers=headers, params=params)
                else:
                    print("Failed to refresh token. Cannot continue fetching order list.")
                    break # Cannot proceed without a valid token

            if resp.status_code != 200:
                print(f"Failed to fetch order list for {data_inicial} to {data_final}: {resp.status_code} {resp.text}")
                break

            data = resp.json()
            items = data.get("itens", [])
            if not items:
                break
            current_page_ids = [item["id"] for item in items if "id" in item]
            month_order_ids.extend(current_page_ids) # Keep name month_order_ids for now
            print(f"Fetched {len(current_page_ids)} order IDs for {data_inicial} to {data_final} (total for period: {len(month_order_ids)})")

            if len(items) < params["limit"]:
                break
            params["offset"] += params["limit"]
            time.sleep(1) # Respect API rate limits for listing

        print(f"Fetching details and processing {len(month_order_ids)} orders for {data_inicial} to {data_final}...")
        detailed_orders_batch = []
        for idx, order_id in enumerate(month_order_ids):
            url = f"{API_BASE}/ordem-servico/{order_id}"
            try:
                resp = requests.get(url, headers=headers)
                
                # Check for 401 and refresh token
                if resp.status_code == 401:
                    print(f"Received 401 Unauthorized for Order ID {order_id}. Attempting to refresh token...")
                    new_token = refresh_access_token()
                    if new_token:
                        headers["Authorization"] = f"Bearer {new_token}"
                        print(f"Token refreshed. Retrying fetch for Order ID {order_id}...")
                        resp = requests.get(url, headers=headers)
                    else:
                        print(f"Failed to refresh token. Cannot fetch details for Order ID {order_id}.")
                        continue # Skip this order if token refresh fails

                resp.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                order_data = resp.json()

                if isinstance(order_data, dict) and "id" in order_data:
                     detailed_orders_batch.append(order_data)
                else:
                     print(f"Warning: Unexpected detail format for order {order_id}. Skipping.")

            except requests.exceptions.RequestException as e:
                print(f"Error fetching details for Order ID {order_id}: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    print(f"Response status code: {e.response.status_code}")
                    print(f"Response text: {e.response.text}")
                # Continue to the next order even if fetching one fails
            except Exception as e:
                print(f"An unexpected error occurred fetching details for Order ID {order_id}: {e}")
                # Continue to the next order

            # Process and save in batches
            if len(detailed_orders_batch) >= batch_size or (idx == len(month_order_ids) - 1 and detailed_orders_batch):
                print(f"Processing batch of {len(detailed_orders_batch)} orders...")
                try:
                    for order_data_item in detailed_orders_batch:
                        process_and_save_order(cursor, order_data_item)
                    conn.commit()
                    print(f"Successfully processed and committed batch.")
                except Exception as e:
                    conn.rollback()
                    print(f"Error processing or saving batch: {e}. Rolling back batch.")
                finally:
                    detailed_orders_batch = [] # Clear batch regardless of success

            time.sleep(1) # Respect API rate limits for details

        # Move to the previous 3-month period
        current_month -= 3
        if current_month < 1:
            current_month += 12
            current_year -= 1

    # Process any remaining items in the last batch (if the loop finishes mid-batch)
    if detailed_orders_batch:
         print(f"Processing final batch of {len(detailed_orders_batch)} orders...")
         try:
             for order_data_item in detailed_orders_batch:
                 process_and_save_order(cursor, order_data_item)
             conn.commit()
             print(f"Successfully processed and committed final batch.")
         except Exception as e:
             conn.rollback()
             print(f"Error processing or saving final batch: {e}. Rolling back final batch.")


def main():
    token = get_access_token()
    if not token:
        print("No access token found.")
        return

    conn = get_db_connection()
    if not conn:
        return

    try:
        cur = conn.cursor()
        fetch_and_process_orders(token, conn, cur)
        cur.close()
    except Exception as e:
        print(f"An error occurred during the fetching and processing: {e}")
    finally:
        close_db_connection(conn)

if __name__ == "__main__":
    main()
