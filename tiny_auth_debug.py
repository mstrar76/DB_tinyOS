import http.server
import socketserver
import webbrowser
import requests
import json
import time
from urllib.parse import urlparse, parse_qs, urlencode

# --- Configurações (Usando os mesmos valores do script original) ---
CLIENT_ID = "tiny-api-f24a1e97d89c12a4d4ba533080f41afc78a91413-1742858724"
CLIENT_SECRET = "2rjVzKqsNCtFFJPDbUhaTqDXli22hm9v" 
PORT = 8080  # Porta onde o servidor local irá rodar
REDIRECT_URI = f"http://localhost:{PORT}/callback" 
AUTH_URL = "https://accounts.tiny.com.br/realms/tiny/protocol/openid-connect/auth"
TOKEN_URL = "https://accounts.tiny.com.br/realms/tiny/protocol/openid-connect/token"
API_SCOPES = "openid email offline_access" # Adicionando scopes para garantir refresh token

# --- Armazenamento do Token ---
token_data = {
    "access_token": None,
    "refresh_token": None,
    "expires_at": 0,
}
TOKEN_FILE = "tiny_token.json"

def save_token_to_file():
    """Salva o token atual em um arquivo JSON."""
    try:
        with open(TOKEN_FILE, "w") as f:
            json.dump(token_data, f)
        print(f"Token salvo em {TOKEN_FILE}")
    except IOError as e:
        print(f"Erro ao salvar token no arquivo: {e}")

def load_token_from_file():
    """Carrega o token de um arquivo JSON, se existir."""
    global token_data
    try:
        with open(TOKEN_FILE, "r") as f:
            loaded_data = json.load(f)
            # Verifica se o token carregado ainda é válido
            if loaded_data.get("expires_at", 0) > time.time() + 60:
                token_data = loaded_data
                print(f"Token carregado de {TOKEN_FILE} (válido até {time.ctime(loaded_data.get('expires_at', 0))})")
                return True
            else:
                print(f"Token em {TOKEN_FILE} expirado ou inválido, ignorando.")
                # Limpa dados antigos
                token_data = {"access_token": None, "refresh_token": None, "expires_at": 0}
                save_token_to_file()
                return False
    except FileNotFoundError:
        print(f"Arquivo {TOKEN_FILE} não encontrado, iniciando sem token.")
        return False
    except (IOError, json.JSONDecodeError) as e:
        print(f"Erro ao carregar token do arquivo: {e}")
        return False

def exchange_code_for_token(authorization_code):
    """Troca o código de autorização por tokens de acesso e refresh."""
    global token_data
    payload = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'code': authorization_code,
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    try:
        print(f"Enviando requisição para trocar código por token: {TOKEN_URL}")
        print(f"Payload: {payload}")
        response = requests.post(TOKEN_URL, headers=headers, data=payload)
        print(f"Resposta recebida: Status {response.status_code}")
        
        response.raise_for_status()
        data = response.json()
        print("Resposta JSON recebida com sucesso")

        token_data["access_token"] = data.get("access_token")
        token_data["refresh_token"] = data.get("refresh_token")
        expires_in = data.get("expires_in", 0)
        token_data["expires_at"] = time.time() + expires_in
        
        print(f"Tokens obtidos com sucesso! Expira em {expires_in} segundos ({time.ctime(token_data['expires_at'])})")
        print(f"Access token: {token_data['access_token'][:20]}... (truncado)")
        print(f"Refresh token: {token_data['refresh_token'][:20]}... (truncado)")
        
        save_token_to_file()
        return True, "Tokens obtidos com sucesso!"

    except requests.exceptions.RequestException as e:
        error_details = f"Erro na requisição: {e}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details += f" - Resposta: {e.response.text}"
            except Exception:
                pass
        print(f"Erro ao trocar código por token: {error_details}")
        return False, f"Erro ao trocar código por token: {error_details}"
    except json.JSONDecodeError:
        print(f"Erro ao decodificar JSON da resposta do token: {response.text}")
        return False, f"Erro ao decodificar JSON da resposta do token: {response.text}"

