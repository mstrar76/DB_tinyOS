import requests
import json
import time
import os
from datetime import datetime
from dotenv import load_dotenv
from db_utils import get_db_connection, close_db_connection

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

def update_client_origin_from_markers(os_id, markers):
    """Extrai a origem do cliente a partir dos marcadores e atualiza o campo origem_cliente na tabela ordens_servico."""
    if not markers:
        return None
    
    # Lista de possíveis marcadores de origem do cliente (case-insensitive, ignora acentos)
    origin_keywords = [
        "txmidia", "cliente existente", "indicação", "indicacao",
        "origem:social", "origem:gpt", "origem:local"
    ]
    
    # Normalizar marcadores para comparação
    def normalize(s):
        import unicodedata
        return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII').lower()
    
    # Gerar lista normalizada mantendo o mesmo índice dos marcadores originais.
    normalized_markers = []
    for m in markers:
        if isinstance(m, str):
            normalized_markers.append(normalize(m))
        elif isinstance(m, dict):
            nome = m.get("nome")
            if isinstance(nome, str):
                normalized_markers.append(normalize(nome))
            else:
                normalized_markers.append("")  # placeholder para manter índice
        else:
            normalized_markers.append("")  # placeholder
    
    # Encontrar o primeiro marcador que corresponda a qualquer palavra-chave de origem
    found = None
    for keyword in origin_keywords:
        for i, marker in enumerate(normalized_markers):
            if keyword in marker:
                # Usar o marcador original, não o normalizado
                found = markers[i]
                break
        if found:
            break
    
    if found:
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE ordens_servico SET origem_cliente = %s WHERE id = %s""",
                (found, os_id)
            )
            conn.commit()
            print(f"  Atualizado origem_cliente para OS {os_id}: {found}")
            return found
        except Exception as e:
            print(f"  Erro ao atualizar origem_cliente para OS {os_id}: {e}")
            conn.rollback()
            return None
        finally:
            close_db_connection(conn)
    
    return None

def process_markers_for_order(os_id, markers):
    """Processa os marcadores de uma OS, inserindo-os nas tabelas marcadores e ordem_servico_marcadores."""
    if not markers or not os_id:
        return 0
    
    conn = get_db_connection()
    if not conn:
        return 0
    
    try:
        cursor = conn.cursor()
        markers_inserted = 0
        
        # Primeiro, limpar os marcadores existentes para esta OS
        cursor.execute(
            """DELETE FROM ordem_servico_marcadores WHERE id_ordem_servico = %s""",
            (os_id,)
        )
        
        for marker in markers:
            # Extrair nome do marcador (string) caso o objeto seja um dicionário
            if isinstance(marker, dict):
                marker_name = marker.get("nome")
            else:
                marker_name = marker
            
            if not marker_name:
                continue  # ignora marcadores sem nome válido
            
            # Verificar se o marcador já existe na tabela marcadores
            cursor.execute(
                """SELECT id FROM marcadores WHERE nome = %s""",
                (marker_name,)
            )
            result = cursor.fetchone()
            
            if result:
                marker_id = result[0]
            else:
                # Inserir novo marcador
                cursor.execute(
                    """INSERT INTO marcadores (nome) VALUES (%s) RETURNING id""",
                    (marker_name,)
                )
                marker_id = cursor.fetchone()[0]
            
            # Inserir na tabela de junção
            cursor.execute(
                """INSERT INTO ordem_servico_marcadores (id_ordem_servico, id_marcador) 
                   VALUES (%s, %s) ON CONFLICT DO NOTHING""",
                (os_id, marker_id)
            )
            markers_inserted += 1
        
        conn.commit()
        return markers_inserted
    except Exception as e:
        print(f"  Erro ao processar marcadores para OS {os_id}: {e}")
        conn.rollback()
        return 0
    finally:
        close_db_connection(conn)

def fetch_orders_with_tags(token, data_inicial, data_final, situacao="3"):
    """
    Busca ordens com seus marcadores usando o endpoint de listagem.
    Este endpoint inclui o campo 'marcadores' que não está disponível no endpoint de detalhes.
    """
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "situacao": situacao,  # 3 = Finalizada
        "dataInicialEmissao": data_inicial,
        "dataFinalEmissao": data_final,
        "limit": 100,
        "offset": 0
    }
    all_orders = []

    print(f"Buscando ordens para o período de {data_inicial} a {data_final}...")

    try:
        while True:
            resp = requests.get(f"{API_BASE}/ordem-servico", headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("itens", [])
            
            if not items:
                break
                
            # Armazenar os itens com seus marcadores
            for item in items:
                # Extrair apenas os campos necessários para economizar memória
                order_info = {
                    "id": item.get("id"),
                    "marcadores": item.get("marcadores", []),
                    # Outros campos que podem ser úteis do endpoint de listagem
                    "numeroOrdemServico": item.get("numeroOrdemServico"),
                    "data": item.get("data"),
                    "situacao": item.get("situacao")
                }
                all_orders.append(order_info)
            
            print(f"Obtidas {len(items)} ordens para {data_inicial} a {data_final} (total até agora: {len(all_orders)})")

            if len(items) < params["limit"]:
                break
                
            params["offset"] += params["limit"]
            time.sleep(1)  # Respeitar os limites de taxa da API
            
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar lista de ordens para {data_inicial} a {data_final}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Código de status da resposta: {e.response.status_code}")
            print(f"Texto da resposta: {e.response.text}")
    except Exception as e:
        print(f"Erro inesperado ao buscar ordens: {e}")

    return all_orders

def fetch_order_details(token, order_id):
    """Busca dados detalhados para uma ordem específica."""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{API_BASE}/ordem-servico/{order_id}"
    
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        order_data = resp.json()
        
        if isinstance(order_data, dict) and "id" in order_data:
            return order_data
        else:
            print(f"Aviso: Formato inesperado para ordem {order_id}. Ignorando.")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar detalhes para Ordem ID {order_id}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Código de status da resposta: {e.response.status_code}")
            print(f"Texto da resposta: {e.response.text}")
        return None
    except Exception as e:
        print(f"Erro inesperado ao buscar detalhes para Ordem ID {order_id}: {e}")
        return None

def process_orders_with_tags(token, orders_with_tags, existing_ids=None, batch_size=50):
    """
    Processa as ordens com marcadores, buscando detalhes completos e combinando os dados.
    Atualiza também o campo origem_cliente baseado nos marcadores e insere os marcadores nas tabelas apropriadas.
    
    Retorna: (detailed_orders, stats)
    - detailed_orders: lista de ordens detalhadas processadas
    - stats: dicionário com estatísticas de processamento
    """
    if existing_ids is None:
        existing_ids = []
    
    # Inicializar estatísticas
    stats = {
        "total_orders": len(orders_with_tags),
        "origins_updated": 0,
        "markers_processed": 0,
        "total_markers": 0
    }
    
    # Processar todas as ordens, não apenas as novas, para atualizar marcadores e origem_cliente
    print(f"Ordens totais obtidas: {len(orders_with_tags)}")
    
    # Primeiro, processar marcadores e atualizar origem_cliente para todas as ordens
    print("\nProcessando marcadores e atualizando origem_cliente...")
    for order_info in orders_with_tags:
        order_id = order_info["id"]
        marcadores = order_info.get("marcadores", [])
        
        if marcadores:
            stats["total_markers"] += len(marcadores)
            
            # Inserir marcadores nas tabelas apropriadas
            markers_processed = process_markers_for_order(order_id, marcadores)
            stats["markers_processed"] += markers_processed
            print(f"  OS {order_id}: {markers_processed} marcadores processados")
            
            # Atualizar origem_cliente baseado nos marcadores
            origin = update_client_origin_from_markers(order_id, marcadores)
            if origin:
                stats["origins_updated"] += 1
    
    print(f"Total de campos origem_cliente atualizados: {stats['origins_updated']}")
    print(f"Total de marcadores processados: {stats['markers_processed']} de {stats['total_markers']}\n")
    
    # Agora processar apenas ordens novas para detalhes completos
    new_orders = [order for order in orders_with_tags if order["id"] not in existing_ids]
    print(f"Ordens novas a serem processadas para detalhes completos: {len(new_orders)}")
    
    detailed_orders = []
    
    # Processar em lotes para gerenciar melhor o uso de memória
    for i in range(0, len(new_orders), batch_size):
        batch = new_orders[i:i+batch_size]
        print(f"Processando lote {i//batch_size + 1}/{(len(new_orders) + batch_size - 1)//batch_size} ({len(batch)} ordens)")
        
        batch_detailed = []
        for idx, order_info in enumerate(batch):
            order_id = order_info["id"]
            print(f"  Ordem {idx+1}/{len(batch)}: Buscando detalhes para ID {order_id}")
            
            # Buscar detalhes completos da ordem
            order_details = fetch_order_details(token, order_id)
            
            if order_details:
                # Adicionar o campo marcadores aos detalhes da ordem
                order_details["marcadores"] = order_info.get("marcadores", [])
                batch_detailed.append(order_details)
                print(f"    Detalhes obtidos com sucesso. Marcadores: {order_info.get('marcadores', [])}")
            
            # Pausa para respeitar os limites de taxa da API
            time.sleep(1)
        
        # Adicionar as ordens do lote ao resultado total
        detailed_orders.extend(batch_detailed)
        
        # Salvar o lote em um arquivo temporário para segurança
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_filename = f"{TEMP_FILE_PREFIX}batch_{i//batch_size + 1}_{timestamp}.json"
        with open(temp_filename, "w", encoding="utf-8") as f:
            json.dump({"detailed_orders": batch_detailed}, f, ensure_ascii=False, indent=2)
        print(f"Lote {i//batch_size + 1} salvo em {temp_filename}")
    
    return detailed_orders, stats

def save_and_process_orders(detailed_orders, period_label):
    """Salva as ordens detalhadas em um arquivo JSON e as processa para o banco de dados."""
    if not detailed_orders:
        print(f"Nenhuma ordem nova para o período {period_label}.")
        return
        
    # Salvar em arquivo JSON
    output_filename = f"orders_{period_label}_with_tags.json"
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
    """Atualiza as ordens para um período específico, incluindo marcadores.
    
    Retorna: dict com estatísticas do processamento
    """
    print(f"\n{'='*50}")
    print(f"Atualizando ordens para o período: {period_label} ({data_inicial} a {data_final})")
    print(f"{'='*50}")
    
    # Buscar ordens com marcadores para o período
    orders_with_tags = fetch_orders_with_tags(token, data_inicial, data_final)
    
    if not orders_with_tags:
        print(f"Nenhuma ordem encontrada para o período {period_label}.")
        return {"new_orders": 0, "origins_updated": 0, "markers_processed": 0}
    
    # Buscar detalhes das ordens e combinar com os marcadores
    detailed_orders, stats = process_orders_with_tags(token, orders_with_tags, existing_ids)
    
    # Salvar e processar as ordens
    save_and_process_orders(detailed_orders, period_label)
    
    # Adicionar informações adicionais às estatísticas
    stats["new_orders"] = len(detailed_orders)
    stats["period"] = period_label
    
    return stats

def main():
    """Função principal para atualizar ordens de 2024 e 2025 com marcadores."""
    print("Iniciando atualização de ordens de 2024 e 2025 com marcadores...")
    
    # Obter token de acesso
    token = get_access_token()
    if not token:
        print("Nenhum token de acesso encontrado.")
        return
    
    # Obter IDs existentes para evitar duplicação
    existing_ids = get_existing_order_ids()
    
    # Períodos a serem atualizados
    periods = [
        # 2024 - Processar todos os meses de 2024
        {"data_inicial": "2024-01-01", "data_final": "2024-01-31", "label": "2024_01"},
        {"data_inicial": "2024-02-01", "data_final": "2024-02-29", "label": "2024_02"},
        {"data_inicial": "2024-03-01", "data_final": "2024-03-31", "label": "2024_03"},
        {"data_inicial": "2024-04-01", "data_final": "2024-04-30", "label": "2024_04"},
        {"data_inicial": "2024-05-01", "data_final": "2024-05-31", "label": "2024_05"},
        {"data_inicial": "2024-06-01", "data_final": "2024-06-30", "label": "2024_06"},
        {"data_inicial": "2024-07-01", "data_final": "2024-07-31", "label": "2024_07"},
        {"data_inicial": "2024-08-01", "data_final": "2024-08-31", "label": "2024_08"},
        {"data_inicial": "2024-09-01", "data_final": "2024-09-30", "label": "2024_09"},
        {"data_inicial": "2024-10-01", "data_final": "2024-10-31", "label": "2024_10"},
        {"data_inicial": "2024-11-01", "data_final": "2024-11-30", "label": "2024_11"},
        {"data_inicial": "2024-12-01", "data_final": "2024-12-31", "label": "2024_12"},
        
        # 2025 - Processar todos os meses até maio de 2025
        {"data_inicial": "2025-01-01", "data_final": "2025-01-31", "label": "2025_01"},
        {"data_inicial": "2025-02-01", "data_final": "2025-02-29", "label": "2025_02"},
        {"data_inicial": "2025-03-01", "data_final": "2025-03-31", "label": "2025_03"},
        {"data_inicial": "2025-04-01", "data_final": "2025-04-30", "label": "2025_04"},
        {"data_inicial": "2025-05-01", "data_final": "2025-05-13", "label": "2025_05"}  # Até a data atual
    ]
    
    # Estatísticas globais
    global_stats = {
        "total_new_orders": 0,
        "total_origins_updated": 0,
        "total_markers_processed": 0,
        "total_orders_processed": 0
    }
    
    # Processar cada período
    for period in periods:
        print(f"\n{'='*70}")
        print(f"Processando período: {period['label']} ({period['data_inicial']} a {period['data_final']})")
        print(f"{'='*70}")
        
        period_stats = update_orders_for_period(
            token, 
            period["data_inicial"], 
            period["data_final"], 
            period["label"],
            existing_ids
        )
        
        # Atualizar estatísticas globais
        global_stats["total_new_orders"] += period_stats.get("new_orders", 0)
        global_stats["total_origins_updated"] += period_stats.get("origins_updated", 0)
        global_stats["total_markers_processed"] += period_stats.get("markers_processed", 0)
        global_stats["total_orders_processed"] += period_stats.get("total_orders", 0)
    
    # Exibir resumo final
    print("\n" + "="*70)
    print("RESUMO DA ATUALIZAÇÃO")
    print("="*70)
    print(f"Total de ordens processadas: {global_stats['total_orders_processed']}")
    print(f"Total de novas ordens detalhadas: {global_stats['total_new_orders']}")
    print(f"Total de campos origem_cliente atualizados: {global_stats['total_origins_updated']}")
    print(f"Total de marcadores processados: {global_stats['total_markers_processed']}")
    print("="*70)
    
    print("\nImportante: O campo 'origem_cliente' foi atualizado para todas as ordens")
    print("com marcadores que indicam a origem do cliente (txmidia, cliente existente,")
    print("indicação, origem:social, origem:gpt, origem:local).")
    print("="*70)

if __name__ == "__main__":
    main()
