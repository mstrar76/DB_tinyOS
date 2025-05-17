import http.server
import socketserver
import webbrowser
import requests
import json
import time
import threading
import logging
import datetime
from urllib.parse import urlparse, parse_qs, urlencode

# --- Configurações (Substitua pelos seus valores) ---
CLIENT_ID = "tiny-api-f24a1e97d89c12a4d4ba533080f41afc78a91413-1742858724"
CLIENT_SECRET = "2rjVzKqsNCtFFJPDbUhaTqDXli22hm9v" # Mantenha isso seguro!
PORT = 8080  # Porta onde o servidor local irá rodar
REDIRECT_URI = f"http://localhost:{PORT}/callback" # URI de redirecionamento (deve ser registrado no Tiny)
AUTH_URL = "https://accounts.tiny.com.br/realms/tiny/protocol/openid-connect/auth"
TOKEN_URL = "https://accounts.tiny.com.br/realms/tiny/protocol/openid-connect/token"
API_SCOPES = "openid" # Adicione outros scopes se necessário, separados por espaço

# --- Configuração do sistema de logs estruturados ---
def setup_logger():
    """Configura o sistema de logs estruturados em formato JSON."""
    logger = logging.getLogger('tiny_auth')
    logger.setLevel(logging.INFO)
    
    # Handler para arquivo
    file_handler = logging.FileHandler('tiny_auth.log')
    
    # Formatter para JSON estruturado
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            log_record = {
                "timestamp": datetime.datetime.now().isoformat(),
                "level": record.levelname,
                "service": "tiny_auth_server",
                "correlation_id": getattr(record, 'correlation_id', 'N/A'),
                "message": record.getMessage()
            }
            
            # Adiciona informações de exceção se disponíveis
            if record.exc_info:
                log_record["exception"] = {
                    "type": str(record.exc_info[0].__name__),
                    "message": str(record.exc_info[1]),
                }
                
            # Adiciona informações contextuais extras
            for key, value in record.__dict__.items():
                if key.startswith('ctx_') and key != 'ctx_correlation_id':
                    log_record[key[4:]] = value
                    
            return json.dumps(log_record)
    
    file_handler.setFormatter(JsonFormatter())
    logger.addHandler(file_handler)
    
    # Handler para console com formato mais legível
    console_handler = logging.StreamHandler()
    console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    return logger

# Inicializa o logger
logger = setup_logger()

# --- Armazenamento Simples de Token (Em memória - não persistente entre reinícios) ---
# Para persistência, considere salvar em um arquivo ou banco de dados simples.
token_data = {
    "access_token": None,
    "refresh_token": None,
    "expires_at": 0,
    "last_renewal": 0,  # Timestamp da última renovação
}
TOKEN_FILE = "tiny_token.json" # Arquivo para persistência (opcional)

# Flag para controlar o ciclo de vida do servidor
server_running = True

# Intervalo para verificar e renovar o token (em segundos)
# Configurado para verificar a cada 15 minutos (900 segundos)
TOKEN_CHECK_INTERVAL = 900

# Margem de segurança para renovação do token (em segundos)
# Renova quando faltarem 30 minutos para expirar (1800 segundos)
TOKEN_RENEWAL_MARGIN = 1800

def save_token_to_file():
    """Salva o token atual em um arquivo JSON."""
    try:
        with open(TOKEN_FILE, "w") as f:
            json.dump(token_data, f)
        logger.info("Token salvo no arquivo", extra={"ctx_file": TOKEN_FILE})
    except IOError as e:
        logger.error(f"Erro ao salvar token no arquivo", exc_info=True, extra={"ctx_file": TOKEN_FILE})

def load_token_from_file():
    """Carrega o token de um arquivo JSON, se existir."""
    global token_data
    try:
        with open(TOKEN_FILE, "r") as f:
            loaded_data = json.load(f)
            # Verifica se o token carregado ainda é válido (uma verificação básica)
            if loaded_data.get("expires_at", 0) > time.time() + 60: # Adiciona uma margem de 60s
                 token_data = loaded_data
                 logger.info("Token carregado do arquivo", extra={"ctx_file": TOKEN_FILE})
            else:
                 logger.warning("Token expirado ou inválido, ignorando", extra={"ctx_file": TOKEN_FILE})
                 # Limpa dados antigos se expirados para forçar nova autenticação
                 token_data = {"access_token": None, "refresh_token": None, "expires_at": 0, "last_renewal": 0}
                 save_token_to_file() # Salva o estado limpo
    except FileNotFoundError:
        logger.info(f"Arquivo {TOKEN_FILE} não encontrado, iniciando sem token.")
    except (IOError, json.JSONDecodeError) as e:
        logger.error("Erro ao carregar token do arquivo", exc_info=True, extra={"ctx_file": TOKEN_FILE})


