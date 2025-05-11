import requests
import json
import time
import os
from dotenv import load_dotenv
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().isoformat()}] {msg}")

# Carregar variáveis de ambiente
load_dotenv()

API_BASE = "https://api.tiny.com.br/public-api/v3"
TOKEN_FILE = "tiny_token.json"

def get_access_token():
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("access_token")
    except Exception as e:
        log(f"Erro ao ler o token de acesso: {e}")
        return None

def fetch_orders(token, data_inicial, data_final):
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "dataInicialEmissao": data_inicial,
        "dataFinalEmissao": data_final,
        "limit": 100,
        "offset": 0
    }
    all_orders = []
    log(f"Buscando ordens de {data_inicial} até {data_final}...")
    try:
        while True:
            resp = requests.get(f"{API_BASE}/ordem-servico", headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("itens", [])
            if not items:
                break
            all_orders.extend(items)
            log(f"Obtidas {len(items)} ordens nesta página (total até agora: {len(all_orders)})")
            if len(items) < params["limit"]:
                break
            params["offset"] += params["limit"]
            time.sleep(1)
    except Exception as e:
        log(f"Erro ao buscar lista de ordens: {e}")
    return all_orders

def main():
    token = get_access_token()
    if not token:
        log("Token de acesso não encontrado.")
        return
    data_inicial = "2024-01-01"
    data_final = "2025-05-08"
    orders = fetch_orders(token, data_inicial, data_final)
    if not orders:
        log("Nenhuma ordem encontrada no período.")
        return
    output = {"detailed_orders": orders}
    filename = f"orders_2024_01_01_a_2025_05_08_with_tags.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    log(f"Salvo {len(orders)} ordens em {filename}")

if __name__ == "__main__":
    main()
