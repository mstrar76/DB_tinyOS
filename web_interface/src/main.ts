import './style.css';
import { supabase } from './supabaseClient';
import { PostgrestError } from '@supabase/supabase-js';
import { logger } from './logger';

// Define types for the service order data
interface ServiceOrder {
  id: number;
  numero_ordem_servico: string;
  situacao: string;
  data_emissao: string;
  data_prevista: string | null;
  data_conclusao: string | null;
  total_servicos: number;
  total_ordem_servico: number;
  total_pecas: number;
  equipamento: string;
  equipamento_serie: string;
  descricao_problema: string;
  observacoes: string;
  observacoes_internas: string;
  orcar: string;
  orcado: string;
  alq_comissao: number;
  vlr_comissao: number;
  desconto: number;
  tecnico: string;
  id_contato: number | null;
  id_vendedor: number | null;
  id_categoria_os: number | null;
  id_forma_pagamento: number | null;
  linha_dispositivo: string;
  tipo_servico: string;
  origem_cliente: string;
  // Campos adicionados para dados do cliente e marcadores
  nome_cliente: string;
  telefone_cliente: string;
  email_cliente: string;
  marcadores: any[];
  // Add any other fields that may be present in the API response
  [key: string]: any;
}

// Define column metadata (display names, rendering functions, etc.)
interface ColumnMetadata {
  id: string;
  displayName: string;
  checked: boolean;
  render?: (value: any) => string;
}

// Define API response (Supabase returns data and error directly)
// interface ApiResponse {
//   data: ServiceOrder[];
//   error?: string;
// }

// Remove the API_BASE_URL as we are using Supabase directly
// const API_BASE_URL = 'http://localhost:5000/api';

// Status options for the select dropdown
const STATUS_OPTIONS = [
  { value: '', label: 'Todos' },
  { value: 'Em andamento', label: 'Em andamento' },
  { value: 'Finalizada', label: 'Finalizada' },
  { value: 'Aprovada', label: 'Aprovada' },
  { value: 'Cancelada', label: 'Cancelada' },
  // Add other statuses as necessary
];

// Column definitions
const COLUMNS: ColumnMetadata[] = [
  { id: 'numero_ordem_servico', displayName: 'Número OS', checked: true },
  { id: 'situacao', displayName: 'Status', checked: true },
  { id: 'data_emissao', displayName: 'Data Emissão', checked: true,
    render: (value) => value ? new Date(value).toLocaleDateString('pt-BR') : '-' },
  { id: 'nome_cliente', displayName: 'Nome do Cliente', checked: true,
    render: (value) => value || '-' },
  { id: 'telefone_cliente', displayName: 'Telefone', checked: true,
    render: (value) => value || '-' },
  { id: 'email_cliente', displayName: 'E-mail', checked: true,
    render: (value) => value || '-' },
  { id: 'marcadores', displayName: 'Marcadores', checked: true,
    render: (value) => {
      if (!value || !Array.isArray(value) || value.length === 0) return '-';
      return value.map((m: any) => m.nome || '').filter(Boolean).join(', ');
    }
  },
  { id: 'data_prevista', displayName: 'Data Prevista', checked: false,
    render: (value) => value ? new Date(value).toLocaleDateString('pt-BR') : '-' },
  { id: 'data_conclusao', displayName: 'Data Conclusão', checked: false,
    render: (value) => value ? new Date(value).toLocaleDateString('pt-BR') : '-' },
  { id: 'total_ordem_servico', displayName: 'Valor Total', checked: true,
    render: (value) => value ? `R$ ${value.toFixed(2)}`.replace('.', ',') : 'R$ 0,00' },
  { id: 'total_servicos', displayName: 'Valor Serviços', checked: false,
    render: (value) => value ? `R$ ${value.toFixed(2)}`.replace('.', ',') : 'R$ 0,00' },
  { id: 'total_pecas', displayName: 'Valor Peças', checked: false,
    render: (value) => value ? `R$ ${value.toFixed(2)}`.replace('.', ',') : 'R$ 0,00' },
  { id: 'equipamento', displayName: 'Equipamento', checked: true },
  { id: 'equipamento_serie', displayName: 'Série', checked: false },
  { id: 'tecnico', displayName: 'Técnico', checked: true },
  { id: 'linha_dispositivo', displayName: 'Linha/Dispositivo', checked: false },
  { id: 'tipo_servico', displayName: 'Tipo de Serviço', checked: false },
  { id: 'origem_cliente', displayName: 'Origem do Cliente', checked: false },
  { id: 'descricao_problema', displayName: 'Descrição do Problema', checked: false },
  { id: 'observacoes', displayName: 'Observações', checked: false },
  { id: 'observacoes_internas', displayName: 'Observações Internas', checked: false },
  // Add other columns as needed
];