def exchange_code_for_token(authorization_code):
    """Troca o código de autorização por tokens de acesso e refresh."""
    global token_data
    correlation_id = f"auth-{int(time.time())}"
    logger.info("Iniciando troca de código por token", extra={"ctx_correlation_id": correlation_id})
    
    payload = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'code': authorization_code,
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    try:
        response = requests.post(TOKEN_URL, headers=headers, data=payload)
        response.raise_for_status()  # Lança exceção para erros HTTP (4xx ou 5xx)
        data = response.json()

        token_data["access_token"] = data.get("access_token")
        token_data["refresh_token"] = data.get("refresh_token") # Importante para renovar
        expires_in = data.get("expires_in", 0)
        token_data["expires_at"] = time.time() + expires_in
        token_data["last_renewal"] = time.time()
        
        logger.info("Tokens obtidos com sucesso", extra={
            "ctx_correlation_id": correlation_id,
            "ctx_expires_in": expires_in,
            "ctx_expires_at": datetime.datetime.fromtimestamp(token_data["expires_at"]).isoformat()
        })
        
        save_token_to_file() # Salva o novo token
        return True, "Tokens obtidos com sucesso!"

    except requests.exceptions.RequestException as e:
        error_details = f"Erro na requisição: {e}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                 error_details += f" - Resposta: {e.response.text}"
            except Exception:
                 pass # Ignora se não conseguir ler a resposta
        
        logger.error(f"Erro ao trocar código por token", exc_info=True, extra={"ctx_correlation_id": correlation_id})
        return False, f"Erro ao trocar código por token: {error_details}"
    except json.JSONDecodeError:
        logger.error(f"Erro ao decodificar JSON da resposta do token", exc_info=True, extra={
            "ctx_correlation_id": correlation_id,
            "ctx_response_text": response.text
        })
        return False, f"Erro ao decodificar JSON da resposta do token: {response.text}"

def refresh_access_token():
    """Usa o refresh token para obter um novo access token."""
    global token_data
    correlation_id = f"refresh-{int(time.time())}"
    
    if not token_data.get("refresh_token"):
        logger.warning("Refresh token não encontrado. Reautenticação necessária.", extra={"ctx_correlation_id": correlation_id})
        return False

    payload = {
        'grant_type': 'refresh_token',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': token_data["refresh_token"],
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    try:
        logger.info("Iniciando renovação do access token", extra={"ctx_correlation_id": correlation_id})
        response = requests.post(TOKEN_URL, headers=headers, data=payload)
        response.raise_for_status()
        data = response.json()

        token_data["access_token"] = data.get("access_token")
        # Alguns provedores podem emitir um novo refresh token
        if "refresh_token" in data:
            token_data["refresh_token"] = data["refresh_token"]
        expires_in = data.get("expires_in", 0)
        token_data["expires_at"] = time.time() + expires_in
        token_data["last_renewal"] = time.time()
        
        logger.info("Access token renovado com sucesso", extra={
            "ctx_correlation_id": correlation_id,
            "ctx_expires_in": expires_in,
            "ctx_expires_at": datetime.datetime.fromtimestamp(token_data["expires_at"]).isoformat()
        })
        
        save_token_to_file() # Salva o novo token
        return True

    except requests.exceptions.RequestException as e:
        error_details = f"Erro na requisição de refresh: {e}"
        if hasattr(e, 'response') and e.response is not None:
             try:
                 error_details += f" - Resposta: {e.response.text}"
             except Exception:
                 pass
                 
        logger.error(f"Erro ao renovar token", exc_info=True, extra={
            "ctx_correlation_id": correlation_id,
            "ctx_error_details": error_details
        })
        
        # Se o refresh token falhar (expirado, revogado), limpa tudo para forçar nova auth
        token_data = {"access_token": None, "refresh_token": None, "expires_at": 0, "last_renewal": 0}
        save_token_to_file()
        return False
    except json.JSONDecodeError:
        logger.error("Erro ao decodificar JSON da resposta do refresh token", exc_info=True, extra={
            "ctx_correlation_id": correlation_id,
            "ctx_response_text": response.text
        })
        return False


class AuthHandler(http.server.SimpleHTTPRequestHandler):
    """Manipulador para as requisições HTTP."""

    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        # Rota de Callback: Recebe o código de autorização do Tiny
        if parsed_url.path == '/callback':
            authorization_code = query_params.get('code', [None])[0]
            error = query_params.get('error', [None])[0]

            if error:
                message = f"<h1>Erro na Autorização</h1><p>O Tiny retornou um erro: {error}</p>"
                self.send_response(400)
            elif authorization_code:
                print(f"Código de autorização recebido: {authorization_code}")
                success, result_message = exchange_code_for_token(authorization_code)
                if success:
                    message = f"<h1>Autenticação Concluída!</h1><p>Access token obtido com sucesso.</p><p>Você pode fechar esta janela.</p>"
                    self.send_response(200)
                else:
                    message = f"<h1>Erro na Autenticação</h1><p>{result_message}</p>"
                    self.send_response(500)
            else:
                message = "<h1>Erro</h1><p>Nenhum código de autorização recebido na URL de callback.</p>"
                self.send_response(400)

            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(message.encode('utf-8'))

        # Rota para Function Calls obterem o Token
        elif parsed_url.path == '/get_token':
            # Verifica se o token existe e está prestes a expirar (ex: nos próximos 60 segundos)
            if token_data.get("access_token") and token_data.get("expires_at", 0) < time.time() + 60:
                print("Token expirado ou prestes a expirar, tentando renovar...")
                if not refresh_access_token():
                    # Se a renovação falhar, indica que precisa de reautenticação
                    self.send_response(401) # Unauthorized
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    error_response = {"error": "Token renewal failed. Re-authentication required."}
                    self.wfile.write(json.dumps(error_response).encode('utf-8'))
                    return # Sai após enviar a resposta de erro

            # Se o token existe (e foi renovado se necessário)
            if token_data.get("access_token"):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                token_response = {"access_token": token_data["access_token"]}
                self.wfile.write(json.dumps(token_response).encode('utf-8'))
            else:
                # Se não há token, indica que precisa autenticar
                self.send_response(401) # Unauthorized
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = {"error": "No valid token available. Authentication required."}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))

        # Rota Raiz: Inicia o fluxo de autenticação
        elif parsed_url.path == '/':
            # Carrega o token do arquivo ao acessar a raiz, caso o servidor tenha sido reiniciado
            load_token_from_file()

            # Verifica se já temos um token válido
            if token_data.get("access_token") and token_data.get("expires_at", 0) > time.time() + 60:
                 message = f"""
                 <h1>Servidor de Autenticação Tiny</h1>
                 <p>Já existe um token de acesso válido. Pronto para uso.</p>
                 <p><a href="/get_token" target="_blank">Ver Token Atual (para debug)</a></p>
                 <p><a href="/auth">Iniciar Reautenticação (se necessário)</a></p>
                 """
                 self.send_response(200)
            else:
                 # Se não há token ou expirou, mostra o link para iniciar
                 message = f"""
                 <h1>Servidor de Autenticação Tiny</h1>
                 <p>Nenhum token de acesso válido encontrado ou o token expirou.</p>
                 <p><a href="/auth">Iniciar Autenticação com Tiny</a></p>
                 """
                 self.send_response(200)

            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(message.encode('utf-8'))

        # Rota para iniciar a autenticação manualmente
        elif parsed_url.path == '/auth':
            auth_params = {
                'client_id': CLIENT_ID,
                'redirect_uri': REDIRECT_URI,
                'scope': API_SCOPES,
                'response_type': 'code',
            }
            # Redireciona o navegador do usuário para a página de autorização do Tiny
            self.send_response(302) # Found (Redirecionamento temporário)
            self.send_header('Location', f"{AUTH_URL}?{urlencode(auth_params)}")
            self.end_headers()

        # Outras rotas não encontradas
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>404 - Pagina Nao Encontrada</h1>")


