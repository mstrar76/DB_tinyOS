import json
import os
import logging
from datetime import datetime
import time
from db_utils import get_db_connection, close_db_connection
import requests

# Configuração de logging estruturado em formato JSON
def setup_logger():
    logger = logging.getLogger("save_special_orders_to_db")
    logger.setLevel(logging.INFO)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    
    # Formatter JSON
    formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "service": "save_special_orders_to_db", "message": %(message)s}'
    )
    console_handler.setFormatter(formatter)
    
    # Handler para arquivo
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"save_special_orders_to_db_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    logger.handlers = [console_handler, file_handler]
    return logger

logger = setup_logger()

# Constantes
API_BASE = "https://api.tiny.com.br/public-api/v3"
TOKEN_FILE = "tiny_token.json"
RESULTS_DIR = "order_api_responses"
RESULTS_FILE = None  # Será definido dinamicamente

def get_access_token():
    """Obtém o token de acesso do arquivo de token."""
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("access_token")
    except Exception as e:
        logger.error(json.dumps({"error": f"Falha ao ler token: {e}"}))
        return None

def get_refresh_token():
    """Obtém o token de atualização do arquivo de token."""
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("refresh_token")
    except Exception as e:
        logger.error(json.dumps({"error": f"Falha ao ler token de atualização: {e}"}))
        return None

def save_tokens(tokens_data):
    """Salva os novos dados de tokens no arquivo de token."""
    try:
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump(tokens_data, f, indent=2)
        logger.info(json.dumps({"message": f"Tokens salvos com sucesso em {TOKEN_FILE}"}))
    except Exception as e:
        logger.error(json.dumps({"error": f"Erro ao salvar tokens em {TOKEN_FILE}: {e}"}))

def refresh_access_token():
    """Atualiza o token de acesso usando o token de atualização."""
    refresh_token = get_refresh_token()
    if not refresh_token:
        logger.error(json.dumps({"error": "Nenhum token de atualização disponível. Não é possível atualizar."}))
        return None

    # Assumindo que client_id e client_secret estão disponíveis como variáveis de ambiente
    client_id = os.environ.get("TINY_CLIENT_ID")
    client_secret = os.environ.get("TINY_CLIENT_SECRET")

    if not client_id or not client_secret:
        logger.error(json.dumps({"error": "Variáveis de ambiente TINY_CLIENT_ID ou TINY_CLIENT_SECRET não definidas."}))
        return None

    payload = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token
    }

    try:
        logger.info(json.dumps({"message": "Tentando atualizar o token de acesso..."}))
        response = requests.post("https://accounts.tiny.com.br/realms/tiny/protocol/openid-connect/token", data=payload)
        response.raise_for_status()

        tokens_data = response.json()
        save_tokens(tokens_data)
        logger.info(json.dumps({"message": "Token de acesso atualizado com sucesso."}))
        return tokens_data.get("access_token")

    except requests.exceptions.RequestException as e:
        logger.error(json.dumps({"error": f"Erro ao atualizar o token de acesso: {e}"}))
        if hasattr(e, 'response') and e.response is not None:
            logger.error(json.dumps({"status_code": e.response.status_code, "response": e.response.text}))
        return None
    except Exception as e:
        logger.error(json.dumps({"error": f"Ocorreu um erro inesperado durante a atualização do token: {e}"}))
        return None

def fetch_order_details(order_id, token):
    """Busca os detalhes de uma ordem pelo ID."""
    url = f"{API_BASE}/ordem-servico/{order_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        
        # Verificar se o token expirou (401)
        if response.status_code == 401:
            logger.info(json.dumps({"message": f"Token expirado para ordem ID {order_id}. Tentando atualizar..."}))
            new_token = refresh_access_token()
            if new_token:
                headers["Authorization"] = f"Bearer {new_token}"
                response = requests.get(url, headers=headers)
            else:
                logger.error(json.dumps({"error": "Falha ao atualizar token. Não é possível continuar."}))
                return None
        
        if response.status_code != 200:
            logger.error(json.dumps({
                "error": f"Falha ao buscar detalhes da ordem ID {order_id}",
                "status_code": response.status_code,
                "response": response.text
            }))
            return None
        
        return response.json()
    
    except Exception as e:
        logger.error(json.dumps({"error": f"Erro ao buscar detalhes da ordem ID {order_id}: {e}"}))
        return None

