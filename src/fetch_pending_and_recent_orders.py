import requests
import json
import time
from db_utils import get_db_connection, close_db_connection
from datetime import datetime, timedelta
import os
import logging
import logging.config
import json
import random
import csv

API_BASE = "https://api.tiny.com.br/public-api/v3"
TOKEN_FILE = "tiny_token.json"
TINY_ACCOUNTS_TOKEN_URL = "https://accounts.tiny.com.br/realms/tiny/protocol/openid-connect/token"
FAILED_ORDERS_FILE = "falhas_extrac_pending.csv"

# Configuração de logging estruturado em formato JSON
def setup_logging():
    """Configura logging estruturado em formato JSON"""
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                'format': '%(asctime)s %(name)s %(levelname)s %(message)s %(service)s %(correlation_id)s',
            },
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'level': 'INFO',
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': 'pending_orders_extraction.log',
                'formatter': 'standard',
                'level': 'INFO',
            }
        },
        'loggers': {
            '': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
            }
        }
    }
    
    # Tenta usar o formatador JSON se disponível, caso contrário usa o padrão
    try:
        from pythonjsonlogger import jsonlogger
    except ImportError:
        print("pythonjsonlogger não encontrado. Usando formatador padrão.")
        # Remove o formatador JSON se não estiver disponível
        if 'json' in logging_config['formatters']:
            del logging_config['formatters']['json']
    
    logging.config.dictConfig(logging_config)

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
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret
    }
    try:
        resp = requests.post(TINY_ACCOUNTS_TOKEN_URL, data=payload)
        resp.raise_for_status()
        tokens_data = resp.json()
        save_tokens(tokens_data)
        return tokens_data.get("access_token")
    except Exception as e:
        print(f"Error refreshing token: {e}")
        return None

def parse_numeric(value_str):
    """Converte string numérica para float, tratando valores vazios e formatos diferentes."""
    if not value_str or value_str.strip() == "":
        return 0.0
    return float(value_str.replace(".", "").replace(",", "."))

