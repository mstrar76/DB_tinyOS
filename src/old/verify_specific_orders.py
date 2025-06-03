import requests
import json
import os
import logging
from datetime import datetime
import sys

# Configuração de logging estruturado em formato JSON
def setup_logger():
    logger = logging.getLogger("verify_specific_orders")
    logger.setLevel(logging.INFO)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    
    # Formatter JSON
    formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "service": "verify_specific_orders", "message": %(message)s}'
    )
    console_handler.setFormatter(formatter)
    
    # Handler para arquivo
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"verify_specific_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    logger.handlers = [console_handler, file_handler]
    return logger

logger = setup_logger()

# Constantes
API_BASE = "https://api.tiny.com.br/public-api/v3"
TOKEN_FILE = "tiny_token.json"
OUTPUT_DIR = "order_api_responses"

# Lista de ordens a verificar
ORDER_NUMBERS = [
    30406, 30422, 30441, 30429, 30428, 30451, 30507, 30520, 30551, 30557, 
    30555, 30575, 30583, 30581, 30593, 30634, 31067, 30639, 30654, 30664, 
    30673, 30689, 30685, 30684, 30701, 30736, 30735, 30733, 30746, 30745, 
    30757, 30784, 30783, 30796, 30812, 30819, 30844, 30859, 30858, 30853, 
    30863, 30867, 30891, 30887, 30886, 30894, 30892, 30907, 30910, 30937, 
    30955, 30977, 30975, 31007, 31013, 31015, 31033, 31043, 31055, 31062, 
    31071, 31080, 31077, 31075, 31101, 31098, 31094, 31111, 31110, 31104, 
    31115, 31117, 31116, 31136, 31142, 31139
]

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

def fetch_order_by_number(order_number, token):
    """Busca uma ordem pelo número da ordem."""
    url = f"{API_BASE}/ordem-servico"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"numeroOrdemServico": order_number}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        # Verificar se o token expirou (401)
        if response.status_code == 401:
            logger.info(json.dumps({"message": f"Token expirado para ordem {order_number}. Tentando atualizar..."}))
            new_token = refresh_access_token()
            if new_token:
                headers["Authorization"] = f"Bearer {new_token}"
                response = requests.get(url, headers=headers, params=params)
            else:
                logger.error(json.dumps({"error": "Falha ao atualizar token. Não é possível continuar."}))
                return None
        
        if response.status_code != 200:
            logger.error(json.dumps({
                "error": f"Falha ao buscar ordem {order_number}",
                "status_code": response.status_code,
                "response": response.text
            }))
            return None
        
        data = response.json()
        items = data.get("itens", [])
        
        if not items:
            logger.warning(json.dumps({"message": f"Nenhuma ordem encontrada com o número {order_number}"}))
            return None
        
        # Retorna o primeiro item encontrado (deveria ser único pelo número da ordem)
        return items[0]
    
    except Exception as e:
        logger.error(json.dumps({"error": f"Erro ao buscar ordem {order_number}: {e}"}))
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

def save_order_details(order_number, order_data):
    """Salva os detalhes da ordem em um arquivo JSON."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    filename = f"order_{order_number}_details.json"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(order_data, f, ensure_ascii=False, indent=2)
        logger.info(json.dumps({"message": f"Detalhes da ordem {order_number} salvos em {filepath}"}))
    except Exception as e:
        logger.error(json.dumps({"error": f"Erro ao salvar detalhes da ordem {order_number}: {e}"}))

def main():
    # Obter token de acesso
    token = get_access_token()
    if not token:
        logger.error(json.dumps({"error": "Nenhum token de acesso encontrado. Abortando."}))
        return
    
    # Criar arquivo de resultados
    results_file = os.path.join(OUTPUT_DIR, f"orders_verification_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    results = []
    
    # Verificar cada ordem
    for order_number in ORDER_NUMBERS:
        logger.info(json.dumps({"action": "verify_order", "order_number": order_number}))
        
        # Buscar ordem pelo número
        order = fetch_order_by_number(order_number, token)
        
        if not order:
            # Ordem não encontrada
            result = {
                "numero_ordem": order_number,
                "encontrada": False,
                "status": "Não encontrada na API",
                "data": None,
                "valor": None,
                "detalhes": None
            }
        else:
            # Ordem encontrada, buscar detalhes
            order_id = order.get("id")
            order_details = fetch_order_details(order_id, token) if order_id else None
            
            # Salvar detalhes em arquivo separado
            if order_details:
                save_order_details(order_number, order_details)
            
            # Preparar resultado
            result = {
                "numero_ordem": order_number,
                "encontrada": True,
                "status": order.get("situacao"),
                "data": order.get("data"),
                "valor": order.get("totalOrdemServico"),
                "detalhes": {
                    "id": order_id,
                    "data_emissao": order.get("data"),
                    "data_prevista": order.get("dataPrevista"),
                    "data_conclusao": order.get("dataConclusao"),
                    "nome_contato": order.get("nomeContato"),
                    "total_servicos": order.get("totalServicos"),
                    "total_pecas": order.get("totalPecas"),
                    "total_ordem": order.get("totalOrdemServico")
                }
            }
        
        # Adicionar resultado à lista
        results.append(result)
        
        # Imprimir resultado no console
        status_str = result["status"] if result["encontrada"] else "Não encontrada"
        data_str = result["data"] if result["encontrada"] else "-"
        valor_str = f"R$ {result['valor']}" if result["encontrada"] and result["valor"] else "R$ 0,00"
        
        print(f"{order_number}\t{data_str}\t{status_str}\t{valor_str}")
        
        # Aguardar um pouco para respeitar limites de taxa da API
        import time
        time.sleep(0.5)
    
    # Salvar todos os resultados em um único arquivo
    try:
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info(json.dumps({"message": f"Resultados salvos em {results_file}"}))
        print(f"\nResultados completos salvos em {results_file}")
    except Exception as e:
        logger.error(json.dumps({"error": f"Erro ao salvar resultados: {e}"}))

if __name__ == "__main__":
    main()