// Current filter state
interface FilterState {
  dateFilter: string;
  startDate: string | null;
  endDate: string | null;
  status: string;
  dynamicField: string;
  dynamicValue: string;
}

// Create and initialize the filter state
let filterState: FilterState = {
  dateFilter: 'day', // Default to "today"
  startDate: null,
  endDate: null,
  status: '',
  dynamicField: '',
  dynamicValue: ''
};

// DOM Elements
const dateFilterSelect = document.getElementById('date-filter') as HTMLSelectElement;
const customDateRange = document.getElementById('custom-date-range') as HTMLDivElement;
const startDateInput = document.getElementById('start-date') as HTMLInputElement;
const endDateInput = document.getElementById('end-date') as HTMLInputElement;
const statusSelect = document.getElementById('status-filter') as HTMLSelectElement;
const dynamicFieldSelect = document.getElementById('dynamic-field-select') as HTMLSelectElement;
const dynamicFieldValue = document.getElementById('dynamic-field-value') as HTMLInputElement;
const clearFiltersButton = document.getElementById('clear-filters') as HTMLButtonElement;
const applyFiltersButton = document.getElementById('apply-filters') as HTMLButtonElement;
const columnButtonsContainer = document.getElementById('column-buttons') as HTMLDivElement;
const tableHeader = document.getElementById('table-header') as HTMLTableRowElement;
const tableBody = document.getElementById('table-body') as HTMLTableSectionElement;

// Variable to store the currently displayed service orders
let currentServiceOrders: ServiceOrder[] = [];

// Initialize the UI when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  // Setup status options
  setupStatusOptions();

  // Setup column buttons
  setupColumnButtons();

  // Setup event listeners
  setupEventListeners();

  // Initialize date inputs with default values
  initializeDateInputs();
});

// Setup status dropdown options
function setupStatusOptions(): void {
  STATUS_OPTIONS.forEach(option => {
    const optionElement = document.createElement('option');
    optionElement.value = option.value;
    optionElement.textContent = option.label;
    statusSelect.appendChild(optionElement);
  });
}

// Setup column buttons for selection
function setupColumnButtons(): void {
  // Clear existing buttons first
  columnButtonsContainer.innerHTML = '';

  // Filter out the 'id' column as it should not be selectable
  const selectableColumns = COLUMNS.filter(column => column.id !== 'id');

  selectableColumns.forEach(column => {
    // Skip 'numero_ordem_servico' as it should always be visible and not have a toggle button
    if (column.id === 'numero_ordem_servico') {
      // Ensure it's checked by default
      const osColumn = COLUMNS.find(c => c.id === 'numero_ordem_servico');
      if (osColumn) {
        osColumn.checked = true;
      }
      return;
    }

    const button = document.createElement('button');
    button.type = 'button';
    button.id = `column-btn-${column.id}`;
    // Add classes for button styling (using Tailwind)
    button.className = `px-3 py-1 text-sm font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 ${
      column.checked ? 'bg-indigo-600 text-white hover:bg-indigo-700' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
    }`;
    button.textContent = column.displayName;
    button.dataset.columnId = column.id;

    // Add event listener to toggle column visibility
    button.addEventListener('click', () => {
      const columnIndex = COLUMNS.findIndex(c => c.id === column.id);
      if (columnIndex !== -1) {
        // Toggle the checked state
        COLUMNS[columnIndex].checked = !COLUMNS[columnIndex].checked;
        // Update button style based on the new state
        button.className = `px-3 py-1 text-sm font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 ${
          COLUMNS[columnIndex].checked ? 'bg-indigo-600 text-white hover:bg-indigo-700' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
        }`;
        // Update the table header and repopulate the table immediately
        updateTableHeader();
        populateTable(currentServiceOrders);
      }
    });

    columnButtonsContainer.appendChild(button);
  });
}

