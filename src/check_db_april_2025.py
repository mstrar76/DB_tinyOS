import psycopg2
import json
from dotenv import load_dotenv
import os
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().isoformat()}] {msg}")

# Carregar variáveis de ambiente
load_dotenv()

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
        print("Database connection established.")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def close_db_connection(conn):
    """Fecha a conexão com o banco de dados."""
    if conn:
        conn.close()
        print("Database connection closed.")

def check_april_2025_orders():
    """Verifica as ordens de serviço de abril de 2025 no banco de dados."""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        
        # Verificar contagem de ordens de abril de 2025
        cur.execute("""
            SELECT COUNT(*) 
            FROM ordens_servico 
            WHERE data_emissao BETWEEN '2025-04-01' AND '2025-04-30';
        """)
        count_april = cur.fetchone()[0]
        print(f"Total de ordens de abril de 2025 no banco: {count_april}")
        
        # Verificar contagem de marcadores para ordens de abril de 2025
        cur.execute("""
            SELECT COUNT(*) 
            FROM marcadores_ordem_servico mos
            JOIN ordens_servico os ON mos.id_ordem_servico = os.id
            WHERE os.data_emissao BETWEEN '2025-04-01' AND '2025-04-30';
        """)
        count_markers = cur.fetchone()[0]
        print(f"Total de marcadores para ordens de abril de 2025: {count_markers}")
        
        # Verificar algumas ordens específicas
        for os_number in ["31116", "31113", "31068", "31069", "31050"]:
            cur.execute("""
                SELECT id, numero_ordem_servico, data_emissao, situacao, equipamento, 
                       descricao_problema, linha_dispositivo, tipo_servico, origem_cliente
                FROM ordens_servico 
                WHERE numero_ordem_servico = %s;
            """, (os_number,))
            order = cur.fetchone()
            
            if order:
                print(f"\nOS #{os_number} (ID: {order[0]}):")
                print(f"  Data de emissão: {order[2]}")
                print(f"  Situação: {order[3]}")
                print(f"  Equipamento: {order[4]}")
                print(f"  Problema: {order[5]}")
                print(f"  Linha: {order[6]}")
                print(f"  Tipo de serviço: {order[7]}")
                print(f"  Origem do cliente: {order[8]}")
                
                # Verificar marcadores desta ordem
                cur.execute("""
                    SELECT descricao 
                    FROM marcadores_ordem_servico 
                    WHERE id_ordem_servico = %s;
                """, (order[0],))
                markers = cur.fetchall()
                
                if markers:
                    print("  Marcadores:")
                    for marker in markers:
                        print(f"    - {marker[0]}")
                else:
                    print("  Marcadores: Nenhum encontrado")
            else:
                print(f"\nOS #{os_number}: Não encontrada no banco de dados")
        
    except Exception as e:
        print(f"Erro ao verificar ordens de abril de 2025: {e}")
    finally:
        close_db_connection(conn)

if __name__ == "__main__":
    check_april_2025_orders()
