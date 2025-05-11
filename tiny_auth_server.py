import http.server
import socketserver
import webbrowser
import requests
import json
import time
from urllib.parse import urlparse, parse_qs, urlencode

# --- Configurações (Substitua pelos seus valores) ---
CLIENT_ID = "tiny-api-f24a1e97d89c12a4d4ba533080f41afc78a91413-1742858724"
CLIENT_SECRET = "2rjVzKqsNCtFFJPDbUhaTqDXli22hm9v" # Mantenha isso seguro!
PORT = 8080  # Porta onde o servidor local irá rodar
REDIRECT_URI = f"http://localhost:{PORT}/callback" # URI de redirecionamento (deve ser registrado no Tiny)
AUTH_URL = "https://accounts.tiny.com.br/realms/tiny/protocol/openid-connect/auth"
TOKEN_URL = "https://accounts.tiny.com.br/realms/tiny/protocol/openid-connect/token"
API_SCOPES = "openid" # Adicione outros scopes se necessário, separados por espaço

# --- Armazenamento Simples de Token (Em memória - não persistente entre reinícios) ---
# Para persistência, considere salvar em um arquivo ou banco de dados simples.
token_data = {
    "access_token": None,
    "refresh_token": None,
    "expires_at": 0,
}
TOKEN_FILE = "tiny_token.json" # Arquivo para persistência (opcional)

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
            # Verifica se o token carregado ainda é válido (uma verificação básica)
            if loaded_data.get("expires_at", 0) > time.time() + 60: # Adiciona uma margem de 60s
                 token_data = loaded_data
                 print(f"Token carregado de {TOKEN_FILE}")
            else:
                 print(f"Token em {TOKEN_FILE} expirado ou inválido, ignorando.")
                 # Limpa dados antigos se expirados para forçar nova autenticação
                 token_data = {"access_token": None, "refresh_token": None, "expires_at": 0}
                 save_token_to_file() # Salva o estado limpo
    except FileNotFoundError:
        print(f"Arquivo {TOKEN_FILE} não encontrado, iniciando sem token.")
    except (IOError, json.JSONDecodeError) as e:
        print(f"Erro ao carregar token do arquivo: {e}")


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
        response = requests.post(TOKEN_URL, headers=headers, data=payload)
        response.raise_for_status()  # Lança exceção para erros HTTP (4xx ou 5xx)
        data = response.json()

        token_data["access_token"] = data.get("access_token")
        token_data["refresh_token"] = data.get("refresh_token") # Importante para renovar
        expires_in = data.get("expires_in", 0)
        token_data["expires_at"] = time.time() + expires_in
        print("Tokens obtidos com sucesso!")
        save_token_to_file() # Salva o novo token
        return True, "Tokens obtidos com sucesso!"

    except requests.exceptions.RequestException as e:
        error_details = f"Erro na requisição: {e}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                 error_details += f" - Resposta: {e.response.text}"
            except Exception:
                 pass # Ignora se não conseguir ler a resposta
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
        response = requests.post(TOKEN_URL, headers=headers, data=payload)
        response.raise_for_status()
        data = response.json()

        token_data["access_token"] = data.get("access_token")
        # Alguns provedores podem emitir um novo refresh token
        if "refresh_token" in data:
            token_data["refresh_token"] = data["refresh_token"]
        expires_in = data.get("expires_in", 0)
        token_data["expires_at"] = time.time() + expires_in
        print("Access token renovado com sucesso!")
        save_token_to_file() # Salva o novo token
        return True

    except requests.exceptions.RequestException as e:
        error_details = f"Erro na requisição de refresh: {e}"
        if hasattr(e, 'response') and e.response is not None:
             try:
                 error_details += f" - Resposta: {e.response.text}"
             except Exception:
                 pass
        print(f"Erro ao renovar token: {error_details}")
        # Se o refresh token falhar (expirado, revogado), limpa tudo para forçar nova auth
        token_data = {"access_token": None, "refresh_token": None, "expires_at": 0}
        save_token_to_file()
        return False
    except json.JSONDecodeError:
        print(f"Erro ao decodificar JSON da resposta do refresh token: {response.text}")
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


def run_server():
    """Inicia o servidor HTTP local."""
    # Tenta carregar o token do arquivo ao iniciar o servidor
    load_token_from_file()

    with socketserver.TCPServer(("", PORT), AuthHandler) as httpd:
        print(f"Servidor de autenticação rodando em http://localhost:{PORT}")
        print(f"URI de Redirecionamento configurado: {REDIRECT_URI}")
        print("Acesse http://localhost:{PORT}/ para iniciar.")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()