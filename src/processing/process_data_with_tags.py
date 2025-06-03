import json
import sys
import os
from db_utils import get_db_connection, close_db_connection
from datetime import datetime
import logging

def log_json(level, message, **kwargs):
    """Função de log estruturado."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": message,
        **kwargs
    }
    print(json.dumps(log_entry, ensure_ascii=False))

def validate_order_data(order):
    """Valida se uma ordem tem todos os campos essenciais necessários."""
    # Mapeia os nomes dos campos esperados para os nomes reais no JSON
    field_mapping = {
        'id': 'id',
        'numero': 'numeroOrdemServico',
        'situacao': 'situacao',
        'dataEmissao': 'data'
    }
    
    missing_fields = []
    for expected_field, actual_field in field_mapping.items():
        if actual_field not in order or order[actual_field] is None:
            missing_fields.append(expected_field)
    
    if missing_fields:
        log_json("WARNING", "Ordem com campos obrigatórios ausentes", 
                order_id=order.get('id', 'desconhecido'), 
                missing_fields=missing_fields,
                actual_fields=field_mapping)
        return False
    return True

def backup_database():
    """Cria um backup do banco de dados antes de operações em massa."""
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"backup_ordens_servico_{timestamp}.sql")
    
    try:
        # Comando para fazer um dump do banco de dados PostgreSQL
        # Substitua as credenciais conforme necessário
        cmd = f"pg_dump -h localhost -U postgres -d seu_banco_de_dados -t ordens_servico -f {backup_file}"
        os.system(f"PGPASSWORD=sua_senha {cmd}")
        log_json("INFO", f"Backup do banco de dados criado com sucesso em {backup_file}")
    except Exception as e:
        log_json("ERROR", f"Falha ao criar backup do banco de dados: {e}")

def process_order_data(json_file_path, update_mode="safe", dry_run=False):
    """
    Lê os dados de ordens de um arquivo JSON e os processa para inserção no banco de dados.
    
    Args:
        json_file_path: Caminho para o arquivo JSON com os dados das ordens
        update_mode: Modo de atualização ('safe', 'complete' ou 'append')
        dry_run: Se True, apenas simula o processamento sem modificar o banco
    """
    log_json("INFO", f"Iniciando processamento do arquivo {json_file_path} no modo {update_mode}")
    
    # Carregar dados do arquivo JSON
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Verificar se o arquivo tem o formato esperado
        if 'detailed_orders' not in data:
            log_json("ERROR", "Formato de arquivo inválido: chave 'detailed_orders' não encontrada")
            return
            
        orders = data['detailed_orders']
        log_json("INFO", f"Total de {len(orders)} ordens encontradas no arquivo")
        
    except Exception as e:
        log_json("ERROR", f"Erro ao carregar o arquivo JSON: {e}")
        return
    
    # Conectar ao banco de dados
    conn = get_db_connection()
    if not conn:
        log_json("ERROR", "Não foi possível conectar ao banco de dados")
        return
    
    try:
        cur = conn.cursor()
        
        # Contadores para estatísticas
        total_orders = len(orders)
        processed_count = 0
        inserted_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        # Criar backup antes de processar (apenas se não for dry_run)
        if not dry_run and update_mode in ["complete", "append"] and total_orders > 0:
            log_json("INFO", f"Criando backup do banco de dados antes do processamento...")
            backup_database()
        
        # Processar cada ordem
        for order in orders:
            try:
                # Validar dados básicos da ordem
                if not validate_order_data(order):
                    log_json("WARNING", "Ordem com dados inválidos, pulando...", order_id=order.get('id', 'desconhecido'))
                    error_count += 1
                    continue
                
                # Obter o ID da ordem para logs
                order_id = order.get('id')
                try:
                    order_id = int(order_id)  # Garantir que é um número inteiro
                except (ValueError, TypeError):
                    log_json("ERROR", f"ID de ordem inválido: {order_id}")
                    error_count += 1
                    continue
                
                order_id = order['id']
                processed_count += 1
                
                # Extrair dados básicos
                numero_ordem_servico = order.get('numeroOrdemServico')  
                situacao = order.get('situacao')
                
                # Tratar datas vazias e inválidas
                def parse_date(date_str):
                    if not date_str or date_str in ['0000-00-00', '0000-00-00 00:00:00']:
                        return None
                    try:
                        # Tenta converter a data para o formato ISO
                        if 'T' in date_str:  # Formato ISO com 'T'
                            return datetime.fromisoformat(date_str.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
                        elif ' ' in date_str:  # Formato 'YYYY-MM-DD HH:MM:SS'
                            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                        else:  # Formato 'YYYY-MM-DD'
                            return datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
                    except (ValueError, TypeError):
                        return None
                
                data_emissao = parse_date(order.get('data'))
                data_prevista = parse_date(order.get('dataPrevista'))
                data_conclusao = parse_date(order.get('dataConclusao'))
                
                # Extrair totais (os totais estão no nível raiz do objeto, não em um objeto 'totais')
                total_servicos = order.get('totalServicos')
                total_ordem_servico = order.get('totalOrdemServico')
                total_pecas = order.get('totalPecas')
                
                # Extrair informações do contato
                contato = order.get('contato', {})
                contact_id = contato.get('id') if contato else None
                
                # Se o contato não existir, definir como NULL
                if contact_id is not None:
                    try:
                        cur.execute("SELECT 1 FROM contatos WHERE id = %s", (contact_id,))
                        if not cur.fetchone():
                            log_json("WARNING", f"Contato {contact_id} não encontrado, definindo como NULL", order_id=order_id)
                            contact_id = None
                    except Exception as e:
                        log_json("ERROR", f"Erro ao verificar contato {contact_id}", error=str(e))
                        contact_id = None
                
                # Extrair informações adicionais
                alq_comissao = order.get('alqComissao')
                vlr_comissao = order.get('vlrComissao')
                desconto = order.get('desconto')
                
                # Garantir que valores numéricos sejam tratados corretamente
                try:
                    alq_comissao = float(alq_comissao) if alq_comissao is not None and str(alq_comissao).strip() else None
                except (ValueError, TypeError):
                    alq_comissao = None
                    
                try:
                    vlr_comissao = float(vlr_comissao) if vlr_comissao is not None and str(vlr_comissao).strip() else None
                except (ValueError, TypeError):
                    vlr_comissao = None
                    
                try:
                    desconto = float(desconto) if desconto is not None and str(desconto).strip() else None
                except (ValueError, TypeError):
                    desconto = None
                
                # Extrair informações do equipamento
                equipamento = order.get('equipamento')
                equipamento_serie = order.get('equipamentoSerie') if order.get('equipamentoSerie') != "" else None
                descricao_problema = order.get('descricaoProblema')
                observacoes = order.get('observacoes')
                observacoes_internas = order.get('observacoesInternas')
                # Campos removidos: orcar, orcado
                id_lista_preco = order.get('idListaPreco') if order.get('idListaPreco') != 0 else None
                tecnico = order.get('tecnico')
                id_conta_contabil = order.get('idContaContabil') if order.get('idContaContabil') != 0 else None
                id_vendedor = order.get('idVendedor') if order.get('idVendedor') != 0 else None
                id_categoria_os = order.get('idCategoriaOs') if order.get('idCategoriaOs') != 0 else None
                id_forma_pagamento = order.get('idFormaPagamento') if order.get('idFormaPagamento') != 0 else None
                linha_dispositivo = order.get('linhaDispositivo')
                tipo_servico = order.get('tipoServico')
                
                # Processar marcadores (tags)
                marcadores = order.get('marcadores', [])
                origem_cliente = 'outros'  # Valor padrão
                
                # Verificar origem do cliente baseado nos marcadores
                for marcador in marcadores:
                    if isinstance(marcador, dict) and 'marcador' in marcador:
                        marcador_desc = marcador['marcador'].get('descricao', '').lower()
                        if 'whatsapp' in marcador_desc:
                            origem_cliente = 'whatsapp'
                            break
                        elif 'instagram' in marcador_desc:
                            origem_cliente = 'instagram'
                            break
                        elif 'facebook' in marcador_desc:
                            origem_cliente = 'facebook'
                            break
                        elif 'google' in marcador_desc:
                            origem_cliente = 'google'
                            break
                        elif 'indicacao' in marcador_desc:
                            origem_cliente = 'indicacao'
                            break
                        elif 'site' in marcador_desc:
                            origem_cliente = 'site'
                            break
                
                # Verificar se a ordem tem dados válidos antes de persistir
                if not validate_order_data(order):
                    log_json("WARNING", "Ordem com dados inválidos ignorada", order_id=order.get('id', 'desconhecido'))
                    continue

                # --- Inserção/Atualização no banco de dados para ordens_servico ---
                if update_mode == "append":
                    # No modo append, só insere se não existir
                    cur.execute("SELECT id FROM ordens_servico WHERE id = %s", (order_id,))
                    if cur.fetchone():
                        log_json("INFO", "Ordem já existe no banco, pulando no modo append", order_id=order_id)
                        skipped_count += 1
                        continue
                    insert_sql = """
                        INSERT INTO ordens_servico (
                            id, numero_ordem_servico, situacao, data_emissao, data_prevista,
                            data_conclusao, total_servicos, total_ordem_servico, total_pecas,
                            equipamento, equipamento_serie, descricao_problema, observacoes,
                            observacoes_internas, alq_comissao, vlr_comissao,
                            desconto, id_lista_preco, tecnico, id_contato, id_vendedor,
                            id_categoria_os, id_forma_pagamento, id_conta_contabil,
                            linha_dispositivo, tipo_servico, origem_cliente, data_extracao
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
                        )
                    """
                    if not dry_run:
                        cur.execute(insert_sql, (
                            order_id, numero_ordem_servico, situacao, data_emissao, data_prevista,
                            data_conclusao, total_servicos, total_ordem_servico, total_pecas,
                            equipamento, equipamento_serie, descricao_problema, observacoes,
                            observacoes_internas, alq_comissao, vlr_comissao,
                            desconto, id_lista_preco, tecnico, contact_id, id_vendedor,
                            id_categoria_os, id_forma_pagamento, id_conta_contabil,
                            linha_dispositivo, tipo_servico, origem_cliente
                        ))
                        inserted_count += 1
                    else:
                        log_json("INFO", "[DRY RUN] Ordem seria inserida", order_id=order_id)
                
                elif update_mode == "complete":
                    # Modo complete: substitui todos os valores, incluindo NULL (usar com cuidado)
                    upsert_sql = """
                        INSERT INTO ordens_servico (
                            id, numero_ordem_servico, situacao, data_emissao, data_prevista,
                            data_conclusao, total_servicos, total_ordem_servico, total_pecas,
                            equipamento, equipamento_serie, descricao_problema, observacoes,
                            observacoes_internas, alq_comissao, vlr_comissao,
                            desconto, id_lista_preco, tecnico, id_contato, id_vendedor,
                            id_categoria_os, id_forma_pagamento, id_conta_contabil,
                            linha_dispositivo, tipo_servico, origem_cliente, data_extracao
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
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
                    if not dry_run:
                        cur.execute(upsert_sql, (
                            order_id, numero_ordem_servico, situacao, data_emissao, data_prevista,
                            data_conclusao, total_servicos, total_ordem_servico, total_pecas,
                            equipamento, equipamento_serie, descricao_problema, observacoes,
                            observacoes_internas, alq_comissao, vlr_comissao,
                            desconto, id_lista_preco, tecnico, contact_id, id_vendedor,
                            id_categoria_os, id_forma_pagamento, id_conta_contabil,
                            linha_dispositivo, tipo_servico, origem_cliente
                        ))
                        updated_count += 1
                    else:
                        log_json("INFO", "[DRY RUN] Ordem seria atualizada", order_id=order_id)
                
                else:  # Modo "safe" (padrão)
                    # No modo safe, só atualiza se a ordem já existir e não sobrescreve campos não nulos com NULL
                    cur.execute("SELECT id FROM ordens_servico WHERE id = %s", (order_id,))
                    if not cur.fetchone():
                        log_json("INFO", "Ordem não encontrada no banco, pulando no modo safe", order_id=order_id)
                        skipped_count += 1
                        continue
                    
                    # Construir a consulta dinamicamente para atualizar apenas campos não nulos
                    update_fields = []
                    update_values = []
                    
                    # Mapear campos para atualização
                    fields_to_update = [
                        ("numero_ordem_servico", numero_ordem_servico),
                        ("situacao", situacao),
                        ("data_emissao", data_emissao),
                        ("data_prevista", data_prevista),
                        ("data_conclusao", data_conclusao),
                        ("total_servicos", total_servicos),
                        ("total_ordem_servico", total_ordem_servico),
                        ("total_pecas", total_pecas),
                        ("equipamento", equipamento),
                        ("equipamento_serie", equipamento_serie),
                        ("descricao_problema", descricao_problema),
                        ("observacoes", observacoes),
                        ("observacoes_internas", observacoes_internas),
                        ("alq_comissao", alq_comissao),
                        ("vlr_comissao", vlr_comissao),
                        ("desconto", desconto),
                        ("id_lista_preco", id_lista_preco),
                        ("tecnico", tecnico),
                        ("id_contato", contact_id),
                        ("id_vendedor", id_vendedor),
                        ("id_categoria_os", id_categoria_os),
                        ("id_forma_pagamento", id_forma_pagamento),
                        ("id_conta_contabil", id_conta_contabil),
                        ("linha_dispositivo", linha_dispositivo),
                        ("tipo_servico", tipo_servico),
                        ("origem_cliente", origem_cliente)
                    ]
                    
                    # Adicionar apenas campos não nulos
                    for field, value in fields_to_update:
                        if value is not None:
                            update_fields.append(f"{field} = %s")
                            update_values.append(value)
                    
                    if not update_fields:
                        log_json("INFO", "Nenhum campo não nulo para atualizar", order_id=order_id)
                        skipped_count += 1
                        continue
                    
                    # Adicionar data de extração
                    update_fields.append("data_extracao = CURRENT_TIMESTAMP")
                    
                    # Construir e executar a consulta
                    update_sql = f"""
                        UPDATE ordens_servico 
                        SET {', '.join(update_fields)}
                        WHERE id = %s
                    """
                    
                    if not dry_run:
                        cur.execute(update_sql, update_values + [order_id])
                        updated_count += 1
                    else:
                        log_json("INFO", f"[DRY RUN] Ordem seria atualizada: {update_sql}", 
                                values=update_values + [order_id], order_id=order_id)
                
                # Processar marcadores (tags) da ordem
                if marcadores and not dry_run:
                    try:
                        # Remover marcadores existentes para esta ordem
                        cur.execute("DELETE FROM marcadores_ordem_servico WHERE id_ordem_servico = %s", (order_id,))
                        
                        # Inserir novos marcadores
                        for marcador in marcadores:
                            if isinstance(marcador, dict) and 'marcador' in marcador:
                                marcador_desc = marcador['marcador'].get('descricao')
                                if marcador_desc:
                                    cur.execute("""
                                        INSERT INTO marcadores_ordem_servico (id_ordem_servico, descricao)
                                        VALUES (%s, %s)
                                    """, (order_id, marcador_desc))
                        
                        log_json("DEBUG", f"Marcadores atualizados para a ordem {order_id}")
                    except Exception as e:
                        log_json("ERROR", f"Erro ao processar marcadores para a ordem {order_id}", error=str(e))
                
                # Commit após cada ordem para evitar perda de dados em caso de falha
                if not dry_run and processed_count % 10 == 0:
                    try:
                        conn.commit()
                        log_json("INFO", f"Commit parcial: {processed_count} ordens processadas")
                    except Exception as e:
                        log_json("ERROR", f"Erro ao fazer commit parcial: {e}")
                        # Tentar reconectar ao banco de dados
                        try:
                            conn = get_db_connection()
                            if conn:
                                cur = conn.cursor()
                                log_json("INFO", "Conexão com o banco de dados restabelecida")
                            else:
                                log_json("ERROR", "Não foi possível reconectar ao banco de dados")
                                break
                        except Exception as e2:
                            log_json("ERROR", f"Falha ao reconectar ao banco de dados: {e2}")
                            break
                
            except Exception as e:
                error_count += 1
                log_json("ERROR", f"Erro ao processar ordem {order_id}", error=str(e), order_id=order_id)
                
                # Fazer rollback da transação atual
                if conn:
                    try:
                        conn.rollback()
                        log_json("INFO", f"Rollback da transação para a ordem {order_id}")
                    except Exception as rollback_error:
                        log_json("ERROR", f"Erro ao fazer rollback: {rollback_error}")
                        # Tentar reconectar ao banco de dados
                        try:
                            conn = get_db_connection()
                            if conn:
                                cur = conn.cursor()
                                log_json("INFO", "Conexão com o banco de dados restabelecida após erro de rollback")
                            else:
                                log_json("ERROR", "Não foi possível reconectar ao banco de dados após erro de rollback")
                                break
                        except Exception as e2:
                            log_json("ERROR", f"Falha ao reconectar ao banco de dados: {e2}")
                            break
                
                # Continuar com a próxima ordem
                continue
        
        # Fazer commit final
        if not dry_run:
            conn.commit()
        
        # Log de resumo
        log_json("INFO", "Processamento concluído", 
                total_orders=total_orders,
                processed=processed_count,
                inserted=inserted_count,
                updated=updated_count,
                skipped=skipped_count,
                errors=error_count)
        
    except Exception as e:
        log_json("ERROR", f"Erro durante o processamento: {e}")
        if conn:
            conn.rollback()
    finally:
        close_db_connection(conn)

def show_help():
    """Exibe a ajuda sobre como usar o script."""
    help_text = """
    Uso: python process_data_with_tags.py <caminho_arquivo_json> [opções]
    
    Opções:
      --modo=<safe|complete|append>  Modo de atualização (padrão: safe)
      --dry-run                     Simula o processamento sem modificar o banco
      --ajuda                       Mostra esta mensagem de ajuda
      
    Modos de atualização:
      - safe:    Atualiza apenas campos não nulos para ordens existentes (padrão)
      - complete:Substitui todos os valores, incluindo NULL (cuidado!)
      - append:  Apenas insere novas ordens, ignora existentes
    """
    print(help_text)

if __name__ == "__main__":
    if len(sys.argv) < 2 or '--ajuda' in sys.argv:
        show_help()
        sys.exit(0)
    
    # Processar argumentos de linha de comando
    json_file = sys.argv[1]
    update_mode = "safe"
    dry_run = False
    
    for arg in sys.argv[2:]:
        if arg.startswith("--modo="):
            update_mode = arg.split("=")[1].lower()
            if update_mode not in ["safe", "complete", "append"]:
                print(f"ERRO: Modo de atualização inválido: {update_mode}")
                show_help()
                sys.exit(1)
        elif arg == "--dry-run":
            dry_run = True
    
    if dry_run:
        print("\n=== MODO DE SIMULAÇÃO (DRY RUN) ===")
        print("Nenhuma alteração será feita no banco de dados.\n")
    
    # Validar arquivo de entrada
    if not os.path.isfile(json_file):
        print(f"ERRO: Arquivo não encontrado: {json_file}")
        sys.exit(1)
    
    # Iniciar processamento
    process_order_data(json_file, update_mode, dry_run)
