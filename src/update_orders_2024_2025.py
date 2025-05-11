import requests
import json
import time
import os
from datetime import datetime
from dotenv import load_dotenv
from db_utils import get_db_connection, close_db_connection
from process_data import process_order_data

# Carregar variáveis de ambiente
load_dotenv()

API_BASE = "https://api.tiny.com.br/public-api/v3"
TOKEN_FILE = "tiny_token.json"
TEMP_FILE_PREFIX = "temp_orders_"

def get_access_token():
    """Obtém o token de acesso do arquivo de token."""
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("access_token")
    except Exception as e:
        print(f"Erro ao ler o token de acesso: {e}")
        return None

def get_existing_order_ids():
    """Obtém os IDs das ordens já existentes no banco de dados."""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM ordens_servico;")
        existing_ids = [row[0] for row in cur.fetchall()]
        print(f"Total de ordens existentes no banco: {len(existing_ids)}")
        return existing_ids
    except Exception as e:
        print(f"Erro ao obter IDs existentes: {e}")
        return []
    finally:
        close_db_connection(conn)

def fetch_order_ids(token, data_inicial, data_final, situacao="3"):
    """Busca IDs de ordens para um intervalo de datas específico usando paginação."""
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "situacao": situacao,  # 3 = Finalizada
        "dataInicialEmissao": data_inicial,
        "dataFinalEmissao": data_final,
        "limit": 100,
        "offset": 0
    }
    all_ids = []

    print(f"Buscando ordens para o período de {data_inicial} a {data_final}...")

    while True:
        try:
            resp = requests.get(f"{API_BASE}/ordem-servico", headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("itens", [])
            
            if not items:
                break
                
            current_page_ids = [item["id"] for item in items if "id" in item]
            all_ids.extend(current_page_ids)
            print(f"Obtidos {len(current_page_ids)} IDs de ordens para {data_inicial} a {data_final} (total até agora: {len(all_ids)})")

            if len(items) < params["limit"]:
                break
                
            params["offset"] += params["limit"]
            time.sleep(1)  # Respeitar os limites de taxa da API
            
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar lista de ordens para {data_inicial} a {data_final}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Código de status da resposta: {e.response.status_code}")
                print(f"Texto da resposta: {e.response.text}")
            break
            
        except Exception as e:
            print(f"Erro inesperado ao buscar ordens: {e}")
            break

    return all_ids

def fetch_order_details(token, order_ids, existing_ids=None, batch_size=50):
    """Busca dados detalhados para cada ID de ordem, em lotes para melhor gerenciamento."""
    if existing_ids is None:
        existing_ids = []
        
    headers = {"Authorization": f"Bearer {token}"}
    detailed_orders = []
    new_ids = [oid for oid in order_ids if oid not in existing_ids]
    
    print(f"IDs totais obtidos: {len(order_ids)}")
    print(f"IDs novos a serem processados: {len(new_ids)}")
    
    # Processar em lotes para gerenciar melhor o uso de memória
    for i in range(0, len(new_ids), batch_size):
        batch_ids = new_ids[i:i+batch_size]
        print(f"Processando lote {i//batch_size + 1}/{(len(new_ids) + batch_size - 1)//batch_size} ({len(batch_ids)} ordens)")
        
        batch_orders = []
        for idx, order_id in enumerate(batch_ids):
            url = f"{API_BASE}/ordem-servico/{order_id}"
            try:
                resp = requests.get(url, headers=headers)
                resp.raise_for_status()
                order_data = resp.json()

                if isinstance(order_data, dict) and "id" in order_data:
                    batch_orders.append(order_data)
                    print(f"  Ordem {idx+1}/{len(batch_ids)}: ID {order_id} obtida com sucesso")
                else:
                    print(f"  Aviso: Formato inesperado para ordem {order_id}. Ignorando.")

            except requests.exceptions.RequestException as e:
                print(f"  Erro ao buscar detalhes para Ordem ID {order_id}: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    print(f"  Código de status da resposta: {e.response.status_code}")
                    print(f"  Texto da resposta: {e.response.text}")
            except Exception as e:
                print(f"  Erro inesperado ao buscar detalhes para Ordem ID {order_id}: {e}")

            # Pausa para respeitar os limites de taxa da API
            time.sleep(1)
        
        # Adicionar as ordens do lote ao resultado total
        detailed_orders.extend(batch_orders)
        
        # Salvar o lote em um arquivo temporário para segurança
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_filename = f"{TEMP_FILE_PREFIX}batch_{i//batch_size + 1}_{timestamp}.json"
        with open(temp_filename, "w", encoding="utf-8") as f:
            json.dump({"detailed_orders": batch_orders}, f, ensure_ascii=False, indent=2)
        print(f"Lote {i//batch_size + 1} salvo em {temp_filename}")
        
    return detailed_orders

def save_and_process_orders(detailed_orders, period_label):
    """Salva as ordens detalhadas em um arquivo JSON e as processa para o banco de dados."""
    if not detailed_orders:
        print(f"Nenhuma ordem nova para o período {period_label}.")
        return
        
    # Salvar em arquivo JSON
    output_filename = f"orders_{period_label}.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump({"detailed_orders": detailed_orders}, f, ensure_ascii=False, indent=2)
    print(f"Salvas {len(detailed_orders)} ordens detalhadas em {output_filename}")
    
    # Processar para o banco de dados
    print(f"Processando {len(detailed_orders)} ordens para o banco de dados...")
    
    # Criar um arquivo temporário para processar os dados
    temp_process_file = f"temp_process_{period_label}.json"
    with open(temp_process_file, "w", encoding="utf-8") as f:
        json.dump({"detailed_orders": detailed_orders}, f, ensure_ascii=False, indent=2)
    
    # Usar a função existente para processar os dados
    from process_data import process_order_data
    process_order_data(temp_process_file)
    
    # Remover o arquivo temporário após o processamento
    try:
        os.remove(temp_process_file)
        print(f"Arquivo temporário {temp_process_file} removido.")
    except Exception as e:
        print(f"Aviso: Não foi possível remover o arquivo temporário {temp_process_file}: {e}")

def update_orders_for_period(token, data_inicial, data_final, period_label, existing_ids):
    """Atualiza as ordens para um período específico."""
    print(f"\n{'='*50}")
    print(f"Atualizando ordens para o período: {period_label} ({data_inicial} a {data_final})")
    print(f"{'='*50}")
    
    # Buscar IDs de ordens para o período
    order_ids = fetch_order_ids(token, data_inicial, data_final)
    
    if not order_ids:
        print(f"Nenhuma ordem encontrada para o período {period_label}.")
        return
    
    # Buscar detalhes das ordens
    detailed_orders = fetch_order_details(token, order_ids, existing_ids)
    
    # Salvar e processar as ordens
    save_and_process_orders(detailed_orders, period_label)
    
    return len(detailed_orders)

def main():
    """Função principal para atualizar ordens de 2024 e 2025."""
    print("Iniciando atualização de ordens de 2024 e 2025...")
    
    # Obter token de acesso
    token = get_access_token()
    if not token:
        print("Nenhum token de acesso encontrado.")
        return
    
    # Obter IDs existentes para evitar duplicação
    existing_ids = get_existing_order_ids()
    
    # Períodos a serem atualizados
    periods = [
        # 2024 - Completar janeiro e fevereiro que estão faltando
        {"data_inicial": "2024-01-01", "data_final": "2024-01-31", "label": "2024_01"},
        {"data_inicial": "2024-02-01", "data_final": "2024-02-29", "label": "2024_02"},
        
        # 2025 - Verificar se há novas ordens finalizadas em cada mês
        {"data_inicial": "2025-01-01", "data_final": "2025-01-31", "label": "2025_01_update"},
        {"data_inicial": "2025-02-01", "data_final": "2025-02-29", "label": "2025_02_update"},
        {"data_inicial": "2025-03-01", "data_final": "2025-03-31", "label": "2025_03_update"},
        {"data_inicial": "2025-04-01", "data_final": "2025-04-30", "label": "2025_04_update"},
        {"data_inicial": "2025-05-01", "data_final": "2025-05-10", "label": "2025_05_new"}  # Até a data atual
    ]
    
    total_new_orders = 0
    
    # Processar cada período
    for period in periods:
        new_orders = update_orders_for_period(
            token, 
            period["data_inicial"], 
            period["data_final"], 
            period["label"],
            existing_ids
        )
        total_new_orders += new_orders if new_orders else 0
    
    print("\n" + "="*50)
    print(f"Atualização concluída. Total de novas ordens processadas: {total_new_orders}")
    print("="*50)

if __name__ == "__main__":
    main()
