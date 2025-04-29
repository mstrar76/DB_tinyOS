# Tiny ERP API v3: Configuration and Usage Guide

## 1. Introduction

This document provides a guide to configuring and using the Tiny ERP API v3. The API allows developers to integrate external applications with Tiny ERP, enabling automation and data synchronization for various modules, including Service Orders (_Ordens de Serviço_).

The API follows REST principles, typically uses JSON for data exchange, and requires secure HTTPS connections.

## 2. Configuration and Authentication

Setting up access to the Tiny ERP API involves registering your application, obtaining credentials, and configuring security settings.

### 2.1. Application Registration and Setup

*   **Create a Tiny ERP Account**: Ensure your subscription plan includes API access.
*   **(Optional) Firebase Setup for Boilerplate Integrations**: If using Tiny's provided integration templates, you might need to:
    *   Set up a Firebase project (Blaze plan recommended).
    *   Generate a `FIREBASE_TOKEN` using `firebase-tools`.
    *   Configure application metadata (like `app_id`, `title`) in configuration files (e.g., `ecom.config.js`).

### 2.2. Token Generation and Management

*   **Obtain API Token**: The primary method for authentication is using an API token.
    *   Generate this token within your Tiny ERP account interface (usually under Settings > API Keys or similar).
*   **Secure Storage**: Store your API token securely. Avoid hardcoding it directly in your application code. Use environment variables or secure configuration management practices.

### 2.3. Digital Certificate Integration (If Required)

*   **Upload A1 Certificate**: Some integrations might require an A1 digital certificate for enhanced security and encrypted communication.
    *   Upload the certificate via the Tiny ERP web interface.
    *   Ensure your development environment has the necessary SSL libraries to handle certificate validation.

### 2.4. Authentication Method

*   **Token-Based Authentication**: Tiny ERP API v3 primarily uses token-based authentication.
    *   Include your API token in every request, typically as a `token` parameter in the query string or request body, or potentially as an `Authorization: Bearer <token>` header (check specific endpoint documentation).

    *   **Example (PHP - Conceptual based on v2 patterns)**:
        ```php
        <?php
        $url = 'https://api.tiny.com.br/api2/produto.obter.php'; // Example endpoint
        $token = 'YOUR_API_TOKEN'; // Replace with your actual token
        $data = "token=$token&id=PRODUCT_ID&formato=JSON"; // Format data for POST

        // Use cURL or another HTTP client to send the request
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_POST, 1);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        $response = curl_exec($ch);
        curl_close($ch);

        $result = json_decode($response, true);
        // Process $result
        ?>
        ```

## 3. Using the API - Example: Service Orders

The API provides various endpoints to interact with different modules. Here's a focus on retrieving Service Orders.

### 3.1. Endpoint: `ObterOrdemServicoAction` (Get Service Order)

*   **Purpose**: Retrieves detailed information about a specific Service Order.
*   **HTTP Method**: `GET`
*   **Path**: `/ordem-servico/{idOrdemServico}`
    *   `{idOrdemServico}`: The unique identifier (ID) of the Service Order you want to fetch.
*   **Required Parameters**:
    *   **Path**: `idOrdemServico` (The Service Order ID). This is required.
    *   **Header/Query**: `token` (Your API token). Authentication is required. The exact placement (header or query parameter) should be confirmed in Tiny's general API v3 guidelines, but it's usually a header like `Authorization: Bearer YOUR_TOKEN` or a query parameter `token=YOUR_TOKEN`.