def parse_numeric(value_str):
    """Converte com segurança uma string para float, lidando com None, strings vazias e vírgulas."""
    if value_str is None or value_str == "":
        return None
    try:
        return float(str(value_str).replace(',', '.'))
    except ValueError:
        return None

def process_and_save_order(cursor, order_data):
    """Processa os dados de uma única ordem e insere/atualiza no banco de dados."""
    try:
        # --- Extração e limpeza de dados para tabelas relacionadas (contatos, enderecos) ---
        contact_data = order_data.get("contato") or {}
        address_data = contact_data.get("endereco") or {}

        # Processa Enderecos primeiro (UPSERT baseado no conteúdo)
        address_id = None
        if address_data:
            endereco = address_data.get("endereco")
            numero = address_data.get("numero")
            complemento = address_data.get("complemento")
            bairro = address_data.get("bairro")
            municipio = address_data.get("municipio")
            cep = address_data.get("cep")
            uf = address_data.get("uf")
            pais = address_data.get("pais")

            cursor.execute("""
                SELECT id FROM enderecos
                WHERE endereco = %s AND numero = %s AND complemento = %s AND bairro = %s
                AND municipio = %s AND cep = %s AND uf = %s AND pais = %s;
            """, (endereco, numero, complemento, bairro, municipio, cep, uf, pais))
            existing_address = cursor.fetchone()

            if existing_address:
                address_id = existing_address[0]
            else:
                cursor.execute("""
                    INSERT INTO enderecos (endereco, numero, complemento, bairro, municipio, cep, uf, pais)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """, (endereco, numero, complemento, bairro, municipio, cep, uf, pais))
                address_id = cursor.fetchone()[0]

        # Processa Contatos (UPSERT baseado no ID da API)
        contact_id = contact_data.get("id")
        if contact_id:
            nome_contato = contact_data.get("nome")
            codigo_contato = contact_data.get("codigo")
            fantasia_contato = contact_data.get("fantasia")
            tipo_pessoa_contato = contact_data.get("tipoPessoa")
            cpf_cnpj_contato = contact_data.get("cpfCnpj")
            inscricao_estadual_contato = contact_data.get("inscricaoEstadual")
            rg_contato = contact_data.get("rg")
            telefone_contato = contact_data.get("telefone")
            celular_contato = contact_data.get("celular")
            email_contato = contact_data.get("email")

            upsert_contact_sql = """
                INSERT INTO contatos (
                    id, nome, codigo, fantasia, tipo_pessoa, cpf_cnpj,
                    inscricao_estadual, rg, telefone, celular, email, id_endereco
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (id) DO UPDATE SET
                    nome = EXCLUDED.nome,
                    codigo = EXCLUDED.codigo,
                    fantasia = EXCLUDED.fantasia,
                    tipo_pessoa = EXCLUDED.tipo_pessoa,
                    cpf_cnpj = EXCLUDED.cpf_cnpj,
                    inscricao_estadual = EXCLUDED.inscricao_estadual,
                    rg = EXCLUDED.rg,
                    telefone = EXCLUDED.telefone,
                    celular = EXCLUDED.celular,
                    email = EXCLUDED.email,
                    id_endereco = EXCLUDED.id_endereco;
            """
            cursor.execute(upsert_contact_sql, (
                contact_id, nome_contato, codigo_contato, fantasia_contato,
                tipo_pessoa_contato, cpf_cnpj_contato, inscricao_estadual_contato,
                rg_contato, telefone_contato, celular_contato, email_contato, address_id
            ))
        else:
            contact_id = None

        # --- Extração e limpeza de dados para ordens_servico ---
        order_id = order_data.get("id")
        if order_id is None:
            logger.warning(json.dumps({"warning": f"Pulando ordem devido a ID ausente: {order_data}"}))
            return # Pula esta ordem

        numero_ordem_servico = order_data.get("numeroOrdemServico")
        situacao_str = order_data.get("situacao", "")
        # Extrair apenas o primeiro caractere do status (ex: "7 - Cancelada" -> "7")
        situacao = situacao_str.split(" - ")[0] if " - " in situacao_str else situacao_str
        # Garantir que situacao seja apenas um caractere
        situacao = situacao[0] if situacao else ""

        data_emissao_str = order_data.get("data")
        data_emissao = data_emissao_str if data_emissao_str and data_emissao_str != '0000-00-00' else None

        data_prevista_str = order_data.get("dataPrevista")
        data_prevista = data_prevista_str if data_prevista_str and not data_prevista_str.startswith('0000-00-00') else None

        data_conclusao_str = order_data.get("dataConclusao")
        data_conclusao = data_conclusao_str if data_conclusao_str and data_conclusao_str != '0000-00-00' else None

        total_servicos = parse_numeric(order_data.get("totalServicos"))
        total_ordem_servico = parse_numeric(order_data.get("totalOrdemServico"))
        total_pecas = parse_numeric(order_data.get("totalPecas"))
        alq_comissao = parse_numeric(order_data.get("alqComissao"))
        vlr_comissao = parse_numeric(order_data.get("vlrComissao"))
        desconto = parse_numeric(order_data.get("desconto"))

        equipamento = order_data.get("equipamento")
        equipamento_serie = order_data.get("equipamentoSerie") if order_data.get("equipamentoSerie") != "" else None
        descricao_problema = order_data.get("descricaoProblema")
        observacoes = order_data.get("observacoes")
        observacoes_internas = order_data.get("observacoesInternas")
        # Removido orcar e orcado conforme solicitado
        id_lista_preco = order_data.get("idListaPreco") if order_data.get("idListaPreco") != 0 else None
        tecnico = order_data.get("tecnico")
        id_conta_contabil = order_data.get("idContaContabil") if order_data.get("idContaContabil") != 0 else None

        vendedor_data = order_data.get("vendedor") or {}
        id_vendedor = vendedor_data.get("id")
        categoria_data = order_data.get("categoria") or {}
        id_categoria_os = categoria_data.get("id")
        categoria_descricao = categoria_data.get("descricao")
        
        # Upsert categoria_os se id e descricao estiverem presentes
        if id_categoria_os and categoria_descricao:
            upsert_categoria_sql = """
                INSERT INTO categorias_os (id, descricao)
                VALUES (%s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    descricao = EXCLUDED.descricao;
            """
            cursor.execute(upsert_categoria_sql, (id_categoria_os, categoria_descricao))
            
        forma_pagamento_data = order_data.get("formaPagamento") or {}
        id_forma_pagamento = forma_pagamento_data.get("id")
        forma_pagamento_nome = forma_pagamento_data.get("nome")
        
        # Upsert forma_pagamento se id e nome estiverem presentes
        if id_forma_pagamento and forma_pagamento_nome is not None:
            upsert_forma_pagamento_sql = """
                INSERT INTO formas_pagamento (id, nome)
                VALUES (%s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    nome = EXCLUDED.nome;
            """
            cursor.execute(upsert_forma_pagamento_sql, (id_forma_pagamento, forma_pagamento_nome))

        # --- Mapeamento de campos personalizados ---
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

        origem_cliente = None # Será tratado posteriormente ao processar marcadores

        # --- Inserção/Atualização no banco de dados para ordens_servico ---
        upsert_sql = """
            INSERT INTO ordens_servico (
                id, numero_ordem_servico, situacao, data_emissao, data_prevista,
                data_conclusao, total_servicos, total_ordem_servico, total_pecas,
                equipamento, equipamento_serie, descricao_problema, observacoes,
                observacoes_internas, alq_comissao, vlr_comissao,
                desconto, id_lista_preco, tecnico, id_contato, id_vendedor,
                id_categoria_os, id_forma_pagamento, id_conta_contabil,
                linha_dispositivo, tipo_servico, origem_cliente
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
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
            desconto, id_lista_preco, tecnico, contact_id, id_vendedor,
            id_categoria_os, id_forma_pagamento, id_conta_contabil,
            linha_dispositivo, tipo_servico, origem_cliente
        ))
        
        logger.info(json.dumps({
            "message": f"Ordem {numero_ordem_servico} (ID: {order_id}) processada com sucesso",
            "situacao": situacao
        }))
        
        return True

    except Exception as e:
        logger.error(json.dumps({"error": f"Erro ao processar Ordem ID {order_data.get('id', 'N/A')}: {e}"}))
        raise # Re-levanta para sinalizar falha para tratamento em lote

def find_latest_results_file():
    """Encontra o arquivo de resultados mais recente no diretório de resultados."""
    if not os.path.exists(RESULTS_DIR):
        logger.error(json.dumps({"error": f"Diretório de resultados '{RESULTS_DIR}' não encontrado"}))
        return None
    
    result_files = [f for f in os.listdir(RESULTS_DIR) if f.startswith("orders_verification_results_") and f.endswith(".json")]
    if not result_files:
        logger.error(json.dumps({"error": "Nenhum arquivo de resultados encontrado"}))
        return None
    
    # Ordena por data de modificação (mais recente primeiro)
    latest_file = max(result_files, key=lambda f: os.path.getmtime(os.path.join(RESULTS_DIR, f)))
    return os.path.join(RESULTS_DIR, latest_file)

def main():
    # Encontrar o arquivo de resultados mais recente
    results_file = find_latest_results_file()
    if not results_file:
        logger.error(json.dumps({"error": "Não foi possível encontrar o arquivo de resultados. Execute verify_specific_orders.py primeiro."}))
        return
    
    logger.info(json.dumps({"message": f"Usando arquivo de resultados: {results_file}"}))
    
    # Carregar resultados
    try:
        with open(results_file, "r", encoding="utf-8") as f:
            results = json.load(f)
    except Exception as e:
        logger.error(json.dumps({"error": f"Erro ao carregar arquivo de resultados: {e}"}))
        return
    
    # Filtrar ordens canceladas (status 7) e finalizadas (status 3)
    target_orders = [order for order in results if order["encontrada"] and (order["status"] == "7" or order["status"] == "3")]
    
    if not target_orders:
        logger.warning(json.dumps({"warning": "Nenhuma ordem cancelada ou finalizada encontrada nos resultados"}))
        return
    
    logger.info(json.dumps({"message": f"Encontradas {len(target_orders)} ordens para processar (canceladas ou finalizadas)"}))
    
    # Obter token de acesso
    token = get_access_token()
    if not token:
        logger.error(json.dumps({"error": "Nenhum token de acesso encontrado. Abortando."}))
        return
    
    # Conectar ao banco de dados
    conn = get_db_connection()
    if not conn:
        logger.error(json.dumps({"error": "Não foi possível conectar ao banco de dados"}))
        return
    
    cursor = conn.cursor()
    
    # Processar cada ordem
    success_count = 0
    error_count = 0
    
    for order_info in target_orders:
        order_number = order_info["numero_ordem"]
        order_id = order_info.get("detalhes", {}).get("id")
        
        if not order_id:
            logger.warning(json.dumps({"warning": f"Ordem {order_number} não possui ID. Pulando."}))
            error_count += 1
            continue
        
        # Verificar se já temos os detalhes completos da ordem
        order_detail_file = os.path.join(RESULTS_DIR, f"order_{order_number}_details.json")
        
        if os.path.exists(order_detail_file):
            # Carregar detalhes do arquivo
            try:
                with open(order_detail_file, "r", encoding="utf-8") as f:
                    order_data = json.load(f)
                logger.info(json.dumps({"message": f"Detalhes da ordem {order_number} carregados do arquivo"}))
            except Exception as e:
                logger.error(json.dumps({"error": f"Erro ao carregar detalhes da ordem {order_number} do arquivo: {e}"}))
                error_count += 1
                continue
        else:
            # Buscar detalhes da API
            logger.info(json.dumps({"message": f"Buscando detalhes da ordem {order_number} da API"}))
            order_data = fetch_order_details(order_id, token)
            if not order_data:
                logger.error(json.dumps({"error": f"Não foi possível obter detalhes da ordem {order_number}"}))
                error_count += 1
                continue
        
        # Processar e salvar a ordem
        try:
            process_and_save_order(cursor, order_data)
            conn.commit()
            success_count += 1
            logger.info(json.dumps({"message": f"Ordem {order_number} salva no banco de dados com sucesso"}))
        except Exception as e:
            conn.rollback()
            logger.error(json.dumps({"error": f"Erro ao salvar ordem {order_number} no banco de dados: {e}"}))
            error_count += 1
        
        # Aguardar um pouco para não sobrecarregar o banco de dados
        time.sleep(0.2)
    
    # Fechar conexão com o banco de dados
    close_db_connection(conn)
    
    # Resumo final
    logger.info(json.dumps({
        "message": "Processamento concluído",
        "ordens_processadas": len(target_orders),
        "sucessos": success_count,
        "erros": error_count
    }))
    
    print(f"\nProcessamento concluído:")
    print(f"- Total de ordens processadas: {len(target_orders)}")
    print(f"- Ordens salvas com sucesso: {success_count}")
    print(f"- Erros: {error_count}")

if __name__ == "__main__":
    main()
