import json
import requests
import os
import sys
from datetime import datetime
import pandas as pd
from db_utils import get_db_connection

def log_json(level, message, **kwargs):
    """Função de log estruturado."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": message,
        **kwargs
    }
    print(json.dumps(log_entry, ensure_ascii=False))

def get_access_token():
    """Obtém o token de acesso do arquivo tiny_token.json"""
    try:
        with open('tiny_token.json', 'r', encoding='utf-8') as f:
            token_data = json.load(f)
        return token_data.get('access_token')
    except Exception as e:
        log_json("ERROR", f"Erro ao ler o token de acesso: {e}")
        return None

def buscar_ordem_na_api(ordem_id):
    """Busca uma ordem de serviço na API do Tiny"""
    token = get_access_token()
    if not token:
        log_json("ERROR", "Token da API Tiny não encontrado")
        return None
    
    url = "https://api.tiny.com.br/api2/os.obter.php"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        'id': ordem_id,
        'formato': 'json'
    }
    
    try:
        # Primeiro tenta com o token no header (método mais recente)
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Verifica se a resposta foi bem-sucedida
        if 'retorno' in data and 'status_processamento' in data['retorno'] and data['retorno']['status_processamento'] == '3':
            return data['retorno'].get('os', {})
            
        # Se falhar, tenta o método antigo com o token no parâmetro
        log_json("WARNING", "Tentando método antigo de autenticação", ordem_id=ordem_id)
        params['token'] = token
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'retorno' in data and 'status_processamento' in data['retorno'] and data['retorno']['status_processamento'] == '3':
            return data['retorno'].get('os', {})
            
        log_json("ERROR", f"Resposta inesperada da API", resposta=data)
        return None
        
    except requests.exceptions.RequestException as e:
        log_json("ERROR", f"Erro na requisição à API Tiny", ordem_id=ordem_id, error=str(e))
        return None
    except Exception as e:
        log_json("ERROR", f"Erro ao processar resposta da API", ordem_id=ordem_id, error=str(e))
        return None

def get_ordens_sem_contato(limit=10):
    """Busca ordens de serviço sem contato no banco de dados"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor() as cur:
            query = """
            SELECT 
                id, 
                numero_ordem_servico, 
                situacao, 
                data_emissao, 
                equipamento,
                descricao_problema
            FROM 
                ordens_servico 
            WHERE 
                id_contato IS NULL
            ORDER BY 
                data_emissao DESC
            LIMIT %s;
            """
            
            cur.execute(query, (limit,))
            colnames = [desc[0] for desc in cur.description]
            resultados = cur.fetchall()
            
            ordens = []
            for row in resultados:
                ordens.append(dict(zip(colnames, row)))
                
            return ordens
            
    except Exception as e:
        log_json("ERROR", "Erro ao buscar ordens sem contato", error=str(e))
        return []
    finally:
        if conn:
            conn.close()

def main():
    print("Buscando ordens sem contato no banco de dados...")
    ordens = get_ordens_sem_contato(limit=50)  # Limita a 50 ordens para não sobrecarregar
    
    if not ordens:
        print("Nenhuma ordem sem contato encontrada no banco.")
        return
    
    print(f"Encontradas {len(ordens)} ordens sem contato. Verificando na API...")
    
    resultados = []
    
    for ordem in ordens:
        ordem_id = ordem['id']
        log_json("INFO", "Verificando ordem na API", ordem_id=ordem_id)
        
        # Busca a ordem na API
        ordem_api = buscar_ordem_na_api(ordem_id)
        
        # Verifica se a ordem foi encontrada na API
        if not ordem_api:
            log_json("WARNING", "Ordem não encontrada na API", ordem_id=ordem_id)
            resultado = {
                'id_ordem': ordem_id,
                'numero_os': ordem['numero_ordem_servico'],
                'situacao': ordem['situacao'],
                'data_emissao': ordem['data_emissao'].strftime('%Y-%m-%d') if ordem['data_emissao'] else '',
                'equipamento': ordem['equipamento'],
                'status': 'Ordem não encontrada na API',
                'contato_id': None,
                'contato_nome': None,
                'contato_email': None,
                'descricao_problema': ordem.get('descricao_problema', '')[:100] + ('...' if len(ordem.get('descricao_problema', '')) > 100 else '')
            }
            resultados.append(resultado)
            continue
        
        # Verifica se tem contato na API
        contato = ordem_api.get('contato', {})
        contato_id = contato.get('id')
        contato_nome = contato.get('nome')
        contato_email = contato.get('email')
        
        if contato_id:
            status = f"Contato encontrado na API (ID: {contato_id})"
        else:
            status = "Sem contato na API"
        
        # Adiciona ao resultado
        resultado = {
            'id_ordem': ordem_id,
            'numero_os': ordem['numero_ordem_servico'],
            'situacao': ordem['situacao'],
            'data_emissao': ordem['data_emissao'].strftime('%Y-%m-%d') if ordem['data_emissao'] else '',
            'equipamento': ordem['equipamento'],
            'status': status,
            'contato_id': contato_id,
            'contato_nome': contato_nome,
            'contato_email': contato_email,
            'descricao_problema': ordem.get('descricao_problema', '')[:100] + ('...' if len(ordem.get('descricao_problema', '')) > 100 else '')
        }
        
        resultados.append(resultado)
        
        # Pequena pausa para não sobrecarregar a API
        import time
        time.sleep(0.5)
    
    # Salva os resultados em um arquivo CSV
    if resultados:
        df = pd.DataFrame(resultados)
        data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"ordens_sem_contato_{data_hora}.csv"
        df.to_csv(nome_arquivo, index=False, encoding='utf-8-sig')
        print(f"\nRelatório salvo em: {nome_arquivo}")
        
        # Exibe um resumo
        print("\nResumo da verificação:")
        print(f"- Total de ordens verificadas: {len(resultados)}")
        
        # Conta os diferentes status
        status_counts = df['status'].value_counts()
        print("\nStatus encontrados:")
        for status, count in status_counts.items():
            print(f"- {status}: {count} ordens")
        
    else:
        print("Nenhum resultado para salvar.")

if __name__ == "__main__":
    main()