// Setup all event listeners
function setupEventListeners(): void {
  // Date filter change
  dateFilterSelect.addEventListener('change', () => {
    filterState.dateFilter = dateFilterSelect.value;
    toggleCustomDateRange();
  });

  // Dynamic field select change
  dynamicFieldSelect.addEventListener('change', () => {
    filterState.dynamicField = dynamicFieldSelect.value;
    dynamicFieldValue.disabled = !filterState.dynamicField;
    dynamicFieldValue.placeholder = filterState.dynamicField
      ? 'Digite o valor para filtrar'
      : 'Selecione um campo primeiro';
    dynamicFieldValue.value = '';
    filterState.dynamicValue = '';
  });

  // Dynamic field value change
  dynamicFieldValue.addEventListener('input', () => {
    filterState.dynamicValue = dynamicFieldValue.value;
  });

  // Status filter change
  statusSelect.addEventListener('change', () => {
    filterState.status = statusSelect.value;
  });

  // Custom date inputs
  startDateInput.addEventListener('change', () => {
    filterState.startDate = startDateInput.value;
  });

  endDateInput.addEventListener('change', () => {
    filterState.endDate = endDateInput.value;
  });

  // Clear filters button
  clearFiltersButton.addEventListener('click', clearFilters);

  // Apply filters button
  applyFiltersButton.addEventListener('click', fetchData);
}

// Initialize date inputs with default values
function initializeDateInputs(): void {
  // Set today as the default end date for custom range
  const today = new Date();
  const formattedToday = formatDateForInput(today);
  endDateInput.value = formattedToday;
  filterState.endDate = formattedToday;

  // Set one month ago as the default start date for custom range
  const oneMonthAgo = new Date();
  oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1);
  const formattedOneMonthAgo = formatDateForInput(oneMonthAgo);
  startDateInput.value = formattedOneMonthAgo;
  filterState.startDate = formattedOneMonthAgo;

  // Update display based on selected date filter
  toggleCustomDateRange();
}

// Format date for input fields (YYYY-MM-DD)
function formatDateForInput(date: Date): string {
  return date.toISOString().split('T')[0];
}

// Toggle custom date range visibility based on date filter selection
function toggleCustomDateRange(): void {
  if (filterState.dateFilter === 'custom') {
    customDateRange.classList.remove('hidden');
  } else {
    customDateRange.classList.add('hidden');

    // Calculate start and end dates based on selection
    const today = new Date();
    let startDate = new Date();

    switch (filterState.dateFilter) {
      case 'day':
        // Today (start and end date are the same)
        startDate = new Date(today);
        break;
      case 'week':
        // Last 7 days
        startDate.setDate(today.getDate() - 7);
        break;
      case 'month':
        // Last 30 days
        startDate.setDate(today.getDate() - 30);
        break;
      default:
        startDate = new Date(today);
        break;
    }

    // Update filter state
    filterState.startDate = formatDateForInput(startDate);
    filterState.endDate = formatDateForInput(today);
  }
}

// Clear all filters
function clearFilters(): void {
  // Reset filter state
  filterState = {
    dateFilter: 'day',
    startDate: formatDateForInput(new Date()),
    endDate: formatDateForInput(new Date()),
    status: '',
    dynamicField: '',
    dynamicValue: ''
  };

  // Reset UI controls
  dateFilterSelect.value = filterState.dateFilter;
  statusSelect.value = filterState.status;
  dynamicFieldSelect.value = filterState.dynamicField;
  dynamicFieldValue.value = filterState.dynamicValue;
  dynamicFieldValue.disabled = true;
  dynamicFieldValue.placeholder = 'Selecione um campo primeiro';

  // Hide custom date range
  toggleCustomDateRange();

  // Clear the table and show message
  tableBody.innerHTML = `
    <tr>
      <td colspan="100%" class="px-6 py-4 text-center text-gray-500">
        Filtros limpos. Clique em "Aplicar Filtros" para buscar dados.
      </td>
    </tr>
  `;
}

// Update the table header based on selected columns
function updateTableHeader(): void {
  // Clear existing headers
  tableHeader.innerHTML = '';

  // Add headers for selected columns
  COLUMNS.filter(column => column.checked).forEach(column => {
    const th = document.createElement('th');
    th.className = 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider';
    th.textContent = column.displayName;

    // Add resize handle
    const resizeHandle = document.createElement('div');
    resizeHandle.className = 'resize-handle';
    resizeHandle.dataset.columnId = column.id; // Store column ID for reference

    // Append handle to the header
    th.appendChild(resizeHandle);

    tableHeader.appendChild(th);

    // Add event listener for resizing
    resizeHandle.addEventListener('mousedown', startResize);
  });
}

