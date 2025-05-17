import requests
import json
import time
from db_utils import get_db_connection, close_db_connection
from datetime import datetime
import os
import logging
import random
import csv

API_BASE = "https://api.tiny.com.br/public-api/v3"
TOKEN_FILE = "tiny_token.json"
TINY_ACCOUNTS_TOKEN_URL = "https://accounts.tiny.com.br/realms/tiny/protocol/openid-connect/token"
FAILED_ORDERS_FILE = "falhas_extrac.csv"

logger = logging.getLogger(__name__)

def get_access_token():
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
    try:
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump(tokens_data, f, indent=2)
        print(f"Tokens successfully saved to {TOKEN_FILE}")
    except Exception as e:
        print(f"Error saving tokens to {TOKEN_FILE}: {e}")

def refresh_access_token():
    refresh_token = get_refresh_token()
    if not refresh_token:
        print("No refresh token available. Cannot refresh.")
        return None
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
        response.raise_for_status()
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
    if value_str is None or value_str == "":
        return None
    try:
        return float(str(value_str).replace(',', '.'))
    except ValueError:
        return None

def process_and_save_order(cursor, order_data):
    """Processa os dados de uma ordem de serviço e insere/atualiza no banco de dados.
    Ignora os campos 'orcar' e 'orcado' que podem causar erros."""
    try:
        # --- Extração e limpeza de dados para tabelas relacionadas (contatos, enderecos) ---
        contact_data = order_data.get("contato") or {}
        address_data = contact_data.get("endereco") or {}

        # Processa Enderecos primeiro (UPSERT baseado no conteúdo)
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

        # Processa Contatos (UPSERT baseado no ID da API)
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

        # --- Extração e limpeza de dados para ordens_servico ---
        order_id = order_data.get("id")
        if order_id is None:
            logger.error(f"Skipping order due to missing ID: {order_data}")
            return # Pula esta ordem

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
        # Removidos os campos problemáticos orcar e orcado
        id_lista_preco = order_data.get("idListaPreco") if order_data.get("idListaPreco") != 0 else None
        tecnico = order_data.get("tecnico")
        id_conta_contabil = order_data.get("idContaContabil") if order_data.get("idContaContabil") != 0 else None

        vendedor_data = order_data.get("vendedor") or {}
        id_vendedor = vendedor_data.get("id")
        categoria_data = order_data.get("categoria") or {}
        id_categoria_os = categoria_data.get("id")
        categoria_descricao = categoria_data.get("descricao")
        # Upsert categoria_os se id e descricao estiverem presentes
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
        # Upsert forma_pagamento se id e nome estiverem presentes
        if id_forma_pagamento and forma_pagamento_nome is not None:
            upsert_forma_pagamento_sql = """
                INSERT INTO formas_pagamento (id, nome)
                VALUES (%s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    nome = EXCLUDED.nome;
            """
            cursor.execute(upsert_forma_pagamento_sql, (id_forma_pagamento, forma_pagamento_nome))

        # --- Mapeamento de campos personalizados ---
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

        origem_cliente = None # Será tratado posteriormente ao processar marcadores

        # --- Inserção/Atualização no banco de dados para ordens_servico ---
        # Removidos os campos orcar e orcado da query
        upsert_sql = """
            INSERT INTO ordens_servico (
                id, numero_ordem_servico, situacao, data_emissao, data_prevista,
                data_conclusao, total_servicos, total_ordem_servico, total_pecas,
                equipamento, equipamento_serie, descricao_problema, observacoes,
                observacoes_internas, alq_comissao, vlr_comissao,
                desconto, id_lista_preco, tecnico, id_contato, id_vendedor,
                id_categoria_os, id_forma_pagamento, id_conta_contabil,
                linha_dispositivo, tipo_servico, origem_cliente
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
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
            observacoes_internas, alq_comissao, vlr_comissao,
            desconto, id_lista_preco, tecnico, contact_id, id_vendedor,
            id_categoria_os, id_forma_pagamento, id_conta_contabil,
            linha_dispositivo, tipo_servico, origem_cliente
        ))
        # Nota: commit é tratado fora desta função para processamento em lote

    except Exception as e:
        logger.error(f"Error processing Order ID {order_data.get('id', 'N/A')}: {e}")
        # Nota: rollback é tratado fora desta função para processamento em lote
        raise # Re-levanta a exceção para sinalizar falha para tratamento em lote

def fetch_and_process_orders(token, conn, cursor):
    """Extrai OS do período de 2014-01-01 até 2016-12-31, utilizando lotes mensais."""
    headers = {"Authorization": f"Bearer {token}"}
    batch_size = 50
    
    # Define lotes mensais de 2014 a 2016
    batches = []
    
    # Gera lotes mensais para 2014-2016
    for year in range(2014, 2017):
        for month in range(1, 13):
            # Para meses de 31 dias
            if month in [1, 3, 5, 7, 8, 10, 12]:
                batches.append((f"{year}-{month:02d}-01", f"{year}-{month:02d}-31"))
            # Para fevereiro (considerando anos bissextos)
            elif month == 2:
                if year == 2016:  # 2016 foi ano bissexto
                    batches.append((f"{year}-{month:02d}-01", f"{year}-{month:02d}-29"))
                else:
                    batches.append((f"{year}-{month:02d}-01", f"{year}-{month:02d}-28"))
            # Para meses de 30 dias
            else:
                batches.append((f"{year}-{month:02d}-01", f"{year}-{month:02d}-30"))
    
    logger.info(f"Total de lotes mensais a processar: {len(batches)}")
    
    # Armazena falhas para tentativas futuras
    failed_orders = []
    
    for start_date, end_date in batches:
        logger.info(f"Fetching orders for {start_date} to {end_date}...")
        params = {
            "situacao": "3",  # Finalizada
            "dataInicialEmissao": start_date,
            "dataFinalEmissao": end_date,
            "limit": 100,
            "offset": 0
        }
        month_order_ids = []
        while True:
            try:
                resp = requests.get(f"{API_BASE}/ordem-servico", headers=headers, params=params)
                
                if resp.status_code == 401:
                    logger.error("Received 401 Unauthorized. Attempting to refresh token...")
                    new_token = refresh_access_token()
                    if new_token:
                        token = new_token
                        headers["Authorization"] = f"Bearer {token}"
                        logger.info("Token refreshed. Retrying the last request...")
                        resp = requests.get(f"{API_BASE}/ordem-servico", headers=headers, params=params)
                    else:
                        logger.error("Failed to refresh token. Cannot continue fetching order list.")
                        break
                        
                if resp.status_code != 200:
                    logger.error(f"Failed to fetch order list for {start_date} to {end_date}: {resp.status_code} {resp.text}")
                    # Tenta novamente com um pequeno atraso para problemas temporários
                    time.sleep(2)
                    continue
                
                data = resp.json()
                items = data.get("itens", [])
                if not items:
                    break
                
                current_page_ids = [item["id"] for item in items if "id" in item]
                month_order_ids.extend(current_page_ids)
                logger.info(f"Fetched {len(current_page_ids)} order IDs for {start_date} to {end_date} (total for period: {len(month_order_ids)})")
                
                if len(items) < params["limit"]:
                    break
                    
                params["offset"] += params["limit"]
                time.sleep(1)  # Respeita limites de taxa da API
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Network error during order list fetch: {str(e)}")
                time.sleep(5)  # Aguarda um pouco mais em caso de erro de rede
                continue
        
        logger.info(f"Fetching details and processing {len(month_order_ids)} orders for {start_date} to {end_date}...")
        processed_count = 0
        failed_count = 0
        
        for idx, order_id in enumerate(month_order_ids):
            url = f"{API_BASE}/ordem-servico/{order_id}"
            try:
                resp = requests.get(url, headers=headers, timeout=30)  # Adiciona timeout para evitar esperas infinitas
                
                if resp.status_code == 401:
                    logger.error("Received 401 Unauthorized while fetching order details. Attempting to refresh token...")
                    new_token = refresh_access_token()
                    if new_token:
                        token = new_token
                        headers["Authorization"] = f"Bearer {token}"
                        logger.info("Token refreshed. Retrying the request...")
                        resp = requests.get(url, headers=headers, timeout=30)
                    else:
                        logger.error("Failed to refresh token. Skipping this order.")
                        failed_orders.append((order_id, start_date, "Token refresh failure"))
                        failed_count += 1
                        continue
                        
                if resp.status_code == 500:
                    logger.error(f"Received 500 error for order ID {order_id}. Skipping this order.")
                    failed_orders.append((order_id, start_date, "Internal Server Error"))
                    failed_count += 1
                    continue
                    
                if resp.status_code != 200:
                    logger.error(f"Failed to fetch order details for ID {order_id}: {resp.status_code} {resp.text}")
                    failed_orders.append((order_id, start_date, f"HTTP {resp.status_code}: {resp.text}"))
                    failed_count += 1
                    continue
                    
                order_data = resp.json().get("ordemServico", {})
                if not order_data:
                    logger.error(f"Empty or invalid order data received for ID {order_id}")
                    failed_orders.append((order_id, start_date, "Empty or invalid order data"))
                    failed_count += 1
                    continue
                    
                process_and_save_order(cursor, order_data)
                processed_count += 1
                
                # Commit a cada lote para evitar perder muitos dados em caso de falha
                if (processed_count % batch_size == 0):
                    try:
                        conn.commit()
                        logger.info(f"Batch committed. Processed {processed_count}/{len(month_order_ids)} orders so far.")
                    except Exception as e:
                        logger.error(f"Error committing batch: {str(e)}")
                        conn.rollback()
                        
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout fetching order ID {order_id}. Skipping this order.")
                failed_orders.append((order_id, start_date, "Request timeout"))
                failed_count += 1
                continue
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Network error fetching order ID {order_id}: {str(e)}")
                failed_orders.append((order_id, start_date, f"Network error: {str(e)}"))
                failed_count += 1
                continue
                    
            except Exception as e:
                logger.error(f"Error processing order ID {order_id}: {str(e)}")
                failed_orders.append((order_id, start_date, f"Processing error: {str(e)}"))
                failed_count += 1
                continue
    
        # Commit final após processar todas as ordens do mês
        try:
            conn.commit()
            logger.info(f"Completed processing for {start_date} to {end_date}. Successfully processed: {processed_count}, Failed: {failed_count}")
        except Exception as e:
            logger.error(f"Error in final commit for period {start_date} to {end_date}: {str(e)}")
            conn.rollback()
    
    # Salva ordens que falharam para processamento posterior
    if failed_orders:
        logger.info(f"Writing {len(failed_orders)} failed orders to 'falhas_extrac.csv'")
        try:
            with open('falhas_extrac.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['order_id', 'date_range', 'error'])
                writer.writerows(failed_orders)
            logger.info(f"Failed orders saved to 'falhas_extrac.csv'")
        except Exception as e:
            logger.error(f"Error saving failed orders: {str(e)}")
    else:
        logger.info("All orders were processed successfully!")

def main():
    conn = get_db_connection()
    cursor = conn.cursor()
    token = get_access_token()
    if not token:
        print("No access token available. Exiting.")
        return
    fetch_and_process_orders(token, conn, cursor)
    close_db_connection(conn, cursor)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
