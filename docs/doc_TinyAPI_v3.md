```markdown
# Tiny API v3

**Versão:** 3.0

## Introdução

Este documento descreve a API Pública v3 do Tiny.

## Autenticação e Autorização

Seu aplicativo solicita autorização ao usuário para acessar seus dados. Isso é feito redirecionando o usuário para uma página de login do Tiny.

### Solicitação de Autorização

Exemplo de URL de solicitação de autorização:
`https://accounts.tiny.com.br/realms/tiny/protocol/openid-connect/auth?client_id=CLIENT_ID&redirect_uri=REDIRECT_URI&scope=openid&response_type=code`

### Obtenção do Código de Autorização

Após o usuário conceder a autorização, o Tiny o redireciona de volta para seu aplicativo com um código de autorização.

### Solicitação de Token de Acesso

Seu aplicativo envia o código de autorização, juntamente com as credenciais do aplicativo, para o Tiny para solicitar um token de acesso.

```bash
curl --location 'https://accounts.tiny.com.br/realms/tiny/protocol/openid-connect/token' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'grant_type=authorization_code' \
--data-urlencode 'client_id=CLIENT_ID' \
--data-urlencode 'client_secret=CLIENT_SECRET' \
--data-urlencode 'redirect_uri=REDIRECT_URI' \
--data-urlencode 'code=AUTHORIZATION_CODE'
```

### Utilização do Token de Acesso

Finalmente, seu aplicativo pode usar o token de acesso para fazer solicitações à API em nome do usuário.

```
Authorization: Bearer {access_token}
```

### Solicitação do Refresh Token

Considere que o token de acesso gerado expirará após 4 horas. Depois disso será necessária a renovação do token, utilizando o refresh token adquirido no passo anterior. O refresh token tem duração de 1 dia.

```bash
curl --location 'https://accounts.tiny.com.br/realms/tiny/protocol/openid-connect/token' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'grant_type=refresh_token' \
--data-urlencode 'client_id=CLIENT_ID' \
--data-urlencode 'client_secret=CLIENT_SECRET' \
--data-urlencode 'refresh_token=REFRESH_TOKEN'
```

## Servidores

*   "https://api.tiny.com.br/public-api/v3"

## Endpoints

### Categorias

#### GET /categorias/todas

*   **Operation ID:** `ListarArvoreCategoriasAction`
*   **Description:**
*   **Parameters:** None
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ListarArvoreCategoriasModelResponse`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

### Categorias de receita e despesa

#### GET /categorias-receita-despesa

*   **Operation ID:** `ListarCategoriasReceitaDespesaAction`
*   **Description:**
*   **Parameters:**
    *   `descricao` (query): Pesquisa por descrição completa da categorias de receita e despesa. Type: string.
    *   `grupo` (query): Pesquisa por grupo de categorias de receita e despesa. Type: string.
    *   `orderBy` (query): Define a ordenação da listagem por ordem crescente ou decrescente. Type: string. Enum: `asc - Crescente`, `desc - Descrescente`. Example: `asc`.
    *   `limit` (query): Limite da paginação. Type: integer. Default: 100.
    *   `offset` (query): Offset da paginação. Type: integer. Default: 0.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:**
            ```json
            {
              "type": "object",
              "properties": {
                "itens": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/ListagemCategoriasReceitaDespesaResponseModel"
                  }
                },
                "paginacao": {
                  "$ref": "#/components/schemas/PaginatedResultModel"
                }
              }
            }
            ```
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

### Contas a pagar

#### GET /contas-pagar

*   **Operation ID:** `ListarContasPagarAction`
*   **Description:**
*   **Parameters:**
    *   `nomeCliente` (query): Pesquisa por nome do cliente de contas a pagar. Type: string.
    *   `situacao` (query): Pesquisa por situação de contas a pagar. Type: string. Enum: `aberto - Aberto`, `cancelada - Cancelada`, `pago - Pago`, `parcial - Parcial`, `prevista - Prevista`. Example: `aberto`.
    *   `dataInicialEmissao` (query): Pesquisa por data inicial da emissão de contas a pagar. Type: string. Example: `2024-01-01`.
    *   `dataFinalEmissao` (query): Pesquisa por data final da emissão de contas a pagar. Type: string. Example: `2024-01-01`.
    *   `dataInicialVencimento` (query): Pesquisa por data inicial do vencimento de contas a pagar. Type: string. Example: `2024-01-01`.
    *   `dataFinalVencimento` (query): Pesquisa por data final do vencimento de contas a pagar. Type: string. Example: `2024-01-01`.
    *   `numeroDocumento` (query): Pesquisa por número do documento de contas a pagar. Type: string.
    *   `numeroBanco` (query): Pesquisa por número do banco de contas a pagar. Type: string.
    *   `marcadores` (query): Pesquisa por marcadores. Type: array of string.
    *   `idContato` (query): Pesquisa por ID do contato de contas a pagar. Type: integer. Example: 123.
    *   `orderBy` (query): Define a ordenação da listagem por ordem crescente ou decrescente. Type: string. Enum: `asc - Crescente`, `desc - Descrescente`. Example: `asc`.
    *   `limit` (query): Limite da paginação. Type: integer. Default: 100.
    *   `offset` (query): Offset da paginação. Type: integer. Default: 0.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ListagemContasPagarResponseModel`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /contas-pagar

*   **Operation ID:** `CriarContaPagarAction`
*   **Description:**
*   **Parameters:** None
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/CriarContaPagarRequestModel`
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/CriarContaPagarResponseModel`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /contas-pagar/{idContaPagar}

*   **Operation ID:** `ObterContaPagarAction`
*   **Description:**
*   **Parameters:**
    *   `idContaPagar` (path): Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ObterContaPagarModelResponse`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /contas-pagar/{idContaPagar}/marcadores

*   **Operation ID:** `ObterMarcadoresContaPagarAction`
*   **Description:**
*   **Parameters:**
    *   `id` (path): Identificador da Conta a Pagar. Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:**
            ```json
            {
              "type": "array",
              "items": {
                "$ref": "#/components/schemas/ObterMarcadorResponseModel"
              }
            }
            ```
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

### Contas a receber

#### GET /contas-receber/{idContaReceber}

*   **Operation ID:** `ObterContaReceberAction`
*   **Description:**
*   **Parameters:**
    *   `idContaReceber` (path): Identificador da conta receber. Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ObterContaReceberResponseModel`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### PUT /contas-receber/{idContaReceber}

*   **Operation ID:** `AtualizarContaReceberAction`
*   **Description:**
*   **Parameters:**
    *   `idContaReceber` (path): Identificador da conta receber. Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/AtualizarContaReceberRequestModel`
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /contas-receber/{idContaReceber}/baixar

*   **Operation ID:** `BaixarContaReceberAction`
*   **Description:**
*   **Parameters:**
    *   `idContaReceber` (path): Identificador da conta a receber. Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/BaixarContaReceberModelRequest`
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /contas-receber

*   **Operation ID:** `ListarContasReceberAction`
*   **Description:**
*   **Parameters:**
    *   `nomeCliente` (query): Pesquisa por nome do cliente de contas a receber. Type: string.
    *   `situacao` (query): Pesquisa por situação de contas a receber. Type: string. Enum: `aberto - Aberto`, `cancelada - Cancelada`, `pago - Pago`, `parcial - Parcial`, `prevista - Prevista`. Example: `aberto`.
    *   `dataInicialEmissao` (query): Pesquisa por data inicial da emissão de contas a receber. Type: string. Example: `2024-01-01`.
    *   `dataFinalEmissao` (query): Pesquisa por data final da emissão de contas a receber. Type: string. Example: `2024-01-01`.
    *   `dataInicialVencimento` (query): Pesquisa por data inicial do vencimento de contas a receber. Type: string. Example: `2024-01-01`.
    *   `dataFinalVencimento` (query): Pesquisa por data final do vencimento de contas a receber. Type: string. Example: `2024-01-01`.
    *   `numeroDocumento` (query): Pesquisa por número do documento de contas a receber. Type: string.
    *   `numeroBanco` (query): Pesquisa por número do banco de contas a receber. Type: string.
    *   `idNota` (query): Pesquisa por identificador da nota de contas a receber. Type: int.
    *   `idVenda` (query): Pesquisa por identificador da venda de contas a receber. Type: int.
    *   `marcadores` (query): Pesquisa por marcadores. Type: array of string.
    *   `orderBy` (query): Define a ordenação da listagem por ordem crescente ou decrescente. Type: string. Enum: `asc - Crescente`, `desc - Descrescente`. Example: `asc`.
    *   `limit` (query): Limite da paginação. Type: integer. Default: 100.
    *   `offset` (query): Offset da paginação. Type: integer. Default: 0.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:**
            ```json
            {
              "type": "object",
              "properties": {
                "itens": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/ListagemContasReceberResponseModel"
                  }
                },
                "paginacao": {
                  "$ref": "#/components/schemas/PaginatedResultModel"
                }
              }
            }
            ```
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /contas-receber

*   **Operation ID:** `CriarContaReceberAction`
*   **Description:**
*   **Parameters:** None
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/CriarContaReceberRequestModel`
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/CriarContaReceberResponseModel`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /contas-receber/{idContaReceber}/marcadores

*   **Operation ID:** `ObterMarcadoresContaReceberAction`
*   **Description:**
*   **Parameters:**
    *   `idContaReceber` (path): Identificador da conta receber. Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:**
            ```json
            {
              "type": "array",
              "items": {
                "$ref": "#/components/schemas/ObterMarcadorResponseModel"
              }
            }
            ```
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

### Contatos

#### GET /contatos/{idContato}

*   **Operation ID:** `ObterContatoAction`
*   **Description:**
*   **Parameters:**
    *   `idContato` (path): Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ObterContatoModelResponse`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### PUT /contatos/{idContato}

*   **Operation ID:** `AtualizarContatoAction`
*   **Description:**
*   **Parameters:**
    *   `idContato` (path): Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/AtualizarContatoModelRequest`
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /contatos/{idContato}/pessoas/{idPessoa}

*   **Operation ID:** `ObterContatoContatoAction`
*   **Description:**
*   **Parameters:**
    *   `idContato` (path): Required. Type: integer.
    *   `idPessoa` (path): Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ObterContatoContatoModelResponse`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### PUT /contatos/{idContato}/pessoas/{idPessoa}

*   **Operation ID:** `AtualizarContatoContatoAction`
*   **Description:**
*   **Parameters:**
    *   `idContato` (path): Required. Type: integer.
    *   `idPessoa` (path): Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/AtualizarContatoContatoModelRequest`
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### DELETE /contatos/{idContato}/pessoas/{idPessoa}

*   **Operation ID:** `ExcluirContatoContatoAction`
*   **Description:**
*   **Parameters:**
    *   `idContato` (path): Required. Type: integer.
    *   `idPessoa` (path): Required. Type: integer.
*   **Responses:**
    *   `200 OK`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /contatos

*   **Operation ID:** `ListarContatosAction`
*   **Description:**
*   **Parameters:**
    *   `nome` (query): Pesquisa por nome parcial ou completo. Type: string.
    *   `codigo` (query): Pesquisa por codigo completo. Type: string.
    *   `situacao` (query): Pesquisa por situacao. Type: string. Enum: `B - Ativo`, `A - Ativo Com Acesso Sistema`, `I - Inativo`, `E - Excluido`. Example: `B`.
    *   `idVendedor` (query): Pesquisa por vendedor padrão. Type: integer.
    *   `cpfCnpj` (query): Pesquisa por CPF ou CNPJ. Type: string.
    *   `celular` (query): Pesquisa pelo celular. Type: string.
    *   `dataCriacao` (query): Pesquisa por data de criação. Type: string. Example: `2023-01-01 10:00:00`.
    *   `dataAtualizacao` (query): Pesquisa por data de atualização. Type: string. Example: `2023-01-01 10:00:00`.
    *   `orderBy` (query): Define a ordenação da listagem por ordem crescente ou decrescente. Type: string. Enum: `asc - Crescente`, `desc - Descrescente`. Example: `asc`.
    *   `limit` (query): Limite da paginação. Type: integer. Default: 100.
    *   `offset` (query): Offset da paginação. Type: integer. Default: 0.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:**
            ```json
            {
              "type": "object",
              "properties": {
                "itens": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/ListagemContatoModelResponse"
                  }
                },
                "paginacao": {
                  "$ref": "#/components/schemas/PaginatedResultModel"
                }
              }
            }
            ```
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /contatos

*   **Operation ID:** `CriarContatoAction`
*   **Description:**
*   **Parameters:** None
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/CriarContatoModelRequest`
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/CriarContatoModelResponse`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /contatos/{idContato}/pessoas

*   **Operation ID:** `ListarContatosContatoAction`
*   **Description:**
*   **Parameters:**
    *   `idContato` (path): Required. Type: integer.
    *   `limit` (query): Limite da paginação. Type: integer. Default: 100.
    *   `offset` (query): Offset da paginação. Type: integer. Default: 0.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:**
            ```json
            {
              "type": "object",
              "properties": {
                "itens": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/ListagemContatosContatoModelResponse"
                  }
                },
                "paginacao": {
                  "$ref": "#/components/schemas/PaginatedResultModel"
                }
              }
            }
            ```
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /contatos/{idContato}/pessoas

*   **Operation ID:** `CriarContatoContatoAction`
*   **Description:**
*   **Parameters:**
    *   `idContato` (path): Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/CriarContatoContatoModelRequest`
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/CriarContatoContatoModelResponse`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /contatos/tipos

*   **Operation ID:** `ListarTiposDeContatosAction`
*   **Description:**
*   **Parameters:**
    *   `nome` (query): Pesquisa por nome parcial ou completo do tipo de contato. Type: string.
    *   `limit` (query): Limite da paginação. Type: integer. Default: 100.
    *   `offset` (query): Offset da paginação. Type: integer. Default: 0.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:**
            ```json
            {
              "type": "object",
              "properties": {
                "itens": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/ListarTiposDeContatosModelResponse"
                  }
                },
                "paginacao": {
                  "$ref": "#/components/schemas/PaginatedResultModel"
                }
              }
            }
            ```
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

### Dados da empresa

#### GET /info

*   **Operation ID:** `ObterInfoContaAction`
*   **Description:**
*   **Parameters:** None
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ObterInfoContaModelResponse`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

### Estoque

#### GET /estoque/{idProduto}

*   **Operation ID:** `ObterProdutoEstoqueAction`
*   **Description:**
*   **Parameters:**
    *   `idProduto` (path): Identificador do produto. Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ObterEstoqueProdutoModelResponse`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /estoque/{idProduto}

*   **Operation ID:** `AtualizarProdutoEstoqueAction`
*   **Description:**
*   **Parameters:**
    *   `idProduto` (path): Identificador do produto. Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/AtualizarProdutoEstoqueModelRequest`
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/AtualizarProdutoEstoqueModelResponse`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

### Expedição

#### POST /expedicao/{idAgrupamento}/origens

*   **Operation ID:** `AdicionarOrigensAgrupamentoAction`
*   **Description:**
*   **Parameters:**
    *   `idAgrupamento` (path): Identificador do agrupamento. Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/CriarAgrupamentoRequestModel`
*   **Responses:**
    *   `200 OK`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### PUT /expedicao/{idAgrupamento}/expedicao/{idExpedicao}

*   **Operation ID:** `AlterarExpedicaoAgrupamentoAction`
*   **Description:**
*   **Parameters:**
    *   `idAgrupamento` (path): Identificador do agrupamento. Required. Type: integer.
    *   `idExpedicao` (path): Identificador da expedição. Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/ExpedicaoRequestModel`
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /expedicao/{idAgrupamento}/concluir

*   **Operation ID:** `ConcluirAgrupamentoAction`
*   **Description:**
*   **Parameters:**
    *   `idAgrupamento` (path): Identificador do agrupamento. Required. Type: integer.
*   **Responses:**
    *   `200 OK`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /expedicao

*   **Operation ID:** `ListarAgrupamentosAction`
*   **Description:**
*   **Parameters:**
    *   `idFormaEnvio` (query): Pesquisa através do identificador da forma de envio. Type: int.
    *   `dataInicial` (query): Pesquisa através da data inicial dos agrupamentos. Type: string. Example: `2024-01-01`.
    *   `dataFinal` (query): Pesquisa através da data final dos agrupamentos. Type: string. Example: `2024-01-01`.
    *   `orderBy` (query): Define a ordenação da listagem por ordem crescente ou decrescente. Type: string. Enum: `asc - Crescente`, `desc - Descrescente`. Example: `asc`.
    *   `limit` (query): Limite da paginação. Type: integer. Default: 100.
    *   `offset` (query): Offset da paginação. Type: integer. Default: 0.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:**
            ```json
            {
              "type": "object",
              "properties": {
                "itens": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/ListagemAgrupamentosModel"
                  }
                },
                "paginacao": {
                  "$ref": "#/components/schemas/PaginatedResultModel"
                }
              }
            }
            ```
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /expedicao

*   **Operation ID:** `CriarAgrupamentoAction`
*   **Description:**
*   **Parameters:** None
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/CriarAgrupamentoRequestModel`
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/CriarAgrupamentoResponseModel`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /expedicao/{idAgrupamento}

*   **Operation ID:** `ObterAgrupamentoAction`
*   **Description:**
*   **Parameters:**
    *   `idAgrupamento` (path): Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ObterAgrupamentoResponseModel`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /expedicao/{idAgrupamento}/etiquetas

*   **Operation ID:** `ObterEtiquetasAgrupamentoAction`
*   **Description:**
*   **Parameters:**
    *   `idAgrupamento` (path): Identificador do agrupamento. Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ObterEtiquetasResponseModel`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /expedicao/{idAgrupamento}/expedicao/{idExpedicao}/etiquetas

*   **Operation ID:** `ObterEtiquetasExpedicaoAgrupamentoAction`
*   **Description:**
*   **Parameters:**
    *   `idAgrupamento` (path): Identificador do agrupamento. Required. Type: integer.
    *   `idExpedicao` (path): Identificador da expedição. Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ObterEtiquetasResponseModel`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

### Formas de pagamento

#### GET /formas-pagamento

*   **Operation ID:** `ListarFormasPagamentoAction`
*   **Description:**
*   **Parameters:**
    *   `nome` (query): Pesquisa por nome parcial ou completo da forma de pagamento. Type: string.
    *   `situacao` (query): Pesquisa por situação da forma de pagamento. Type: string. Enum: `1 - Habilitada`, `2 - Desabilitada`. Example: `1`.
    *   `limit` (query): Limite da paginação. Type: integer. Default: 100.
    *   `offset` (query): Offset da paginação. Type: integer. Default: 0.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:**
            ```json
            {
              "type": "object",
              "properties": {
                "itens": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/ListagemFormasPagamentoResponseModel"
                  }
                },
                "paginacao": {
                  "$ref": "#/components/schemas/PaginatedResultModel"
                }
              }
            }
            ```
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /formas-pagamento/{idFormaPagamento}

*   **Operation ID:** `ObterFormaPagamentoAction`
*   **Description:**
*   **Parameters:**
    *   `idFormaPagamento` (path): Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ObterFormaPagamentoResponseModel`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

