# Documentação da Interface Web do tinyOS

## Visão Geral

A interface web do projeto tinyOS permite visualizar e filtrar ordens de serviço armazenadas no banco de dados Supabase. O frontend é construído usando TypeScript, HTML e CSS com Tailwind CSS, e é executado através do Vite como servidor de desenvolvimento.

## Estrutura de Diretórios e Arquivos

```
web_interface/
├── .env                     # Variáveis de ambiente para conexão com o Supabase
├── index.html               # Página HTML principal com a estrutura da interface
├── package.json             # Configuração npm e dependências
├── public/                  # Arquivos estáticos
├── src/
│   ├── main.ts              # Código principal que controla a interface
│   ├── supabaseClient.ts    # Cliente de conexão ao Supabase
│   ├── logger.ts            # Sistema de logging estruturado
│   └── style.css            # Estilos CSS (com Tailwind)
└── tsconfig.json            # Configuração do TypeScript
```

## Componentes Principais

### 1. `supabaseClient.ts`

Este arquivo configura a conexão com o banco de dados Supabase. Ele inicializa o cliente Supabase usando as variáveis de ambiente do arquivo `.env`.

```typescript
import { createClient } from '@supabase/supabase-js';

// Carrega variáveis de ambiente do arquivo .env no diretório web_interface
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

// Verifica se as variáveis de ambiente foram carregadas
if (!supabaseUrl || !supabaseAnonKey) {
  console.error('Supabase URL and Anon Key environment variables are not set.');
}

// Cria uma instância do cliente Supabase
export const supabase = createClient(supabaseUrl, supabaseAnonKey);
```

### 2. `logger.ts`

Implementa um sistema de logging estruturado em formato JSON que facilita o diagnóstico de problemas e o monitoramento do sistema. Os logs incluem:
- Timestamps
- Níveis de severidade (debug, info, warn, error)
- Nome do serviço
- IDs de correlação para rastreamento
- Dados adicionais contextuais

```typescript
// Exemplo de uso
import { logger } from './logger';

logger.info('Iniciando busca de dados', { filters: filterState });
logger.error('Erro na conexão com Supabase', { errorMessage: error.message });
```

### 3. `main.ts`

O arquivo principal que controla a interface do usuário. Ele implementa:
- Definições de tipos para ordens de serviço e metadados de colunas
- Filtros de dados (data, status, campos personalizados)
- Controles para visibilidade de colunas
- Funcionalidade de busca e exibição de dados do Supabase
- Tratamento de erros com logging estruturado

## Configuração e Variáveis de Ambiente

Para que a interface web funcione corretamente, é necessário um arquivo `.env` no diretório `web_interface/` com as seguintes variáveis:

```
VITE_SUPABASE_URL="https://seu-projeto.supabase.co"
VITE_SUPABASE_ANON_KEY="sua-chave-anon-key"
```

**Importante:** Este arquivo `.env` deve estar incluído no `.gitignore` para evitar o versionamento de segredos.

## Conexão com o Supabase

1. **Inicialização da Conexão**: Ocorre no arquivo `supabaseClient.ts`, que lê as variáveis de ambiente e cria uma instância do cliente Supabase.

2. **Consulta de Dados**: No arquivo `main.ts`, a função `fetchData()` constrói e executa queries para o Supabase com base nos filtros selecionados pelo usuário:

```typescript
async function fetchData(): Promise<void> {
  try {
    // Inicia a construção da query
    let query = supabase.from('ordens_servico').select(
      COLUMNS.filter(column => column.checked).map(column => column.id).join(',') || '*'
    );

    // Aplica filtros
    if (filterState.startDate) {
      query = query.gte('data_emissao', filterState.startDate);
    }
    if (filterState.endDate) {
      query = query.lte('data_emissao', filterState.endDate);
    }
    if (filterState.status) {
      query = query.eq('situacao', filterState.status);
    }
    if (filterState.dynamicField && filterState.dynamicValue) {
      query = query.ilike(filterState.dynamicField, `%${filterState.dynamicValue}%`);
    }

    // Executa a query
    const { data, error } = await query;

    // Processa o resultado...
  } catch (error) {
    // Loga erros...
  }
}
```

## Sistema de Logging

O sistema de logging estruturado foi implementado para atender às necessidades de diagnóstico e monitoramento:

1. **Formato Estruturado**: Todos os logs são gerados em formato JSON, facilitando a análise e o processamento automatizado.

2. **Níveis de Severidade**: Cada log inclui um nível de severidade (debug, info, warn, error) para filtrar adequadamente.

3. **IDs de Correlação**: Cada instância do logger gera um ID único de correlação, permitindo rastrear requisições relacionadas.

4. **Contextualização**: Os logs podem incluir dados adicionais para fornecer contexto, como parâmetros de filtro, dados de resposta ou detalhes de erros.

## Funcionalidades do Rodapé Fixo

- O rodapé da interface web é fixo e permanece sempre visível, mesmo ao rolar a página.
- Os totais de valores (Valor Total, Valor Serviços, Valor Peças) só aparecem no rodapé quando as respectivas colunas estão visíveis na tabela. Se uma coluna de valor não estiver selecionada, o total correspondente não será exibido no rodapé.
- O rodapé é responsivo e se adapta ao tamanho da tela, garantindo boa visualização em diferentes dispositivos.
- O total de ordens exibidas permanece sempre visível no rodapé.

## Execução da Interface Web

Para iniciar o servidor de desenvolvimento:

1. Certifique-se de que o arquivo `.env` está configurado corretamente no diretório `web_interface/`.

2. Execute o comando no diretório `web_interface/`:
   ```bash
   npm run dev
   ```

3. Acesse a interface no navegador através do endereço fornecido (geralmente http://localhost:5173 ou similar).

## Solução de Problemas

Se a interface não estiver funcionando corretamente:

1. **Verificar Variáveis de Ambiente**: Certifique-se de que o arquivo `.env` existe no diretório `web_interface/` e contém as credenciais corretas do Supabase.

2. **Consultar Logs**: Abra o console do navegador (F12) para verificar os logs estruturados, que devem fornecer informações detalhadas sobre erros ou problemas de conexão.

3. **Verificar Conectividade**: Certifique-se de que o Supabase está acessível e que as políticas de segurança permitem acesso às tabelas necessárias.