*   **Request Body**: None for `GET` requests.
*   **Success Response (200 OK)**: A JSON object containing the details of the service order. Based on the schema extracted from `swagger.json`:
    ```json
    {
      "retorno": {
        "status_processamento": 3,
        "status": "OK",
        "ordem_servico": {
          "id": 0,
          "situacao": "4 - Nao Aprovada",
          "data": "string",
          "dataPrevista": "string",
          "dataConclusao": "string",
          "totalServicos": "string",
          "totalOrdemServico": "string",
          "totalPecas": "string",
          "numeroOrdemServico": "string",
          "equipamento": "string",
          "equipamentoSerie": "string",
          "descricaoProblema": "string",
          "observacoes": "string",
          "orcar": "string",
          "orcado": "string",
          "observacoesServico": "string",
          "observacoesInternas": "string",
          "alqComissao": 0.0,
          "vlrComissao": 0,
          "idForma": 0,
          "idContaContabil": 0,
          "desconto": "string",
          "idListaPreco": 0,
          "idLocalPrestacao": null,
          "idDeposito": 0,
          "vendedor": {
            "id": 0
          },
          "contato": {
            "id": 0
          },
          "tecnico": "string",
          "categoria": {
             "id": 0,
             "descricao": "string"
          },
          "formaPagamento": {
            "id": 0,
            "nome": "string"
          },
          "itens": [
             {}
          ]
        }
      }
    }
    ```
    *(Note: This schema is directly derived from the `swagger.json` definition. For full details of nested schemas like 'vendedor', 'contato', 'categoria', 'formaPagamento', and 'itens', please refer to the complete `swagger.json` file.)*

### 3.2. Error Handling

*   The API will return standard HTTP status codes for errors:
    *   `401 Unauthorized`: Invalid or missing API token.
    *   `404 Not Found`: The requested Service Order ID does not exist.
    *   `429 Too Many Requests`: API rate limit exceeded. Implement backoff strategies.
    *   `400 Bad Request`: Invalid parameters or request format.
    *   `5xx Server Error`: An issue occurred on Tiny's side.
*   The response body for errors usually contains a JSON object with details about the error.

### 3.3. Endpoint: `/ordem-servico` (GET - ListarOrdemServicoAction)

*   **Operation ID:** `ListarOrdemServicoAction`
*   **Description:** Retrieves a list of service orders, with optional filtering and pagination.
*   **HTTP Method:** `GET`
*   **Path:** `/ordem-servico`
*   **Query Parameters:**
    *   `nomeCliente` (string, optional): Pesquisa por nome do cliente de ordem de servico.
    *   `situacao` (string, optional): Pesquisa por situação de ordem de servico. Allowed values: `4 - Nao Aprovada`, `3 - Finalizada`, `0 - Em Aberto`, `2 - Serv Concluido`, `1 - Orcada`, `5 - Aprovada`, `6 - Em Andamento`, `7 - Cancelada`. Example: `4`.
    *   `dataInicialEmissao` (string, optional): Pesquisa por data inicial da emissão de ordem de servico. Example: `2024-01-01`.
    *   `dataFinalEmissao` (string, optional): Pesquisa por data final da emissão de ordem de servico. Example: `2024-01-01`.
    *   `numeroOrdemServico` (string, optional): Pesquisa por número de ordem de servico.
    *   `marcadores` (array of strings, optional): Pesquisa por marcadores.
    *   `idContato` (integer, optional): Pesquisa por ID do contato de ordem de servico. Example: `123`.
    *   `orderBy` (string, optional): Define a ordenação da listagem. Allowed values: `asc - Crescente`, `desc - Decrescente`. Example: `asc`.
    *   `limit` (integer, optional): Limite da paginação. Default: `100`.
    *   `offset` (integer, optional): Offset da paginação. Default: `0`.
*   **Responses:**
    *   `200 OK`: Success. Response body will be a `ListagemOrdemServicoResponseModel` (schema details to be added).
    *   `400 Bad Request`:  Error response, details in `ErrorDTO` schema.
    *   `401 Unauthorized`
    *   `403 Forbidden`
    *   `404 Not Found`
    *   `500 Internal Server Error`
    *   `503 Service Unavailable`
*   **Security:** Requires Bearer Token authentication.