### Intermediadores

#### GET /intermediadores

*   **Operation ID:** `ListarIntermediadoresAction`
*   **Description:**
*   **Parameters:**
    *   `nome` (query): Pesquisa por nome parcial ou completo do intermediador. Type: string.
    *   `cnpj` (query): Pesquisa por cnpj do intermediador.
    *   `limit` (query): Limite da paginação. Type: integer. Default: 100.
    *   `offset` (query): Offset da paginação. Type: integer. Default: 0.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:**
            ```json
            {
              "type": "object",
              "properties": {
                "itens": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/ListagemIntermediadoresResponseModel"
                  }
                },
                "paginacao": {
                  "$ref": "#/components/schemas/PaginatedResultModel"
                }
              }
            }
            ```
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /intermediadores/{idIntermediador}

*   **Operation ID:** `ObterIntermediadorAction`
*   **Description:**
*   **Parameters:**
    *   `idIntermediador` (path): Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ObterIntermediadorResponseModel`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

### Lista de Preços

#### GET /listas-precos

*   **Operation ID:** `ListarListasDePrecosAction`
*   **Description:**
*   **Parameters:**
    *   `nome` (query): Pesquisa por nome parcial ou completo da lista de preços. Type: string.
    *   `limit` (query): Limite da paginação. Type: integer. Default: 100.
    *   `offset` (query): Offset da paginação. Type: integer. Default: 0.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:**
            ```json
            {
              "type": "object",
              "properties": {
                "itens": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/ListagemListaDePrecosModelResponse"
                  }
                },
                "paginacao": {
                  "$ref": "#/components/schemas/PaginatedResultModel"
                }
              }
            }
            ```
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /listas-precos/{idListaDePreco}

*   **Operation ID:** `ObterListaDePrecosAction`
*   **Description:**
*   **Parameters:**
    *   `idListaDePreco` (path): Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ObterListaDePrecosModelResponse`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

### Logistica

#### GET /formas-envio

*   **Operation ID:** `ListarFormasEnvioAction`
*   **Description:**
*   **Parameters:**
    *   `nome` (query): Pesquisa por nome parcial ou completo da forma de envio. Type: string.
    *   `tipo` (query): Pesquisa por tipo de forma de envio. Type: string. Enum: `0 - Sem Frete`, `1 - Correios`, `2 - Transportadora`, `3 - Mercado Envios`, `4 - B2w Entrega`, `5 - Correios Ff`, `6 - Customizado`, `7 - Jadlog`, `8 - Totalexpress`, `9 - Olist`, `10 - Gateway`, `11 - Magalu Entregas`, `12 - Shopee Envios`, `13 - Ns Entregas`, `14 - Viavarejo Envvias`, `15 - Madeira Envios`, `16 - Ali Envios`, `17 - Loggi`, `18 - Conecta La Etiquetas`, `19 - Amazon Dba`, `20 - Magalu Fulfillment`, `21 - Ns Magalu Entregas`, `22 - Shein Envios`, `23 - Mandae`, `24 - Olist Envios`, `25 - Kwai Envios`, `26 - Beleza Envios`. Example: `0`.
    *   `situacao` (query): Pesquisa por situação da forma de envio. Type: string. Enum: `0 - Sem Frete`, `1 - Correios`, `2 - Transportadora`, `3 - Mercado Envios`, `4 - B2w Entrega`, `5 - Correios Ff`, `6 - Customizado`, `7 - Jadlog`, `8 - Totalexpress`, `9 - Olist`, `10 - Gateway`, `11 - Magalu Entregas`, `12 - Shopee Envios`, `13 - Ns Entregas`, `14 - Viavarejo Envvias`, `15 - Madeira Envios`, `16 - Ali Envios`, `17 - Loggi`, `18 - Conecta La Etiquetas`, `19 - Amazon Dba`, `20 - Magalu Fulfillment`, `21 - Ns Magalu Entregas`, `22 - Shein Envios`, `23 - Mandae`, `24 - Olist Envios`, `25 - Kwai Envios`, `26 - Beleza Envios`. Example: `0`.
    *   `limit` (query): Limite da paginação. Type: integer. Default: 100.
    *   `offset` (query): Offset da paginação. Type: integer. Default: 0.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:**
            ```json
            {
              "type": "object",
              "properties": {
                "itens": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/ListagemFormasEnvioResponseModel"
                  }
                },
                "paginacao": {
                  "$ref": "#/components/schemas/PaginatedResultModel"
                }
              }
            }
            ```
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /formas-envio/{idFormaEnvio}

*   **Operation ID:** `ObterFormaEnvioAction`
*   **Description:**
*   **Parameters:**
    *   `idFormaEnvio` (path): Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ObterFormaEnvioResponseModel`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

### Marcas

#### PUT /marcas/{idMarca}

*   **Operation ID:** `AtualizarMarcaAction`
*   **Description:**
*   **Parameters:**
    *   `idMarca` (path): Identificador da marca. Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/BaseMarcaModel`
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /marcas

*   **Operation ID:** `ListarMarcasAction`
*   **Description:**
*   **Parameters:**
    *   `descricao` (query): Pesquisa por descrição completa da marca. Type: string.
    *   `limit` (query): Limite da paginação. Type: integer. Default: 100.
    *   `offset` (query): Offset da paginação. Type: integer. Default: 0.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:**
            ```json
            {
              "type": "object",
              "properties": {
                "itens": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/ListagemMarcasResponseModel"
                  }
                },
                "paginacao": {
                  "$ref": "#/components/schemas/PaginatedResultModel"
                }
              }
            }
            ```
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /marcas

*   **Operation ID:** `CriarMarcaAction`
*   **Description:**
*   **Parameters:** None
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/BaseMarcaModel`
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/CriarMarcaModelResponse`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

### Notas

#### GET /notas/{idNota}/marcadores

*   **Operation ID:** `ObterMarcadoresNotaFiscalAction`
*   **Description:**
*   **Parameters:**
    *   `idNota` (path): Identificador da nota fiscal. Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:**
            ```json
            {
              "type": "array",
              "items": {
                "$ref": "#/components/schemas/ObterMarcadorResponseModel"
              }
            }
            ```
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### PUT /notas/{idNota}/marcadores

*   **Operation ID:** `AtualizarMarcadoresNotaFiscalAction`
*   **Description:**
*   **Parameters:**
    *   `idNota` (path): Identificador da nota fiscal. Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:**
        ```json
        {
          "type": "array",
          "items": {
            "$ref": "#/components/schemas/AtualizarMarcadorRequestModel"
          }
        }
        ```
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /notas/{idNota}/marcadores

*   **Operation ID:** `CriarMarcadoresNotaFiscalAction`
*   **Description:**
*   **Parameters:**
    *   `idNota` (path): Identificador da nota fiscal. Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:**
        ```json
        {
          "type": "array",
          "items": {
            "$ref": "#/components/schemas/CriarMarcadorRequestModel"
          }
        }
        ```
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### DELETE /notas/{idNota}/marcadores

*   **Operation ID:** `ExcluirMarcadoresNotaFiscalAction`
*   **Description:**
*   **Parameters:**
    *   `idNota` (path): Identificador da nota fiscal. Required. Type: integer.
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /notas/{idNota}/emitir

*   **Operation ID:** `AutorizarNotaFiscalAction`
*   **Description:**
*   **Parameters:**
    *   `idNota` (path): Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/AutorizarNotaFiscalModelRequest`
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/AutorizarNotaFiscalModelResponse`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /notas/xml

*   **Operation ID:** `IncluirXmlNotaFiscalAction`
*   **Description:**
*   **Parameters:** None
*   **Request Body:**
    *   **Content:** `multipart/form-data`
    *   **Schema:** `#/components/schemas/IncluirXmlNotaFiscalRequestModel`
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/IncluirXmlNotaFiscalResponseModel`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /notas/{idNota}/lancar-contas

*   **Operation ID:** `LancarContasNotaFiscalAction`
*   **Description:**
*   **Parameters:**
    *   `idNota` (path): Identificador da nota fiscal. Required. Type: integer.
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /notas/{idNota}/lancar-estoque

*   **Operation ID:** `LancarEstoqueNotaFiscalAction`
*   **Description:**
*   **Parameters:**
    *   `idNota` (path): Identificador da nota fiscal. Required. Type: integer.
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /notas

*   **Operation ID:** `ListarNotasFiscaisAction`
*   **Description:**
*   **Parameters:**
    *   `tipo` (query): Pesquisa por tipo de nota. Type: string. Enum: `E - Entrada`, `S - Saida`. Example: `E`.
    *   `numero` (query): Pesquisa por número da nota. Type: int.
    *   `cpfCnpj` (query): Pesquisa por CPF ou CNPJ. Type: string.
    *   `dataInicial` (query): Pesquisa por data de criação. Type: string. Example: `2023-01-01`.
    *   `dataFinal` (query): Pesquisa por data de criação. Type: string. Example: `2023-01-01`.
    *   `situacao` (query): Pesquisa pela situacão da nota. Type: string. Enum: `1 - Pendente`, `2 - Emitida`, `3 - Cancelada`, `4 - Enviada Aguardando Recibo`, `5 - Rejeitada`, `6 - Autorizada`, `7 - Emitida Danfe`, `8 - Registrada`, `9 - Enviada Aguardando Protocolo`, `10 - Denegada`. Example: `1`.
    *   `numeroPedidoEcommerce` (query): Pesquisa pelo número do pedido no e-commerce. Type: string.
    *   `idVendedor` (query): Pesquisa por identificador do vendedor. Type: int.
    *   `idFormaEnvio` (query): Pesquisa por identificador da forma de envio. Type: int.
    *   `marcadores` (query): Pesquisa por marcadores. Type: array of string.
    *   `orderBy` (query): Define a ordenação da listagem por ordem crescente ou decrescente. Type: string. Enum: `asc - Crescente`, `desc - Descrescente`. Example: `asc`.
    *   `limit` (query): Limite da paginação. Type: integer. Default: 100.
    *   `offset` (query): Offset da paginação. Type: integer. Default: 0.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:**
            ```json
            {
              "type": "object",
              "properties": {
                "itens": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/ListagemNotaFiscalModelResponse"
                  }
                },
                "paginacao": {
                  "$ref": "#/components/schemas/PaginatedResultModel"
                }
              }
            }
            ```
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /notas/{idNota}/link

*   **Operation ID:** `ObterLinkNotaFiscalAction`
*   **Description:**
*   **Parameters:**
    *   `idNota` (path): Identificador da nota fiscal. Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ObterLinkNotaFiscalModelResponse`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /notas/{idNota}

*   **Operation ID:** `ObterNotaFiscalAction`
*   **Description:**
*   **Parameters:**
    *   `idNota` (path): Identificador da nota fiscal. Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ObterNotaFiscalModelResponse`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /notas/{idNota}/xml

*   **Operation ID:** `ObterXmlNotaFiscalAction`
*   **Description:**
*   **Parameters:**
    *   `idNota` (path): Identificador da nota fiscal. Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ObterXmlNotaFiscalModelResponse`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

### Ordem de Compra

#### GET /ordem-compra/{idOrdemCompra}

*   **Operation ID:** `ObterOrdemCompraAction`
*   **Description:**
*   **Parameters:**
    *   `idOrdemCompra` (path): Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ObterOrdemCompraModelResponse`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### PUT /ordem-compra/{idOrdemCompra}

*   **Operation ID:** `AtualizarOrdemCompraAction`
*   **Description:**
*   **Parameters:**
    *   `idOrdemCompra` (path): Identificador da ordem de compra. Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/AtualizarOrdemCompraModelRequest`
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### PUT /ordem-compra/{idOrdemCompra}/situacao

*   **Operation ID:** `AtualizarSituacaoOrdemCompraAction`
*   **Description:**
*   **Parameters:**
    *   `idOrdemCompra` (path): Identificador da ordem de compra. Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/AtualizarSituacaoOrdemCompraRequestModel`
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /ordem-compra

*   **Operation ID:** `ListarOrdensCompraAction`
*   **Description:**
*   **Parameters:**
    *   `numero` (query): Pesquisa através do número da ordem de compra. Type: int.
    *   `dataInicial` (query): Pesquisa através da data de criação da ordem de compra. Type: string.
    *   `dataFinal` (query): Pesquisa através da data de criação da ordem de compra. Type: string.
    *   `marcadores` (query): Pesquisa através dos marcadores da ordem de compra. Type: array of string.
    *   `nomeFornecedor` (query): Pesquisa através do nome do fornecedor da ordem de compra. Type: string.
    *   `codigoFornecedor` (query): Pesquisa através do código do fornecedor da ordem de compra. Type: string.
    *   `situacao` (query): Pesquisa através da situação da ordem de compra. Type: string. Enum: `0 - Em Aberto`, `1 - Atendido`, `2 - Cancelado`, `3 - Em Andamento`. Example: `0`.
    *   `orderBy` (query): Define a ordenação da listagem por ordem crescente ou decrescente. Type: string. Enum: `asc - Crescente`, `desc - Descrescente`. Example: `asc`.
    *   `limit` (query): Limite da paginação. Type: integer. Default: 100.
    *   `offset` (query): Offset da paginação. Type: integer. Default: 0.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:**
            ```json
            {
              "type": "object",
              "properties": {
                "itens": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/ListarOrdemCompraModelResponse"
                  }
                },
                "paginacao": {
                  "$ref": "#/components/schemas/PaginatedResultModel"
                }
              }
            }
            ```
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /ordem-compra

*   **Operation ID:** `CriarOrdemCompraAction`
*   **Description:**
*   **Parameters:** None
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/CriarOrdemCompraModelRequest`
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/CriarOrdemCompraModelResponse`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /ordem-compra/{idOrdemCompra}/lancar-contas

*   **Operation ID:** `LancarContasOrdemCompraAction`
*   **Description:**
*   **Parameters:**
    *   `idOrdemCompra` (path): Identificador da ordem de compra. Required. Type: integer.
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /ordem-compra/{idOrdemCompra}/lancar-estoque

*   **Operation ID:** `LancarEstoqueOrdemCompraAction`
*   **Description:**
*   **Parameters:**
    *   `idOrdemCompra` (path): Identificador da ordem de compra. Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/LancarEstoqueOrdemCompraRequestModel`
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

### Ordem de Serviço

#### GET /ordem-servico/{idOrdemServico}

*   **Operation ID:** `ObterOrdemServicoAction`
*   **Description:**
*   **Parameters:**
    *   `idOrdemServico` (path): Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ObterOrdemServicoModelResponse`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### PUT /ordem-servico/{idOrdemServico}

*   **Operation ID:** `AtualizarOrdemServicoAction`
*   **Description:**
*   **Parameters:**
    *   `idOrdemServico` (path): Identificador da ordem de serviço. Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/AtualizarOrdemServicoRequestModel`
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### PUT /ordem-servico/{idOrdemServico}/situacao

*   **Operation ID:** `AtualizarSituacaoOrdemServicoAction`
*   **Description:**
*   **Parameters:**
    *   `idOrdemServico` (path): Identificador da ordem de serviço. Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/AtualizarSituacaoPedidoModelRequest`
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /ordem-servico

*   **Operation ID:** `ListarOrdemServicoAction`
*   **Description:**
*   **Parameters:**
    *   `nomeCliente` (query): Pesquisa por nome do cliente de ordem de servico. Type: string.
    *   `situacao` (query): Pesquisa por situação de ordem de servico. Type: string. Enum: `4 - Nao Aprovada`, `3 - Finalizada`, `0 - Em Aberto`, `2 - Serv Concluido`, `1 - Orcada`, `5 - Aprovada`, `6 - Em Andamento`, `7 - Cancelada`. Example: `4`.
    *   `dataInicialEmissao` (query): Pesquisa por data inicial da emissão de ordem de servico. Type: string. Example: `2024-01-01`.
    *   `dataFinalEmissao` (query): Pesquisa por data final da emissão de ordem de servico. Type: string. Example: `2024-01-01`.
    *   `numeroOrdemServico` (query): Pesquisa por número de ordem de servico. Type: string.
    *   `marcadores` (query): Pesquisa por marcadores. Type: array of string.
    *   `idContato` (query): Pesquisa por ID do contato de ordem de servico. Type: integer. Example: 123.
    *   `orderBy` (query): Define a ordenação da listagem por ordem crescente ou decrescente. Type: string. Enum: `asc - Crescente`, `desc - Descrescente`. Example: `asc`.
    *   `limit` (query): Limite da paginação. Type: integer. Default: 100.
    *   `offset` (query): Offset da paginação. Type: integer. Default: 0.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ListagemOrdemServicoResponseModel`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /ordem-servico

*   **Operation ID:** `CriarOrdemServicoAction`
*   **Description:**
*   **Parameters:** None
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/CriarOrdemServicoRequestModel`
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/CriarOrdemServicoResponseModel`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /ordem-servico/{idOrdemServico}/gerar-nota-fiscal

*   **Operation ID:** `GerarNotaFiscalOrdemServicoAction`
*   **Description:**
*   **Parameters:**
    *   `idOrdemServico` (path): Identificador da ordem de serviço. Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/GerarNotaFiscalOrdemServicoModelResponse`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /ordem-servico/{idOrdemServico}/lancar-contas

*   **Operation ID:** `LancarContasOrdemServicoAction`
*   **Description:**
*   **Parameters:**
    *   `idOrdemServico` (path): Identificador da ordem de serviço. Required. Type: integer.
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /ordem-servico/{idOrdemServico}/lancar-estoque

*   **Operation ID:** `LancarEstoqueOrdemServicoAction`
*   **Description:**
*   **Parameters:**
    *   `idOrdemServico` (path): Identificador da ordem de serviço. Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/LancarEstoqueOrdemServicoRequestModel`
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

### Pedidos

#### PUT /pedidos/{idPedido}/despacho

