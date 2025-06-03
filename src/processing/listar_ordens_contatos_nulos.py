import os
import csv
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

# Carrega as variáveis de ambiente
load_dotenv()

def get_db_connection():
    """Estabelece conexão com o banco de dados"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT')
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def get_ordens_com_contatos_nulos():
    """Busca ordens de serviço com contatos nulos"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor() as cur:
            # Consulta para obter as ordens com contatos nulos
            query = """
            SELECT 
                os.id,
                os.numero_ordem_servico,
                os.situacao,
                os.data_emissao,
                os.equipamento,
                os.descricao_problema
            FROM 
                ordens_servico os
            WHERE 
                os.id_contato IS NULL
            ORDER BY 
                os.data_emissao DESC;
            """
            
            cur.execute(query)
            colnames = [desc[0] for desc in cur.description]  # Nomes das colunas
            resultados = cur.fetchall()
            
            # Converter os resultados em uma lista de dicionários
            ordens = []
            for row in resultados:
                ordens.append(dict(zip(colnames, row)))
                
            return ordens
            
    except Exception as e:
        print(f"Erro ao executar a consulta: {e}")
        return []
    finally:
        if conn:
            conn.close()

def salvar_para_csv(ordens, nome_arquivo):
    """Salva as ordens em um arquivo CSV"""
    if not ordens:
        print("Nenhuma ordem encontrada para salvar.")
        return
    
    try:
        with open(nome_arquivo, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=ordens[0].keys())
            writer.writeheader()
            writer.writerows(ordens)
        print(f"Dados salvos com sucesso em {nome_arquivo}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo CSV: {e}")

def main():
    print("Buscando ordens de serviço com contatos nulos...")
    ordens = get_ordens_com_contatos_nulos()
    
    if not ordens:
        print("Nenhuma ordem com contato nulo encontrada.")
        return
    
    print(f"Encontradas {len(ordens)} ordens com contatos nulos.")
    
    # Nome do arquivo com data/hora
    data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"ordens_contatos_nulos_{data_hora}.csv"
    
    # Salvar em CSV
    salvar_para_csv(ordens, nome_arquivo)

if __name__ == "__main__":
    main()