// Variables to track resizing state
let currentResizer: HTMLElement | null = null;
let startX: number = 0;
let startWidth: number = 0;
let currentColumn: HTMLTableCellElement | null = null;

// Function to start resizing
function startResize(e: MouseEvent): void {
  currentResizer = e.target as HTMLElement;
  currentColumn = currentResizer.parentElement as HTMLTableCellElement;
  startX = e.clientX;
  startWidth = currentColumn.offsetWidth;

  // Add event listeners to the document for dragging
  document.addEventListener('mousemove', resizeColumn);
  document.addEventListener('mouseup', stopResize);
}

// Function to handle column resizing
function resizeColumn(e: MouseEvent): void {
  if (currentColumn) {
    const diffX = e.clientX - startX;
    // Ensure minimum width (e.g., 50px)
    currentColumn.style.width = `${Math.max(50, startWidth + diffX)}px`;
  }
}

// Function to stop resizing
function stopResize(): void {
  // Remove event listeners from the document
  document.removeEventListener('mousemove', resizeColumn);
  document.removeEventListener('mouseup', stopResize);

  // Reset state
  currentResizer = null;
  currentColumn = null;
}

// Build query parameters for API request (No longer needed for Supabase direct access)
// function buildQueryParams(): URLSearchParams { ... }


// Fetch data from Supabase
async function fetchData(): Promise<void> {
  logger.info('Iniciando busca de dados', { filters: filterState });
  try {
    // Show loading state
    tableBody.innerHTML = `
      <tr>
        <td colspan="100%" class="px-6 py-4 text-center text-gray-500">
          Carregando dados...
        </td>
      </tr>
    `;

    // Verificar se o cliente Supabase está inicializado
    if (!supabase) {
      logger.error('Cliente Supabase não inicializado');
      throw new Error('Cliente Supabase não inicializado. Verifique as variáveis de ambiente.');
    }

    // Log das credenciais (apenas para debug, sem exibir valores sensíveis)
    logger.debug('Verificando configuração do Supabase', {
      urlConfigured: !!import.meta.env.VITE_SUPABASE_URL,
      keyConfigured: !!import.meta.env.VITE_SUPABASE_ANON_KEY,
      tableTarget: 'ordens_servico'
    });

    // Start building the Supabase query com join apenas para obter dados do cliente
    // Simplificando para evitar erro de relacionamento com marcadores
    let query = supabase.from('ordens_servico').select(`
      id,
      numero_ordem_servico,
      situacao,
      data_emissao,
      data_prevista,
      data_conclusao,
      total_servicos,
      total_ordem_servico,
      total_pecas,
      equipamento,
      equipamento_serie,
      tecnico,
      linha_dispositivo,
      tipo_servico,
      origem_cliente,
      descricao_problema,
      observacoes,
      observacoes_internas,
      contatos:id_contato (nome, celular, email)
    `);

    // Apply filters
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
      // Use ilike for case-insensitive partial matching for text fields
      query = query.ilike(filterState.dynamicField, `%${filterState.dynamicValue}%`);
    }

    logger.debug('Query Supabase construída', {
      filters: {
        startDate: filterState.startDate,
        endDate: filterState.endDate,
        status: filterState.status,
        dynamicField: filterState.dynamicField,
        dynamicValue: filterState.dynamicValue
      },
      columns: COLUMNS.filter(column => column.checked).map(column => column.id)
    });

    // Execute the query
    const { data, error } = await query;

    logger.info('Resposta recebida do Supabase', { 
      dataCount: data ? data.length : 0,
      hasError: !!error 
    });
    
    if (error) {
      logger.error('Erro na consulta Supabase', { 
        errorMessage: error.message,
        errorCode: error.code,
        details: error.details,
        hint: error.hint
      });
      throw new Error(`Erro ao consultar o Supabase: ${error.message}`);
    }

    // Processar os dados para trazer informações dos relacionamentos para o nível principal
    const serviceOrders: ServiceOrder[] = (data || []).map((order: any) => {
      // Extrair dados de contato para campos de nível superior
      const processedOrder: any = {
        ...order,
        nome_cliente: order.contatos?.nome || '-',
        telefone_cliente: order.contatos?.celular || '-',
        email_cliente: order.contatos?.email || '-'
      };

      // Buscar marcadores para cada ordem de serviço
      processedOrder.marcadores = [];

      return processedOrder;
    });

    // Após montar os serviceOrders, buscar marcadores para cada ordem
    for (const order of serviceOrders) {
      try {
        const { data: marcadoresData, error: marcadoresError } = await supabase
          .from('marcadores_ordem_servico')
          .select('descricao')
          .eq('id_ordem_servico', order.id);
        if (marcadoresError) {
          logger.warn('Erro ao buscar marcadores', { ordem: order.id, error: marcadoresError.message });
          order.marcadores = [];
        } else {
          // Garante um array de descrições
          order.marcadores = (marcadoresData || []).map(m => ({ nome: m.descricao }));
        }
      } catch (err: any) {
        logger.error('Exceção ao buscar marcadores', { ordem: order.id, errorMessage: err.message, stack: err.stack });
        order.marcadores = [];
      }
    }

    // Store the fetched data
    currentServiceOrders = serviceOrders;

    // Update the table header
    updateTableHeader();

    // Populate the table
    populateTable(currentServiceOrders);
    logger.info('Tabela populada com sucesso', { recordCount: serviceOrders.length });

  } catch (error: any) { // Explicitly type error for better handling
    logger.error('Erro ao buscar dados', { 
      errorMessage: error.message,
      stack: error.stack
    });

    // Show error message
    tableBody.innerHTML = `
      <tr>
        <td colspan="100%" class="px-6 py-4 text-center text-red-500">
          Erro ao buscar dados: ${error.message}<br>
          Por favor, verifique a configuração do Supabase e tente novamente.
        </td>
      </tr>
    `;
  }
}