*   **Operation ID:** `AtualizarInfoRastreamentoPedidoAction`
*   **Description:**
*   **Parameters:**
    *   `idPedido` (path): Identificador do pedido. Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/AtualizarInfoRastreamentoPedidoModelRequest`
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /pedidos/{idPedido}/marcadores

*   **Operation ID:** `ObterMarcadoresPedidoAction`
*   **Description:**
*   **Parameters:**
    *   `idPedido` (path): Identificador do pedido. Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:**
            ```json
            {
              "type": "array",
              "items": {
                "$ref": "#/components/schemas/ObterMarcadorResponseModel"
              }
            }
            ```
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### PUT /pedidos/{idPedido}/marcadores

*   **Operation ID:** `AtualizarMarcadoresPedidoAction`
*   **Description:**
*   **Parameters:**
    *   `idPedido` (path): Identificador do pedido. Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:**
        ```json
        {
          "type": "array",
          "items": {
            "$ref": "#/components/schemas/AtualizarMarcadorRequestModel"
          }
        }
        ```
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /pedidos/{idPedido}/marcadores

*   **Operation ID:** `CriarMarcadoresPedidoAction`
*   **Description:**
*   **Parameters:**
    *   `idPedido` (path): Identificador do pedido. Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:**
        ```json
        {
          "type": "array",
          "items": {
            "$ref": "#/components/schemas/CriarMarcadorRequestModel"
          }
        }
        ```
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### DELETE /pedidos/{idPedido}/marcadores

*   **Operation ID:** `ExcluirMarcadoresPedidoAction`
*   **Description:**
*   **Parameters:**
    *   `idPedido` (path): Identificador do pedido. Required. Type: integer.
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /pedidos/{idPedido}

*   **Operation ID:** `ObterPedidoAction`
*   **Description:**
*   **Parameters:**
    *   `idPedido` (path): Identificador do pedido. Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ObterPedidoModelResponse`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### PUT /pedidos/{idPedido}

*   **Operation ID:** `AtualizarPedidoAction`
*   **Description:**
*   **Parameters:**
    *   `idPedido` (path): Identificador do pedido. Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/AtualizarPedidoModelRequest`
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### PUT /pedidos/{idPedido}/situacao

*   **Operation ID:** `AtualizarSituacaoPedidoAction`
*   **Description:**
*   **Parameters:**
    *   `idPedido` (path): Identificador do pedido. Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/AtualizarSituacaoPedidoModelRequest`
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /pedidos

*   **Operation ID:** `ListarPedidosAction`
*   **Description:**
*   **Parameters:**
    *   `numero` (query): Pesquisa por número do pedido. Type: int.
    *   `nomeCliente` (query): Pesquisa por nome do cliente. Type: string.
    *   `codigoCliente` (query): Pesquisa por código do cliente. Type: string.
    *   `cnpj` (query): Pesquisa por CPF/CNPJ do cliente. Type: string.
    *   `dataInicial` (query): Pesquisa através da data de criação do pedido. Type: string.
    *   `dataFinal` (query): Pesquisa através da data de criação do pedido. Type: string.
    *   `dataAtualizacao` (query): Pesquisa através da data de atualização do pedido. Type: string.
    *   `situacao` (query): Pesquisa com base na situação informada. Type: string. Enum: `8 - Dados Incompletos`, `0 - Aberta`, `3 - Aprovada`, `4 - Preparando Envio`, `1 - Faturada`, `7 - Pronto Envio`, `5 - Enviada`, `6 - Entregue`, `2 - Cancelada`, `9 - Nao Entregue`. Example: `8`.
    *   `numeroPedidoEcommerce` (query): Pesquisa por número do pedido no e-commerce. Type: string.
    *   `idVendedor` (query): Pesquisa por id do vendedor. Type: int.
    *   `marcadores` (query): Pesquisa por marcadores. Type: array of string.
    *   `orderBy` (query): Define a ordenação da listagem por ordem crescente ou decrescente. Type: string. Enum: `asc - Crescente`, `desc - Descrescente`. Example: `asc`.
    *   `limit` (query): Limite da paginação. Type: integer. Default: 100.
    *   `offset` (query): Offset da paginação. Type: integer. Default: 0.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:**
            ```json
            {
              "type": "object",
              "properties": {
                "itens": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/ListagemPedidoModelResponse"
                  }
                },
                "paginacao": {
                  "$ref": "#/components/schemas/PaginatedResultModel"
                }
              }
            }
            ```
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /pedidos

*   **Operation ID:** `CriarPedidoAction`
*   **Description:**
*   **Parameters:** None
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/CriarPedidoModelRequest`
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/CriarPedidoModelResponse`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /pedidos/{idPedido}/estornar-contas

*   **Operation ID:** `EstornarContasPedidoAction`
*   **Description:**
*   **Parameters:**
    *   `idPedido` (path): Identificador do pedido. Required. Type: integer.
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /pedidos/{idPedido}/estornar-estoque

*   **Operation ID:** `EstornarEstoquePedidoAction`
*   **Description:**
*   **Parameters:**
    *   `idPedido` (path): Identificador do pedido. Required. Type: integer.
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /pedidos/{idPedido}/gerar-nota-fiscal

*   **Operation ID:** `GerarNotaFiscalPedidoAction`
*   **Description:**
*   **Parameters:**
    *   `idPedido` (path): Identificador do pedido. Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/GerarNotaFiscalPedidoModelResponse`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /pedidos/{idPedido}/lancar-contas

*   **Operation ID:** `LancarContasPedidoAction`
*   **Description:**
*   **Parameters:**
    *   `idPedido` (path): Identificador do pedido. Required. Type: integer.
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /pedidos/{idPedido}/lancar-estoque

*   **Operation ID:** `LancarEstoquePedidoAction`
*   **Description:**
*   **Parameters:**
    *   `idPedido` (path): Identificador do pedido. Required. Type: integer.
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

### Produtos

#### PUT /produtos/{idProduto}/preco

*   **Operation ID:** `AtualizarPrecoProdutoAction`
*   **Description:**
*   **Parameters:**
    *   `idProduto` (path): Identificador do produto. Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/AtualizarPrecoProdutoRequestModel`
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/AtualizarPrecoProdutoResponseModel`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /produtos/{idProduto}

*   **Operation ID:** `ObterProdutoAction`
*   **Description:**
*   **Parameters:**
    *   `idProduto` (path): Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ObterProdutoModelResponse`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### PUT /produtos/{idProduto}

*   **Operation ID:** `AtualizarProdutoAction`
*   **Description:**
*   **Parameters:**
    *   `idProduto` (path): Identificador do produto. Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/AtualizarProdutoRequestModel`
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /produtos/{idProduto}/fabricado

*   **Operation ID:** `ObterProdutoFabricadoAction`
*   **Description:**
*   **Parameters:** None (Note: Path parameter `idProduto` is missing in the spec for this operation, but present in the path. Assuming it's required.)
    *   `idProduto` (path): Identificador do produto. Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ProducaoProdutoResponseModel`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### PUT /produtos/{idProduto}/fabricado

*   **Operation ID:** `AtualizarProdutoFabricadoAction`
*   **Description:**
*   **Parameters:**
    *   `idProduto` (path): Identificador do produto. Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/ProducaoProdutoRequestModel`
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /produtos/{idProduto}/kit

*   **Operation ID:** `ObterProdutoKitAction`
*   **Description:**
*   **Parameters:** None (Note: Path parameter `idProduto` is missing in the spec for this operation, but present in the path. Assuming it's required.)
    *   `idProduto` (path): Identificador do produto. Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:**
            ```json
            {
              "type": "array",
              "items": {
                "$ref": "#/components/schemas/ProdutoKitResponseModel"
              }
            }
            ```
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### PUT /produtos/{idProduto}/kit

*   **Operation ID:** `AtualizarProdutoKitAction`
*   **Description:**
*   **Parameters:** None (Note: Path parameter `idProduto` is missing in the spec for this operation, but present in the path. Assuming it's required.)
    *   `idProduto` (path): Identificador do produto. Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:**
        ```json
        {
          "type": "array",
          "items": {
            "$ref": "#/components/schemas/ProdutoKitRequestModel"
          }
        }
        ```
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### PUT /produtos/{idProduto}/variacoes/{idVariacao}

*   **Operation ID:** `AtualizarProdutoVariacaoAction`
*   **Description:**
*   **Parameters:**
    *   `idProduto` (path): Identificador do produto. Required. Type: integer.
    *   `idVariacao` (path): Identificador da variação. Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/AtualizarProdutoVariacaoRequestModel`
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### DELETE /produtos/{idProduto}/variacoes/{idVariacao}

*   **Operation ID:** `DeletarProdutoVariacaoAction`
*   **Description:**
*   **Parameters:**
    *   `idProduto` (path): Identificador do produto. Required. Type: integer.
    *   `idVariacao` (path): Identificador da variação. Required. Type: integer.
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /produtos

*   **Operation ID:** `ListarProdutosAction`
*   **Description:**
*   **Parameters:**
    *   `nome` (query): Pesquisa por nome parcial ou completo do produto. Type: string.
    *   `codigo` (query): Pesquisa pelo código do produto. Type: string.
    *   `gtin` (query): Pesquisa através do código GTIN do produto. Type: int.
    *   `situacao` (query): Pesquisa com base na situação informada. Type: string.
    *   `dataCriacao` (query): Pesquisa através da data de criação do produto. Type: string. Example: `2023-01-01 10:00:00`.
    *   `dataAlteracao` (query): Pesquisa através da data de última alteração do produto. Type: string. Example: `2023-01-01 10:00:00`.
    *   `limit` (query): Limite da paginação. Type: integer. Default: 100.
    *   `offset` (query): Offset da paginação. Type: integer. Default: 0.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:**
            ```json
            {
              "type": "object",
              "properties": {
                "itens": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/ListagemProdutosResponseModel"
                  }
                },
                "paginacao": {
                  "$ref": "#/components/schemas/PaginatedResultModel"
                }
              }
            }
            ```
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /produtos

*   **Operation ID:** `CriarProdutoAction`
*   **Description:**
*   **Parameters:** None
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/CriarProdutoRequestModel`
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/CriarProdutoComVariacoesResponseModel`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /produtos/{idProduto}/variacoes

*   **Operation ID:** `CriarProdutoVariacaoAction`
*   **Description:**
*   **Parameters:**
    *   `idProduto` (path): Identificador do produto. Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/VariacaoProdutoRequestModel`
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/CriarProdutoResponseModel`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /produtos/{idProduto}/custos

*   **Operation ID:** `ListaCustosProdutoAction`
*   **Description:**
*   **Parameters:**
    *   `idProduto` (path): Required. Type: integer.
    *   `dataInicial` (query): Especifica a data de início para a filtragem dos custos do produto.. Type: string. Example: `2023-01-01`.
    *   `dataFinal` (query): Especifica a data de fim para a filtragem dos custos do produto.. Type: string. Example: `2023-01-01`.
    *   `limit` (query): Limite da paginação. Type: integer. Default: 100.
    *   `offset` (query): Offset da paginação. Type: integer. Default: 0.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:**
            ```json
            {
              "type": "object",
              "properties": {
                "itens": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/ListagemProdutoCustosResponseModel"
                  }
                },
                "paginacao": {
                  "$ref": "#/components/schemas/PaginatedResultModel"
                }
              }
            }
            ```
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /produtos/{idProduto}/tags

*   **Operation ID:** `ObterTagsProdutoAction`
*   **Description:**
*   **Parameters:**
    *   `idProduto` (path): Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ObterTagsProdutoModelResponse`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

### Separação

#### PUT /separacao/{idSeparacao}/situacao

*   **Operation ID:** `AlterarSituacaoSeparacaoAction`
*   **Description:**
*   **Parameters:**
    *   `idSeparacao` (path): Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/AlterarSituacaoSeparacaoModelRequest`
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /separacao

*   **Operation ID:** `ListarSeparacaoAction`
*   **Description:**
*   **Parameters:**
    *   `situacao` (query): Pesquisa por situacao da separação.. Type: string. Enum: `1 - Sit Aguardando Separacao`, `2 - Sit Separada`, `3 - Sit Embalada`, `4 - Sit Em Separacao`. Example: `1`.
    *   `idFormaEnvio` (query): Pesquisa através do identificador da forma de envio.. Type: int.
    *   `dataInicial` (query): Pesquisa através da data inicial dos pedidos.. Type: string. Example: `2023-01-01`.
    *   `dataFinal` (query): Pesquisa através da data final dos pedidos.. Type: string. Example: `2023-01-01`.
    *   `orderBy` (query): Define a ordenação da listagem por ordem crescente ou decrescente. Type: string. Enum: `asc - Crescente`, `desc - Descrescente`. Example: `asc`.
    *   `limit` (query): Limite da paginação. Type: integer. Default: 100.
    *   `offset` (query): Offset da paginação. Type: integer. Default: 0.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:**
            ```json
            {
              "type": "object",
              "properties": {
                "itens": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/ListagemSeparacaoResponseModel"
                  }
                },
                "paginacao": {
                  "$ref": "#/components/schemas/PaginatedResultModel"
                }
              }
            }
            ```
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /separacao/{idSeparacao}

*   **Operation ID:** `ObterSeparacaoAction`
*   **Description:**
*   **Parameters:**
    *   `idSeparacao` (path): Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ObterSeparacaoResponseModel`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

### Serviços

#### GET /servicos/{idServico}

*   **Operation ID:** `ObterServicoAction`
*   **Description:**
*   **Parameters:**
    *   `idServico` (path): Required. Type: integer.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ServicosModelResponse`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### PUT /servicos/{idServico}

*   **Operation ID:** `AtualizarServicoAction`
*   **Description:**
*   **Parameters:**
    *   `idServico` (path): Identificador do serviço. Required. Type: integer.
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/AtualizarServicoRequestModel`
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### GET /servicos

*   **Operation ID:** `ListarServicosAction`
*   **Description:**
*   **Parameters:**
    *   `nome` (query): Pesquisa pelo nome do serviço. Type: string.
    *   `codigo` (query): Pesquisa pelo código do serviço. Type: string.
    *   `situacao` (query): Pesquisa com base na situação informada. Type: string. Enum: `A - Ativo`, `I - Inativo`, `E - Excluido`. Example: `A`.
    *   `orderBy` (query): Define a ordenação da listagem por ordem crescente ou decrescente. Type: string. Enum: `asc - Crescente`, `desc - Descrescente`. Example: `asc`.
    *   `limit` (query): Limite da paginação. Type: integer. Default: 100.
    *   `offset` (query): Offset da paginação. Type: integer. Default: 0.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:**
            ```json
            {
              "type": "object",
              "properties": {
                "itens": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/ServicosModelResponse"
                  }
                },
                "paginacao": {
                  "$ref": "#/components/schemas/PaginatedResultModel"
                }
              }
            }
            ```
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /servicos

*   **Operation ID:** `CriarServicoAction`
*   **Description:**
*   **Parameters:** None
*   **Request Body:**
    *   Required: true
    *   **Content:** `application/json`
    *   **Schema:** `#/components/schemas/CriarServicoRequestModel`
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ServicoResponseModel`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

#### POST /servicos/{idServico}/transformar-produto

*   **Operation ID:** `TransformarServicoEmProdutoAction`
*   **Description:**
*   **Parameters:**
    *   `idServico` (path): Required. Type: integer.
*   **Responses:**
    *   `204 No Content`
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

### Vendedores

#### GET /vendedores

*   **Operation ID:** `ListarVendedoresAction`
*   **Description:**
*   **Parameters:**
    *   `nome` (query): Pesquisa por nome parcial ou completo. Type: string.
    *   `codigo` (query): Pesquisa por codigo completo. Type: string.
    *   `limit` (query): Limite da paginação. Type: integer. Default: 100.
    *   `offset` (query): Offset da paginação. Type: integer. Default: 0.
*   **Responses:**
    *   `200 OK`:
        *   **Content:** `application/json`
        *   **Schema:**
            ```json
            {
              "type": "object",
              "properties": {
                "itens": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/ListagemVendedoresModelResponse"
                  }
                },
                "paginacao": {
                  "$ref": "#/components/schemas/PaginatedResultModel"
                }
              }
            }
            ```
    *   `400 Bad Request`:
        *   **Content:** `application/json`
        *   **Schema:** `#/components/schemas/ErrorDTO`
    *   `404 Not Found`
    *   `403 Forbidden`
    *   `503 Service Unavailable`
    *   `401 Unauthorized`
    *   `500 Internal Server Error`
*   **Security:**
    *   `bearerAuth`

## Componentes

### Schemas (Modelos de Dados)

#### ErrorDTO

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `mensagem` (string):
    *   `detalhes` (array): nullable. Items: `#/components/schemas/ErrorDetailDTO`.

#### ErrorDetailDTO

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `campo` (string):
    *   `mensagem` (string):

#### AnexoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `url` (string): nullable.
    *   `externo` (any):

#### AnexoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `url` (string): nullable.
    *   `externo` (boolean): nullable.

#### CategoriaRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.

#### CategoriaResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `nome` (string): nullable.
    *   `caminhoCompleto` (string): nullable.

#### ListarArvoreCategoriasModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `descricao` (string): nullable.
    *   `filhas` (array): nullable. Items: `#/components/schemas/ListarArvoreCategoriasModelResponse`.

#### CategoriaReceitaDespesaResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `descricao` (string):

#### ListagemCategoriasReceitaDespesaResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `descricao` (string):
    *   `grupo` (string):

#### ContaContabilModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.

#### ContaContabilRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):

#### CriarContaPagarRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `data` (string): nullable.
    *   `dataVencimento` (string): nullable.
    *   `valor` (number): float, nullable.
    *   `numeroDocumento` (string): nullable.
    *   `contato` (`#/components/schemas/ContatoRequestModel`):
    *   `historico` (string): nullable.
    *   `categoria` (`#/components/schemas/CategoriaRequestModel`):
    *   `dataCompetencia` (string): nullable.
    *   `ocorrencia` (string): nullable. Enum: `U - Unica`, `W - Semanal`, `M - Mensal`, `T - Trimestral`, `S - Semestral`, `A - Anual`, `P - Parcelada`. Example: `U`.
    *   `formaPagamento` (integer): nullable. Enum: `0 - Nao Definida`, `2 - Dinheiro`, `3 - Credito`, `4 - Debito`, `5 - Boleto`, `6 - Deposito`, `7 - Cheque`, `8 - Crediario`, `10 - Outra`, `12 - Duplicata Mercantil`, `14 - Vale`, `15 - Pix`, `16 - Vale Alimentacao`, `17 - Vale Refeicao`, `18 - Vale Presente`, `19 - Vale Combustivel`, `20 - Deposito Bancario`, `21 - Transferencia Bancaria Carteira Digital`, `22 - Fidelidade Cashback Credito Virtual`. Example: `0`.
    *   `diaVencimento` (integer): nullable.
    *   `quantidadeParcelas` (integer): nullable.
    *   `diaSemanaVencimento` (integer): nullable.

#### CriarContaPagarResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):

#### ListagemContasPagarResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `situacao` (string): nullable. Enum: `aberto - Aberto`, `cancelada - Cancelada`, `pago - Pago`, `parcial - Parcial`, `prevista - Prevista`. Example: `aberto`.
    *   `data` (string): nullable.
    *   `dataVencimento` (string): nullable.
    *   `historico` (string): nullable.
    *   `valor` (number): float, nullable.
    *   `numeroDocumento` (string): nullable.
    *   `numeroBanco` (string): nullable.
    *   `serieDocumento` (string): nullable.
    *   `cliente` (`#/components/schemas/ContatoModelResponse`):
    *   `marcadores` (any):

#### ObterContaPagarModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `situacao` (string): nullable. Enum: `aberto - Aberto`, `cancelada - Cancelada`, `pago - Pago`, `parcial - Parcial`, `prevista - Prevista`. Example: `aberto`.
    *   `data` (string):
    *   `dataVencimento` (string):
    *   `dataCompetencia` (string):
    *   `dataLiquidacao` (string): nullable.
    *   `diaVencimento` (integer): nullable.
    *   `diaSemanaVencimento` (integer): nullable. Enum: `0 - Domingo`, `1 - Segunda`, `2 - Terca`, `3 - Quarta`, `4 - Quinta`, `5 - Sexta`, `6 - Sabado`. Example: `0`.
    *   `numeroDocumento` (string):
    *   `serieDocumento` (string): nullable.
    *   `ocorrencia` (string): nullable. Enum: `U - Unica`, `W - Semanal`, `M - Mensal`, `T - Trimestral`, `S - Semestral`, `A - Anual`, `P - Parcelada`. Example: `U`.
    *   `quantidadeParcelas` (integer): nullable.
    *   `valor` (number): float, nullable.
    *   `saldo` (number): float, nullable.
    *   `contato` (`#/components/schemas/ContatoModelResponse`):
    *   `categoria` (`#/components/schemas/CategoriaReceitaDespesaResponseModel`):
    *   `formaPagamento` (`#/components/schemas/FormaPagamentoResponseModel`):
    *   `historico` (string):
    *   `marcadores` (any):

#### AtualizarContaReceberRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   (object with properties below)
*   **Properties:**
    *   `taxa` (number): float, nullable.
    *   `dataVencimento` (string): nullable.
    *   `categoria` (`#/components/schemas/CategoriaRequestModel`):
    *   `dataCompetencia` (string): nullable.
    *   `atualizarContaRecorrente` (boolean):

#### BaixarContaReceberModelRequest

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `contaDestino` (`#/components/schemas/ContaContabilRequestModel`):
    *   `data` (string): nullable.
    *   `categoria` (`#/components/schemas/CategoriaRequestModel`):
    *   `historico` (string): nullable.
    *   `taxa` (number): float, nullable.
    *   `juros` (number): float, nullable.
    *   `desconto` (number): float, nullable.
    *   `valorPago` (number): float, nullable.
    *   `acrescimo` (number): float, nullable.

#### CriarContaReceberRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `data` (string): nullable.
    *   `dataVencimento` (string): nullable.
    *   `valor` (number): float, nullable.
    *   `numeroDocumento` (string): nullable.
    *   `contato` (`#/components/schemas/ContatoRequestModel`):
    *   `historico` (string): nullable.
    *   `categoria` (`#/components/schemas/CategoriaRequestModel`):
    *   `dataCompetencia` (string): nullable.
    *   `formaRecebimento` (integer): nullable. Enum: `0 - Nao Definida`, `1 - Multiplas`, `2 - Dinheiro`, `3 - Credito`, `4 - Debito`, `5 - Boleto`, `6 - Deposito`, `7 - Cheque`, `8 - Crediario`, `9 - Conta Receber`, `10 - Outra`, `11 - Personalizada`, `12 - Duplicata Mercantil`, `13 - Paypal`, `14 - Vale`, `15 - Pix`, `23 - Link Pagamento`. Example: `0`.
    *   `ocorrencia` (string): nullable. Enum: `U - Unica`, `W - Semanal`, `M - Mensal`, `T - Trimestral`, `S - Semestral`, `A - Anual`, `P - Parcelada`. Example: `U`.
    *   `diaVencimento` (integer): nullable.
    *   `diaSemanaVencimento` (integer): nullable.
    *   `quantidadeParcelas` (integer): nullable.

#### CriarContaReceberResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):

#### ListagemContasReceberResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `situacao` (string): nullable. Enum: `aberto - Aberto`, `cancelada - Cancelada`, `pago - Pago`, `parcial - Parcial`, `prevista - Prevista`. Example: `aberto`.
    *   `data` (string): nullable.
    *   `dataVencimento` (string): nullable.
    *   `historico` (string): nullable.
    *   `valor` (number): float, nullable.
    *   `numeroDocumento` (string): nullable.
    *   `numeroBanco` (string): nullable.
    *   `serieDocumento` (string): nullable.
    *   `cliente` (`#/components/schemas/ContatoModelResponse`):

#### ObterContaReceberResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `situacao` (string): nullable. Enum: `aberto - Aberto`, `cancelada - Cancelada`, `pago - Pago`, `parcial - Parcial`, `prevista - Prevista`. Example: `aberto`.
    *   `data` (string): nullable.
    *   `dataVencimento` (string): nullable.
    *   `dataCompetencia` (string): nullable.
    *   `dataLiquidacao` (string): nullable.
    *   `diaVencimento` (integer): nullable.
    *   `diaSemanaVencimento` (integer): nullable. Enum: `0 - Domingo`, `1 - Segunda`, `2 - Terca`, `3 - Quarta`, `4 - Quinta`, `5 - Sexta`, `6 - Sabado`. Example: `0`.
    *   `numeroDocumento` (string): nullable.
    *   `serieDocumento` (string): nullable.
    *   `ocorrencia` (string): nullable. Enum: `U - Unica`, `W - Semanal`, `M - Mensal`, `T - Trimestral`, `S - Semestral`, `A - Anual`, `P - Parcelada`. Example: `U`.
    *   `quantidadeParcelas` (integer): nullable.
    *   `valor` (number): float, nullable.
    *   `saldo` (number): float, nullable.
    *   `taxa` (number): float, nullable.
    *   `cliente` (`#/components/schemas/ContatoModelResponse`):
    *   `categoria` (`#/components/schemas/CategoriaReceitaDespesaResponseModel`):
    *   `formaRecebimento` (`#/components/schemas/FormaRecebimentoResponseModel`):
    *   `historico` (string): nullable.
    *   `linkBoleto` (string): nullable.

#### AtualizarContatoContatoModelRequest

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/BasePessoaContatoModel`

#### AtualizarContatoModelRequest

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/CriarAtualizarContatoModelRequest`

#### BaseContatoModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `nome` (string): nullable.
    *   `codigo` (string): nullable.
    *   `fantasia` (string): nullable.
    *   `tipoPessoa` (string): nullable. Enum: `J - Juridica`, `F - Fisica`, `E - Estrangeiro`, `X - Estrangeiro No Brasil`. Example: `J`.
    *   `cpfCnpj` (string): nullable.
    *   `inscricaoEstadual` (string): nullable.
    *   `rg` (string): nullable.
    *   `telefone` (string): nullable.
    *   `celular` (string): nullable.
    *   `email` (string): nullable.
    *   `endereco` (`#/components/schemas/EnderecoModel`):

#### BasePessoaContatoModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `nome` (string): nullable.
    *   `telefone` (string): nullable.
    *   `ramal` (string): nullable.
    *   `email` (string): nullable.
    *   `setor` (string): nullable.

#### ContatoModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/BaseContatoModel`
    *   (object with properties below)
*   **Properties:**
    *   `enderecoCobranca` (`#/components/schemas/EnderecoModel`):
    *   `inscricaoMunicipal` (string): nullable.
    *   `telefoneAdicional` (string): nullable.
    *   `emailNfe` (string): nullable.
    *   `site` (string): nullable.
    *   `regimeTributario` (integer): nullable. Enum: `1 - Simples Nacional`, `2 - Simples Nacional Excesso Receita`, `3 - Regime Normal`, `4 - Mei`. Example: `1`.
    *   `estadoCivil` (integer): nullable. Enum: `1 - Casado`, `2 - Solteiro`, `3 - Viuvo`, `4 - Separado`, `5 - Desquitado`. Example: `1`.
    *   `profissao` (string): nullable.
    *   `sexo` (string): nullable. Enum: `masculino - Masculino`, `feminino - Feminino`. Example: `masculino`.
    *   `dataNascimento` (string): nullable.
    *   `naturalidade` (string): nullable.
    *   `nomePai` (string): nullable.
    *   `nomeMae` (string): nullable.
    *   `cpfPai` (string): nullable.
    *   `cpfMae` (string): nullable.
    *   `limiteCredito` (number): float, nullable.
    *   `situacao` (string): nullable. Enum: `B - Ativo`, `A - Ativo Com Acesso Sistema`, `I - Inativo`, `E - Excluido`. Example: `B`.
    *   `observacoes` (string): nullable.

#### ContatoModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/BaseContatoModel`
    *   (object with properties below)
*   **Properties:**
    *   `id` (integer):

#### CriarAtualizarContatoModelRequest

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/ContatoModel`
    *   (object with properties below)
*   **Properties:**
    *   `vendedor` (`#/components/schemas/VendedorRequestModel`):
    *   `tipos` (array): Items: integer.
    *   `contatos` (array): nullable. Items: `#/components/schemas/CriarContatoContatoModelRequest`.

#### CriarContatoContatoModelRequest

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/BasePessoaContatoModel`

#### CriarContatoContatoModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.

#### CriarContatoModelRequest

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/CriarAtualizarContatoModelRequest`

#### CriarContatoModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):

#### ListagemContatoModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/BaseContatoModel`
    *   (object with properties below)
*   **Properties:**
    *   `id` (integer):
    *   `vendedor` (oneOf): nullable. OneOf: `#/components/schemas/VendedorResponseModel`.
    *   `situacao` (string): nullable. Enum: `B - Ativo`, `A - Ativo Com Acesso Sistema`, `I - Inativo`, `E - Excluido`. Example: `B`.
    *   `dataCriacao` (string): nullable.
    *   `dataAtualizacao` (string): nullable.

#### ListagemContatosContatoModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/PessoaContatoModel`
    *   (object with properties below)
*   **Properties:**
    *   `id` (integer): nullable.

#### ListarTiposDeContatosModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `nome` (string):
    *   `perfilContato` (string): Enum: `0 - Outro`, `1 - Cliente`, `2 - Fornecedor`, `3 - Vendedor`, `4 - Transportador`, `5 - Funcionario`. Example: `0`.

#### ObterContatoContatoModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/PessoaContatoModel`
    *   (object with properties below)
*   **Properties:**
    *   `id` (integer): nullable.

#### ObterContatoModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/ContatoModel`
    *   (object with properties below)
*   **Properties:**
    *   `id` (integer):
    *   `dataCriacao` (string): nullable.
    *   `dataAtualizacao` (string): nullable.
    *   `vendedor` (oneOf): nullable. OneOf: `#/components/schemas/VendedorResponseModel`.
    *   `tipos` (array): nullable. Items: `#/components/schemas/TipoContatoModel`.
    *   `contatos` (array): nullable. Items: `#/components/schemas/PessoaContatoModel`.

#### PessoaContatoModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/BasePessoaContatoModel`
    *   (object with properties below)
*   **Properties:**
    *   `id` (integer): nullable.

#### TipoContatoModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `descricao` (string): nullable.

#### ObterInfoContaModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `razaoSocial` (string):
    *   `cpfCnpj` (string):
    *   `fantasia` (string):
    *   `enderecoEmpresa` (`#/components/schemas/EnderecoModel`):
    *   `fone` (string):
    *   `email` (string):
    *   `inscricaoEstadual` (string):
    *   `regimeTributario` (integer): Enum: `1 - Simples Nacional`, `2 - Simples Nacional Excesso Receita`, `3 - Regime Normal`, `4 - Mei`. Example: `1`.

#### DepositoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):

#### DepositoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `nome` (string):

#### BaseEcommerceModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `nome` (string): nullable.

#### EcommerceRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `numeroPedidoEcommerce` (string): nullable.

#### EcommerceResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `nome` (string): nullable.
    *   `numeroPedidoEcommerce` (string): nullable.
    *   `numeroPedidoCanalVenda` (string): nullable.
    *   `canalVenda` (string): nullable.

#### EmbalagemRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `tipo` (integer): nullable. Enum: `0 - Nao Definido`, `1 - Envelope`, `2 - Caixa`, `3 - Cilindro`. Example: `0`.

#### EmbalagemResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `tipo` (integer): nullable. Enum: `0 - Nao Definido`, `1 - Envelope`, `2 - Caixa`, `3 - Cilindro`. Example: `0`.
    *   `descricao` (string): nullable.

#### EnderecoEntregaModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/EnderecoModel`
    *   (object with properties below)
*   **Properties:**
    *   `nomeDestinatario` (string): nullable.
    *   `cpfCnpj` (string): nullable.
    *   `tipoPessoa` (string): nullable.

#### EnderecoModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `endereco` (string): nullable.
    *   `numero` (string): nullable.
    *   `complemento` (string): nullable.
    *   `bairro` (string): nullable.
    *   `municipio` (string): nullable.
    *   `cep` (string): nullable.
    *   `uf` (string): nullable.
    *   `pais` (string): nullable.

#### AtualizarProdutoEstoqueModelRequest

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `deposito` (`#/components/schemas/DepositoRequestModel`):
    *   `tipo` (string): nullable. Enum: `B - Balanco`, `E - Entrada`, `S - Saida`. Example: `B`.
    *   `data` (string): nullable.
    *   `quantidade` (number): float, nullable.
    *   `precoUnitario` (number): float, nullable.
    *   `observacoes` (string): nullable.

#### AtualizarProdutoEstoqueModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `idLancamento` (integer):

#### DepositoModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `nome` (string):
    *   `desconsiderar` (boolean):
    *   `saldo` (number): float.
    *   `reservado` (number): float.
    *   `disponivel` (number): float.

#### ObterEstoqueProdutoModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `nome` (string):
    *   `codigo` (string):
    *   `unidade` (string):
    *   `saldo` (number): float.
    *   `reservado` (number): float.
    *   `disponivel` (number): float.
    *   `depositos` (array): Items: `#/components/schemas/DepositoModel`.

#### CriarAgrupamentoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `idsNotasFiscais` (array): Items: integer.
    *   `idsPedidos` (array): Items: integer.
    *   `objetosAvulsos` (array): Items: `#/components/schemas/ObjetoAvulsoRequestModel`.

#### CriarAgrupamentoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):

#### ExpedicaoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `descricao` (string): nullable.
    *   `volume` (`#/components/schemas/VolumeExpedicaoRequestModel`):
    *   `logistica` (`#/components/schemas/LogisticaExpedicaoRequestModel`):

#### LogisticaExpedicaoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `formaFrete` (`#/components/schemas/FormaFreteRequestModel`):
    *   `codigoRastreio` (string): nullable.
    *   `urlRastreio` (string): nullable.
    *   `possuiValorDeclarado` (any):
    *   `valorDeclarado` (number): float, nullable.
    *   `possuiAvisoRecebimento` (any):

#### VolumeExpedicaoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `embalagem` (`#/components/schemas/EmbalagemRequestModel`):
    *   `largura` (number): float, nullable.
    *   `altura` (number): float, nullable.
    *   `comprimento` (number): float, nullable.
    *   `diametro` (number): float, nullable.
    *   `pesoBruto` (number): float, nullable.
    *   `quantidadeVolumes` (number): float, nullable. Description: Apenas para notas e pedidos.

#### ListagemAgrupamentosModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `identificacao` (string):
    *   `data` (string):
    *   `quantidadeObjetos` (integer):
    *   `formaEnvio` (`#/components/schemas/FormaEnvioResponseModel`):

#### LogisticaObjetoAvulsoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `formaFrete` (`#/components/schemas/FormaFreteRequestModel`):
    *   `codigoRastreio` (string): nullable.
    *   `urlRastreio` (string): nullable.
    *   `possuiValorDeclarado` (any):
    *   `valorDeclarado` (number): float, nullable.
    *   `possuiAvisoRecebimento` (any):

#### ObjetoAvulsoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `descricao` (string): nullable.
    *   `data` (string): nullable.
    *   `destinatario` (`#/components/schemas/ContatoRequestModel`):
    *   `volume` (`#/components/schemas/VolumeObjetoAvulsoRequestModel`):
    *   `logistica` (`#/components/schemas/LogisticaObjetoAvulsoRequestModel`):

#### VolumeObjetoAvulsoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `embalagem` (`#/components/schemas/EmbalagemRequestModel`):
    *   `largura` (number): float, nullable.
    *   `altura` (number): float, nullable.
    *   `comprimento` (number): float, nullable.
    *   `diametro` (number): float, nullable.
    *   `pesoBruto` (number): float, nullable.

#### ExpedicaoNotaResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `numero` (integer): nullable.
    *   `data` (string): nullable.
    *   `situacao` (integer): nullable. Enum: `1 - Pendente`, `2 - Emitida`, `3 - Cancelada`, `4 - Enviada Aguardando Recibo`, `5 - Rejeitada`, `6 - Autorizada`, `7 - Emitida Danfe`, `8 - Registrada`, `9 - Enviada Aguardando Protocolo`, `10 - Denegada`. Example: `1`.

#### ExpedicaoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `data` (string):
    *   `situacao` (string):
    *   `venda` (`#/components/schemas/ExpedicaoVendaResponseModel`):
    *   `notaFiscal` (`#/components/schemas/ExpedicaoNotaResponseModel`):
    *   `destinatario` (`#/components/schemas/ContatoModelResponse`):
    *   `volume` (`#/components/schemas/VolumeExpedicaoResponseModel`):
    *   `logistica` (`#/components/schemas/LogisticaExpedicaoResponseModel`):

#### ExpedicaoVendaResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `numero` (integer): nullable.
    *   `data` (string): nullable.
    *   `situacao` (integer): nullable. Enum: `8 - Dados Incompletos`, `0 - Aberta`, `3 - Aprovada`, `4 - Preparando Envio`, `1 - Faturada`, `7 - Pronto Envio`, `5 - Enviada`, `6 - Entregue`, `2 - Cancelada`, `9 - Nao Entregue`. Example: `8`.

#### LogisticaExpedicaoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `codigoRastreio` (string):
    *   `urlRastreio` (string):
    *   `possuiValorDeclarado` (boolean):
    *   `valorDeclarado` (number): float.
    *   `possuiAvisoRecebimento` (boolean):
    *   `formaFrete` (`#/components/schemas/FormaFreteResponseModel`):
    *   `transportador` (`#/components/schemas/TransportadorExpedicaoResponseModel`):

#### ObterAgrupamentoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `identificacao` (string):
    *   `data` (string):
    *   `formaEnvio` (`#/components/schemas/FormaEnvioResponseModel`):
    *   `expedicoes` (array): Items: `#/components/schemas/ExpedicaoResponseModel`.

#### TransportadorExpedicaoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `nome` (string):

#### VolumeExpedicaoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `embalagem` (`#/components/schemas/EmbalagemResponseModel`):
    *   `largura` (number): float.
    *   `altura` (number): float.
    *   `comprimento` (number): float.
    *   `diametro` (number): float.
    *   `pesoBruto` (number): float.
    *   `quantidadeVolumes` (integer):

#### ObterEtiquetasResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `urls` (array): Items: string.

#### PaginatedResultModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `limit` (integer):
    *   `offset` (integer):
    *   `total` (integer):

#### FormaEnvioModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `nome` (string): nullable.
    *   `tipo` (string): nullable. Enum: `0 - Sem Frete`, `1 - Correios`, `2 - Transportadora`, `3 - Mercado Envios`, `4 - B2w Entrega`, `5 - Correios Ff`, `6 - Customizado`, `7 - Jadlog`, `8 - Totalexpress`, `9 - Olist`, `10 - Gateway`, `11 - Magalu Entregas`, `12 - Shopee Envios`, `13 - Ns Entregas`, `14 - Viavarejo Envvias`, `15 - Madeira Envios`, `16 - Ali Envios`, `17 - Loggi`, `18 - Conecta La Etiquetas`, `19 - Amazon Dba`, `20 - Magalu Fulfillment`, `21 - Ns Magalu Entregas`, `22 - Shein Envios`, `23 - Mandae`, `24 - Olist Envios`, `25 - Kwai Envios`, `26 - Beleza Envios`. Example: `0`.
    *   `situacao` (string): nullable. Enum: `1 - Habilitada`, `2 - Desabilitada`. Example: `1`.

#### FormaEnvioRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):

#### FormaEnvioResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `nome` (string): nullable.

#### ListagemFormasEnvioResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/FormaEnvioModel`
    *   (object with properties below)
*   **Properties:**
    *   `id` (integer):
    *   `gatewayLogistico` (`#/components/schemas/GatewayLogisticoResponseModel`):

#### ObterFormaEnvioResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/FormaEnvioModel`
    *   (object with properties below)
*   **Properties:**
    *   `id` (integer):
    *   `gatewayLogistico` (`#/components/schemas/GatewayLogisticoResponseModel`):
    *   `formasFrete` (array): nullable. Items: `#/components/schemas/FormaFreteModel`.

#### FormaFreteModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `nome` (string): nullable.
    *   `codigo` (string): nullable.
    *   `codigoExterno` (string): nullable.
    *   `tipoEntrega` (string): nullable. Enum: `0 - Nao Definida`, `1 - Normal`, `2 - Expressa`, `3 - Agendada`, `4 - Economica`, `5 - Super Expressa`, `6 - Retirada`. Example: `0`.

#### FormaFreteRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):

#### FormaFreteResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `nome` (string): nullable.

#### FormaPagamentoModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `nome` (string): nullable.
    *   `situacao` (string): nullable. Enum: `1 - Habilitada`, `2 - Desabilitada`. Example: `1`.

#### FormaPagamentoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.

#### FormaPagamentoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `nome` (string): nullable.

#### ListagemFormasPagamentoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/FormaPagamentoModel`

#### ObterFormaPagamentoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/FormaPagamentoModel`

#### FormaRecebimentoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `nome` (string): nullable.

#### GatewayLogisticoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `nome` (string): nullable.

#### IntermediadorModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `nome` (string): nullable.
    *   `cnpj` (string): nullable.
    *   `canalVenda` (string): nullable.

#### IntermediadorRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.

#### IntermediadorResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `nome` (string):
    *   `cnpj` (string):

#### ListagemIntermediadoresResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/IntermediadorModel`

#### ObterIntermediadorResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/IntermediadorModel`

#### ExcecaoListaPrecoModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `idProduto` (integer): nullable.
    *   `codigo` (string): nullable.
    *   `preco` (number): float, nullable.
    *   `precoPromocional` (number): float, nullable.

#### ListaPrecoModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `descricao` (string): nullable.
    *   `acrescimoDesconto` (number): float, nullable.

#### ListaPrecoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.

#### ListaPrecoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `nome` (string):
    *   `acrescimoDesconto` (number): float.

#### ListagemListaDePrecosModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/ListaPrecoModel`

#### ObterListaDePrecosModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/ListaPrecoModel`
    *   (object with properties below)
*   **Properties:**
    *   `excecoes` (`#/components/schemas/ExcecaoListaPrecoModel`):

#### MarcaRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.

#### MarcaResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `nome` (string): nullable.

#### AtualizarMarcadorRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/BaseMarcadorModel`

#### BaseMarcadorModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `descricao` (string): nullable.

#### CriarMarcadorRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/BaseMarcadorModel`

#### ObterMarcadorResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/BaseMarcadorModel`

#### BaseMarcaModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `descricao` (string):

#### CriarMarcaModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):

#### ListagemMarcasResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `descricao` (string):

#### MeioPagamentoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.

#### MeioPagamentoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `nome` (string): nullable.

#### NaturezaOperacaoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.

#### NaturezaOperacaoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `nome` (string): nullable.

#### AutorizarNotaFiscalModelRequest

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `enviarEmail` (boolean):

#### AutorizarNotaFiscalModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `chaveAcesso` (string):
    *   `linkAcesso` (string):
    *   `situacao` (integer): Enum: `1 - Pendente`, `2 - Emitida`, `3 - Cancelada`, `4 - Enviada Aguardando Recibo`, `5 - Rejeitada`, `6 - Autorizada`, `7 - Emitida Danfe`, `8 - Registrada`, `9 - Enviada Aguardando Protocolo`, `10 - Denegada`. Example: `1`.
    *   `xml` (string):

#### BaseNotaFiscalModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `situacao` (string): nullable. Enum: `1 - Pendente`, `2 - Emitida`, `3 - Cancelada`, `4 - Enviada Aguardando Recibo`, `5 - Rejeitada`, `6 - Autorizada`, `7 - Emitida Danfe`, `8 - Registrada`, `9 - Enviada Aguardando Protocolo`, `10 - Denegada`. Example: `1`.
    *   `tipo` (string): nullable. Enum: `E - Entrada`, `S - Saida`. Example: `E`.
    *   `numero` (string): nullable.
    *   `serie` (string): nullable.
    *   `chaveAcesso` (string): nullable.
    *   `dataEmissao` (string): nullable.
    *   `cliente` (`#/components/schemas/NotaFiscalClienteModel`):
    *   `enderecoEntrega` (`#/components/schemas/EnderecoEntregaModelResponse`):
    *   `valor` (number): float, nullable.
    *   `valorProdutos` (number): float, nullable.
    *   `valorFrete` (number): float, nullable.
    *   `vendedor` (`#/components/schemas/VendedorResponseModel`):
    *   `idFormaEnvio` (integer): nullable.
    *   `idFormaFrete` (integer): nullable.
    *   `codigoRastreamento` (string): nullable.
    *   `urlRastreamento` (string): nullable.
    *   `fretePorConta` (string): nullable.
    *   `qtdVolumes` (integer): nullable.
    *   `pesoBruto` (number): float, nullable.
    *   `pesoLiquido` (number): float, nullable.

#### IncluirXmlNotaFiscalRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `xml` (string): binary.
    *   `numeroPedido` (integer): nullable.

#### IncluirXmlNotaFiscalResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `idNota` (integer):

#### ListagemNotaFiscalModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/BaseNotaFiscalModel`
    *   (object with properties below)
*   **Properties:**
    *   `id` (integer):
    *   `ecommerce` (`#/components/schemas/EcommerceResponseModel`):

#### NotaFiscalClienteModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/BaseContatoModel`
    *   (object with properties below)
*   **Properties:**
    *   `id` (integer):

#### NotaFiscalEnderecoEntregaModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/EnderecoModel`
    *   (object with properties below)
*   **Properties:**
    *   `nomeDestinatario` (string): nullable.
    *   `cpfCnpj` (string): nullable.
    *   `tipoPessoa` (string): nullable.

#### NotaFiscalItemModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `idProduto` (integer): nullable.
    *   `codigo` (string): nullable.
    *   `descricao` (string): nullable.
    *   `unidade` (string): nullable.
    *   `quantidade` (number): float, nullable.
    *   `valorUnitario` (number): float, nullable.
    *   `valorTotal` (number): float, nullable.
    *   `cfop` (string): nullable.

#### NotaFiscalParcelaModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `dias` (integer): nullable.
    *   `data` (string): nullable.
    *   `valor` (number): float, nullable.
    *   `observacoes` (string): nullable.
    *   `idFormaPagamento` (string): nullable.
    *   `idMeioPagamento` (string): nullable.

#### ObterLinkNotaFiscalModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `link` (string):

#### ObterNotaFiscalModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/BaseNotaFiscalModel`
    *   (object with properties below)
*   **Properties:**
    *   `id` (integer):
    *   `finalidade` (string): nullable. Enum: `1 - Nfe Normal`, `2 - Nfe Complementar`, `3 - Nfe Ajuste`, `4 - Devolucao Retorno`, `7 - Nfe Cupom Referenciado`, `8 - Devolucao Retorno Sem Nfe`, `9 - Nfe Chave Acesso Referenciada`. Example: `1`.
    *   `regimeTributario` (integer): nullable. Enum: `1 - Simples Nacional`, `2 - Simples Nacional Excesso Receita`, `3 - Regime Normal`, `4 - Mei`. Example: `1`.
    *   `dataInclusao` (string): nullable.
    *   `baseIcms` (number): float, nullable.
    *   `valorIcms` (number): float, nullable.
    *   `baseIcmsSt` (number): float, nullable.
    *   `valorIcmsSt` (number): float, nullable.
    *   `valorServicos` (number): float, nullable.
    *   `valorFrete` (number): float, nullable.
    *   `valorSeguro` (number): float, nullable.
    *   `valorOutras` (number): float, nullable.
    *   `valorIpi` (number): float, nullable.
    *   `valorIssqn` (number): float, nullable.
    *   `valorDesconto` (number): float, nullable.
    *   `valorFaturado` (number): float, nullable.
    *   `idIntermediador` (integer): nullable.
    *   `idNaturezaOperacao` (integer): nullable.
    *   `idFormaPagamento` (integer): nullable.
    *   `idMeioPagamento` (integer): nullable.
    *   `observacoes` (string): nullable.
    *   `condicaoPagamento` (string): nullable.
    *   `itens` (array): Items: `#/components/schemas/NotaFiscalItemModelResponse`.
    *   `parcelas` (array): Items: `#/components/schemas/NotaFiscalParcelaModelResponse`.
    *   `ecommerce` (`#/components/schemas/EcommerceResponseModel`):

#### ObterXmlNotaFiscalModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `xmlNfe` (string):
    *   `xmlCancelamento` (string):

#### AtualizarOrdemCompraModelRequest

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/CriarAtualizarOrdemCompraModelRequest`

#### AtualizarSituacaoOrdemCompraRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `situacao` (integer): nullable. Enum: `0 - Em Aberto`, `1 - Atendido`, `2 - Cancelado`, `3 - Em Andamento`. Example: `0`.

#### CriarAtualizarOrdemCompraModelRequest

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `data` (string): nullable.
    *   `dataPrevista` (string): nullable.
    *   `desconto` (number): float, nullable.
    *   `condicao` (string): nullable.
    *   `observacoes` (string): nullable.
    *   `observacoesInternas` (string): nullable.
    *   `fretePorConta` (string): nullable. Enum: `R - Remetente`, `D - Destinatario`, `T - Terceiros`, `3 - Proprio Remetente`, `4 - Proprio Destinatario`, `S - Sem Transporte`. Example: `R`.
    *   `transportador` (string): nullable.
    *   `parcelas` (array): Items: `#/components/schemas/OrdemCompraParcelaModelRequest`.

#### CriarOrdemCompraModelRequest

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Required:**
    *   `itens`
*   **All Of:**
    *   `#/components/schemas/CriarAtualizarOrdemCompraModelRequest`
    *   (object with properties below)
*   **Properties:**
    *   `contato` (`#/components/schemas/ContatoRequestModel`):
    *   `categoria` (`#/components/schemas/CategoriaRequestModel`):
    *   `frete` (number): float, nullable.
    *   `itens` (array): Items: `#/components/schemas/OrdemCompraItemModelRequest`.

#### CriarOrdemCompraModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `numeroPedido` (string):
    *   `data` (string):
    *   `situacao` (string): nullable. Enum: `0 - Em Aberto`, `1 - Atendido`, `2 - Cancelado`, `3 - Em Andamento`. Example: `0`.

#### LancarEstoqueOrdemCompraRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `deposito` (`#/components/schemas/DepositoRequestModel`):

#### ListarOrdemCompraModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `numero` (string): nullable.
    *   `data` (string):
    *   `situacao` (string): nullable. Enum: `0 - Em Aberto`, `1 - Atendido`, `2 - Cancelado`, `3 - Em Andamento`. Example: `0`.
    *   `desconto` (string):
    *   `frete` (number): float.
    *   `totalProdutos` (number): float.
    *   `totalPedidoCompra` (number): float.
    *   `dataPrevista` (string):
    *   `contato` (`#/components/schemas/ContatoModelResponse`):
    *   `categoria` (`#/components/schemas/CategoriaResponseModel`):
    *   `notaFiscal` (`#/components/schemas/OrdemCompraNotaFiscalModelResponse`):
    *   `fretePorConta` (string): nullable. Enum: `R - Remetente`, `D - Destinatario`, `T - Terceiros`, `3 - Proprio Remetente`, `4 - Proprio Destinatario`, `S - Sem Transporte`. Example: `R`.
    *   `observacoes` (string):
    *   `observacoesInternas` (string): nullable.

#### ObterOrdemCompraModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `numeroPedido` (string): nullable.
    *   `data` (string):
    *   `situacao` (string): nullable. Enum: `0 - Em Aberto`, `1 - Atendido`, `2 - Cancelado`, `3 - Em Andamento`. Example: `0`.
    *   `desconto` (string):
    *   `frete` (number): float.
    *   `totalProdutos` (number): float.
    *   `totalPedidoCompra` (number): float.
    *   `dataPrevista` (string):
    *   `itens` (array): Items: `#/components/schemas/OrdemCompraItemModelResponse`.
    *   `contato` (`#/components/schemas/ContatoModelResponse`):
    *   `categoria` (`#/components/schemas/CategoriaResponseModel`):
    *   `notaFiscal` (`#/components/schemas/OrdemCompraNotaFiscalModelResponse`):
    *   `parcelas` (array): Items: `#/components/schemas/OrdemCompraParcelaModelResponse`.
    *   `fretePorConta` (string): nullable. Enum: `R - Remetente`, `D - Destinatario`, `T - Terceiros`, `3 - Proprio Remetente`, `4 - Proprio Destinatario`, `S - Sem Transporte`. Example: `R`.
    *   `observacoes` (string):
    *   `observacoesInternas` (string): nullable.
    *   `pvFrete` (number): float.

#### OrdemCompraItemModelRequest

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/ProdutoRequestModel`
    *   (object with properties below)
*   **Properties:**
    *   `produto` (`#/components/schemas/ProdutoRequestModel`):
    *   `quantidade` (number): float, nullable.
    *   `valor` (number): float, nullable.
    *   `informacoesAdicionais` (string): nullable.
    *   `aliquotaIPI` (number): float, nullable.
    *   `valorICMS` (number): float, nullable.

#### OrdemCompraItemModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `produto` (`#/components/schemas/ProdutoResponseModel`):
    *   `gtin` (string): nullable.
    *   `quantidade` (number): float.
    *   `preco` (number): float.
    *   `ipi` (number): float.

#### OrdemCompraNotaFiscalModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `numero` (string):
    *   `dataEmissao` (string):
    *   `valor` (string):
    *   `natureza` (string):

#### OrdemCompraParcelaModelRequest

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `dias` (integer):
    *   `dataVencimento` (string):
    *   `valor` (number): float.
    *   `contaContabil` (`#/components/schemas/ContaContabilModel`):
    *   `meioPagamento` (string): nullable. Enum: `1 - Dinheiro`, `2 - Cheque`, `3 - Cartao Credito`, `4 - Cartao Debito`, `5 - Credito Loja`, `10 - Vale Alimentacao`, `11 - Vale Refeicao`, `12 - Vale Presente`, `13 - Vale Combustivel`, `14 - Duplicata Mercantil`, `15 - Boleto`, `16 - Deposito Bancario`, `17 - Pix`, `18 - Transferencia Bancaria Carteira Digital`, `19 - Fidelidade Cashback Credito Virtual`, `90 - Sem Pagamento`, `99 - Outros`. Example: `1`.
    *   `observacoes` (string):

#### OrdemCompraParcelaModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `numero` (integer):
    *   `dias` (integer):
    *   `dataVencimento` (string):
    *   `valor` (number): float.
    *   `contaContabil` (`#/components/schemas/ContaContabilModel`):
    *   `meioPagamento` (string): nullable. Enum: `1 - Dinheiro`, `2 - Cheque`, `3 - Cartao Credito`, `4 - Cartao Debito`, `5 - Credito Loja`, `10 - Vale Alimentacao`, `11 - Vale Refeicao`, `12 - Vale Presente`, `13 - Vale Combustivel`, `14 - Duplicata Mercantil`, `15 - Boleto`, `16 - Deposito Bancario`, `17 - Pix`, `18 - Transferencia Bancaria Carteira Digital`, `19 - Fidelidade Cashback Credito Virtual`, `90 - Sem Pagamento`, `99 - Outros`. Example: `1`.
    *   `observacoes` (string):

#### AnexoOrdemServicoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `url` (string): nullable.

#### AtualizarOrdemServicoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/OrdemServicoRequestModel`
    *   (object with properties below)
*   **Properties:**
    *   `cliente` (`#/components/schemas/ContatoRequestModel`):

#### AtualizarSituacaoOrdemServicoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `situacao` (integer): nullable. Enum: `4 - Nao Aprovada`, `3 - Finalizada`, `0 - Em Aberto`, `2 - Serv Concluido`, `1 - Orcada`, `5 - Aprovada`, `6 - Em Andamento`, `7 - Cancelada`. Example: `4`.

#### CriarOrdemServicoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/OrdemServicoRequestModel`
    *   (object with properties below)
*   **Properties:**
    *   `cliente` (`#/components/schemas/ContatoRequestModel`):

#### CriarOrdemServicoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `numero` (integer):

#### GerarNotaFiscalOrdemServicoModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `numero` (integer):
    *   `serie` (integer):

#### ItemOrdemServicoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `servico` (`#/components/schemas/ServicoRequestModel`):
    *   `quantidade` (number): float, nullable.
    *   `valorUnitario` (number): float, nullable.
    *   `porcentagemDesconto` (number): float, nullable.
    *   `orcar` (any):

#### LancarEstoqueOrdemServicoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `deposito` (`#/components/schemas/DepositoRequestModel`):

#### ListagemOrdemServicoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `situacao` (string): nullable. Enum: `4 - Nao Aprovada`, `3 - Finalizada`, `0 - Em Aberto`, `2 - Serv Concluido`, `1 - Orcada`, `5 - Aprovada`, `6 - Em Andamento`, `7 - Cancelada`. Example: `4`.
    *   `data` (string): nullable.
    *   `dataPrevista` (string): nullable.
    *   `valor` (number): float, nullable.
    *   `numeroOrdemServico` (string): nullable.
    *   `cliente` (`#/components/schemas/ContatoModelResponse`):
    *   `marcadores` (any):

#### ObterOrdemServicoModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `situacao` (string): nullable. Enum: `4 - Nao Aprovada`, `3 - Finalizada`, `0 - Em Aberto`, `2 - Serv Concluido`, `1 - Orcada`, `5 - Aprovada`, `6 - Em Andamento`, `7 - Cancelada`. Example: `4`.
    *   `data` (string):
    *   `dataPrevista` (string):
    *   `totalServicos` (string):
    *   `totalOrdemServico` (string):
    *   `totalPecas` (string):
    *   `numeroOrdemServico` (string):
    *   `equipamento` (string):
    *   `equipamentoSerie` (string):
    *   `descricaoProblema` (string):
    *   `observacoes` (string):
    *   `orcar` (string):
    *   `orcado` (string):
    *   `observacoesServico` (string):
    *   `observacoesInternas` (string):
    *   `alqComissao` (number): float.
    *   `vlrComissao` (integer):
    *   `idForma` (integer):
    *   `idContaContabil` (integer):
    *   `desconto` (string):
    *   `idListaPreco` (integer):
    *   `idLocalPrestacao` (string): nullable.
    *   `idDeposito` (integer):
    *   `dataConclusao` (string):
    *   `vendedor` (`#/components/schemas/ContatoModelResponse`):
    *   `contato` (`#/components/schemas/ContatoModelResponse`):
    *   `tecnico` (string):
    *   `categoria` (`#/components/schemas/CategoriaReceitaDespesaResponseModel`):
    *   `formaPagamento` (`#/components/schemas/FormaPagamentoResponseModel`):

#### OrdemServicoAssistenciaTecnicaRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `equipamento` (string): nullable.
    *   `numeroSerieEquipamento` (string): nullable.
    *   `pecas` (array): nullable. Items: `#/components/schemas/PecaOrdemServicoRequestModel`.

#### OrdemServicoPagamentoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/PagamentoRequestModel`
    *   (object with properties below)
*   **Properties:**
    *   `categoria` (`#/components/schemas/CategoriaRequestModel`):

#### OrdemServicoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `listaPreco` (`#/components/schemas/ListaPrecoRequestModel`):
    *   `descricao` (string): nullable.
    *   `consideracaoFinal` (string): nullable.
    *   `dataInicio` (string): nullable.
    *   `dataPrevista` (string): nullable.
    *   `dataConclusao` (string): nullable.
    *   `valorDesconto` (number): float, nullable.
    *   `observacao` (string): nullable.
    *   `observacaoInterna` (string): nullable.
    *   `servicos` (array): nullable. Items: `#/components/schemas/ItemOrdemServicoRequestModel`.
    *   `vendedor` (`#/components/schemas/VendedorOrdemServicoRequestModel`):
    *   `tecnico` (string): nullable.
    *   `marcadores` (array): nullable. Items: `#/components/schemas/CriarMarcadorRequestModel`.
    *   `anexos` (array): nullable. Items: `#/components/schemas/AnexoOrdemServicoRequestModel`.
    *   `pagamento` (`#/components/schemas/OrdemServicoPagamentoRequestModel`):
    *   `assistenciaTecnica` (`#/components/schemas/OrdemServicoAssistenciaTecnicaRequestModel`):

#### PecaOrdemServicoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `produto` (`#/components/schemas/ProdutoRequestModel`):
    *   `quantidade` (number): float, nullable.
    *   `valorUnitario` (number): float, nullable.
    *   `unidade` (string): nullable.
    *   `porcentagemDesconto` (number): float, nullable.

#### VendedorOrdemServicoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/VendedorRequestModel`
    *   (object with properties below)
*   **Properties:**
    *   `porcentagemComissao` (number): float, nullable.

#### PagamentoParcelasRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `parcelas` (array): nullable. Items: `#/components/schemas/ParcelaModelRequest`.

#### PagamentoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `formaPagamento` (`#/components/schemas/FormaPagamentoRequestModel`):
    *   `meioPagamento` (`#/components/schemas/MeioPagamentoRequestModel`):
    *   `parcelas` (array): nullable. Items: `#/components/schemas/ParcelaModelRequest`.

#### PagamentoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `formaPagamento` (`#/components/schemas/FormaPagamentoResponseModel`):
    *   `meioPagamento` (`#/components/schemas/MeioPagamentoResponseModel`):
    *   `condicaoPagamento` (string): nullable.
    *   `parcelas` (array): nullable. Items: `#/components/schemas/ParcelaModelResponse`.

#### ParcelaModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `dias` (integer): nullable.
    *   `data` (string): nullable.
    *   `valor` (number): float, nullable.
    *   `observacoes` (string): nullable.

#### ParcelaModelRequest

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/ParcelaModel`
    *   (object with properties below)
*   **Properties:**
    *   `formaPagamento` (`#/components/schemas/FormaPagamentoRequestModel`):
    *   `meioPagamento` (`#/components/schemas/MeioPagamentoRequestModel`):

#### ParcelaModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/ParcelaModel`
    *   (object with properties below)
*   **Properties:**
    *   `formaPagamento` (`#/components/schemas/FormaPagamentoResponseModel`):
    *   `meioPagamento` (`#/components/schemas/MeioPagamentoResponseModel`):

#### AtualizarInfoRastreamentoPedidoModelRequest

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `codigoRastreamento` (string): nullable.
    *   `urlRastreamento` (string): nullable.
    *   `formaEnvio` (`#/components/schemas/FormaEnvioRequestModel`):
    *   `formaFrete` (`#/components/schemas/FormaFreteRequestModel`):
    *   `fretePagoEmpresa` (number): float, nullable.
    *   `dataPrevista` (string): nullable.
    *   `idContatoTransportadora` (integer): nullable.
    *   `volumes` (integer): nullable.
    *   `pesoBruto` (number): float, nullable.
    *   `pesoLiquido` (number): float, nullable.
    *   `observacoes` (string): nullable.

#### AtualizarPedidoModelRequest

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/BasePedidoModel`
    *   (object with properties below)
*   **Properties:**
    *   `pagamento` (`#/components/schemas/PagamentoParcelasRequestModel`):

#### AtualizarSituacaoPedidoModelRequest

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `situacao` (integer): nullable. Enum: `8 - Dados Incompletos`, `0 - Aberta`, `3 - Aprovada`, `4 - Preparando Envio`, `1 - Faturada`, `7 - Pronto Envio`, `5 - Enviada`, `6 - Entregue`, `2 - Cancelada`, `9 - Nao Entregue`. Example: `8`.

#### BasePedidoModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `dataPrevista` (string): nullable.
    *   `dataEnvio` (string): nullable.
    *   `observacoes` (string): nullable.
    *   `observacoesInternas` (string): nullable.

#### ContatoPedidoModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `codigo` (string): nullable.
    *   `nome` (string): nullable.
    *   `fantasia` (string): nullable.
    *   `tipoPessoa` (string): nullable.
    *   `cnpj` (string): nullable.
    *   `inscricaoEstadual` (string): nullable.
    *   `rg` (string): nullable.
    *   `endereco` (`#/components/schemas/EnderecoContatoPedidoModel`):
    *   `fone` (string): nullable.
    *   `email` (string): nullable.

#### ContatoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.

#### CriarPedidoModelRequest

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Required:**
    *   `idContato`
    *   `itens`
*   **All Of:**
    *   `#/components/schemas/PedidoModel`
    *   (object with properties below)
*   **Properties:**
    *   `idContato` (integer):
    *   `listaPreco` (`#/components/schemas/ListaPrecoRequestModel`):
    *   `naturezaOperacao` (`#/components/schemas/NaturezaOperacaoRequestModel`):
    *   `vendedor` (`#/components/schemas/VendedorRequestModel`):
    *   `enderecoEntrega` (`#/components/schemas/EnderecoEntregaPedidoModelRequest`):
    *   `ecommerce` (`#/components/schemas/EcommerceRequestModel`):
    *   `transportador` (`#/components/schemas/TransportadorRequestModel`):
    *   `intermediador` (`#/components/schemas/IntermediadorRequestModel`):
    *   `deposito` (`#/components/schemas/DepositoRequestModel`):
    *   `pagamento` (`#/components/schemas/PagamentoRequestModel`):
    *   `itens` (array): Items: `#/components/schemas/ItemPedidoRequestModel`.

#### CriarPedidoModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `numeroPedido` (string):

#### EnderecoContatoPedidoModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `endereco` (string): nullable.
    *   `enderecoNro` (string): nullable.
    *   `complemento` (string): nullable.
    *   `bairro` (string): nullable.
    *   `cidade` (string): nullable.
    *   `cep` (string): nullable.
    *   `uf` (string): nullable.
    *   `fone` (string): nullable.
    *   `nomeDestinatario` (string): nullable.
    *   `cpfCnpj` (string): nullable.
    *   `tipoPessoa` (string): nullable.
    *   `ie` (string): nullable.

#### EnderecoEntregaPedidoModelRequest

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/EnderecoEntregaPedidoModel`

#### GerarNotaFiscalPedidoModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `numero` (integer):
    *   `serie` (integer):

#### ItemPedidoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `produto` (`#/components/schemas/ProdutoRequestModel`):
    *   `quantidade` (number): float, nullable.
    *   `valorUnitario` (number): float, nullable.
    *   `infoAdicional` (string): nullable.

#### ItemPedidoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `produto` (`#/components/schemas/ProdutoResponseModel`):
    *   `quantidade` (number): float.
    *   `valorUnitario` (number): float.
    *   `infoAdicional` (string):

#### ListagemPedidoModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `situacao` (integer): nullable.
    *   `numeroPedido` (integer): nullable.
    *   `ecommerce` (`#/components/schemas/EcommerceResponseModel`):
    *   `dataCriacao` (string): nullable.
    *   `dataPrevista` (string): nullable.
    *   `cliente` (`#/components/schemas/PedidoClienteModel`):
    *   `valor` (string): nullable.
    *   `vendedor` (`#/components/schemas/VendedorResponseModel`):
    *   `transportador` (`#/components/schemas/TransportadorResponseModel`):

#### ObterPedidoModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/PedidoModel`
    *   (object with properties below)
*   **Properties:**
    *   `id` (integer): nullable.
    *   `numeroPedido` (integer): nullable.
    *   `idNotaFiscal` (integer): nullable.
    *   `dataFaturamento` (string): nullable.
    *   `valorTotalProdutos` (number): float, nullable.
    *   `valorTotalPedido` (number): float, nullable.
    *   `listaPreco` (`#/components/schemas/ListaPrecoResponseModel`):
    *   `cliente` (`#/components/schemas/PedidoClienteModel`):
    *   `enderecoEntrega` (`#/components/schemas/EnderecoEntregaModelResponse`):
    *   `ecommerce` (`#/components/schemas/EcommerceResponseModel`):
    *   `transportador` (`#/components/schemas/TransportadorResponseModel`):
    *   `deposito` (`#/components/schemas/DepositoResponseModel`):
    *   `vendedor` (`#/components/schemas/VendedorResponseModel`):
    *   `naturezaOperacao` (`#/components/schemas/NaturezaOperacaoResponseModel`):
    *   `intermediador` (`#/components/schemas/IntermediadorResponseModel`):
    *   `pagamento` (`#/components/schemas/PagamentoResponseModel`):
    *   `itens` (array): nullable. Items: `#/components/schemas/ItemPedidoResponseModel`.

#### PedidoClienteModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/BaseContatoModel`
    *   (object with properties below)
*   **Properties:**
    *   `id` (integer):

#### PedidoModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/BasePedidoModel`
    *   (object with properties below)
*   **Properties:**
    *   `situacao` (integer): nullable. Enum: `8 - Dados Incompletos`, `0 - Aberta`, `3 - Aprovada`, `4 - Preparando Envio`, `1 - Faturada`, `7 - Pronto Envio`, `5 - Enviada`, `6 - Entregue`, `2 - Cancelada`, `9 - Nao Entregue`. Example: `8`.
    *   `data` (string): nullable.
    *   `dataEntrega` (string): nullable.
    *   `numeroOrdemCompra` (string): nullable.
    *   `valorDesconto` (number): float, nullable.
    *   `valorFrete` (number): float, nullable.
    *   `valorOutrasDespesas` (number): float, nullable.

#### AtualizarPrecoProdutoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `preco` (number): float, nullable.
    *   `precoPromocional` (number): float, nullable.

#### AtualizarPrecoProdutoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `preco` (number): float, nullable.
    *   `precoPromocional` (number): float, nullable.

#### AtualizarProdutoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/ProdutoModel`
    *   (object with properties below)
*   **Properties:**
    *   `descricao` (string): nullable.
    *   `estoque` (`#/components/schemas/EstoqueProdutoRequestModel`):

#### AtualizarProdutoVariacaoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/ProdutoModel`
    *   (object with properties below)
*   **Properties:**
    *   `estoque` (oneOf): nullable. OneOf: `#/components/schemas/EstoqueProdutoRequestModel`.

#### CriarProdutoComVariacoesResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/CriarProdutoResponseModel`
    *   (object with properties below)
*   **Properties:**
    *   `variacoes` (array): Items: `#/components/schemas/CriarProdutoResponseModel`.

#### CriarProdutoEstoqueRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/EstoqueProdutoRequestModel`
    *   (object with properties below)
*   **Properties:**
    *   `inicial` (number): float, nullable.

#### CriarProdutoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Required:**
    *   `tipo`
    *   `descricao`
*   **All Of:**
    *   `#/components/schemas/ProdutoModel`
    *   (object with properties below)
*   **Properties:**
    *   `descricao` (string): nullable.
    *   `tipo` (string): nullable. Enum: `K - Kit`, `S - Simples`, `V - Com Variacoes`, `F - Fabricado`, `M - Materia Prima`. Example: `K`.
    *   `estoque` (`#/components/schemas/CriarProdutoEstoqueRequestModel`):
    *   `seo` (`#/components/schemas/SeoProdutoRequestModel`):
    *   `anexos` (array): Items: `#/components/schemas/AnexoRequestModel`.
    *   `grade` (array): Items: string.
    *   `producao` (`#/components/schemas/ProducaoProdutoRequestModel`):
    *   `kit` (array): Items: `#/components/schemas/ProdutoKitRequestModel`.
    *   `variacoes` (array): Items: `#/components/schemas/VariacaoProdutoRequestModel`.

#### CriarProdutoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `codigo` (string):
    *   `descricao` (string):

#### DimensoesProdutoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `embalagem` (`#/components/schemas/EmbalagemRequestModel`):
    *   `largura` (number): float, nullable.
    *   `altura` (number): float, nullable.
    *   `comprimento` (number): float, nullable.
    *   `diametro` (number): float, nullable.
    *   `pesoLiquido` (number): float, nullable.
    *   `pesoBruto` (number): float, nullable.

#### DimensoesProdutoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `embalagem` (`#/components/schemas/EmbalagemResponseModel`):
    *   `largura` (number): float, nullable.
    *   `altura` (number): float, nullable.
    *   `comprimento` (number): float, nullable.
    *   `diametro` (number): float, nullable.
    *   `pesoLiquido` (number): float, nullable.
    *   `pesoBruto` (number): float, nullable.
    *   `quantidadeVolumes` (integer): nullable.

#### EstoqueProdutoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `controlar` (boolean):
    *   `sobEncomenda` (boolean):
    *   `minimo` (number): float, nullable.
    *   `maximo` (number): float, nullable.
    *   `diasPreparacao` (integer): nullable.
    *   `localizacao` (string): nullable.

#### EstoqueProdutoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `controlar` (boolean): nullable.
    *   `sobEncomenda` (boolean): nullable.
    *   `diasPreparacao` (integer): nullable.
    *   `localizacao` (string): nullable.
    *   `minimo` (number): float, nullable.
    *   `maximo` (number): float, nullable.
    *   `quantidade` (number): float, nullable.

#### EstoqueVariacaoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `inicial` (number): float, nullable.

#### FornecedorProdutoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `codigoProdutoNoFornecedor` (string): nullable.
    *   `padrao` (boolean):

#### FornecedorProdutoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `nome` (string): nullable.
    *   `codigoProdutoNoFornecedor` (string): nullable.

#### GradeVariacaoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `chave` (string): nullable.
    *   `valor` (string): nullable.

#### GradeVariacaoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `chave` (string): nullable.
    *   `valor` (string): nullable.

#### ListagemProdutoCustosResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `data` (string): nullable.
    *   `saldoAtual` (number): float, nullable.
    *   `saldoAnterior` (number): float, nullable.
    *   `precoCusto` (number): float, nullable.
    *   `custoMedio` (number): float, nullable.
    *   `precoVenda` (number): float, nullable.
    *   `impostosRecuperaveis` (number): float, nullable.

#### ListagemProdutosResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `sku` (string):
    *   `descricao` (string):
    *   `tipo` (string): Enum: `K - Kit`, `S - Simples`, `V - Com Variacoes`, `F - Fabricado`, `M - Materia Prima`. Example: `K`.
    *   `situacao` (string): Enum: `A - Ativo`, `I - Inativo`, `E - Excluido`. Example: `A`.
    *   `dataCriacao` (string): nullable.
    *   `dataAlteracao` (string): nullable.
    *   `unidade` (string):
    *   `gtin` (string):
    *   `precos` (`#/components/schemas/PrecoProdutoResponseModel`):

#### MarcaProdutoModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `nome` (string): nullable.

#### MedicamentoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `codigoAnvisa` (string): nullable.
    *   `valorMaximo` (number): float, nullable.
    *   `motivoIsenscao` (string): nullable.

#### ObterProdutoModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/ProdutoResponseModel`
    *   (object with properties below)
*   **Properties:**
    *   `descricaoComplementar` (string): nullable.
    *   `tipo` (string): nullable. Enum: `K - Kit`, `S - Simples`, `V - Com Variacoes`, `F - Fabricado`, `M - Materia Prima`. Example: `K`.
    *   `situacao` (string): nullable. Enum: `A - Ativo`, `I - Inativo`, `E - Excluido`. Example: `A`.
    *   `produtoPai` (`#/components/schemas/ProdutoResponseModel`):
    *   `unidade` (string): nullable.
    *   `unidadePorCaixa` (string): nullable.
    *   `ncm` (string): nullable.
    *   `gtin` (string): nullable.
    *   `origem` (string): Enum: `0 - Nacional Exceto Codigo 3 A 5`, `4 - Nacional Producao Conforme Ajustes`, `5 - Nacional Conteudo Importacao Inferior 40`, `3 - Nacional Conteudo Importacao Superior 40`, `8 - Nacional Conteudo Importacao Superior 70`, `1 - Estrangeira Importacao Direta Exceto Codigo 6`, `6 - Estrangeira Importacao Direta Sem Similar`, `2 - Estrangeira Adquirida Mercado Interno`, `7 - Estrangeira Adquirida Mercado Interno Sem Similar`. Example: `0`.
    *   `garantia` (string): nullable.
    *   `observacoes` (string): nullable.
    *   `categoria` (`#/components/schemas/CategoriaResponseModel`):
    *   `marca` (`#/components/schemas/MarcaResponseModel`):
    *   `dimensoes` (`#/components/schemas/DimensoesProdutoResponseModel`):
    *   `precos` (`#/components/schemas/PrecoProdutoResponseModel`):
    *   `estoque` (`#/components/schemas/EstoqueProdutoResponseModel`):
    *   `fornecedores` (array): nullable. Items: `#/components/schemas/FornecedorProdutoResponseModel`.
    *   `seo` (`#/components/schemas/SeoProdutoModelResponse`):
    *   `tributacao` (`#/components/schemas/TributacaoProdutoResponseModel`):
    *   `anexos` (array): Items: `#/components/schemas/AnexoResponseModel`.
    *   `variacoes` (array): Items: `#/components/schemas/VariacaoProdutoResponseModel`.
    *   `kit` (array): Items: `#/components/schemas/ProdutoKitResponseModel`.
    *   `producao` (`#/components/schemas/ProducaoProdutoResponseModel`):

#### ObterTagsProdutoModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `codigo` (string): nullable.
    *   `nome` (string): nullable.
    *   `tags` (array): nullable. Items: `#/components/schemas/TagProdutoModelResponse`.

#### PrecoProdutoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `preco` (number): float, nullable.
    *   `precoPromocional` (number): float, nullable.
    *   `precoCusto` (number): float, nullable.

#### PrecoProdutoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `preco` (number): float, nullable.
    *   `precoPromocional` (number): float, nullable.
    *   `precoCusto` (number): float, nullable.
    *   `precoCustoMedio` (number): float, nullable.

#### PrecoVariacaoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `preco` (number): float, nullable.
    *   `precoPromocional` (number): float, nullable.

#### ProducaoProdutoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `produtos` (array): Items: `#/components/schemas/ProdutoFabricadoRequestModel`.
    *   `etapas` (array): Items: string.

#### ProducaoProdutoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `produtos` (array): Items: `#/components/schemas/ProdutoFabricadoResponseModel`.
    *   `etapas` (array): Items: string.

#### ProdutoFabricadoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `produto` (`#/components/schemas/ProdutoRequestModel`):
    *   `quantidade` (number): float, nullable.

#### ProdutoFabricadoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `produto` (`#/components/schemas/ProdutoResponseModel`):
    *   `quantidade` (number): float.

#### ProdutoKitRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `produto` (`#/components/schemas/ProdutoRequestModel`):
    *   `quantidade` (number): float, nullable.

#### ProdutoKitResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `produto` (`#/components/schemas/ProdutoResponseModel`):
    *   `quantidade` (number): float.

#### ProdutoModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Required:**
    *   `sku`
*   **Properties:**
    *   `sku` (string): nullable.
    *   `descricaoComplementar` (string): nullable.
    *   `unidade` (string): nullable.
    *   `unidadePorCaixa` (string): nullable.
    *   `ncm` (string): nullable.
    *   `gtin` (string): nullable.
    *   `origem` (integer): nullable.
    *   `codigoEspecificadorSubstituicaoTributaria` (string): nullable.
    *   `garantia` (string): nullable.
    *   `observacoes` (string): nullable.
    *   `marca` (`#/components/schemas/MarcaRequestModel`):
    *   `categoria` (`#/components/schemas/CategoriaRequestModel`):
    *   `precos` (`#/components/schemas/PrecoProdutoRequestModel`):
    *   `dimensoes` (`#/components/schemas/DimensoesProdutoRequestModel`):
    *   `tributacao` (`#/components/schemas/TributacaoProdutoRequestModel`):
    *   `seo` (`#/components/schemas/SeoProdutoRequestModel`):
    *   `fornecedores` (array): Items: `#/components/schemas/FornecedorProdutoRequestModel`.

#### ProdutoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.

#### ProdutoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `sku` (string): nullable.
    *   `descricao` (string): nullable.

#### SeoProdutoModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `titulo` (string): nullable.
    *   `descricao` (string): nullable.
    *   `keywords` (array): nullable. Items: string.
    *   `linkVideo` (string): nullable.
    *   `slug` (string): nullable.

#### SeoProdutoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `titulo` (string): nullable.
    *   `descricao` (string): nullable.
    *   `keywords` (array): Items: string.
    *   `linkVideo` (string): nullable.
    *   `slug` (string): nullable.

#### TagProdutoModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `nome` (string): nullable.

#### TributacaoProdutoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `gtinEmbalagem` (string): nullable.
    *   `valorIPIFixo` (number): float, nullable.
    *   `classeIPI` (string): nullable.

#### TributacaoProdutoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `gtinEmbalagem` (string): nullable.
    *   `valorIPIFixo` (number): float, nullable.
    *   `classeIPI` (string): nullable.

#### VariacaoProdutoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `sku` (string): nullable.
    *   `gtin` (string): nullable.
    *   `precos` (`#/components/schemas/PrecoVariacaoRequestModel`):
    *   `estoque` (`#/components/schemas/EstoqueVariacaoRequestModel`):
    *   `grade` (array): nullable. Items: `#/components/schemas/GradeVariacaoRequestModel`.

#### VariacaoProdutoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `descricao` (string): nullable.
    *   `sku` (string): nullable.
    *   `gtin` (string): nullable.
    *   `precos` (`#/components/schemas/PrecoProdutoResponseModel`):
    *   `estoque` (`#/components/schemas/EstoqueProdutoResponseModel`):
    *   `grade` (array): nullable. Items: `#/components/schemas/GradeVariacaoRequestModel`.

#### AlterarSituacaoSeparacaoModelRequest

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `situacao` (integer): nullable. Enum: `1 - Sit Aguardando Separacao`, `2 - Sit Separada`, `3 - Sit Embalada`, `4 - Sit Em Separacao`. Example: `1`.

#### ItemSeparacaoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `produto` (`#/components/schemas/ProdutoResponseModel`):
    *   `quantidade` (number): float.
    *   `unidade` (string):
    *   `localizacao` (string):
    *   `infoAdicional` (string):

#### ListagemSeparacaoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `situacao` (string): Enum: `1 - Sit Aguardando Separacao`, `2 - Sit Separada`, `3 - Sit Embalada`, `4 - Sit Em Separacao`. Example: `1`.
    *   `dataCriacao` (string): nullable.
    *   `dataSeparacao` (string): nullable.
    *   `dataCheckout` (string): nullable.
    *   `cliente` (`#/components/schemas/ContatoModelResponse`):
    *   `venda` (`#/components/schemas/SeparacaoVendaResponseModel`):
    *   `notaFiscal` (`#/components/schemas/SeparacaoNotaResponseModel`):
    *   `ecommerce` (`#/components/schemas/EcommerceResponseModel`):
    *   `formaEnvio` (`#/components/schemas/FormaEnvioResponseModel`):

#### ObterSeparacaoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `situacao` (integer): nullable. Enum: `1 - Sit Aguardando Separacao`, `2 - Sit Separada`, `3 - Sit Embalada`, `4 - Sit Em Separacao`. Example: `1`.
    *   `situacaoCheckout` (integer): nullable. Enum: `1 - Sit Checkout Disponivel`, `2 - Sit Checkout Bloqueado`. Example: `1`.
    *   `dataCriacao` (string): nullable.
    *   `dataSeparacao` (string): nullable.
    *   `dataCheckout` (string): nullable.
    *   `cliente` (`#/components/schemas/ContatoModelResponse`):
    *   `venda` (`#/components/schemas/SeparacaoVendaResponseModel`):
    *   `notaFiscal` (`#/components/schemas/SeparacaoNotaResponseModel`):
    *   `itens` (array): nullable. Items: `#/components/schemas/ItemSeparacaoResponseModel`.
    *   `ecommerce` (`#/components/schemas/EcommerceResponseModel`):
    *   `formaEnvio` (`#/components/schemas/FormaEnvioResponseModel`):
    *   `volumes` (string): nullable.

#### SeparacaoNotaResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `numero` (integer): nullable.
    *   `dataEmissao` (string): nullable.
    *   `situacao` (integer): nullable. Enum: `1 - Pendente`, `2 - Emitida`, `3 - Cancelada`, `4 - Enviada Aguardando Recibo`, `5 - Rejeitada`, `6 - Autorizada`, `7 - Emitida Danfe`, `8 - Registrada`, `9 - Enviada Aguardando Protocolo`, `10 - Denegada`. Example: `1`.

#### SeparacaoVendaResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `numero` (integer): nullable.
    *   `data` (string): nullable.
    *   `situacao` (integer): nullable. Enum: `8 - Dados Incompletos`, `0 - Aberta`, `3 - Aprovada`, `4 - Preparando Envio`, `1 - Faturada`, `7 - Pronto Envio`, `5 - Enviada`, `6 - Entregue`, `2 - Cancelada`, `9 - Nao Entregue`. Example: `8`.

#### AtualizarServicoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/BaseServicoRequestModel`
    *   (object with properties below)
*   **Properties:**
    *   `nome` (string): nullable.

#### BaseServicoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `codigo` (string): nullable.
    *   `preco` (number): float, nullable.
    *   `unidade` (string): nullable.
    *   `situacao` (string): nullable. Enum: `A - Ativo`, `I - Inativo`, `E - Excluido`. Example: `A`.
    *   `tipoItemSped` (string): nullable. Enum: `00 - Mercadoria Para Revenda`, `01 - Materia Prima`, `02 - Embalagem`, `03 - Produto Em Processo`, `04 - Produto Acabado`, `05 - Subproduto`, `06 - Produto Intermediario`, `07 - Material Uso Consumo`, `08 - Ativo Imobilizado`, `09 - Servicos`, `10 - Outros Insumos`, `99 - Outras`. Example: `00`.
    *   `codigoListaServicos` (string): nullable.
    *   `nbs` (string): nullable.
    *   `descricaoComplementar` (string): nullable.
    *   `observacoes` (string): nullable.

#### CriarServicoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **All Of:**
    *   `#/components/schemas/BaseServicoRequestModel`
    *   (object with properties below)
*   **Properties:**
    *   `nome` (string): nullable.

#### ServicoRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.

#### ServicoResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `codigo` (string):
    *   `descricao` (string):

#### ServicosModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `nome` (string): nullable.
    *   `codigo` (string): nullable.
    *   `preco` (number): float, nullable.
    *   `situacao` (string): nullable.
    *   `descricaoComplementar` (string): nullable.
    *   `observacoes` (string): nullable.
    *   `unidade` (string): nullable.
    *   `tipoItemSped` (string): nullable.
    *   `nbs` (string): nullable.
    *   `codigoListaServicos` (string): nullable.

#### TransportadorRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `fretePorConta` (string): nullable. Enum: `R - Remetente`, `D - Destinatario`, `T - Terceiros`, `3 - Proprio Remetente`, `4 - Proprio Destinatario`, `S - Sem Transporte`. Example: `R`.
    *   `formaEnvio` (`#/components/schemas/FormaEnvioRequestModel`):
    *   `formaFrete` (`#/components/schemas/FormaFreteRequestModel`):
    *   `codigoRastreamento` (string): nullable.
    *   `urlRastreamento` (string): nullable.

#### TransportadorResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer): nullable.
    *   `nome` (string): nullable.
    *   `fretePorConta` (string): nullable. Enum: `R - Remetente`, `D - Destinatario`, `T - Terceiros`, `3 - Proprio Remetente`, `4 - Proprio Destinatario`, `S - Sem Transporte`. Example: `R`.
    *   `formaEnvio` (`#/components/schemas/FormaEnvioResponseModel`):
    *   `formaFrete` (`#/components/schemas/FormaFreteResponseModel`):
    *   `codigoRastreamento` (string): nullable.
    *   `urlRastreamento` (string): nullable.

#### ListagemVendedoresModelResponse

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `contato` (`#/components/schemas/ContatoModelResponse`):

#### VendedorRequestModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):

#### VendedorResponseModel

*   **Title:**
*   **Description:**
*   **Type:** object
*   **Properties:**
    *   `id` (integer):
    *   `nome` (string): nullable.

### Parameters (Reusable Definitions)

*Note: These are reusable parameter definitions. Their usage is described within the specific path operations.*

#### descricaoCategoriasReceitaDespesa

*   **Name:** `descricao`
*   **In:** query
*   **Description:** Pesquisa por descrição completa da categorias de receita e despesa
*   **Required:** false
*   **Schema:**
    *   Type: string

#### grupoCategoriasReceitaDespesa

*   **Name:** `grupo`
*   **In:** query
*   **Description:** Pesquisa por grupo de categorias de receita e despesa
*   **Required:** false
*   **Schema:**
    *   Type: string

#### nomeClienteContasPagar

*   **Name:** `nomeCliente`
*   **In:** query
*   **Description:** Pesquisa por nome do cliente de contas a pagar
*   **Required:** false
*   **Schema:**
    *   Type: string

#### situacaoContasPagar

*   **Name:** `situacao`
*   **In:** query
*   **Description:** Pesquisa por situação de contas a pagar
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Enum: `aberto - Aberto`, `cancelada - Cancelada`, `pago - Pago`, `parcial - Parcial`, `prevista - Prevista`
    *   Example: `aberto`

#### dataInicialEmissaoContasPagar

*   **Name:** `dataInicialEmissao`
*   **In:** query
*   **Description:** Pesquisa por data inicial da emissão de contas a pagar
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Example: `2024-01-01`

#### dataFinalEmissaoContasPagar

*   **Name:** `dataFinalEmissao`
*   **In:** query
*   **Description:** Pesquisa por data final da emissão de contas a pagar
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Example: `2024-01-01`

#### dataInicialVencimentoContasPagar

*   **Name:** `dataInicialVencimento`
*   **In:** query
*   **Description:** Pesquisa por data inicial do vencimento de contas a pagar
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Example: `2024-01-01`

#### dataFinalVencimentoContasPagar

*   **Name:** `dataFinalVencimento`
*   **In:** query
*   **Description:** Pesquisa por data final do vencimento de contas a pagar
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Example: `2024-01-01`

#### numeroDocumentoContasPagar

*   **Name:** `numeroDocumento`
*   **In:** query
*   **Description:** Pesquisa por número do documento de contas a pagar
*   **Required:** false
*   **Schema:**
    *   Type: string

#### numeroBancoContasPagar

*   **Name:** `numeroBanco`
*   **In:** query
*   **Description:** Pesquisa por número do banco de contas a pagar
*   **Required:** false
*   **Schema:**
    *   Type: string

#### marcadoresContaPagar

*   **Name:** `marcadores`
*   **In:** query
*   **Description:** Pesquisa por marcadores
*   **Required:** false
*   **Schema:**
    *   Type: array
    *   Items:
        *   Type: string

#### idContatoContaPagar

*   **Name:** `idContato`
*   **In:** query
*   **Description:** Pesquisa por ID do contato de contas a pagar
*   **Required:** false
*   **Schema:**
    *   Type: integer
    *   Example: 123

#### nomeClienteContasReceber

*   **Name:** `nomeCliente`
*   **In:** query
*   **Description:** Pesquisa por nome do cliente de contas a receber
*   **Required:** false
*   **Schema:**
    *   Type: string

#### situacaoContasReceber

*   **Name:** `situacao`
*   **In:** query
*   **Description:** Pesquisa por situação de contas a receber
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Enum: `aberto - Aberto`, `cancelada - Cancelada`, `pago - Pago`, `parcial - Parcial`, `prevista - Prevista`
    *   Example: `aberto`

#### dataInicialEmissaoContasReceber

*   **Name:** `dataInicialEmissao`
*   **In:** query
*   **Description:** Pesquisa por data inicial da emissão de contas a receber
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Example: `2024-01-01`

#### dataFinalEmissaoContasReceber

*   **Name:** `dataFinalEmissao`
*   **In:** query
*   **Description:** Pesquisa por data final da emissão de contas a receber
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Example: `2024-01-01`

#### dataInicialVencimentoContasReceber

*   **Name:** `dataInicialVencimento`
*   **In:** query
*   **Description:** Pesquisa por data inicial do vencimento de contas a receber
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Example: `2024-01-01`

#### dataFinalVencimentoContasReceber

*   **Name:** `dataFinalVencimento`
*   **In:** query
*   **Description:** Pesquisa por data final do vencimento de contas a receber
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Example: `2024-01-01`

#### numeroDocumentoContasReceber

*   **Name:** `numeroDocumento`
*   **In:** query
*   **Description:** Pesquisa por número do documento de contas a receber
*   **Required:** false
*   **Schema:**
    *   Type: string

#### numeroBancoContasReceber

*   **Name:** `numeroBanco`
*   **In:** query
*   **Description:** Pesquisa por número do banco de contas a receber
*   **Required:** false
*   **Schema:**
    *   Type: string

#### idNotaContasReceber

*   **Name:** `idNota`
*   **In:** query
*   **Description:** Pesquisa por identificador da nota de contas a receber
*   **Required:** false
*   **Schema:**
    *   Type: int

#### idVendaContasReceber

*   **Name:** `idVenda`
*   **In:** query
*   **Description:** Pesquisa por identificador da venda de contas a receber
*   **Required:** false
*   **Schema:**
    *   Type: int

