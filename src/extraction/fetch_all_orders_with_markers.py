import requests
import json
import time
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from db_utils import get_db_connection, close_db_connection
# Alterado para usar process_data_with_tags
from process_data_with_tags import process_order_data as process_order_data_with_tags

# Carregar variáveis de ambiente
load_dotenv()

API_BASE = "https://api.tiny.com.br/public-api/v3"
TOKEN_FILE = "tiny_token.json" # Idealmente, o token deveria ser passado como argumento ou variável de ambiente
TEMP_FILE_PREFIX = "temp_all_orders_"

# Configuração de logging estruturado (simplificado para este script)
def log_message(level, message, **kwargs):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "script": "fetch_all_orders_with_markers",
        "message": message,
        **kwargs
    }
    print(json.dumps(log_entry, ensure_ascii=False))

def get_access_token():
    """Obtém o token de acesso do arquivo de token."""
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        token = data.get("access_token")
        if not token:
            log_message("ERROR", "Access token não encontrado no arquivo", file=TOKEN_FILE)
            return None
        return token
    except FileNotFoundError:
        log_message("ERROR", "Arquivo de token não encontrado", file=TOKEN_FILE)
        return None
    except Exception as e:
        log_message("ERROR", f"Erro ao ler o token de acesso: {e}", file=TOKEN_FILE)
        return None

def get_existing_order_ids_from_db():
    """Obtém os IDs das ordens já existentes no banco de dados."""
    conn = get_db_connection()
    if not conn:
        return []
    
    existing_ids = []
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM ordens_servico;")
        existing_ids = [row[0] for row in cur.fetchall()]
        log_message("INFO", f"Total de ordens existentes no banco: {len(existing_ids)}")
    except Exception as e:
        log_message("ERROR", f"Erro ao obter IDs existentes do banco: {e}")
    finally:
        close_db_connection(conn)
    return existing_ids

