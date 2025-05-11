import requests
import json
import time
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from db_utils import get_db_connection, close_db_connection

# Configuração de logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler()]
)

def log_json(level, message, **kwargs):
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "service": "fetch_missing_orders_march_2024",
        "message": message,
        **kwargs
    }
    logging.log(getattr(logging, level.upper(), logging.INFO), json.dumps(log_data, ensure_ascii=False))

# Carregar variáveis de ambiente
load_dotenv()

API_BASE = "https://api.tiny.com.br/public-api/v3"
TOKEN_FILE = "tiny_token.json"
TEMP_FILE_PREFIX = "temp_missing_orders_"

def get_access_token():
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("access_token")
    except Exception as e:
        log_json("ERROR", f"Erro ao ler o token de acesso: {e}")
        return None

def fetch_orders_with_tags(token, data_inicial, data_final, situacao="3"):
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "situacao": situacao,  # 3 = Finalizada
        "dataInicialEmissao": data_inicial,
        "dataFinalEmissao": data_final,
        "limit": 100,
        "offset": 0
    }
    all_orders = []
    log_json("INFO", f"Buscando ordens finalizadas de {data_inicial} a {data_final}")
    try:
        while True:
            resp = requests.get(f"{API_BASE}/ordem-servico", headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("itens", [])
            if not items:
                break
            for item in items:
                order_info = {
                    "id": item.get("id"),
                    "marcadores": item.get("marcadores", []),
                    "numeroOrdemServico": item.get("numeroOrdemServico"),
                    "data": item.get("data"),
                    "situacao": item.get("situacao")
                }
                all_orders.append(order_info)
            log_json("INFO", f"Obtidas {len(items)} ordens nesta página", total_so_far=len(all_orders))
            if len(items) < params["limit"]:
                break
            params["offset"] += params["limit"]
            time.sleep(1)
    except Exception as e:
        log_json("ERROR", f"Erro ao buscar lista de ordens: {e}")
    return all_orders

def fetch_order_details(token, order_id):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{API_BASE}/ordem-servico/{order_id}"
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        order_data = resp.json()
        if isinstance(order_data, dict) and "id" in order_data:
            return order_data
        else:
            log_json("WARNING", f"Formato inesperado para ordem {order_id}")
            return None
    except Exception as e:
        log_json("ERROR", f"Erro ao buscar detalhes para Ordem ID {order_id}: {e}")
        return None

def process_orders_with_tags(token, orders_with_tags):
    detailed_orders = []
    for idx, order_info in enumerate(orders_with_tags):
        order_id = order_info["id"]
        log_json("INFO", f"Buscando detalhes para ordem {order_id}", ordem_idx=idx+1)
        order_details = fetch_order_details(token, order_id)
        if order_details:
            order_details["marcadores"] = order_info.get("marcadores", [])
            detailed_orders.append(order_details)
        time.sleep(1)
    return detailed_orders

def save_and_process_orders(detailed_orders, period_label):
    if not detailed_orders:
        log_json("WARNING", f"Nenhuma ordem detalhada para o período {period_label}")
        return
    output_filename = f"orders_missing_{period_label}_with_tags.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump({"detailed_orders": detailed_orders}, f, ensure_ascii=False, indent=2)
    log_json("INFO", f"Salvas {len(detailed_orders)} ordens detalhadas em {output_filename}")
    # Processar para o banco de dados
    try:
        from process_data_with_tags import process_order_data
        process_order_data(output_filename)
        log_json("INFO", f"Processamento para o banco de dados concluído para {period_label}")
    except Exception as e:
        log_json("ERROR", f"Erro ao processar para o banco de dados: {e}")

def main():
    token = get_access_token()
    if not token:
        log_json("ERROR", "Token de acesso não encontrado.")
        return
    period_label = "2024_02_29_a_2024_03_13"
    data_inicial = "2024-02-29"
    data_final = "2024-03-13"
    orders_with_tags = fetch_orders_with_tags(token, data_inicial, data_final)
    if not orders_with_tags:
        log_json("WARNING", "Nenhuma ordem encontrada para o período especificado.")
        return
    detailed_orders = process_orders_with_tags(token, orders_with_tags)
    save_and_process_orders(detailed_orders, period_label)

if __name__ == "__main__":
    main()
