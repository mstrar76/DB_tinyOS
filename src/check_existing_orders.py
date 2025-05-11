import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

def get_db_connection():
    """Estabelece e retorna uma conexão com o banco de dados PostgreSQL usando variáveis de ambiente."""
    try:
        conn = psycopg2.connect(
            host=os.environ.get("DB_HOST"),
            database=os.environ.get("DB_NAME"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            port=os.environ.get("DB_PORT")
        )
        print("Conexão com o banco de dados estabelecida.")
        return conn
    except psycopg2.OperationalError as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def close_db_connection(conn):
    """Fecha a conexão com o banco de dados."""
    if conn:
        conn.close()
        print("Conexão com o banco de dados fechada.")

def check_existing_orders():
    """Verifica as ordens existentes no banco de dados e retorna estatísticas."""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        
        # Contagem total de ordens
        cur.execute("SELECT COUNT(*) FROM ordens_servico;")
        total_orders = cur.fetchone()[0]
        print(f"\nTotal de ordens no banco de dados: {total_orders}")
        
        # Contagem por situação
        cur.execute("""
            SELECT situacao, COUNT(*) 
            FROM ordens_servico 
            GROUP BY situacao 
            ORDER BY COUNT(*) DESC;
        """)
        situation_counts = cur.fetchall()
        
        print("\nQuantidade de ordens por situação:")
        situation_map = {
            '0': 'Em Aberto',
            '1': 'Orçada',
            '2': 'Serviço Concluído',
            '3': 'Finalizada',
            '4': 'Não Aprovada',
            '5': 'Aprovada',
            '6': 'Em Andamento',
            '7': 'Cancelada'
        }
        
        for situation, count in situation_counts:
            situation_desc = situation_map.get(situation, f"Desconhecido ({situation})")
            print(f"  {situation_desc}: {count}")
        
        # Contagem por ano/mês
        cur.execute("""
            SELECT 
                EXTRACT(YEAR FROM data_emissao) AS ano,
                EXTRACT(MONTH FROM data_emissao) AS mes,
                COUNT(*) 
            FROM ordens_servico 
            WHERE data_emissao IS NOT NULL
            GROUP BY ano, mes 
            ORDER BY ano DESC, mes DESC;
        """)
        date_counts = cur.fetchall()
        
        print("\nQuantidade de ordens por ano/mês:")
        for year, month, count in date_counts:
            print(f"  {int(year)}/{int(month):02d}: {count}")
        
        # Verificar ordens de 2024 e 2025
        cur.execute("""
            SELECT 
                EXTRACT(YEAR FROM data_emissao) AS ano,
                COUNT(*) 
            FROM ordens_servico 
            WHERE EXTRACT(YEAR FROM data_emissao) IN (2024, 2025)
            GROUP BY ano 
            ORDER BY ano;
        """)
        year_counts = cur.fetchall()
        
        print("\nOrdens de 2024 e 2025:")
        for year, count in year_counts:
            print(f"  {int(year)}: {count}")
        
        # Verificar últimas ordens adicionadas
        cur.execute("""
            SELECT 
                id, 
                numero_ordem_servico, 
                data_emissao, 
                situacao,
                data_extracao
            FROM ordens_servico 
            ORDER BY data_extracao DESC 
            LIMIT 10;
        """)
        latest_orders = cur.fetchall()
        
        print("\nÚltimas 10 ordens adicionadas:")
        for order in latest_orders:
            order_id, order_number, emission_date, situation, extraction_date = order
            situation_desc = situation_map.get(situation, f"Desconhecido ({situation})")
            print(f"  ID: {order_id}, Número OS: {order_number}, Data: {emission_date}, Situação: {situation_desc}, Extraído em: {extraction_date}")
        
        # Verificar ordens por mês em 2024
        if any(int(year) == 2024 for year, _ in year_counts):
            cur.execute("""
                SELECT 
                    EXTRACT(MONTH FROM data_emissao) AS mes,
                    COUNT(*) 
                FROM ordens_servico 
                WHERE EXTRACT(YEAR FROM data_emissao) = 2024
                GROUP BY mes 
                ORDER BY mes;
            """)
            month_counts_2024 = cur.fetchall()
            
            print("\nOrdens de 2024 por mês:")
            for month, count in month_counts_2024:
                print(f"  Mês {int(month)}: {count}")
        
        # Verificar ordens por mês em 2025
        if any(int(year) == 2025 for year, _ in year_counts):
            cur.execute("""
                SELECT 
                    EXTRACT(MONTH FROM data_emissao) AS mes,
                    COUNT(*) 
                FROM ordens_servico 
                WHERE EXTRACT(YEAR FROM data_emissao) = 2025
                GROUP BY mes 
                ORDER BY mes;
            """)
            month_counts_2025 = cur.fetchall()
            
            print("\nOrdens de 2025 por mês:")
            for month, count in month_counts_2025:
                print(f"  Mês {int(month)}: {count}")
        
    except Exception as e:
        print(f"Erro ao consultar o banco de dados: {e}")
    finally:
        close_db_connection(conn)

if __name__ == "__main__":
    print("Verificando ordens existentes no banco de dados...")
    check_existing_orders()
