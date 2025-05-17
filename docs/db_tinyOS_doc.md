# Supabase Database Access Documentation — tinyOS Service Orders

This document provides detailed instructions for connecting to and querying the Supabase database used by the tinyOS project. It is intended as a reference for any application (backend, frontend, scripts, or external integrations) that needs to access the service order data.

## 1. Connection Credentials and Configuration

To connect to the Supabase database, you need the **Supabase Project URL** and the **Supabase Public API Key (Anon Key)**.

### Where to Find Credentials in the Supabase Dashboard

- Acesse o [Supabase Dashboard](https://app.supabase.com/), selecione o projeto e navegue até:
  - `Settings` ▸ `Project Settings` ▸ `API`
- Lá você encontrará:
  - **Project URL** (ex: `https://xxxx.supabase.co`)
  - **Anon Public Key** (chave pública para clientes)
  - **Service Role Key** (chave de serviço, uso restrito)
  - **Connection string** para Postgres (exemplo abaixo)

### Variáveis de ambiente recomendadas

- **Frontend (Vite, etc.):**
  - `VITE_SUPABASE_URL`
  - `VITE_SUPABASE_ANON_KEY`
- **Backend/scripts (Python, Node.js):**
  - `SUPABASE_URL`
  - `SUPABASE_ANON_KEY`
  - `SUPABASE_SERVICE_ROLE_KEY` (apenas para operações administrativas seguras)
  - `SUPABASE_DB_URL` (string de conexão Postgres)

**Example `.env` file:**

```dotenv
# For frontend (Vite, etc.)
VITE_SUPABASE_URL="YOUR_SUPABASE_PROJECT_URL"
VITE_SUPABASE_ANON_KEY="YOUR_SUPABASE_ANON_KEY"

# For backend or scripts
SUPABASE_URL="YOUR_SUPABASE_PROJECT_URL"
SUPABASE_ANON_KEY="YOUR_SUPABASE_ANON_KEY"
# Other environment variables...
```

**Important:** The `.env` file **MUST NOT** be versioned in your code repository (Git). Always ensure it is listed in your `.gitignore`.

## 2. Best Practices for Secrets and Environment Management

- **Never expose the Service Role Key** in any client-side code or public repository. Only the Anon Key is safe for public use.
- Use different environment files for development, staging, and production. Do not share secrets between environments.
- For deployment, inject environment variables using your hosting platform’s secret management tools or environment configuration.
- Rotate keys regularly and immediately if a leak is suspected.

## 3. Example: Connecting from JavaScript (Frontend)

```js
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
```

## 4. Example: Connecting from Python (Backend or Script)

```python
import os
from supabase import create_client, Client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

# Example query:
result = supabase.table("ordens_servico").select("*").execute()
print(result.data)
```

### Exemplo de uso seguro da Service Role Key (backend apenas)

> **Atenção:** Nunca exponha a Service Role Key em código cliente, apenas em backends seguros!

```python
import os
from supabase import create_client

url = os.getenv("SUPABASE_URL")
service_role = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
if not service_role:
    raise Exception("Service Role Key não configurada!")
supabase_admin = create_client(url, service_role)
# Use supabase_admin para operações administrativas restritas
```

### Exemplo de conexão direta com o Postgres

```dotenv
SUPABASE_DB_URL="postgresql://USER:PASSWORD@HOST:PORT/DATABASE"
```

Exemplo de uso em Python:
```python
import os
import psycopg2

conn = psycopg2.connect(os.getenv("SUPABASE_DB_URL"))
# ...
```

## 5. Additional Notes

- The Anon Key is suitable for querying public tables and using Row Level Security (RLS) policies. For administrative actions, use the Service Role Key **only in secure backend environments**.
- If you need direct Postgres access, consult the Supabase dashboard for connection details, and be aware of security implications.
- Always validate and sanitize all inputs when writing data to the database.

---

*Last updated: 2025-05-14*

## 1.1. Outras linguagens e SDKs

Supabase oferece SDKs oficiais para várias linguagens e plataformas:
- [JavaScript/TypeScript](https://supabase.com/docs/reference/javascript)
- [Python](https://supabase.com/docs/reference/python)
- [Dart/Flutter](https://supabase.com/docs/reference/dart)
- [Kotlin (Android)](https://supabase.com/docs/reference/kotlin)
- [Swift (iOS)](https://supabase.com/docs/reference/swift)

Consulte a [documentação oficial](https://supabase.com/docs/reference) para exemplos de uso em cada stack.

## 1.2. Políticas de Row Level Security (RLS)

A chave pública `anon` respeita as políticas de Row Level Security (RLS) configuradas no seu projeto Supabase. Para controlar o acesso, ative e personalize as políticas em:
- Dashboard: `Database` ▸ `Tables` ▸ selecione a tabela ▸ `RLS Policies`
- Consulte [documentação oficial de RLS](https://supabase.com/docs/guides/auth/row-level-security) para exemplos e melhores práticas.

## 3. Esquema do Banco de Dados: Tabela `ordens_servico`

A tabela principal para os dados de Ordens de Serviço é `ordens_servico`. Abaixo estão as colunas relevantes e suas descrições, baseadas no arquivo `db/schema.sql`:

| Coluna                 | Tipo de Dado      | Descrição                                                                 | Notas                                       |
| :--------------------- | :---------------- | :------------------------------------------------------------------------ | :------------------------------------------ |
| `id`                   | INTEGER           | Identificador único da Ordem de Serviço.                                  | Chave Primária                              |
| `numero_ordem_servico` | VARCHAR(50)       | Número de identificação da Ordem de Serviço.                              |                                             |
| `situacao`             | VARCHAR(10)       | Código numérico representando a situação da Ordem de Serviço.             | Veja a Tabela de Mapeamento de Situação abaixo. |
| `data_emissao`         | DATE              | Data de emissão da Ordem de Serviço.                                      |                                             |
| `data_prevista`        | TIMESTAMP NULL    | Data prevista para conclusão da Ordem de Serviço.                         | Pode ser NULO.                              |
| `data_conclusao`       | DATE NULL         | Data de conclusão da Ordem de Serviço.                                    | NULO para ordens não finalizadas.           |
| `total_servicos`       | NUMERIC(10, 2)    | Valor total dos serviços na Ordem de Serviço.                             |                                             |
| `total_ordem_servico`  | NUMERIC(10, 2)    | Valor total da Ordem de Serviço (serviços + peças - desconto).            |                                             |
| `total_pecas`          | NUMERIC(10, 2)    | Valor total das peças na Ordem de Serviço.                                |                                             |
| `equipamento`          | VARCHAR(255)      | Descrição do equipamento relacionado à OS.                                |                                             |
| `equipamento_serie`    | VARCHAR(255)      | Número de série do equipamento.                                           |                                             |
| `descricao_problema`   | TEXT              | Descrição detalhada do problema relatado.                                 |                                             |
| `observacoes`          | TEXT              | Observações gerais sobre a Ordem de Serviço.                              |                                             |
| `observacoes_internas` | TEXT              | Observações internas (não visíveis para o cliente).                       |                                             |
| `tecnico`              | VARCHAR(255)      | Nome do técnico responsável pela OS.                                      |                                             |
| `id_contato`           | INTEGER NULL      | ID do contato (cliente) associado à OS.                                   | Chave Estrangeira para `contatos`.          |
| `id_vendedor`          | INTEGER NULL      | ID do vendedor associado à OS.                                            | Chave Estrangeira para `contatos`.          |
| `id_categoria_os`      | INTEGER NULL      | ID da categoria da OS.                                                    | Chave Estrangeira para `categorias_os`.     |
| `id_forma_pagamento`   | INTEGER NULL      | ID da forma de pagamento.                                                 | Chave Estrangeira para `formas_pagamento`.  |
| `data_extracao`        | TIMESTAMP         | Timestamp da extração/criação do registro no banco de dados.              | Valor padrão: `CURRENT_TIMESTAMP`.          |
| `linha_dispositivo`    | VARCHAR(50)       | Campo customizado: Linha do dispositivo.                                  |                                             |
| `tipo_servico`         | VARCHAR(100)      | Campo customizado: Tipo de serviço.                                       |                                             |
| `origem_cliente`       | VARCHAR(50)       | Campo customizado: Origem do cliente (de marcadores).                     |                                             |

**Tabela de Mapeamento de Situação (`situacao`):**

O campo `situacao` armazena um código numérico. O mapeamento para as descrições textuais é o seguinte:

*   `0`: Em Aberto
*   `1`: Orcada
*   `2`: Serv Concluido
*   `3`: Finalizada
*   `4`: Nao Aprovada
*   `5`: Aprovada
*   `6`: Em Andamento
*   `7`: Cancelada

**Tabelas Relacionadas:**

*   `contatos`: Contém informações sobre clientes, vendedores e outros contatos. Relacionada a `ordens_servico` pelos campos `id_contato` e `id_vendedor`.
*   `enderecos`: Contém informações de endereço, relacionada a `contatos`.
*   `categorias_os`: Contém as categorias de Ordens de Serviço. Relacionada a `ordens_servico` pelo campo `id_categoria_os`.
*   `formas_pagamento`: Contém as formas de pagamento. Relacionada a `ordens_servico` pelo campo `id_forma_pagamento`.
*   `marcadores` e `ordem_servico_marcadores`: Tabelas futuras para associar marcadores às Ordens de Serviço.

## 4. Consultando Dados (Exemplos em JavaScript com `supabase-js`)

A biblioteca `supabase-js` oferece uma interface fluente para construir consultas. Abaixo estão alguns exemplos comuns:

**Importando o cliente Supabase:**

Certifique-se de importar a instância `supabase` configurada conforme a Seção 1.

```javascript
import { supabase } from './supabaseClient'; // Ajuste o caminho conforme a estrutura do seu projeto
```

**Exemplo 1: Buscar todas as Ordens de Serviço**

```javascript
async function getAllServiceOrders() {
  const { data, error } = await supabase
    .from('ordens_servico')
    .select('*'); // Seleciona todas as colunas

  if (error) {
    console.error('Erro ao buscar Ordens de Serviço:', error);
    return null;
  } else {
    console.log('Ordens de Serviço:', data);
    return data;
  }
}
```

**Exemplo 2: Buscar uma Ordem de Serviço específica por ID**

```javascript
async function getServiceOrderById(id) {
  const { data, error } = await supabase
    .from('ordens_servico')
    .select('*')
    .eq('id', id) // Filtra onde a coluna 'id' é igual ao valor fornecido
    .single(); // Espera um único resultado

  if (error) {
    console.error(`Erro ao buscar Ordem de Serviço com ID ${id}:`, error);
    return null;
  } else {
    console.log(`Ordem de Serviço com ID ${id}:`, data);
    return data;
  }
}
```

**Exemplo 3: Filtrar Ordens de Serviço por Situação (usando o código numérico)**

```javascript
async function getServiceOrdersBySituation(situationCode) {
  const { data, error } = await supabase
    .from('ordens_servico')
    .select('*')
    .eq('situacao', situationCode); // Filtra pela coluna 'situacao'

  if (error) {
    console.error(`Erro ao buscar Ordens de Serviço com situação ${situationCode}:`, error);
    return null;
  } else {
    console.log(`Ordens de Serviço com situação ${situationCode}:`, data);
    return data;
  }
}

// Exemplo de uso: Buscar todas as ordens finalizadas (código '3')
// getServiceOrdersBySituation('3');
```

**Exemplo 4: Filtrar Ordens de Serviço por Intervalo de Data de Emissão**

```javascript
async function getServiceOrdersByDateRange(startDate, endDate) {
  const { data, error } = await supabase
    .from('ordens_servico')
    .select('*')
    .gte('data_emissao', startDate) // Greater than or equal to (Maior ou igual a)
    .lte('data_emissao', endDate);  // Less than or equal to (Menor ou igual a)

  if (error) {
    console.error(`Erro ao buscar Ordens de Serviço entre ${startDate} e ${endDate}:`, error);
    return null;
  } else {
    console.log(`Ordens de Serviço entre ${startDate} e ${endDate}:`, data);
    return data;
  }
}

// Exemplo de uso: Buscar ordens emitidas em Abril de 2023
// getServiceOrdersByDateRange('2023-04-01', '2023-04-30');
```

**Exemplo 5: Buscar Ordens de Serviço por Texto na Descrição do Problema**

```javascript
async function searchServiceOrdersByProblem(searchText) {
  const { data, error } = await supabase
    .from('ordens_servico')
    .select('*')
    .ilike('descricao_problema', `%${searchText}%`); // Busca case-insensitive (ignora maiúsculas/minúsculas)

  if (error) {
    console.error(`Erro ao buscar Ordens de Serviço com texto "${searchText}":`, error);
    return null;
  } else {
    console.log(`Resultados da busca por "${searchText}":`, data);
    return data;
  }
}

// Exemplo de uso: Buscar ordens com "tela quebrada" na descrição
// searchServiceOrdersByProblem('tela quebrada');
```

**Exemplo 6: Ordenar Ordens de Serviço (por Data de Emissão, Descendente)**

```javascript
async function getServiceOrdersSortedByDate() {
  const { data, error } = await supabase
    .from('ordens_servico')
    .select('*')
    .order('data_emissao', { ascending: false }); // Ordena pela data de emissão, do mais recente para o mais antigo

  if (error) {
    console.error('Erro ao buscar Ordens de Serviço ordenadas:', error);
    return null;
  } else {
    console.log('Ordens de Serviço ordenadas:', data);
    return data;
  }
}
```

**Exemplo 7: Paginação de Resultados (Limit e Offset)**

```javascript
async function getPaginatedServiceOrders(page = 1, pageSize = 10) {
  const offset = (page - 1) * pageSize;
  const { data, error, count } = await supabase
    .from('ordens_servico')
    .select('*', { count: 'exact' }) // Inclui a contagem total de registros
    .range(offset, offset + pageSize - 1); // Define o intervalo de registros a serem retornados

  if (error) {
    console.error(`Erro ao buscar Ordens de Serviço (Página ${page}):`, error);
    return null;
  } else {
    console.log(`Ordens de Serviço (Página ${page}):`, data);
    console.log('Total de registros:', count);
    return { data, count };
  }
}

// Exemplo de uso: Buscar a segunda página com 20 registros por página
// getPaginatedServiceOrders(2, 20);
```

**Exemplo 8: Buscar Ordem de Serviço Incluindo Nome do Contato Relacionado**

Este exemplo demonstra como buscar dados de uma tabela relacionada (`contatos`) usando `select` com notação de ponto.

```javascript
async function getServiceOrderWithContactName(orderId) {
  const { data, error } = await supabase
    .from('ordens_servico')
    .select(`
      *, // Seleciona todas as colunas da tabela ordens_servico
      contatos ( nome ) // Seleciona apenas a coluna 'nome' da tabela 'contatos' relacionada
    `) // Assumes 'contatos' é o nome da tabela relacionada e 'id_contato' é a chave estrangeira
    .eq('id', orderId)
    .single();

  if (error) {
    console.error(`Erro ao buscar Ordem de Serviço com contato (ID ${orderId}):`, error);
    return null;
  } else {
    console.log(`Ordem de Serviço com contato (ID ${orderId}):`, data);
    // O nome do contato estará em data.contatos.nome (se houver um contato associado)
    return data;
  }
}
```
*(Nota: Este exemplo assume que a relação entre `ordens_servico` e `contatos` via `id_contato` está configurada corretamente no Supabase e que as políticas de RLS permitem o acesso aos dados de `contatos`.)*

## 5. Tratamento de Erros

Ao realizar consultas com `supabase-js`, o resultado sempre incluirá um objeto `error`. É fundamental verificar se `error` é nulo após cada operação.

```javascript
const { data, error } = await supabase.from('sua_tabela').select('*');

if (error) {
  console.error('Ocorreu um erro na consulta:', error);
  // Implemente a lógica de tratamento de erro apropriada para sua aplicação
} else {
  // Processar os dados
}
```

O objeto `error` conterá detalhes sobre o problema, como código do erro, mensagem e detalhes adicionais.

## 6. Recursos Adicionais

*   **Documentação Oficial do Supabase:**
    *   [Documentação Geral do Supabase](https://supabase.com/docs)
    *   [Documentação do Cliente JavaScript (`supabase-js`)](https://supabase.com/docs/reference/javascript/initializing)
    *   [Guia de Row Level Security (RLS)](https://supabase.com/docs/guides/auth/row-level-security)

Esta documentação deve servir como um guia inicial para acessar e consultar os dados de Ordens de Serviço no seu banco de dados Supabase. Lembre-se de consultar a documentação oficial do Supabase para funcionalidades mais avançadas e detalhes específicos.