def process_and_save_order(cursor, order_data):
    """
    Processa os dados de uma ordem de serviço e insere/atualiza no banco de dados.
    Ignora os campos 'orcar' e 'orcado' que podem causar erros.
    """
    try:
        if not order_data or not isinstance(order_data, dict):
            logger.error(f"Empty or invalid order data: {order_data}")
            return False
            
        # Verifica se o ID está presente
        order_id = order_data.get('id')
        if not order_id:
            logger.error(f"Order data missing ID: {order_data}")
            return False
            
        # Extrai os campos necessários com tratamento para valores ausentes
        numero_ordem_servico = order_data.get('numero', '')
        situacao = order_data.get('situacao', {}).get('id', '') if isinstance(order_data.get('situacao'), dict) else order_data.get('situacao', '')
        
        # Trata datas - converte strings vazias para None
        data_emissao = order_data.get('data_emissao')
        data_prevista = order_data.get('data_prevista')
        data_conclusao = order_data.get('data_conclusao')
        
        # Converte strings vazias para None para campos de data
        data_emissao = data_emissao if data_emissao else None
        data_prevista = data_prevista if data_prevista else None
        data_conclusao = data_conclusao if data_conclusao else None
        
        # Trata valores numéricos
        total_servicos = parse_numeric(order_data.get('total_servicos', '0'))
        total_ordem_servico = parse_numeric(order_data.get('total_ordem_servico', '0'))
        total_pecas = parse_numeric(order_data.get('total_pecas', '0'))
        
        # Trata campos de texto
        equipamento = order_data.get('equipamento', '')
        equipamento_serie = order_data.get('equipamento_serie', '')
        descricao_problema = order_data.get('descricao_problema', '')
        observacoes = order_data.get('observacoes', '')
        observacoes_internas = order_data.get('observacoes_internas', '')
        
        # Trata comissão
        alq_comissao = parse_numeric(order_data.get('alq_comissao', '0'))
        vlr_comissao = parse_numeric(order_data.get('vlr_comissao', '0'))
        
        # Trata desconto
        desconto = parse_numeric(order_data.get('desconto', '0'))
        
        # Trata IDs relacionados
        id_lista_preco = order_data.get('id_lista_preco', '')
        tecnico = order_data.get('tecnico', '')
        id_contato = order_data.get('id_contato', '')
        id_vendedor = order_data.get('id_vendedor', '')
        id_categoria_os = order_data.get('id_categoria_os', '')
        id_forma_pagamento = order_data.get('id_forma_pagamento', '')
        id_conta_contabil = order_data.get('id_conta_contabil', '')
        
        # Trata campos adicionais
        linha_dispositivo = order_data.get('linha_dispositivo', '')
        tipo_servico = order_data.get('tipo_servico', '')
        origem_cliente = order_data.get('origem_cliente', '')
        
        # Nota: Campos 'orcar' e 'orcado' são ignorados por serem incompatíveis com o banco
        
        # Upsert (INSERT ... ON CONFLICT) na tabela correta "ordens_servico"
        upsert_sql = """
            INSERT INTO ordens_servico (
                id, numero_ordem_servico, situacao, data_emissao, data_prevista,
                data_conclusao, total_servicos, total_ordem_servico, total_pecas,
                equipamento, equipamento_serie, descricao_problema, observacoes,
                observacoes_internas, alq_comissao, vlr_comissao,
                desconto, id_lista_preco, tecnico, id_contato, id_vendedor,
                id_categoria_os, id_forma_pagamento, id_conta_contabil,
                linha_dispositivo, tipo_servico, origem_cliente, data_extracao
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
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
            desconto, id_lista_preco, tecnico, id_contato, id_vendedor,
            id_categoria_os, id_forma_pagamento, id_conta_contabil,
            linha_dispositivo, tipo_servico, origem_cliente
        ))
        
        return True
    except Exception as e:
        logger.error(f"Error processing Order ID {order_data.get('id', 'N/A')}: {e}")
        # Nota: rollback é tratado fora desta função para processamento em lote
        raise # Re-levanta a exceção para sinalizar falha para tratamento em lote

def fetch_and_process_orders(token, conn, cursor):
    """
    Extrai ordens de serviço com status diferente de finalizada (não-3) 
    e também todas as ordens dos últimos 4 dias (independente do status).
    """
    headers = {"Authorization": f"Bearer {token}"}
    batch_size = 50
    
    # Obtém a data atual e calcula datas para os últimos 4 dias
    today = datetime.now()
    four_days_ago = today - timedelta(days=4)
    
    # Formata as datas para o padrão da API
    today_str = today.strftime("%Y-%m-%d")
    four_days_ago_str = four_days_ago.strftime("%Y-%m-%d")
    
    # Define os lotes para processamento
    batches = []
    
    # 1. Ordens pendentes (não finalizadas) em períodos maiores
    # Dividimos em períodos de 6 meses de 2017 até o ano atual
    current_year = today.year
    years = list(range(2017, current_year + 1))
    
    for year in years:
        # Primeiro semestre
        batches.append((f"{year}-01-01", f"{year}-06-30", None))  # Buscaremos todos os status e filtraremos depois
        # Segundo semestre
        batches.append((f"{year}-07-01", f"{year}-12-31", None))
    
    # 2. Todas as ordens dos últimos 4 dias (independente do status)
    batches.append((four_days_ago_str, today_str, None))  # None indica todos os status
    
    logger.info(f"Total de lotes a processar: {len(batches)}")
    
    # Armazena falhas para tentativas futuras
    failed_orders = []
    
    for start_date, end_date, status_list in batches:
        logger.info(f"Buscando ordens de {start_date} a {end_date}...")
        
        # Configuração base de parâmetros (sem filtro de 'situacao')
        params = {
            "dataInicialEmissao": start_date,
            "dataFinalEmissao": end_date,
            "limit": 100,
            "offset": 0
        }
        
        # Buscamos todos os status e filtramos localmente (mantendo somente situacao != 3)
        process_batch_with_params(headers, params, token, conn, cursor, failed_orders, batch_size)
    
    # Salva as falhas em um arquivo CSV para tentativas futuras
    if failed_orders:
        logger.warning(f"Total de {len(failed_orders)} ordens com falha no processamento.")
        try:
            with open(FAILED_ORDERS_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Order ID', 'Error'])
                writer.writerows(failed_orders)
            logger.info(f"Ordens com falha salvas em {FAILED_ORDERS_FILE}")
        except Exception as e:
            logger.error(f"Erro ao salvar arquivo de falhas: {e}")
    else:
        logger.info("Todas as ordens foram processadas com sucesso!")

def process_batch_with_params(headers, params, token, conn, cursor, failed_orders, batch_size):
    """Processa um lote de ordens com os parâmetros especificados."""
    month_order_ids = []
    offset = 0
    params["offset"] = offset
    
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
                logger.error(f"Failed to fetch order list: {resp.status_code} {resp.text}")
                # Tenta novamente com um pequeno atraso para problemas temporários
                time.sleep(random.uniform(1.0, 3.0))
                continue
                
            data = resp.json()
            
            # Tenta extrair os dados da resposta, considerando diferentes estruturas
            orders = None
            
            # Estrutura 1: dados -> ordens_servico
            if "dados" in data and "ordens_servico" in data["dados"]:
                orders = data["dados"]["ordens_servico"]
            
            # Estrutura 2: retorno -> ordens_servico
            elif "retorno" in data and "ordens_servico" in data["retorno"]:
                orders = data["retorno"]["ordens_servico"]
            
            # Estrutura 3: ordens_servico na raiz
            elif "ordens_servico" in data:
                orders = data["ordens_servico"]
            
            # Estrutura 4: retorno -> itens -> ordemServico
            elif "retorno" in data and "itens" in data["retorno"]:
                itens_list = data["retorno"]["itens"]
                orders = [item.get("ordemServico", item) for item in itens_list]
            
            # Estrutura 5: itens na raiz
            elif "itens" in data:
                itens_list = data["itens"]
                orders = [item.get("ordemServico", item) for item in itens_list]
                
            if not orders:
                logger.warning(f"No orders found in response or unexpected response structure: {data.keys()}")
                break
                
            if len(orders) == 0:
                logger.info("No more orders to fetch in this batch.")
                break
                
            logger.info(f"Fetched {len(orders)} orders. Processing...")
            
            # Extrai os IDs das ordens
            for order in orders:
                order_id = order.get("id")
                # Filtra apenas ordens cuja situacao id é diferente de 3 (finalizada)
                situacao_obj = order.get("situacao")
                situacao_id = None
                if isinstance(situacao_obj, dict):
                    situacao_id = situacao_obj.get("id")
                else:
                    situacao_id = situacao_obj

                if order_id and situacao_id != 3:
                    month_order_ids.append(order_id)
            
            # Atualiza o offset para a próxima página
            offset += len(orders)
            params["offset"] = offset
            
            # Se não tiver mais resultados, sai do loop
            if len(orders) < params["limit"]:
                break
                
            # Pequena pausa para não sobrecarregar a API
            time.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            logger.error(f"Error fetching order list: {e}")
            time.sleep(random.uniform(2.0, 5.0))
            continue
    
    # Processa os IDs das ordens em lotes
    logger.info(f"Total de {len(month_order_ids)} ordens encontradas para processamento.")
    
    for i in range(0, len(month_order_ids), batch_size):
        batch = month_order_ids[i:i+batch_size]
        logger.info(f"Processando lote de {len(batch)} ordens ({i+1}-{i+len(batch)} de {len(month_order_ids)})...")
        
        for order_id in batch:
            try:
                # Busca os detalhes da ordem
                order_resp = requests.get(f"{API_BASE}/ordem-servico/{order_id}", headers=headers)
                
                if order_resp.status_code == 401:
                    logger.error("Token expirado ao buscar detalhes da ordem. Renovando...")
                    new_token = refresh_access_token()
                    if new_token:
                        token = new_token
                        headers["Authorization"] = f"Bearer {token}"
                        order_resp = requests.get(f"{API_BASE}/ordem-servico/{order_id}", headers=headers)
                    else:
                        logger.error("Falha ao renovar token. Pulando ordem.")
                        failed_orders.append([order_id, "Token refresh failed"])
                        continue
                
                if order_resp.status_code != 200:
                    logger.error(f"Falha ao buscar detalhes da ordem {order_id}: {order_resp.status_code} {order_resp.text}")
                    failed_orders.append([order_id, f"API Error: {order_resp.status_code}"])
                    continue
                
                order_data = order_resp.json()
                
                # Tenta extrair os dados da ordem, considerando diferentes estruturas
                order_details = None
                
                # Registra as chaves disponíveis para diagnóstico
                logger.debug(f"Order {order_id} response keys: {order_data.keys()}")
                
                # Tenta diferentes caminhos na estrutura de resposta
                if "ordemServico" in order_data:
                    order_details = order_data["ordemServico"]
                elif "retorno" in order_data and "ordemServico" in order_data["retorno"]:
                    order_details = order_data["retorno"]["ordemServico"]
                elif "dados" in order_data:
                    order_details = order_data["dados"]
                elif "id" in order_data:  # A resposta já é a própria ordem
                    order_details = order_data
                
                if not order_details:
                    logger.error(f"Empty or invalid order data for ID {order_id}: {order_data}")
                    failed_orders.append([order_id, "Empty or invalid order data"])
                    continue
                
                # Processa e salva a ordem
                try:
                    conn.autocommit = False  # Desativa autocommit para permitir rollback
                    success = process_and_save_order(cursor, order_details)
                    if success:
                        conn.commit()
                        logger.debug(f"Order {order_id} processed successfully.")
                    else:
                        conn.rollback()
                        logger.error(f"Failed to process order {order_id}.")
                        failed_orders.append([order_id, "Processing error"])
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Error processing order {order_id}: {e}")
                    failed_orders.append([order_id, str(e)])
                finally:
                    conn.autocommit = True  # Restaura configuração original
                
                # Pequena pausa para não sobrecarregar a API
                time.sleep(random.uniform(0.2, 0.8))
                
            except Exception as e:
                logger.error(f"Unexpected error processing order {order_id}: {e}")
                failed_orders.append([order_id, str(e)])
                continue
        
        # Pausa entre lotes
        time.sleep(random.uniform(1.0, 3.0))

def main():
    # Configura logging estruturado
    setup_logging()
    
    # Obtém token de acesso
    token = get_access_token()
    if not token:
        logger.error("Failed to get access token. Exiting.")
        return
    
    # Conecta ao banco de dados
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to connect to database. Exiting.")
        return
    
    # Cria o cursor após obter a conexão
    cursor = conn.cursor()
    
    try:
        logger.info("Database connection established.")
        fetch_and_process_orders(token, conn, cursor)
    except Exception as e:
        logger.error(f"Error in main process: {e}")
    finally:
        # Fecha o cursor primeiro
        if cursor:
            cursor.close()
        # Depois fecha a conexão
        close_db_connection(conn)
        # O log de fechamento já é feito dentro da função close_db_connection

if __name__ == "__main__":
    main()