def token_monitor_thread():
    """Thread que monitora e renova automaticamente o token antes que expire."""
    global server_running
    logger.info("Iniciando thread de monitoramento de token")
    
    while server_running:
        try:
            current_time = time.time()
            # Verifica se temos um token válido
            if token_data.get("access_token") and token_data.get("refresh_token"):
                time_to_expiry = token_data.get("expires_at", 0) - current_time
                
                # Se o token vai expirar dentro da margem de segurança, renova
                if 0 < time_to_expiry < TOKEN_RENEWAL_MARGIN:
                    logger.info(f"Token expirará em {time_to_expiry:.0f} segundos, iniciando renovação automática")
                    refresh_success = refresh_access_token()
                    
                    if refresh_success:
                        logger.info("Renovação automática de token concluída com sucesso")
                    else:
                        logger.warning("Falha na renovação automática de token")
            
            # Dorme por um período antes de verificar novamente
            time.sleep(TOKEN_CHECK_INTERVAL)
            
        except Exception as e:
            logger.error("Erro na thread de monitoramento de token", exc_info=True)
            time.sleep(300)  # Em caso de erro, aguarda 5 minutos antes de tentar novamente

def run_server():
    """Inicia o servidor HTTP local e a thread de monitoramento de token."""
    global server_running
    # Tenta carregar o token do arquivo ao iniciar o servidor
    load_token_from_file()
    
    # Inicia a thread de monitoramento de token em background
    token_thread = threading.Thread(target=token_monitor_thread, daemon=True)
    token_thread.start()
    logger.info("Thread de monitoramento de token iniciada")

    try:
        with socketserver.TCPServer(("", PORT), AuthHandler) as httpd:
            logger.info(f"Servidor de autenticação rodando em http://localhost:{PORT}")
            logger.info(f"URI de Redirecionamento configurado: {REDIRECT_URI}")
            logger.info("Acesse http://localhost:{PORT}/ para iniciar.")
            httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Servidor interrompido pelo usuário")
        server_running = False
    except Exception as e:
        logger.error("Erro ao executar o servidor", exc_info=True)
        server_running = False

if __name__ == "__main__":
    run_server()