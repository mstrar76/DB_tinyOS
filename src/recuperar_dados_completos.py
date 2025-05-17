#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para recuperar dados completos da TinyERP API e atualizar o banco de dados
com proteção contra corrupção de dados.

Este script realiza as seguintes operações:
1. Busca ordens de serviço do período especificado na API TinyERP
2. Para cada ordem, busca os detalhes completos incluindo todos os campos
3. Salva em um arquivo temporário
4. Processa os dados utilizando o modo "safe" (não sobrescreve com NULL)
"""
import requests
import json
import time
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

API_BASE = "https://api.tiny.com.br/public-api/v3"
TOKEN_FILE = "tiny_token.json"

def log_json(level, message, **kwargs):
    """Registra mensagens de log em formato JSON estruturado."""
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "service": "recuperar_dados_completos",
        "message": message,
        **kwargs
    }
    print(json.dumps(log_data, ensure_ascii=False))

def get_access_token():
    """Obtém o token de acesso da API TinyERP."""
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("access_token")
    except Exception as e:
        log_json("ERROR", f"Erro ao ler o token de acesso: {e}")
        return None

def fetch_order_list(token, data_inicial, data_final, situacao="3"):
    """Busca a lista de ordens de serviço do período especificado."""
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "situacao": situacao,  # 3 = Finalizada
        "dataInicialEmissao": data_inicial,
        "dataFinalEmissao": data_final,
        "limit": 100,
        "offset": 0
    }
    all_orders = []
    log_json("INFO", f"Buscando ordens de {data_inicial} a {data_final}")
    
    try:
        page = 1
        while True:
            log_json("INFO", f"Buscando página {page} (offset={params['offset']})")
            resp = requests.get(f"{API_BASE}/ordem-servico", headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("itens", [])
            
            if not items:
                break
                
            all_orders.extend(items)
            log_json("INFO", f"Obtidas {len(items)} ordens nesta página (total: {len(all_orders)})")
            
            if len(items) < params["limit"]:
                break
                
            params["offset"] += params["limit"]
            page += 1
            time.sleep(1)  # Respeitar limites de API
            
    except Exception as e:
        log_json("ERROR", f"Erro ao buscar lista de ordens: {e}")
        
    return all_orders

def fetch_order_details(token, order_id):
    """Busca os detalhes completos de uma ordem específica."""
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

def process_orders_with_details(token, orders_list, output_file, batch_size=100):
    """
    Busca os detalhes completos de cada ordem e adiciona os marcadores.
    Processa em lotes para evitar problemas de memória.
    """
    total_orders = len(orders_list)
    log_json("INFO", f"Processando {total_orders} ordens em lotes de {batch_size}")
    
    # Cria diretório temporário se não existir
    os.makedirs("temp", exist_ok=True)
    
    # Processa em lotes
    for batch_start in range(0, total_orders, batch_size):
        batch_end = min(batch_start + batch_size, total_orders)
        batch = orders_list[batch_start:batch_end]
        batch_num = (batch_start // batch_size) + 1
        total_batches = (total_orders + batch_size - 1) // batch_size
        
        log_json("INFO", f"Processando lote {batch_num}/{total_batches} ({len(batch)} ordens)")
        
        detailed_orders = []
        for idx, order_info in enumerate(batch):
            order_id = order_info["id"]
            order_markers = order_info.get("marcadores", [])
            
            progress = batch_start + idx + 1
            log_json("INFO", f"[{progress}/{total_orders}] Buscando detalhes para ordem {order_id}")
            
            # Busca detalhes completos
            order_details = fetch_order_details(token, order_id)
            if order_details:
                # Adiciona marcadores do endpoint de listagem
                order_details["marcadores"] = order_markers
                detailed_orders.append(order_details)
            else:
                log_json("WARNING", f"Não foi possível obter detalhes para ordem {order_id}")
            
            # Pausa para respeitar limites de API
            time.sleep(1)
        
        # Salva este lote em um arquivo temporário
        batch_file = f"temp/batch_{batch_num}_orders.json"
        with open(batch_file, "w", encoding="utf-8") as f:
            json.dump({"detailed_orders": detailed_orders}, f, ensure_ascii=False, indent=2)
        
        log_json("INFO", f"Lote {batch_num} salvo em {batch_file} ({len(detailed_orders)} ordens)")
        
        # Processa este lote para o banco de dados
        run_processing_script(batch_file)
    
    # Após processar todos os lotes, combina em um arquivo final
    combine_batches(output_file, total_batches)

def run_processing_script(json_file):
    """Executa o script de processamento para o banco de dados."""
    log_json("INFO", f"Processando arquivo {json_file} para o banco de dados")
    
    cmd = f"python src/process_data_with_tags.py {json_file} --modo safe"
    log_json("INFO", f"Executando: {cmd}")
    
    return_code = os.system(cmd)
    if return_code == 0:
        log_json("INFO", f"Processamento do arquivo {json_file} concluído com sucesso")
    else:
        log_json("ERROR", f"Erro no processamento do arquivo {json_file} (código {return_code})")

def combine_batches(output_file, total_batches):
    """Combina todos os arquivos de lotes em um único arquivo final."""
    log_json("INFO", f"Combinando {total_batches} lotes em {output_file}")
    
    all_orders = []
    for batch_num in range(1, total_batches + 1):
        batch_file = f"temp/batch_{batch_num}_orders.json"
        try:
            with open(batch_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                batch_orders = data.get("detailed_orders", [])
                all_orders.extend(batch_orders)
                log_json("INFO", f"Lote {batch_num}: {len(batch_orders)} ordens adicionadas")
        except Exception as e:
            log_json("ERROR", f"Erro ao ler arquivo {batch_file}: {e}")
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({"detailed_orders": all_orders}, f, ensure_ascii=False, indent=2)
    
    log_json("INFO", f"Arquivo final {output_file} criado com {len(all_orders)} ordens")

def main():
    """Função principal que coordena o processo completo."""
    if len(sys.argv) < 3:
        print("\nUso: python recuperar_dados_completos.py <data_inicial> <data_final> [--lote <tamanho>]")
        print("Exemplo: python recuperar_dados_completos.py 2024-01-01 2025-05-08 --lote 50")
        return
    
    data_inicial = sys.argv[1]
    data_final = sys.argv[2]
    
    # Verificar argumentos adicionais
    batch_size = 100
    if "--lote" in sys.argv:
        lote_idx = sys.argv.index("--lote")
        if lote_idx + 1 < len(sys.argv):
            try:
                batch_size = int(sys.argv[lote_idx + 1])
            except ValueError:
                log_json("WARNING", f"Tamanho de lote inválido: {sys.argv[lote_idx + 1]}. Usando 100.")
    
    token = get_access_token()
    if not token:
        log_json("ERROR", "Token de acesso não encontrado. Verifique o arquivo tiny_token.json.")
        return
    
    # Nome do arquivo de saída com base no período
    output_file = f"ordens_{data_inicial.replace('-', '')}_a_{data_final.replace('-', '')}_completo.json"
    
    # Etapa 1: Buscar lista de ordens
    log_json("INFO", f"Iniciando processo de recuperação para o período de {data_inicial} a {data_final}")
    orders_list = fetch_order_list(token, data_inicial, data_final)
    
    if not orders_list:
        log_json("WARNING", "Nenhuma ordem encontrada para o período especificado.")
        return
    
    log_json("INFO", f"Total de {len(orders_list)} ordens encontradas")
    
    # Etapa 2: Buscar detalhes e processar
    process_orders_with_details(token, orders_list, output_file, batch_size)
    
    log_json("INFO", "Processo de recuperação concluído com sucesso!")
    log_json("INFO", f"Dados salvos em {output_file}")
    
    # Limpar arquivos temporários
    cleanup = input("Deseja remover os arquivos temporários? (S/n): ").strip().lower()
    if cleanup != 'n':
        import shutil
        shutil.rmtree("temp", ignore_errors=True)
        log_json("INFO", "Arquivos temporários removidos")

if __name__ == "__main__":
    main()