*(Note: Schema definitions for `ListagemOrdemServicoResponseModel` and `ErrorDTO` will be added in subsequent steps.)*

### 3.4. Endpoint: `/ordem-servico` (POST - CriarOrdemServicoAction)

*   **Operation ID:** `CriarOrdemServicoAction`
*   **Description:** Creates a new service order.
*   **HTTP Method:** `POST`
*   **Path:** `/ordem-servico`
*   **Request Body:**
    *   Required: Yes
    *   Content Type: `application/json`
    *   Schema: `CriarOrdemServicoRequestModel` (schema details to be added).  This schema defines the structure of the JSON body you need to send when creating a service order.
*   **Responses:**
    *   `200 OK`: Success. Response body will be a `CriarOrdemServicoResponseModel` (schema details to be added).
    *   `400 Bad Request`:  Error response, details in `ErrorDTO` schema.
    *   `401 Unauthorized`
    *   `403 Forbidden`
    *   `404 Not Found`
    *   `500 Internal Server Error`
    *   `503 Service Unavailable`
*   **Security:** Requires Bearer Token authentication.

*(Note: Schema definitions for `CriarOrdemServicoRequestModel`, `CriarOrdemServicoResponseModel`, and `ErrorDTO` will be added in subsequent steps.)*

### 3.5. Endpoint: `/ordem-servico/{idOrdemServico}` (GET - ObterOrdemServicoAction)

*   **Operation ID:** `ObterOrdemServicoAction`
*   **Description:** Retrieves details of a specific service order by its ID.
*   **HTTP Method:** `GET`
*   **Path:** `/ordem-servico/{idOrdemServico}`
    *   `idOrdemServico` (integer, required): The unique identifier of the service order.
*   **Responses:**
    *   `200 OK`: Success. Response body will be a `ObterOrdemServicoModelResponse` (schema details already documented in section 3.1).
    *   `400 Bad Request`:  Error response, details in `ErrorDTO` schema.
    *   `401 Unauthorized`
    *   `403 Forbidden`
    *   `404 Not Found`
    *   `500 Internal Server Error`
    *   `503 Service Unavailable`
*   **Security:** Requires Bearer Token authentication.

*(Note: The response schema `ObterOrdemServicoModelResponse` is already documented in section 3.1. The `ErrorDTO` schema will be documented later.)*

### 3.6. Endpoint: `/ordem-servico/{idOrdemServico}` (PUT - AtualizarOrdemServicoAction)

*   **Operation ID:** `AtualizarOrdemServicoAction`
*   **Description:** Updates an existing service order with the provided ID.
*   **HTTP Method:** `PUT`
*   **Path:** `/ordem-servico/{idOrdemServico}`
    *   `idOrdemServico` (integer, required): The unique identifier of the service order to be updated.
*   **Request Body:**
    *   Required: Yes
    *   Content Type: `application/json`
    *   Schema: `AtualizarOrdemServicoRequestModel` (schema details to be added). This schema defines the structure of the JSON body containing the updated service order information.
*   **Responses:**
    *   `204 No Content`: Success. Indicates the service order was successfully updated. No response body is returned.
    *   `400 Bad Request`:  Error response, details in `ErrorDTO` schema.
    *   `401 Unauthorized`
    *   `403 Forbidden`
    *   `404 Not Found`
    *   `500 Internal Server Error`
    *   `503 Service Unavailable`
*   **Security:** Requires Bearer Token authentication.

*(Note: Schema definitions for `AtualizarOrdemServicoRequestModel` and `ErrorDTO` will be added in subsequent steps.)*

## 4. Contact Endpoints

### 4.1. Endpoint: `/contatos` (GET - ListarContatosAction)

