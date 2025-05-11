import requests
import json
import time
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

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
        "service": "view_abril_2025_markers",
        "message": message,
        **kwargs
    }
    logging.log(getattr(logging, level.upper(), logging.INFO), json.dumps(log_data, ensure_ascii=False))

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

def analyze_orders_with_tags(orders_with_tags):
    # Nesta versão, não buscaremos detalhes adicionais de cada ordem
    # Vamos trabalhar apenas com os dados obtidos na listagem, onde os marcadores estão disponíveis
    log_json("INFO", f"Analisando {len(orders_with_tags)} ordens com marcadores")
    
    # Filtramos para incluir apenas as ordens que têm marcadores
    orders_with_tags_present = []
    for order in orders_with_tags:
        if order.get("marcadores"):
            orders_with_tags_present.append(order)
    
    log_json("INFO", f"Total de {len(orders_with_tags_present)} ordens com marcadores presentes")
    return orders_with_tags_present

def extract_marker_data(orders):
    """Extrai e formata os dados dos marcadores das ordens"""
    marker_data = []
    
    for order in orders:
        order_id = order.get("id")
        numero_os = order.get("numeroOrdemServico")
        data_emissao = order.get("data")
        situacao = order.get("situacao")
        marcadores = order.get("marcadores", [])
        
        # Processa os marcadores para exibição
        marcadores_info = []
        for marcador in marcadores:
            if isinstance(marcador, dict):
                # Se for dicionário, extrair informações
                marker_id = marcador.get("id", "N/A")
                nome = marcador.get("nome", "") or marcador.get("name", "") or marcador.get("value", "") or "N/A"
                marcadores_info.append({"id": marker_id, "nome": nome})
            elif isinstance(marcador, str):
                # Se for string, usar diretamente
                marcadores_info.append({"id": "N/A", "nome": marcador})
        
        marker_data.append({
            "id_ordem": order_id,
            "numero_os": numero_os,
            "data": data_emissao,
            "situacao": situacao,
            "marcadores": marcadores_info
        })
    
    return marker_data

def format_markers_markdown(marker_data):
    """Formata os dados dos marcadores em Markdown para exibição"""
    if not marker_data:
        return "## Nenhum dado de marcadores encontrado para o período"
    
    markdown = "# Dados de Marcadores - Ordens de Serviço de Abril 2025\n\n"
    markdown += f"Total de Ordens com Marcadores: {len(marker_data)}\n\n"
    
    # Agrega contagem de marcadores
    marcadores_count = {}
    for order in marker_data:
        for marcador in order["marcadores"]:
            nome = marcador["nome"]
            if nome in marcadores_count:
                marcadores_count[nome] += 1
            else:
                marcadores_count[nome] = 1
    
    # Tabela de contagem de marcadores
    markdown += "## Contagem de Marcadores\n\n"
    markdown += "| Nome do Marcador | Quantidade |\n"
    markdown += "|-----------------|------------|\n"
    for nome, count in sorted(marcadores_count.items(), key=lambda x: x[1], reverse=True):
        if nome and nome != "N/A":
            markdown += f"| {nome} | {count} |\n"
    
    # Informações detalhadas por ordem
    markdown += "\n## Detalhes por Ordem de Serviço\n\n"
    
    for order in marker_data:
        markdown += f"### OS #{order['numero_os']} (ID: {order['id_ordem']})\n\n"
        markdown += f"**Data de Emissão:** {order['data']}\n\n"
        
        if order["marcadores"]:
            markdown += "**Marcadores:**\n\n"
            markdown += "| ID | Nome |\n"
            markdown += "|----|---------|\n"
            for marcador in order["marcadores"]:
                markdown += f"| {marcador['id']} | {marcador['nome']} |\n"
        else:
            markdown += "**Marcadores:** Nenhum marcador associado\n\n"
        
        markdown += "---\n\n"
    
    return markdown

def main():
    token = get_access_token()
    if not token:
        log_json("ERROR", "Token de acesso não encontrado.")
        return
    
    period_label = "abril_2025"
    data_inicial = "2025-04-01"
    data_final = "2025-04-30"
    
    orders_with_tags = fetch_orders_with_tags(token, data_inicial, data_final)
    if not orders_with_tags:
        print("# Nenhuma ordem encontrada para abril de 2025.")
        return
    
    log_json("INFO", f"Obtidas {len(orders_with_tags)} ordens para o período de {data_inicial} a {data_final}")
    
    # Trabalha diretamente com os dados da listagem, sem buscar detalhes adicionais
    # já que os marcadores só estão disponíveis na listagem
    filtered_orders = analyze_orders_with_tags(orders_with_tags)
    marker_data = extract_marker_data(filtered_orders)
    markdown_output = format_markers_markdown(marker_data)
    
    print("\n\n" + markdown_output)
    
    # Opcional: Salvar em arquivo
    with open(f"marcadores_{period_label}.md", "w", encoding="utf-8") as f:
        f.write(markdown_output)
    log_json("INFO", f"Dados de marcadores salvos em marcadores_{period_label}.md")

if __name__ == "__main__":
    main()
