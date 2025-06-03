import json
import sys
import os
from db_utils import get_db_connection, close_db_connection
from datetime import datetime

# Configuração de logging estruturado
def log_json(level, message, **kwargs):
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "service": "process_data_with_tags",
        "message": message,
        **kwargs
    }
    print(json.dumps(log_data, ensure_ascii=False))

def validate_order_data(order):
    """Valida se uma ordem tem todos os campos essenciais necessários."""
    if not order or not isinstance(order, dict):
        return False
    
    essential_fields = ["id", "numeroOrdemServico"]
    for field in essential_fields:
        if field not in order or not order[field]:
            return False
    return True

def backup_database():
    """Cria um backup do banco de dados antes de operações em massa."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        db_host = os.getenv("DB_HOST", "localhost")
        db_name = os.getenv("DB_NAME", "tinyos")
        db_user = os.getenv("DB_USER", "postgres")
        backup_path = os.path.join(os.getcwd(), "backups")
        os.makedirs(backup_path, exist_ok=True)
        backup_file = os.path.join(backup_path, f"backup_{timestamp}.sql")
        
        cmd = f"pg_dump -h {db_host} -U {db_user} -d {db_name} -f {backup_file}"
        log_json("INFO", f"Iniciando backup do banco de dados: {cmd}")
        os.system(cmd)
        log_json("INFO", f"Backup do banco de dados criado em: {backup_file}")
        return True
    except Exception as e:
        log_json("ERROR", f"Erro ao criar backup: {e}")
        return False

def process_order_data(json_file_path, update_mode="safe", dry_run=False):
    """Reads order data from a JSON file and processes it for database insertion.
    
    Args:
        json_file_path: Caminho para o arquivo JSON com dados das ordens
        update_mode: Modo de atualização ('safe', 'complete' ou 'append')
        dry_run: Se True, simula o processamento sem modificar o banco
    """
    log_json("INFO", f"Iniciando processamento de dados", 
             arquivo=json_file_path, 
             modo=update_mode, 
             simulacao=dry_run)
             
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        log_json("ERROR", f"Arquivo JSON não encontrado", arquivo=json_file_path)
        return
    except json.JSONDecodeError:
        log_json("ERROR", f"Não foi possível decodificar o JSON", arquivo=json_file_path)
        return
    except Exception as e:
        log_json("ERROR", f"Erro ao ler arquivo JSON: {e}", arquivo=json_file_path)
        return

    # Criar backup antes de operações em massa, exceto no modo simulação
    if not dry_run and update_mode != "append":
        backup_database()

    conn = get_db_connection()
    if not conn:
        return

    try:
        cur = conn.cursor()

        orders = data.get("detailed_orders", [])
        if not orders:
            print("No orders found in the JSON data.")
            return

        print(f"Processing {len(orders)} detailed orders...")

        # Verificar se a tabela marcadores_ordem_servico existe, se não, criar
        cur.execute("""
            CREATE TABLE IF NOT EXISTS marcadores_ordem_servico (
                id SERIAL PRIMARY KEY,
                id_ordem_servico INTEGER NOT NULL REFERENCES ordens_servico(id),
                descricao VARCHAR(255) NOT NULL
            );
        """)

        for order in orders:
            try:
                # --- Data Extraction and Cleaning for related tables (contatos, enderecos) ---
                contact_data = order.get("contato") or {}
                address_data = contact_data.get("endereco") or {}

                # Process Enderecos first (UPSERT based on content)
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

                    cur.execute("""
                        SELECT id FROM enderecos
                        WHERE endereco = %s AND numero = %s AND complemento = %s AND bairro = %s
                        AND municipio = %s AND cep = %s AND uf = %s AND pais = %s;
                    """, (endereco, numero, complemento, bairro, municipio, cep, uf, pais))
                    existing_address = cur.fetchone()

                    if existing_address:
                        address_id = existing_address[0]
                    else:
                        cur.execute("""
                            INSERT INTO enderecos (endereco, numero, complemento, bairro, municipio, cep, uf, pais)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING id;
                        """, (endereco, numero, complemento, bairro, municipio, cep, uf, pais))
                        address_id = cur.fetchone()[0]

                # Process Contatos (UPSERT based on API ID)
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
                    cur.execute(upsert_contact_sql, (
                        contact_id, nome_contato, codigo_contato, fantasia_contato,
                        tipo_pessoa_contato, cpf_cnpj_contato, inscricao_estadual_contato,
                        rg_contato, telefone_contato, celular_contato, email_contato, address_id
                    ))
                else:
                    contact_id = None

                # --- Data Extraction and Cleaning for ordens_servico ---
                order_id = order.get("id")
                if order_id is None:
                    print(f"Skipping order due to missing ID: {order}")
                    continue

                numero_ordem_servico = order.get("numeroOrdemServico")
                situacao_str = order.get("situacao", "")
                situacao = situacao_str.split(" - ")[0] if " - " in situacao_str else situacao_str

                data_emissao_str = order.get("data")
                data_emissao = data_emissao_str if data_emissao_str and data_emissao_str != '0000-00-00' else None

                data_prevista_str = order.get("dataPrevista")
                data_prevista = data_prevista_str if data_prevista_str and not data_prevista_str.startswith('0000-00-00') else None

                data_conclusao_str = order.get("dataConclusao")
                data_conclusao = data_conclusao_str if data_conclusao_str and data_conclusao_str != '0000-00-00' else None

                def parse_numeric(value_str):
                    if value_str is None or value_str == "":
                        return None
                    try:
                        return float(str(value_str).replace(',', '.'))
                    except ValueError:
                        print(f"Warning: Could not convert '{value_str}' to numeric for Order ID {order_id}")
                        return None

                total_servicos = parse_numeric(order.get("totalServicos"))
                total_ordem_servico = parse_numeric(order.get("totalOrdemServico"))
                total_pecas = parse_numeric(order.get("totalPecas"))
                alq_comissao = parse_numeric(order.get("alqComissao"))
                vlr_comissao = parse_numeric(order.get("vlrComissao"))
                desconto = parse_numeric(order.get("desconto"))

                equipamento = order.get("equipamento")
                equipamento_serie = order.get("equipamentoSerie") if order.get("equipamentoSerie") != "" else None
                descricao_problema = order.get("descricaoProblema")
                observacoes = order.get("observacoes")
                observacoes_internas = order.get("observacoesInternas")
                # Campos removidos: orcar, orcado
                id_lista_preco = order.get("idListaPreco") if order.get("idListaPreco") != 0 else None
                tecnico = order.get("tecnico")
                id_conta_contabil = order.get("idContaContabil") if order.get("idContaContabil") != 0 else None

                vendedor_data = order.get("vendedor") or {}
                id_vendedor = vendedor_data.get("id")
                categoria_data = order.get("categoria") or {}
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
                forma_pagamento_data = order.get("formaPagamento") or {}
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

                # --- Processamento de marcadores ---
                marcadores = order.get("marcadores", [])
                origem_cliente = None
                
                # Primeiro, determinar a origem do cliente a partir dos marcadores
                for marcador in marcadores:
                    # Verifica se marcador é um dicionário ou uma string
                    if isinstance(marcador, dict):
                        # Se for um dicionário, extrair o nome/valor do marcador
                        marcador_text = marcador.get('nome', '') or marcador.get('name', '') or marcador.get('value', '') or ''
                        marcador_lower = marcador_text.lower() if marcador_text else ""
                    else:
                        # Se for uma string, usar diretamente
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

                # Verificar se a ordem tem dados válidos antes de persistir
                if not validate_order_data(order):
                    log_json("WARNING", "Ordem com dados inválidos ignorada", order_id=order.get('id', 'desconhecido'))
                    continue

                # --- Database Insertion/Update for ordens_servico ---
                if update_mode == "append":
                    # No modo append, só insere se não existir
                    cur.execute("SELECT id FROM ordens_servico WHERE id = %s", (order_id,))
                    if cur.fetchone():
                        log_json("INFO", "Ordem já existe no banco, pulando no modo append", order_id=order_id)
                        continue
                    insert_sql = """
                        INSERT INTO ordens_servico (
                            id, numero_ordem_servico, situacao, data_emissao, data_prevista,
                            data_conclusao, total_servicos, total_ordem_servico, total_pecas,
                            equipamento, equipamento_serie, descricao_problema, observacoes,
                            observacoes_internas, orcar, orcado, alq_comissao, vlr_comissao,
                            desconto, id_lista_preco, tecnico, id_contato, id_vendedor,
                            id_categoria_os, id_forma_pagamento, id_conta_contabil,
                            linha_dispositivo, tipo_servico, origem_cliente, data_extracao
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
                        )
                    """
                    cur.execute(insert_sql, (
                        order_id, numero_ordem_servico, situacao, data_emissao, data_prevista,
                        data_conclusao, total_servicos, total_ordem_servico, total_pecas,
                        equipamento, equipamento_serie, descricao_problema, observacoes,
                        observacoes_internas, orcar, orcado, alq_comissao, vlr_comissao,
                        desconto, id_lista_preco, tecnico, contact_id, id_vendedor,
                        id_categoria_os, id_forma_pagamento, id_conta_contabil,
                        linha_dispositivo, tipo_servico, origem_cliente
                    ))
                elif update_mode == "complete":
                    # Modo complete: substitui todos os valores, incluindo NULL (usar com cuidado)
                    upsert_sql = """
                        INSERT INTO ordens_servico (
                            id, numero_ordem_servico, situacao, data_emissao, data_prevista,
                            data_conclusao, total_servicos, total_ordem_servico, total_pecas,
                            equipamento, equipamento_serie, descricao_problema, observacoes,
                            observacoes_internas, orcar, orcado, alq_comissao, vlr_comissao,
                            desconto, id_lista_preco, tecnico, id_contato, id_vendedor,
                            id_categoria_os, id_forma_pagamento, id_conta_contabil,
                            linha_dispositivo, tipo_servico, origem_cliente, data_extracao
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
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
                            orcar = EXCLUDED.orcar,
                            orcado = EXCLUDED.orcado,
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
                    cur.execute(upsert_sql, (
                        order_id, numero_ordem_servico, situacao, data_emissao, data_prevista,
                        data_conclusao, total_servicos, total_ordem_servico, total_pecas,
                        equipamento, equipamento_serie, descricao_problema, observacoes,
                        observacoes_internas, orcar, orcado, alq_comissao, vlr_comissao,
                        desconto, id_lista_preco, tecnico, contact_id, id_vendedor,
                        id_categoria_os, id_forma_pagamento, id_conta_contabil,
                        linha_dispositivo, tipo_servico, origem_cliente
                    ))
                else:  # Modo "safe" (padrão)
                    # Modo seguro: usa COALESCE para não sobrescrever dados existentes com NULL
                    safe_update_sql = """
                        INSERT INTO ordens_servico (
                            id, numero_ordem_servico, situacao, data_emissao, data_prevista,
                            data_conclusao, total_servicos, total_ordem_servico, total_pecas,
                            equipamento, equipamento_serie, descricao_problema, observacoes,
                            observacoes_internas, orcar, orcado, alq_comissao, vlr_comissao,
                            desconto, id_lista_preco, tecnico, id_contato, id_vendedor,
                            id_categoria_os, id_forma_pagamento, id_conta_contabil,
                            linha_dispositivo, tipo_servico, origem_cliente, data_extracao
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
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
                            equipamento = COALESCE(EXCLUDED.equipamento, ordens_servico.equipamento),
                            equipamento_serie = COALESCE(EXCLUDED.equipamento_serie, ordens_servico.equipamento_serie),
                            descricao_problema = COALESCE(EXCLUDED.descricao_problema, ordens_servico.descricao_problema),
                            observacoes = COALESCE(EXCLUDED.observacoes, ordens_servico.observacoes),
                            observacoes_internas = COALESCE(EXCLUDED.observacoes_internas, ordens_servico.observacoes_internas),
                            orcar = EXCLUDED.orcar,
                            orcado = EXCLUDED.orcado,
                            alq_comissao = EXCLUDED.alq_comissao,
                            vlr_comissao = EXCLUDED.vlr_comissao,
                            desconto = EXCLUDED.desconto,
                            id_lista_preco = EXCLUDED.id_lista_preco,
                            tecnico = COALESCE(EXCLUDED.tecnico, ordens_servico.tecnico),
                            id_contato = EXCLUDED.id_contato,
                            id_vendedor = EXCLUDED.id_vendedor,
                            id_categoria_os = EXCLUDED.id_categoria_os,
                            id_forma_pagamento = EXCLUDED.id_forma_pagamento,
                            id_conta_contabil = EXCLUDED.id_conta_contabil,
                            linha_dispositivo = EXCLUDED.linha_dispositivo,
                            tipo_servico = EXCLUDED.tipo_servico,
                            origem_cliente = COALESCE(EXCLUDED.origem_cliente, ordens_servico.origem_cliente),
                            data_extracao = CURRENT_TIMESTAMP;
                    """
                    cur.execute(safe_update_sql, (
                        order_id, numero_ordem_servico, situacao, data_emissao, data_prevista,
                        data_conclusao, total_servicos, total_ordem_servico, total_pecas,
                        equipamento, equipamento_serie, descricao_problema, observacoes,
                        observacoes_internas, orcar, orcado, alq_comissao, vlr_comissao,
                        desconto, id_lista_preco, tecnico, contact_id, id_vendedor,
                        id_categoria_os, id_forma_pagamento, id_conta_contabil,
                        linha_dispositivo, tipo_servico, origem_cliente
                    ))

                # Processar marcadores
                if marcadores:
                    # Primeiro, limpar os marcadores existentes para esta ordem
                    cur.execute("""
                        DELETE FROM marcadores_ordem_servico
                        WHERE id_ordem_servico = %s;
                    """, (order_id,))
                    
                    # Inserir cada marcador
                    for marcador in marcadores:
                        descricao = None
                        if isinstance(marcador, dict):
                            descricao = marcador.get('descricao', '').strip()
                        elif isinstance(marcador, str):
                            descricao = marcador.strip()
                        if descricao:
                            cur.execute("""
                                INSERT INTO marcadores_ordem_servico (id_ordem_servico, descricao)
                                VALUES (%s, %s)
                            """, (order_id, descricao))

                # Process order items if present
                itens = order.get("itens", [])
                if itens:
                    # First, delete existing items for this order to avoid duplicates
                    cur.execute("DELETE FROM itens_ordem_servico WHERE id_ordem_servico = %s;", (order_id,))
                    
                    # Then insert the new items
                    for item in itens:
                        item_id = item.get("id")
                        id_produto = item.get("idProduto")
                        descricao = item.get("descricao")
                        quantidade = parse_numeric(item.get("quantidade"))
                        valor_unitario = parse_numeric(item.get("valorUnitario"))
                        tipo = item.get("tipo")  # 'P' for product, 'S' for service
                        valor_total = parse_numeric(item.get("valorTotal"))
                        desconto_item = parse_numeric(item.get("desconto"))
                        
                        cur.execute("""
                            INSERT INTO itens_ordem_servico (
                                id, id_ordem_servico, id_produto, descricao, quantidade,
                                valor_unitario, tipo, valor_total, desconto
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s
                            );
                        """, (
                            item_id, order_id, id_produto, descricao, quantidade,
                            valor_unitario, tipo, valor_total, desconto_item
                        ))

                if dry_run:
                    # Em modo simulação, desfaz as alterações
                    conn.rollback()
                    log_json("DEBUG", "[SIMULAÇÃO] Ordem processada com sucesso (rollback aplicado)", 
                           order_id=order_id)
                else:
                    # Commit real em modo normal
                    conn.commit()
                    log_json("INFO", "Ordem processada com sucesso", order_id=order_id)
                
            except Exception as e:
                conn.rollback()
                log_json("ERROR", f"Erro ao processar ordem: {e}", 
                        order_id=order.get('id', 'unknown'))
                
        log_json("INFO", "Processamento concluído", 
                 total_ordens=len(orders), 
                 modo=update_mode, 
                 simulacao=dry_run)
    except Exception as e:
        log_json("ERROR", f"Erro durante o processamento: {e}")
    finally:
        close_db_connection(conn)

def show_help():
    print("\nUso: python process_data_with_tags.py <arquivo_json> [--modo <modo>] [--simulacao]")
    print("\nOpções:")
    print("  <arquivo_json>      : Caminho para o arquivo JSON com os dados das ordens")
    print("  --modo <modo>       : Modo de atualização (safe, complete, append)")
    print("                        - safe: Não sobrescreve dados existentes com NULL (padrão)")
    print("                        - complete: Substitui todos os valores, incluindo NULL")
    print("                        - append: Adiciona apenas ordens novas, não modifica existentes")
    print("  --simulacao         : Executa em modo simulação sem modificar o banco")
    print("  --ajuda             : Mostra esta mensagem de ajuda")
    print("\nExemplos:")
    print("  python process_data_with_tags.py dados.json")
    print("  python process_data_with_tags.py dados.json --modo safe")
    print("  python process_data_with_tags.py dados.json --modo complete --simulacao")

if __name__ == '__main__':
    if len(sys.argv) < 2 or '--ajuda' in sys.argv:
        show_help()
        sys.exit(0)
        
    json_data_file = sys.argv[1]
    update_mode = "safe"
    dry_run = False
    
    # Processar argumentos
    if '--modo' in sys.argv:
        mode_index = sys.argv.index('--modo')
        if mode_index + 1 < len(sys.argv):
            mode = sys.argv[mode_index + 1]
            if mode in ["safe", "complete", "append"]:
                update_mode = mode
            else:
                print(f"Modo inválido: {mode}. Usando modo 'safe' como padrão.")
    
    if '--simulacao' in sys.argv:
        dry_run = True
        print("Executando em modo de simulação (nenhuma alteração será salva)")
    
    process_order_data(json_data_file, update_mode=update_mode, dry_run=dry_run)
