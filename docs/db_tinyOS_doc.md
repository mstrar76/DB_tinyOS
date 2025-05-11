# Documentação de Acesso ao Banco de Dados Supabase - Ordens de Serviço (tinyOS)

Este documento fornece instruções detalhadas para que outros aplicativos desenvolvidos possam acessar e consultar os dados de Ordens de Serviço armazenados no banco de dados Supabase do projeto tinyOS.

## 1. Credenciais de Conexão e Configuração

Para conectar ao banco de dados Supabase, você precisará do **Supabase Project URL** e da **Supabase Public API Key (Anon Key)**.

**Localização das Credenciais:**

As credenciais de segurança para este projeto são armazenadas de forma segura em um arquivo `.env` na raiz do projeto (ou em um diretório específico, como `web_interface/` se aplicável, conforme configurado no projeto).

*   **Supabase Project URL:** Procure por uma variável de ambiente como `VITE_SUPABASE_URL` ou similar no arquivo `.env`.
*   **Supabase Public API Key (Anon Key):** Procure por uma variável de ambiente como `VITE_SUPABASE_ANON_KEY` ou similar no arquivo `.env`.

**Exemplo de arquivo `.env`:**

```dotenv
VITE_SUPABASE_URL="SUA_URL_DO_PROJETO_SUPABASE"
VITE_SUPABASE_ANON_KEY="SUA_CHAVE_ANON_DO_SUPABASE"
# Outras variáveis de ambiente...
```

**Importante:** O arquivo `.env` **NÃO** deve ser versionado no controle de código (Git). Certifique-se de que ele está incluído no seu arquivo `.gitignore`.

**Configuração da Conexão (Exemplo em JavaScript com `supabase-js`):**

Para aplicativos desenvolvidos em JavaScript/TypeScript, a biblioteca oficial `@supabase/supabase-js` é a forma recomendada de interagir com o banco de dados.

Instale a biblioteca:

```bash
npm install @supabase/supabase-js
# ou
yarn add @supabase/supabase-js
```

Configure o cliente Supabase no seu aplicativo, lendo as variáveis de ambiente:

```javascript
import { createClient } from '@supabase/supabase-js';

// Carrega as variáveis de ambiente.
// O método exato para acessar variáveis de ambiente pode variar dependendo do seu framework (Vite, Next.js, Node.js, etc.)
const supabaseUrl = process.env.VITE_SUPABASE_URL; // Exemplo para Vite/Node.js
const supabaseAnonKey = process.env.VITE_SUPABASE_ANON_KEY; // Exemplo para Vite/Node.js

// Verifica se as variáveis de ambiente foram carregadas
if (!supabaseUrl || !supabaseAnonKey) {
  console.error('Variáveis de ambiente Supabase URL e Anon Key não estão configuradas.');
  // Considere lançar um erro ou lidar com esta situação adequadamente
  throw new Error("Supabase URL ou Anon Key está faltando. Verifique seu arquivo .env.");
}

// Cria uma única instância do cliente Supabase
export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Opcional: Verificação simples se o cliente foi criado
if (supabase) {
  console.log('Cliente Supabase inicializado com sucesso.');
}
```

Substitua `process.env.VITE_SUPABASE_URL` e `process.env.VITE_SUPABASE_ANON_KEY` pela forma correta de acessar variáveis de ambiente no seu ambiente de desenvolvimento (por exemplo, `import.meta.env` para Vite, `process.env` para Node.js/Next.js).

## 2. Melhores Práticas de Segurança

*   **Não Hardcodar Segredos:** Conforme a regra `.clinerules/security_no_hardcoded_secrets.md`, nunca inclua suas chaves de API ou outras credenciais diretamente no código-fonte. Sempre use variáveis de ambiente ou um sistema de gerenciamento de segredos.
*   **Row Level Security (RLS):** A chave pública `anon` respeita as políticas de Row Level Security (RLS) configuradas no seu projeto Supabase. Certifique-se de que as políticas de RLS estão configuradas corretamente para controlar quais dados cada usuário (ou a chave `anon`) pode acessar, inserir, atualizar ou deletar.
*   **Princípio do Menor Privilégio:** Para aplicações que necessitam de acesso mais restrito ou permissões específicas, considere criar novas chaves de API com permissões limitadas ou configurar autenticação de usuário e RLS granular em vez de usar a chave `anon` para todas as operações.

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