def fetch_all_orders_summary(token, data_inicial, data_final):
    """
    Busca um resumo de todas as ordens (ID e marcadores_api) para um intervalo de datas,
    sem filtro de situação, usando paginação.
    """
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "dataInicialEmissao": data_inicial,
        "dataFinalEmissao": data_final,
        "limit": 100, # Máximo permitido pela API
        "offset": 0
    }
    # Não inclui "situacao" para buscar todas as situações

    all_orders_summary_list = []
    log_message("INFO", f"Buscando resumos de ordens para o período de {data_inicial} a {data_final}...")

    page_num = 1
    while True:
        try:
            log_message("DEBUG", f"Buscando página {page_num}", params_api=params)
            resp = requests.get(f"{API_BASE}/ordem-servico", headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("itens", [])
            
            if not items:
                log_message("INFO", f"Nenhum item encontrado na página {page_num} para {data_inicial}-{data_final}. Fim da paginação.")
                break
                
            current_page_summaries = []
            for item in items:
                if "id" in item:
                    order_summary = {
                        "id": item["id"],
                        "marcadores_api": item.get("marcadores", []) # Pega os marcadores da listagem
                    }
                    current_page_summaries.append(order_summary)
            
            all_orders_summary_list.extend(current_page_summaries)
            log_message("INFO", f"Obtidos {len(current_page_summaries)} resumos de ordens na página {page_num} para {data_inicial}-{data_final} (total até agora: {len(all_orders_summary_list)})")

            if len(items) < params["limit"]:
                log_message("INFO", f"Última página ({page_num}) alcançada para {data_inicial}-{data_final}.")
                break
                
            params["offset"] += params["limit"]
            page_num += 1
            time.sleep(1.1) # Respeitar os limites de taxa da API (60 GET/min)
            
        except requests.exceptions.RequestException as e:
            log_message("ERROR", f"Erro na API ao buscar lista de ordens (página {page_num}) para {data_inicial}-{data_final}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                log_message("ERROR", f"Detalhes do erro API: status {e.response.status_code}, texto: {e.response.text}")
            break
        except Exception as e:
            log_message("ERROR", f"Erro inesperado ao buscar lista de ordens (página {page_num}): {e}")
            break

    return all_orders_summary_list

def fetch_order_details_batch(token, orders_summary_to_fetch, batch_size=50):
    """
    Busca dados detalhados para cada ordem na lista 'orders_summary_to_fetch',
    adicionando os marcadores no formato correto.
    """
    headers = {"Authorization": f"Bearer {token}"}
    detailed_orders_with_markers = []
    
    num_summaries = len(orders_summary_to_fetch)
    log_message("INFO", f"Total de resumos de ordens para buscar detalhes: {num_summaries}")
    
    for i in range(0, num_summaries, batch_size):
        batch_summaries = orders_summary_to_fetch[i:i+batch_size]
        current_batch_num = i // batch_size + 1
        total_batches = (num_summaries + batch_size - 1) // batch_size
        
        log_message("INFO", f"Processando lote de detalhes {current_batch_num}/{total_batches} ({len(batch_summaries)} ordens)")
        
        batch_detailed_orders = []
        for idx, order_summary in enumerate(batch_summaries):
            order_id = order_summary["id"]
            marcadores_api = order_summary.get("marcadores_api", []) # Marcadores da listagem
            
            url = f"{API_BASE}/ordem-servico/{order_id}"
            log_message("DEBUG", f"Buscando detalhes para Ordem ID {order_id} (item {idx+1}/{len(batch_summaries)} do lote {current_batch_num})")
            
            try:
                resp = requests.get(url, headers=headers)
                resp.raise_for_status()
                order_data = resp.json() # Detalhes completos da OS

                if isinstance(order_data, dict) and "id" in order_data:
                    # Formatar marcadores para o formato esperado por process_data_with_tags.py
                    # [{"marcador": {"descricao": "Desc1"}}, ...]
                    formatted_markers = []
                    if marcadores_api and isinstance(marcadores_api, list):
                        for m_api_item in marcadores_api:
                            if isinstance(m_api_item, str):
                                formatted_markers.append({"marcador": {"descricao": m_api_item}})
                            elif isinstance(m_api_item, dict):
                                if "marcador" in m_api_item and isinstance(m_api_item["marcador"], dict) and "descricao" in m_api_item["marcador"]:
                                    formatted_markers.append({"marcador": {"descricao": m_api_item["marcador"]["descricao"]}})
                                elif "descricao" in m_api_item:
                                    formatted_markers.append({"marcador": {"descricao": m_api_item["descricao"]}})
                                else:
                                    log_message("WARNING", f"Formato de marcador da API inesperado (dict sem 'descricao' ou 'marcador.descricao') para OS ID {order_id}: {m_api_item}")
                            else:
                                log_message("WARNING", f"Tipo de marcador da API inesperado para OS ID {order_id}: {type(m_api_item)}")
                    
                    order_data["marcadores"] = formatted_markers # Adiciona a lista (possivelmente vazia)
                    batch_detailed_orders.append(order_data)
                    log_message("DEBUG", f"  Ordem ID {order_id} obtida e marcadores formatados.")
                else:
                    log_message("WARNING", f"  Formato de resposta inesperado ou ID ausente para ordem {order_id}. Ignorando. Resposta: {order_data}")

            except requests.exceptions.RequestException as e:
                log_message("ERROR", f"  Erro na API ao buscar detalhes para Ordem ID {order_id}: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    log_message("ERROR", f"  Detalhes do erro API: status {e.response.status_code}, texto: {e.response.text}")
            except Exception as e:
                log_message("ERROR", f"  Erro inesperado ao buscar detalhes para Ordem ID {order_id}: {e}")

            time.sleep(1.1) # Pausa para respeitar os limites de taxa da API
        
        detailed_orders_with_markers.extend(batch_detailed_orders)
        
        # Salvar o lote em um arquivo temporário para segurança e depuração
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_filename = f"{TEMP_FILE_PREFIX}batch_details_{current_batch_num}_{timestamp}.json"
        try:
            with open(temp_filename, "w", encoding="utf-8") as f:
                json.dump({"detailed_orders": batch_detailed_orders}, f, ensure_ascii=False, indent=2)
            log_message("INFO", f"Lote de detalhes {current_batch_num} salvo em {temp_filename}")
        except Exception as e:
            log_message("ERROR", f"Erro ao salvar lote temporário {temp_filename}: {e}")
            
    return detailed_orders_with_markers

def save_and_process_orders_with_markers(detailed_orders, period_label):
    """Salva as ordens detalhadas (com marcadores) em um arquivo JSON e as processa para o banco de dados."""
    if not detailed_orders:
        log_message("INFO", f"Nenhuma ordem detalhada para salvar/processar para o período {period_label}.")
        return
        
    # Salvar em arquivo JSON final do período
    output_filename = f"all_orders_with_markers_{period_label}.json"
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump({"detailed_orders": detailed_orders}, f, ensure_ascii=False, indent=2)
        log_message("INFO", f"Salvas {len(detailed_orders)} ordens detalhadas com marcadores em {output_filename}")
    except Exception as e:
        log_message("ERROR", f"Erro ao salvar arquivo final {output_filename}: {e}")
        # Decide se quer parar ou continuar apenas processando
        # return

    # Processar para o banco de dados usando process_data_with_tags
    log_message("INFO", f"Processando {len(detailed_orders)} ordens para o banco de dados (com marcadores)...")
    
    # Criar um arquivo temporário para processar os dados (process_data_with_tags espera um path de arquivo)
    temp_process_file = f"temp_process_all_orders_{period_label}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    try:
        with open(temp_process_file, "w", encoding="utf-8") as f:
            json.dump({"detailed_orders": detailed_orders}, f, ensure_ascii=False, indent=2)
        
        # Usar a função importada com alias
        process_order_data_with_tags(temp_process_file) # Não precisa de dry_run=False, update_mode='safe' por padrão
        
    except Exception as e:
        log_message("ERROR", f"Erro durante o processamento dos dados com tags para {temp_process_file}: {e}")
    finally:
        # Remover o arquivo temporário de processamento
        try:
            if os.path.exists(temp_process_file):
                os.remove(temp_process_file)
                log_message("INFO", f"Arquivo temporário de processamento {temp_process_file} removido.")
        except Exception as e:
            log_message("WARNING", f"Não foi possível remover o arquivo temporário de processamento {temp_process_file}: {e}")

def fetch_and_process_orders_for_period(token, data_inicial, data_final, period_label):
    """Coordena a busca e processamento de todas as ordens para um período específico."""
    log_message("INFO", f"\n{'='*60}\nIniciando busca e processamento para o período: {period_label} ({data_inicial} a {data_final})\n{'='*60}")
    
    # 1. Buscar resumos de todas as ordens (ID + marcadores_api) do período
    all_orders_summary = fetch_all_orders_summary(token, data_inicial, data_final)
    
    if not all_orders_summary:
        log_message("INFO", f"Nenhum resumo de ordem encontrado na API para o período {period_label}. Nenhum processamento adicional.")
        return 0
    
    log_message("INFO", f"Total de {len(all_orders_summary)} resumos de ordens obtidos da API para {period_label}.")
    
    # 2. Buscar detalhes completos para todas as ordens resumidas, adicionando marcadores formatados
    detailed_orders_with_markers = fetch_order_details_batch(token, all_orders_summary)
    
    if not detailed_orders_with_markers:
        log_message("INFO", f"Nenhum detalhe de ordem pôde ser buscado para o período {period_label}.")
        return 0
        
    # 3. Salvar em arquivo e processar para o banco de dados
    save_and_process_orders_with_markers(detailed_orders_with_markers, period_label)
    
    log_message("INFO", f"Processamento para o período {period_label} concluído. {len(detailed_orders_with_markers)} ordens foram processadas.")
    return len(detailed_orders_with_markers)

def main():
    """Função principal para buscar todas as ordens de 2024 e 2025 com marcadores."""
    log_message("INFO", "Iniciando script para buscar todas as ordens de 2024 e 2025 com marcadores...")
    
    token = get_access_token()
    if not token:
        log_message("CRITICAL", "Token de acesso não obtido. Encerrando script.")
        return

    periods_to_process = []
    # Gerar períodos mensais para 2024 e 2025
    for year in [2024, 2025]:
        for month in range(1, 13):
            data_inicial = datetime(year, month, 1).strftime('%Y-%m-%d')
            if month == 12:
                data_final = datetime(year, month, 31).strftime('%Y-%m-%d')
            else:
                # Para calcular o último dia do mês corretamente
                data_final = (datetime(year, month + 1, 1) - timedelta(days=1)).strftime('%Y-%m-%d')
            
            period_label = f"{year}_{month:02d}"
            periods_to_process.append({"start": data_inicial, "end": data_final, "label": period_label})

    # Para testes, pode-se usar um período menor:
    # periods_to_process = [
    #    {"start": "2024-01-01", "end": "2024-01-05", "label": "2024_Jan_Test5dias"} 
    # ]

    total_processed_count = 0
    for period in periods_to_process:
        count = fetch_and_process_orders_for_period(token, period["start"], period["end"], period["label"])
        total_processed_count += count
        log_message("INFO", f"Pausa de 5 segundos antes do próximo período...")
        time.sleep(5) 

    log_message("INFO", f"Script concluído. Total de {total_processed_count} ordens processadas em todos os períodos.")

if __name__ == "__main__":
    main()
