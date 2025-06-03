import requests
import json
import time
import os
import psycopg2
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

def get_db_connection():
    """Estabelece conexão com o banco de dados PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )
        log("Conexão com o banco de dados estabelecida.")
        return conn
    except Exception as e:
        log(f"Erro ao conectar ao banco de dados: {e}")
        return None

def close_db_connection(conn):
    """Fecha a conexão com o banco de dados."""
    if conn:
        conn.close()
        log("Conexão com o banco de dados fechada.")

def fetch_orders_april_2025(token):
    """Busca todas as ordens de abril de 2025 (apenas IDs)."""
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
            log(f"Obtidas {len(items)} ordens nesta página (total até agora: {len(all_orders)})")
            if len(items) < params["limit"]:
                break
            params["offset"] += params["limit"]
            time.sleep(1)
    except Exception as e:
        log(f"Erro ao buscar lista de ordens: {e}")
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
            log(f"Formato inesperado para ordem {order_id}")
            return None
    except Exception as e:
        log(f"Erro ao buscar detalhes para Ordem ID {order_id}: {e}")
        return None

def parse_numeric(value_str):
    """Converte string para valor numérico."""
    if value_str is None or value_str == "":
        return None
    try:
        return float(str(value_str).replace(',', '.'))
    except ValueError:
        log(f"Aviso: Não foi possível converter '{value_str}' para numérico")
        return None

def update_order_in_db(conn, order_details, marcadores):
    """Atualiza uma ordem no banco de dados, preservando os marcadores."""
    if not order_details or "id" not in order_details:
        log("Dados de ordem inválidos para atualização")
        return False
    
    try:
        cur = conn.cursor()
        order_id = order_details.get("id")
        
        # Extrair dados da ordem
        numero_ordem_servico = order_details.get("numeroOrdemServico")
        situacao_str = order_details.get("situacao", "")
        situacao = situacao_str.split(" - ")[0] if " - " in situacao_str else situacao_str

        data_emissao_str = order_details.get("data")
        data_emissao = data_emissao_str if data_emissao_str and data_emissao_str != '0000-00-00' else None

        data_prevista_str = order_details.get("dataPrevista")
        data_prevista = data_prevista_str if data_prevista_str and not data_prevista_str.startswith('0000-00-00') else None

        data_conclusao_str = order_details.get("dataConclusao")
        data_conclusao = data_conclusao_str if data_conclusao_str and data_conclusao_str != '0000-00-00' else None

        total_servicos = parse_numeric(order_details.get("totalServicos"))
        total_ordem_servico = parse_numeric(order_details.get("totalOrdemServico"))
        total_pecas = parse_numeric(order_details.get("totalPecas"))
        alq_comissao = parse_numeric(order_details.get("alqComissao"))
        vlr_comissao = parse_numeric(order_details.get("vlrComissao"))
        desconto = parse_numeric(order_details.get("desconto"))

        equipamento = order_details.get("equipamento")
        equipamento_serie = order_details.get("equipamentoSerie") if order_details.get("equipamentoSerie") != "" else None
        descricao_problema = order_details.get("descricaoProblema")
        observacoes = order_details.get("observacoes")
        observacoes_internas = order_details.get("observacoesInternas")
        orcar = order_details.get("orcar")
        orcado = order_details.get("orcado")
        id_lista_preco = order_details.get("idListaPreco") if order_details.get("idListaPreco") != 0 else None
        tecnico = order_details.get("tecnico")
        id_conta_contabil = order_details.get("idContaContabil") if order_details.get("idContaContabil") != 0 else None

        vendedor_data = order_details.get("vendedor") or {}
        id_vendedor = vendedor_data.get("id")
        
        categoria_data = order_details.get("categoria") or {}
        id_categoria_os = categoria_data.get("id")
        categoria_descricao = categoria_data.get("descricao")
        
        # Upsert categoria_os if id and descricao are present
        if id_categoria_os and categoria_descricao:
            upsert_categoria_sql = """
                INSERT INTO categorias_os (id, descricao)
                VALUES (%s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    descricao = EXCLUDED.descricao;
            """
            cur.execute(upsert_categoria_sql, (id_categoria_os, categoria_descricao))
        
        forma_pagamento_data = order_details.get("formaPagamento") or {}
        id_forma_pagamento = forma_pagamento_data.get("id")
        forma_pagamento_nome = forma_pagamento_data.get("nome")
        
        # Upsert forma_pagamento if id and nome are present
        if id_forma_pagamento and forma_pagamento_nome is not None:
            upsert_forma_pagamento_sql = """
                INSERT INTO formas_pagamento (id, nome)
                VALUES (%s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    nome = EXCLUDED.nome;
            """
            cur.execute(upsert_forma_pagamento_sql, (id_forma_pagamento, forma_pagamento_nome))

        # --- Custom Field Mapping ---
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

        # --- Processamento de marcadores para origem_cliente ---
        origem_cliente = None
        for marcador in marcadores:
            marcador_lower = marcador.lower() if marcador else ""
            if "instagram" in marcador_lower:
                origem_cliente = "instagram"
                break
            elif "facebook" in marcador_lower:
                origem_cliente = "facebook"
                break
            elif "google" in marcador_lower:
                origem_cliente = "google"
                break
            elif "indicacao" in marcador_lower:
                origem_cliente = "indicacao"
                break
            elif "site" in marcador_lower:
                origem_cliente = "site"
                break
            elif "txmidia" in marcador_lower:
                origem_cliente = "txmidia"
                break
            elif "cliente existente" in marcador_lower:
                origem_cliente = "cliente_existente"
                break

        # --- Database Update for ordens_servico ---
        # Importante: Não sobrescrever campos com NULL se já existirem valores
        update_sql = """
            UPDATE ordens_servico SET
                numero_ordem_servico = %s,
                situacao = %s,
                data_emissao = %s,
                data_prevista = %s,
                data_conclusao = %s,
                total_servicos = %s,
                total_ordem_servico = %s,
                total_pecas = %s,
                equipamento = COALESCE(%s, equipamento),
                equipamento_serie = COALESCE(%s, equipamento_serie),
                descricao_problema = COALESCE(%s, descricao_problema),
                observacoes = COALESCE(%s, observacoes),
                observacoes_internas = COALESCE(%s, observacoes_internas),
                orcar = %s,
                orcado = %s,
                alq_comissao = %s,
                vlr_comissao = %s,
                desconto = %s,
                id_lista_preco = %s,
                tecnico = COALESCE(%s, tecnico),
                id_vendedor = %s,
                id_categoria_os = %s,
                id_forma_pagamento = %s,
                id_conta_contabil = %s,
                linha_dispositivo = %s,
                tipo_servico = %s,
                origem_cliente = COALESCE(%s, origem_cliente),
                data_extracao = CURRENT_TIMESTAMP
            WHERE id = %s;
        """
        cur.execute(update_sql, (
            numero_ordem_servico, situacao, data_emissao, data_prevista,
            data_conclusao, total_servicos, total_ordem_servico, total_pecas,
            equipamento, equipamento_serie, descricao_problema, observacoes,
            observacoes_internas, orcar, orcado, alq_comissao, vlr_comissao,
            desconto, id_lista_preco, tecnico, id_vendedor,
            id_categoria_os, id_forma_pagamento, id_conta_contabil,
            linha_dispositivo, tipo_servico, origem_cliente, order_id
        ))
        
        # Verificar se a atualização afetou alguma linha
        if cur.rowcount == 0:
            log(f"Aviso: Ordem ID {order_id} não encontrada no banco para atualização")
            return False
        
        conn.commit()
        log(f"Ordem ID {order_id} atualizada com sucesso")
        return True
        
    except Exception as e:
        conn.rollback()
        log(f"Erro ao atualizar ordem ID {order_id}: {e}")
        return False

def get_marcadores_from_db(conn, order_id):
    """Busca os marcadores de uma ordem no banco de dados."""
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT descricao 
            FROM marcadores_ordem_servico 
            WHERE id_ordem_servico = %s;
        """, (order_id,))
        return [row[0] for row in cur.fetchall()]
    except Exception as e:
        log(f"Erro ao buscar marcadores para ordem ID {order_id}: {e}")
        return []

def main():
    token = get_access_token()
    if not token:
        log("Token de acesso não encontrado.")
        return
    
    # Buscar todas as ordens de abril de 2025
    orders = fetch_orders_april_2025(token)
    if not orders:
        log("Nenhuma ordem encontrada para abril de 2025.")
        return
    
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        # Para cada ordem, buscar detalhes completos e atualizar no banco
        success_count = 0
        error_count = 0
        
        for idx, order_info in enumerate(orders):
            order_id = order_info.get("id")
            log(f"Processando ordem {idx+1}/{len(orders)}: ID {order_id}")
            
            # Buscar marcadores existentes no banco
            marcadores = get_marcadores_from_db(conn, order_id)
            
            # Buscar detalhes completos da API
            order_details = fetch_order_details(token, order_id)
            if not order_details:
                log(f"Erro: Não foi possível obter detalhes para ordem ID {order_id}")
                error_count += 1
                continue
            
            # Atualizar ordem no banco
            if update_order_in_db(conn, order_details, marcadores):
                success_count += 1
            else:
                error_count += 1
            
            # Pausa para respeitar limites de API
            time.sleep(1)
        
        log(f"Processamento concluído: {success_count} ordens atualizadas com sucesso, {error_count} erros")
    
    except Exception as e:
        log(f"Erro durante o processamento: {e}")
    finally:
        close_db_connection(conn)

if __name__ == "__main__":
    main()