#### marcadoresContaReceber

*   **Name:** `marcadores`
*   **In:** query
*   **Description:** Pesquisa por marcadores
*   **Required:** false
*   **Schema:**
    *   Type: array
    *   Items:
        *   Type: string

#### nomeContato

*   **Name:** `nome`
*   **In:** query
*   **Description:** Pesquisa por nome parcial ou completo
*   **Required:** false
*   **Schema:**
    *   Type: string

#### codigoContato

*   **Name:** `codigo`
*   **In:** query
*   **Description:** Pesquisa por codigo completo
*   **Required:** false
*   **Schema:**
    *   Type: string

#### situacaoContato

*   **Name:** `situacao`
*   **In:** query
*   **Description:** Pesquisa por situacao
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Enum: `B - Ativo`, `A - Ativo Com Acesso Sistema`, `I - Inativo`, `E - Excluido`
    *   Example: `B`

#### idVendedorContato

*   **Name:** `idVendedor`
*   **In:** query
*   **Description:** Pesquisa por vendedor padrão
*   **Required:** false
*   **Schema:**
    *   Type: integer

#### cpfCnpjContato

*   **Name:** `cpfCnpj`
*   **In:** query
*   **Description:** Pesquisa por CPF ou CNPJ
*   **Required:** false
*   **Schema:**
    *   Type: string

#### celularContato

*   **Name:** `celular`
*   **In:** query
*   **Description:** Pesquisa pelo celular
*   **Required:** false
*   **Schema:**
    *   Type: string

#### dataCriacaoContato

*   **Name:** `dataCriacao`
*   **In:** query
*   **Description:** Pesquisa por data de criação
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Example: `2023-01-01 10:00:00`

#### dataAtualizacaoContato

*   **Name:** `dataAtualizacao`
*   **In:** query
*   **Description:** Pesquisa por data de atualização
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Example: `2023-01-01 10:00:00`

#### nomeTipoContato

*   **Name:** `nome`
*   **In:** query
*   **Description:** Pesquisa por nome parcial ou completo do tipo de contato
*   **Required:** false
*   **Schema:**
    *   Type: string

#### idFormaEnvioAgrupamento

*   **Name:** `idFormaEnvio`
*   **In:** query
*   **Description:** Pesquisa através do identificador da forma de envio
*   **Required:** false
*   **Schema:**
    *   Type: int

#### dataInicialAgrupamento

*   **Name:** `dataInicial`
*   **In:** query
*   **Description:** Pesquisa através da data inicial dos agrupamentos
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Example: `2024-01-01`

#### dataFinaAgrupamento

*   **Name:** `dataFinal`
*   **In:** query
*   **Description:** Pesquisa através da data final dos agrupamentos
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Example: `2024-01-01`

#### limit

*   **Name:** `limit`
*   **In:** query
*   **Description:** Limite da paginação
*   **Required:** false
*   **Schema:**
    *   Type: integer
    *   Default: 100

#### offset

*   **Name:** `offset`
*   **In:** query
*   **Description:** Offset da paginação
*   **Required:** false
*   **Schema:**
    *   Type: integer
    *   Default: 0

#### orderBy

*   **Name:** `orderBy`
*   **In:** query
*   **Description:** Define a ordenação da listagem por ordem crescente ou decrescente
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Enum: `asc - Crescente`, `desc - Descrescente`
    *   Example: `asc`

#### nomeFormaEnvio

*   **Name:** `nome`
*   **In:** query
*   **Description:** Pesquisa por nome parcial ou completo da forma de envio
*   **Required:** false
*   **Schema:**
    *   Type: string

#### tipoFormaEnvio

*   **Name:** `tipo`
*   **In:** query
*   **Description:** Pesquisa por tipo de forma de envio
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Enum: `0 - Sem Frete`, `1 - Correios`, `2 - Transportadora`, `3 - Mercado Envios`, `4 - B2w Entrega`, `5 - Correios Ff`, `6 - Customizado`, `7 - Jadlog`, `8 - Totalexpress`, `9 - Olist`, `10 - Gateway`, `11 - Magalu Entregas`, `12 - Shopee Envios`, `13 - Ns Entregas`, `14 - Viavarejo Envvias`, `15 - Madeira Envios`, `16 - Ali Envios`, `17 - Loggi`, `18 - Conecta La Etiquetas`, `19 - Amazon Dba`, `20 - Magalu Fulfillment`, `21 - Ns Magalu Entregas`, `22 - Shein Envios`, `23 - Mandae`, `24 - Olist Envios`, `25 - Kwai Envios`, `26 - Beleza Envios`
    *   Example: `0`

#### situacaoFormaEnvio

*   **Name:** `situacao`
*   **In:** query
*   **Description:** Pesquisa por situação da forma de envio
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Enum: `0 - Sem Frete`, `1 - Correios`, `2 - Transportadora`, `3 - Mercado Envios`, `4 - B2w Entrega`, `5 - Correios Ff`, `6 - Customizado`, `7 - Jadlog`, `8 - Totalexpress`, `9 - Olist`, `10 - Gateway`, `11 - Magalu Entregas`, `12 - Shopee Envios`, `13 - Ns Entregas`, `14 - Viavarejo Envvias`, `15 - Madeira Envios`, `16 - Ali Envios`, `17 - Loggi`, `18 - Conecta La Etiquetas`, `19 - Amazon Dba`, `20 - Magalu Fulfillment`, `21 - Ns Magalu Entregas`, `22 - Shein Envios`, `23 - Mandae`, `24 - Olist Envios`, `25 - Kwai Envios`, `26 - Beleza Envios`
    *   Example: `0`

#### nomeFormaPagamento

*   **Name:** `nome`
*   **In:** query
*   **

#### situacaoFormaPagamento

*   **Name:** `situacao`
*   **In:** query
*   **Description:** Pesquisa por situação da forma de pagamento
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Enum: `1 - Habilitada`, `2 - Desabilitada`
    *   Example: `1`

#### nomeIntermediador

*   **Name:** `nome`
*   **In:** query
*   **Description:** Pesquisa por nome parcial ou completo do intermediador
*   **Required:** false
*   **Schema:**
    *   Type: string

#### cnpjIntermediador

*   **Name:** `cnpj`
*   **In:** query
*   **Description:** Pesquisa por cnpj do intermediador
*   **Required:** false
*   **Schema:** (Implicitly string, based on context)

#### nomeListaPreco

*   **Name:** `nome`
*   **In:** query
*   **Description:** Pesquisa por nome parcial ou completo da lista de preços
*   **Required:** false
*   **Schema:**
    *   Type: string

#### descricaoMarca

*   **Name:** `descricao`
*   **In:** query
*   **Description:** Pesquisa por descrição completa da marca
*   **Required:** false
*   **Schema:**
    *   Type: string

#### tipoNota

*   **Name:** `tipo`
*   **In:** query
*   **Description:** Pesquisa por tipo de nota
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Enum: `E - Entrada`, `S - Saida`
    *   Example: `E`

#### numeroNota

*   **Name:** `numero`
*   **In:** query
*   **Description:** Pesquisa por número da nota
*   **Required:** false
*   **Schema:**
    *   Type: int

#### cpfCnpjNota

*   **Name:** `cpfCnpj`
*   **In:** query
*   **Description:** Pesquisa por CPF ou CNPJ
*   **Required:** false
*   **Schema:**
    *   Type: string

#### dataInicialNota

*   **Name:** `dataInicial`
*   **In:** query
*   **Description:** Pesquisa por data de criação
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Example: `2023-01-01`

#### dataFinalNota

*   **Name:** `dataFinal`
*   **In:** query
*   **Description:** Pesquisa por data de criação
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Example: `2023-01-01`

#### situacaoNota

*   **Name:** `situacao`
*   **In:** query
*   **Description:** Pesquisa pela situacão da nota
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Enum: `1 - Pendente`, `2 - Emitida`, `3 - Cancelada`, `4 - Enviada Aguardando Recibo`, `5 - Rejeitada`, `6 - Autorizada`, `7 - Emitida Danfe`, `8 - Registrada`, `9 - Enviada Aguardando Protocolo`, `10 - Denegada`
    *   Example: `1`

#### numeroPedidoEcommerce

*   **Name:** `numeroPedidoEcommerce`
*   **In:** query
*   **Description:** Pesquisa pelo número do pedido no e-commerce
*   **Required:** false
*   **Schema:**
    *   Type: string

#### idVendedorNota

*   **Name:** `idVendedor`
*   **In:** query
*   **Description:** Pesquisa por identificador do vendedor
*   **Required:** false
*   **Schema:**
    *   Type: int

#### idFormaEnvioNota

*   **Name:** `idFormaEnvio`
*   **In:** query
*   **Description:** Pesquisa por identificador da forma de envio
*   **Required:** false
*   **Schema:**
    *   Type: int

#### marcadoresNota

*   **Name:** `marcadores`
*   **In:** query
*   **Description:** Pesquisa por marcadores
*   **Required:** false
*   **Schema:**
    *   Type: array
    *   Items:
        *   Type: string

#### numeroOrdemCompra

*   **Name:** `numero`
*   **In:** query
*   **Description:** Pesquisa através do número da ordem de compra
*   **Required:** false
*   **Schema:**
    *   Type: int

#### dataInicialOrdemCompra

*   **Name:** `dataInicial`
*   **In:** query
*   **Description:** Pesquisa através da data de criação da ordem de compra
*   **Required:** false
*   **Schema:**
    *   Type: string

#### dataFinalOrdemCompra

*   **Name:** `dataFinal`
*   **In:** query
*   **Description:** Pesquisa através da data de criação da ordem de compra
*   **Required:** false
*   **Schema:**
    *   Type: string

#### marcadoresOrdemCompra

*   **Name:** `marcadores`
*   **In:** query
*   **Description:** Pesquisa através dos marcadores da ordem de compra
*   **Required:** false
*   **Schema:**
    *   Type: array
    *   Items:
        *   Type: string

#### nomeFornecedorOrdemCompra

*   **Name:** `nomeFornecedor`
*   **In:** query
*   **Description:** Pesquisa através do nome do fornecedor da ordem de compra
*   **Required:** false
*   **Schema:**
    *   Type: string

#### codigoFornecedorOrdemCompra

*   **Name:** `codigoFornecedor`
*   **In:** query
*   **Description:** Pesquisa através do código do fornecedor da ordem de compra
*   **Required:** false
*   **Schema:**
    *   Type: string

#### situacaoOrdemCompra

*   **Name:** `situacao`
*   **In:** query
*   **Description:** Pesquisa através da situação da ordem de compra
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Enum: `0 - Em Aberto`, `1 - Atendido`, `2 - Cancelado`, `3 - Em Andamento`
    *   Example: `0`

#### nomeClienteOrdemServico

*   **Name:** `nomeCliente`
*   **In:** query
*   **Description:** Pesquisa por nome do cliente de ordem de servico
*   **Required:** false
*   **Schema:**
    *   Type: string

#### situacaoOrdemServico

*   **Name:** `situacao`
*   **In:** query
*   **Description:** Pesquisa por situação de ordem de servico
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Enum: `4 - Nao Aprovada`, `3 - Finalizada`, `0 - Em Aberto`, `2 - Serv Concluido`, `1 - Orcada`, `5 - Aprovada`, `6 - Em Andamento`, `7 - Cancelada`
    *   Example: `4`

#### dataInicialEmissaoOrdemServico

*   **Name:** `dataInicialEmissao`
*   **In:** query
*   **Description:** Pesquisa por data inicial da emissão de ordem de servico
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Example: `2024-01-01`

#### dataFinalEmissaoOrdemServico

*   **Name:** `dataFinalEmissao`
*   **In:** query
*   **Description:** Pesquisa por data final da emissão de ordem de servico
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Example: `2024-01-01`

#### numeroOrdemServico

*   **Name:** `numeroOrdemServico`
*   **In:** query
*   **Description:** Pesquisa por número de ordem de servico
*   **Required:** false
*   **Schema:**
    *   Type: string

#### marcadoresOrdemServico

*   **Name:** `marcadores`
*   **In:** query
*   **Description:** Pesquisa por marcadores
*   **Required:** false
*   **Schema:**
    *   Type: array
    *   Items:
        *   Type: string

#### idContatoOrdemServico

*   **Name:** `idContato`
*   **In:** query
*   **Description:** Pesquisa por ID do contato de ordem de servico
*   **Required:** false
*   **Schema:**
    *   Type: integer
    *   Example: 123

#### numeroPedido

*   **Name:** `numero`
*   **In:** query
*   **Description:** Pesquisa por número do pedido
*   **Required:** false
*   **Schema:**
    *   Type: int

#### nomeClientePedido

*   **Name:** `nomeCliente`
*   **In:** query
*   **Description:** Pesquisa por nome do cliente
*   **Required:** false
*   **Schema:**
    *   Type: string

#### codigoClientePedido

*   **Name:** `codigoCliente`
*   **In:** query
*   **Description:** Pesquisa por código do cliente
*   **Required:** false
*   **Schema:**
    *   Type: string

#### cpfCnpjClientePedido

*   **Name:** `cnpj`
*   **In:** query
*   **Description:** Pesquisa por CPF/CNPJ do cliente
*   **Required:** false
*   **Schema:**
    *   Type: string

#### dataInicialPedido

*   **Name:** `dataInicial`
*   **In:** query
*   **Description:** Pesquisa através da data de criação do pedido
*   **Required:** false
*   **Schema:**
    *   Type: string

#### dataFinalPedido

*   **Name:** `dataFinal`
*   **In:** query
*   **Description:** Pesquisa através da data de criação do pedido
*   **Required:** false
*   **Schema:**
    *   Type: string

#### dataAtualizacaoPedido

*   **Name:** `dataAtualizacao`
*   **In:** query
*   **Description:** Pesquisa através da data de atualização do pedido
*   **Required:** false
*   **Schema:**
    *   Type: string

#### situacaoPedido

*   **Name:** `situacao`
*   **In:** query
*   **Description:** Pesquisa com base na situação informada
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Enum: `8 - Dados Incompletos`, `0 - Aberta`, `3 - Aprovada`, `4 - Preparando Envio`, `1 - Faturada`, `7 - Pronto Envio`, `5 - Enviada`, `6 - Entregue`, `2 - Cancelada`, `9 - Nao Entregue`
    *   Example: `8`

#### numeroPedidoEcommercePedido

*   **Name:** `numeroPedidoEcommerce`
*   **In:** query
*   **Description:** Pesquisa por número do pedido no e-commerce
*   **Required:** false
*   **Schema:**
    *   Type: string

#### idVendedorPedido

*   **Name:** `idVendedor`
*   **In:** query
*   **Description:** Pesquisa por id do vendedor
*   **Required:** false
*   **Schema:**
    *   Type: int

#### marcadoresPedido

*   **Name:** `marcadores`
*   **In:** query
*   **Description:** Pesquisa por marcadores
*   **Required:** false
*   **Schema:**
    *   Type: array
    *   Items:
        *   Type: string

#### dataInicialCustoProduto

*   **Name:** `dataInicial`
*   **In:** query
*   **Description:** Especifica a data de início para a filtragem dos custos do produto.
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Example: `2023-01-01`

#### dataFinalCustoProduto

*   **Name:** `dataFinal`
*   **In:** query
*   **Description:** Especifica a data de fim para a filtragem dos custos do produto.
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Example: `2023-01-01`

#### nomeProduto

*   **Name:** `nome`
*   **In:** query
*   **Description:** Pesquisa por nome parcial ou completo do produto
*   **Required:** false
*   **Schema:**
    *   Type: string

#### codigoProduto

*   **Name:** `codigo`
*   **In:** query
*   **Description:** Pesquisa pelo código do produto
*   **Required:** false
*   **Schema:**
    *   Type: string

#### gtin

*   **Name:** `gtin`
*   **In:** query
*   **Description:** Pesquisa através do código GTIN do produto
*   **Required:** false
*   **Schema:**
    *   Type: int

#### situacao

*   **Name:** `situacao`
*   **In:** query
*   **Description:** Pesquisa com base na situação informada
*   **Required:** false
*   **Schema:**
    *   Type: string

#### dataCriacao

*   **Name:** `dataCriacao`
*   **In:** query
*   **Description:** Pesquisa através da data de criação do produto
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Example: `2023-01-01 10:00:00`

#### dataAlteracao

*   **Name:** `dataAlteracao`
*   **In:** query
*   **Description:** Pesquisa através da data de última alteração do produto
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Example: `2023-01-01 10:00:00`

#### situacaoSeparacao

*   **Name:** `situacao`
*   **In:** query
*   **Description:** Pesquisa por situacao da separação.
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Enum: `1 - Sit Aguardando Separacao`, `2 - Sit Separada`, `3 - Sit Embalada`, `4 - Sit Em Separacao`
    *   Example: `1`

#### idFormaEnvio

*   **Name:** `idFormaEnvio`
*   **In:** query
*   **Description:** Pesquisa através do identificador da forma de envio.
*   **Required:** false
*   **Schema:**
    *   Type: int

#### dataInicialVenda

*   **Name:** `dataInicial`
*   **In:** query
*   **Description:** Pesquisa através da data inicial dos pedidos.
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Example: `2023-01-01`

#### dataFinalVenda

*   **Name:** `dataFinal`
*   **In:** query
*   **Description:** Pesquisa através da data final dos pedidos.
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Example: `2023-01-01`

#### nome

*   **Name:** `nome`
*   **In:** query
*   **Description:** Pesquisa pelo nome do serviço
*   **Required:** false
*   **Schema:**
    *   Type: string

#### codigo

*   **Name:** `codigo`
*   **In:** query
*   **Description:** Pesquisa pelo código do serviço
*   **Required:** false
*   **Schema:**
    *   Type: string

#### situacaoServico

*   **Name:** `situacao`
*   **In:** query
*   **Description:** Pesquisa com base na situação informada
*   **Required:** false
*   **Schema:**
    *   Type: string
    *   Enum: `A - Ativo`, `I - Inativo`, `E - Excluido`
    *   Example: `A`

#### nomeVendedor

*   **Name:** `nome`
*   **In:** query
*   **Description:** Pesquisa por nome parcial ou completo
*   **Required:** false
*   **Schema:**
    *   Type: string

#### codigoVendedor

*   **Name:** `codigo`
*   **In:** query
*   **Description:** Pesquisa por codigo completo
*   **Required:** false
*   **Schema:**
    *   Type: string

### Security Schemes

#### bearerAuth

*   **Type:** http
*   **Scheme:** bearer
*   **BearerFormat:** JWT

```
--- END OF FILE swagger.json ---
```


