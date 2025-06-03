import os
import json
import requests
import pandas as pd
from dotenv import load_dotenv
from db_utils import get_db_connection
from datetime import datetime

# Carrega as variáveis de ambiente
load_dotenv()

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

def get_ordens_com_contatos_nulos():
    """Busca ordens de serviço com contatos nulos no banco de dados"""
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
                equipamento
            FROM 
                ordens_servico
            WHERE 
                id_contato IS NULL
            ORDER BY 
                data_emissao DESC;
            """
            
            cur.execute(query)
            colnames = [desc[0] for desc in cur.description]
            resultados = cur.fetchall()
            
            ordens = []
            for row in resultados:
                ordens.append(dict(zip(colnames, row)))
                
            return ordens
            
    except Exception as e:
        log_json("ERROR", "Erro ao buscar ordens no banco de dados", error=str(e))
        return []
    finally:
        if conn:
            conn.close()

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
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Verifica se a resposta foi bem-sucedida
        if 'retorno' in data and 'status_processamento' in data['retorno'] and data['retorno']['status_processamento'] == '3':
            return data['retorno'].get('os', {})
            
        # Se falhar, tenta o método antigo com o token no parâmetro
        log_json("WARNING", "Tentando método antigo de autenticação", ordem_id=ordem_id)
        params['token'] = token
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if 'retorno' in data and 'status_processamento' in data['retorno'] and data['retorno']['status_processamento'] == '3':
            return data['retorno'].get('os', {})
        else:
            log_json("WARNING", "Erro na resposta da API Tiny", 
                    ordem_id=ordem_id, 
                    resposta=data)
            return None
            
    except Exception as e:
        log_json("ERROR", "Erro ao buscar ordem na API Tiny", 
                ordem_id=ordem_id, 
                error=str(e))
        return None

def verificar_contato_na_os(ordem_api):
    """Verifica se a ordem da API tem um contato válido"""
    if not ordem_api:
        return False, "Ordem não encontrada na API"
    
    contato = ordem_api.get('os', {}).get('contato', {})
    if not contato or 'id' not in contato or not contato['id']:
        return False, "Sem contato na ordem da API"
    
    return True, f"Contato encontrado: ID {contato['id']} - {contato.get('nome', 'Sem nome')}"

def main():
    print("Buscando ordens com contatos nulos no banco de dados...")
    ordens = get_ordens_com_contatos_nulos()
    
    if not ordens:
        print("Nenhuma ordem com contato nulo encontrada no banco.")
        return
    
    print(f"Encontradas {len(ordens)} ordens com contatos nulos. Verificando na API...")
    
    resultados = []
    
    for ordem in ordens[:50]:  # Limita a 50 ordens para não sobrecarregar a API
        ordem_id = ordem['id']
        log_json("INFO", "Verificando ordem na API", ordem_id=ordem_id)
        
        # Busca a ordem na API
        ordem_api = buscar_ordem_na_api(ordem_id)
        
        # Verifica se tem contato na API
        tem_contato, mensagem = verificar_contato_na_os(ordem_api)
        
        # Adiciona ao resultado
        resultado = {
            'id_ordem': ordem_id,
            'numero_os': ordem['numero_ordem_servico'],
            'situacao': ordem['situacao'],
            'data_emissao': ordem['data_emissao'].strftime('%Y-%m-%d') if ordem['data_emissao'] else '',
            'equipamento': ordem['equipamento'],
            'tem_contato_na_api': 'Sim' if tem_contato else 'Não',
            'status_contato': mensagem,
            'contato_id': ordem_api.get('os', {}).get('contato', {}).get('id') if ordem_api else None,
            'contato_nome': ordem_api.get('os', {}).get('contato', {}).get('nome') if ordem_api else None
        }
        
        resultados.append(resultado)
        
        # Pequena pausa para não sobrecarregar a API
        import time
        time.sleep(0.5)
    
    # Salva os resultados em um arquivo CSV
    if resultados:
        df = pd.DataFrame(resultados)
        data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"verificacao_contatos_api_{data_hora}.csv"
        df.to_csv(nome_arquivo, index=False, encoding='utf-8-sig')
        print(f"\nRelatório salvo em: {nome_arquivo}")
        
        # Exibe um resumo
        print("\nResumo da verificação:")
        print(f"- Total de ordens verificadas: {len(resultados)}")
        print(f"- Ordens com contato na API: {len([r for r in resultados if r['tem_contato_na_api'] == 'Sim'])}")
        print(f"- Ordens sem contato na API: {len([r for r in resultados if r['tem_contato_na_api'] == 'Não'])}")
    else:
        print("Nenhum resultado para salvar.")

if __name__ == "__main__":
    main()
