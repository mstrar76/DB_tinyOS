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

OS_NUMEROS = ["31116", "31113", "31068", "31069", "31050"]

def get_access_token():
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("access_token")
    except Exception as e:
        log(f"Erro ao ler o token de acesso: {e}")
        return None

def fetch_orders_april_2025(token):
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "dataInicialEmissao": "2025-04-01",
        "dataFinalEmissao": "2025-04-30",
        "limit": 100,
        "offset": 0
    }
    all_orders = []
    log("Buscando ordens de abril de 2025...")
    try:
        while True:
            resp = requests.get(f"{API_BASE}/ordem-servico", headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("itens", [])
            if not items:
                break
            all_orders.extend(items)
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
    orders = fetch_orders_april_2025(token)
    if not orders:
        log("Nenhuma ordem encontrada para abril de 2025.")
        return
    # Filtrar pelas OS de interesse
    filtered = [o for o in orders if str(o.get("numeroOrdemServico")) in OS_NUMEROS]
    if not filtered:
        print("Nenhuma das OS especificadas foi encontrada na listagem de abril de 2025.")
        return
    print("\n# Marcadores brutos das OS especificadas\n")
    for o in filtered:
        print(f"## OS {o.get('numeroOrdemServico')} (ID: {o.get('id')})")
        print(f"Data de emissão: {o.get('data')}")
        print("Marcadores brutos:")
        print("```")
        print(json.dumps(o.get("marcadores", []), ensure_ascii=False, indent=2))
        print("```")
        print("---\n")

if __name__ == "__main__":
    main()