def refresh_access_token():
    """Usa o refresh token para obter um novo access token."""
    global token_data
    if not token_data.get("refresh_token"):
        print("Refresh token não encontrado. Reautenticação necessária.")
        return False

    payload = {
        'grant_type': 'refresh_token',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': token_data["refresh_token"],
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    try:
        print("Tentando renovar o access token usando refresh token...")
        print(f"Refresh token: {token_data['refresh_token'][:20]}... (truncado)")
        response = requests.post(TOKEN_URL, headers=headers, data=payload)
        print(f"Resposta do refresh: Status {response.status_code}")
        
        response.raise_for_status()
        data = response.json()
        print("Resposta JSON de refresh recebida com sucesso")

        token_data["access_token"] = data.get("access_token")
        if "refresh_token" in data:
            token_data["refresh_token"] = data["refresh_token"]
            print("Novo refresh token recebido")
        
        expires_in = data.get("expires_in", 0)
        token_data["expires_at"] = time.time() + expires_in
        
        print(f"Access token renovado com sucesso! Expira em {expires_in} segundos ({time.ctime(token_data['expires_at'])})")
        save_token_to_file()
        return True

    except requests.exceptions.RequestException as e:
        error_details = f"Erro na requisição de refresh: {e}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details += f" - Resposta: {e.response.text}"
            except Exception:
                pass
        print(f"Erro ao renovar token: {error_details}")
        # Limpa tudo para forçar nova auth
        token_data = {"access_token": None, "refresh_token": None, "expires_at": 0}
        save_token_to_file()
        return False
    except json.JSONDecodeError:
        print(f"Erro ao decodificar JSON da resposta do refresh token: {response.text}")
        return False

def generate_auth_url():
    """Gera a URL de autorização para o fluxo OAuth."""
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': API_SCOPES,
    }
    auth_url = f"{AUTH_URL}?{urlencode(params)}"
    return auth_url

class AuthHandler(http.server.SimpleHTTPRequestHandler):
    """Manipulador para as requisições HTTP."""
    
    # Suprimir logs de acesso padrão
    def log_message(self, format, *args):
        if args and len(args) > 2 and "200" not in args[1]:  # Só loga erros
            super().log_message(format, *args)

    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        # Rota principal: Redireciona para a URL de autorização
        if parsed_url.path == '/' or parsed_url.path == '':
            auth_url = generate_auth_url()
            self.send_response(302)  # Redirect
            self.send_header('Location', auth_url)
            self.end_headers()
            print(f"Redirecionando para URL de autorização: {auth_url}")

        # Rota de Callback: Recebe o código de autorização
        elif parsed_url.path == '/callback':
            authorization_code = query_params.get('code', [None])[0]
            error = query_params.get('error', [None])[0]

            if error:
                message = f"<h1>Erro na Autorização</h1><p>O Tiny retornou um erro: {error}</p>"
                self.send_response(400)
                print(f"Erro na autorização: {error}")
            elif authorization_code:
                print(f"Código de autorização recebido: {authorization_code[:10]}... (truncado)")
                success, result_message = exchange_code_for_token(authorization_code)
                if success:
                    message = f"""
                    <h1>Autenticação Concluída!</h1>
                    <p>Access token obtido com sucesso.</p>
                    <p>Você pode fechar esta janela e retornar ao terminal.</p>
                    <script>
                        setTimeout(function() {{
                            window.close();
                        }}, 5000);
                    </script>
                    """
                    self.send_response(200)
                else:
                    message = f"<h1>Erro na Autenticação</h1><p>{result_message}</p>"
                    self.send_response(500)
                    print(f"Erro na autenticação: {result_message}")
            else:
                message = "<h1>Erro</h1><p>Nenhum código de autorização recebido na URL de callback.</p>"
                self.send_response(400)
                print("Nenhum código de autorização recebido")

            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(message.encode('utf-8'))

        # Rota para Function Calls obterem o Token
        elif parsed_url.path == '/get_token':
            # Verifica se o token existe e está prestes a expirar
            if token_data.get("access_token") and token_data.get("expires_at", 0) < time.time() + 60:
                print("Token expirado ou prestes a expirar, tentando renovar...")
                if not refresh_access_token():
                    self.send_response(401)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    error_response = {"error": "Token renewal failed. Re-authentication required."}
                    self.wfile.write(json.dumps(error_response).encode('utf-8'))
                    return

            if token_data.get("access_token"):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                token_response = {"access_token": token_data["access_token"]}
                self.wfile.write(json.dumps(token_response).encode('utf-8'))
            else:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = {"error": "No valid token available. Authentication required."}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("<h1>404 Not Found</h1>".encode('utf-8'))

def run_server():
    """Inicia o servidor HTTP local e abre o navegador."""
    # Tenta carregar token existente
    token_valid = load_token_from_file()
    
    # Configura e inicia o servidor
    handler = AuthHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Servidor iniciado em http://localhost:{PORT}")
        
        # Se não temos token válido, abre o navegador automaticamente
        if not token_valid:
            auth_url = f"http://localhost:{PORT}/"
            print(f"Abrindo navegador para autenticação: {auth_url}")
            webbrowser.open(auth_url)
        else:
            print(f"Token válido encontrado. Acesse http://localhost:{PORT}/ se precisar reautenticar.")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor encerrado pelo usuário.")

if __name__ == "__main__":
    run_server()