*   **Operation ID:** `ListarContatosAction`
*   **Description:** Retrieves a list of contacts, with optional filtering and pagination.
*   **HTTP Method:** `GET`
*   **Path:** `/contatos`
*   **Query Parameters:**
    *   `nome` (string, optional): Pesquisa por nome parcial ou completo.
    *   `codigo` (string, optional): Pesquisa por codigo completo.
    *   `situacao` (string, optional): Pesquisa por situacao. Allowed values: `B - Ativo`, `A - Ativo Com Acesso Sistema`, `I - Inativo`, `E - Excluido`. Example: `B`.
    *   `idVendedor` (integer, optional): Pesquisa por vendedor padrão.
    *   `cpfCnpj` (string, optional): Pesquisa por CPF ou CNPJ.
    *   `celular` (string, optional): Pesquisa pelo celular.
    *   `dataCriacao` (string, optional): Pesquisa por data de criação. Example: `2023-01-01 10:00:00`.
    *   `dataAtualizacao` (string, optional): Pesquisa por data de atualização. Example: `2023-01-01 10:00:00`.
    *   `orderBy` (string, optional): Define a ordenação da listagem. Allowed values: `asc - Crescente`, `desc - Decrescente`. Example: `asc`.
    *   `limit` (integer, optional): Limite da paginação. Default: `100`.
    *   `offset` (integer, optional): Offset da paginação. Default: `0`.
*   **Responses:**
    *   `200 OK`: Success. Response body is an object with: 
        *   `itens`: An array of `ListagemContatoModelResponse` objects (schema details to be added).
        *   `paginacao`: A `PaginatedResultModel` object with pagination details (schema details to be added).
    *   `400 Bad Request`:  Error response, details in `ErrorDTO` schema.
    *   `401 Unauthorized`
    *   `403 Forbidden`
    *   `404 Not Found`
    *   `500 Internal Server Error`
    *   `503 Service Unavailable`
*   **Security:** Requires Bearer Token authentication.

*(Note: Schema definitions for `ListagemContatoModelResponse`, `PaginatedResultModel`, and `ErrorDTO` will be added later.)*

### 4.2. Endpoint: `/contatos` (POST - CriarContatoAction)

*   **Operation ID:** `CriarContatoAction`
*   **Description:** Creates a new contact.
*   **HTTP Method:** `POST`
*   **Path:** `/contatos`
*   **Request Body:**
    *   Required: Yes
    *   Content Type: `application/json`
    *   Schema: `CriarContatoModelRequest` (schema details to be added). This schema defines the structure of the JSON request body for creating a new contact.
*   **Responses:**
    *   `200 OK`: Success. Response body will be a `CriarContatoModelResponse` (schema details to be added).
    *   `400 Bad Request`:  Error response, details in `ErrorDTO` schema.
    *   `401 Unauthorized`
    *   `403 Forbidden`
    *   `404 Not Found`
    *   `500 Internal Server Error`
    *   `503 Service Unavailable`
*   **Security:** Requires Bearer Token authentication.

*(Note: Schema definitions for `CriarContatoModelRequest`, `CriarContatoModelResponse`, and `ErrorDTO` will be added in subsequent steps.)*

## 4. Best Practices

*   **Security**: Always use HTTPS. Never expose your API token in client-side code or insecure channels.
*   **Rate Limiting**: Be mindful of API rate limits. Implement caching and efficient data fetching strategies.
*   **Error Handling**: Robustly handle potential API errors and HTTP status codes.
*   **Logging**: Log API requests and responses (excluding sensitive data like tokens) for debugging purposes.

## 5. Further Information

*   **Official Tiny ERP API Documentation**: Always consult the latest official documentation for the most accurate and up-to-date information.
    *   [API v3 Configuration and Usage (Knowledge Base)](https://ajuda.tiny.com.br/kb/articles/erp/integracoes/gestao-de-integracoes/aplicativos-api-v3-configuracoes-e-utilizacao)
    *   [API v3 Swagger UI (Service Order Example)](https://erp.tiny.com.br/public-api/v3/swagger/index.html#/Ordem%20de%20Serviço/ObterOrdemServicoAction)