// Populate the table with data
function populateTable(data: ServiceOrder[]): void {
  // Clear existing rows
  tableBody.innerHTML = '';
  
  if (data.length === 0) {
    // Show message for no data
    tableBody.innerHTML = `
      <tr>
        <td colspan="100%" class="px-6 py-4 text-center text-gray-500">
          Nenhum resultado encontrado para os filtros aplicados.
        </td>
      </tr>
    `;
    return;
  }
  
  // Get visible columns
  const visibleColumns = COLUMNS.filter(column => column.checked);
  
  // Calcula totais
  let totalOrdem = 0;
  let totalServico = 0;
  let totalPecas = 0;

  // Create a row for each service order
  data.forEach(order => {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-gray-50';
    
    // Soma os valores se existirem
    totalOrdem += typeof order.total_ordem_servico === 'number' ? order.total_ordem_servico : 0;
    totalServico += typeof order.total_servicos === 'number' ? order.total_servicos : 0;
    totalPecas += typeof order.total_pecas === 'number' ? order.total_pecas : 0;

    // Add cells for each visible column
    visibleColumns.forEach(column => {
      const td = document.createElement('td');
      td.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-900';
      
      // Get raw value
      const value = order[column.id];
      
      // Use render function if available or default to the raw value
      td.textContent = column.render ? column.render(value) : (value || '-');
      
      tr.appendChild(td);
    });
    
    tableBody.appendChild(tr);
  });

  // Atualiza rodapé
  const totalOrders = data.length;
  const formatCurrency = (v: number) => `R$ ${v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  const elTotalOrders = document.getElementById('total-orders');
  const elTotalOrdem = document.getElementById('total-valor-ordem');
  const elTotalServico = document.getElementById('total-valor-servico');
  const elTotalPecas = document.getElementById('total-valor-pecas');
  if (elTotalOrders) elTotalOrders.textContent = `Total de ordens: ${totalOrders}`;
  if (elTotalOrdem) elTotalOrdem.textContent = `Valor Total: ${formatCurrency(totalOrdem)}`;
  if (elTotalServico) elTotalServico.textContent = `Valor Serviços: ${formatCurrency(totalServico)}`;
  if (elTotalPecas) elTotalPecas.textContent = `Valor Peças: ${formatCurrency(totalPecas)}`;
}

// Initialize the page - first time setup
updateTableHeader();
toggleCustomDateRange();
