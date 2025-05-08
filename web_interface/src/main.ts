import './style.css';
import { supabase } from './supabaseClient';
import { PostgrestError } from '@supabase/supabase-js';

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
  { id: 'id', displayName: 'ID', checked: true },
  { id: 'numero_ordem_servico', displayName: 'Número OS', checked: true },
  { id: 'situacao', displayName: 'Status', checked: true },
  { id: 'data_emissao', displayName: 'Data Emissão', checked: true,
    render: (value) => value ? new Date(value).toLocaleDateString('pt-BR') : '-' },
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
const columnCheckboxesContainer = document.getElementById('column-checkboxes') as HTMLDivElement;
const tableHeader = document.getElementById('table-header') as HTMLTableRowElement;
const tableBody = document.getElementById('table-body') as HTMLTableSectionElement;

// Initialize the UI when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  // Setup status options
  setupStatusOptions();

  // Setup column checkboxes
  setupColumnCheckboxes();

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

// Setup column checkboxes for selection
function setupColumnCheckboxes(): void {
  // Clear existing checkboxes first
  columnCheckboxesContainer.innerHTML = '';

  // Create a checkbox for each column
  COLUMNS.forEach(column => {
    const checkboxDiv = document.createElement('div');
    checkboxDiv.className = 'flex items-start';

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.id = `column-${column.id}`;
    checkbox.className = 'h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500 mt-1';
    checkbox.checked = column.checked;
    checkbox.dataset.columnId = column.id;

    const label = document.createElement('label');
    label.htmlFor = `column-${column.id}`;
    label.className = 'ml-2 block text-sm text-gray-700';
    label.textContent = column.displayName;

    checkboxDiv.appendChild(checkbox);
    checkboxDiv.appendChild(label);
    columnCheckboxesContainer.appendChild(checkboxDiv);

    // Add event listener to update table when checkbox changes
    checkbox.addEventListener('change', () => {
      const columnIndex = COLUMNS.findIndex(c => c.id === column.id);
      if (columnIndex !== -1) {
        COLUMNS[columnIndex].checked = checkbox.checked;
        updateTableHeader();
      }
    });
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
    tableHeader.appendChild(th);
  });
}

// Build query parameters for API request (No longer needed for Supabase direct access)
// function buildQueryParams(): URLSearchParams { ... }


// Fetch data from Supabase
async function fetchData(): Promise<void> {
  console.log('fetchData function called');
  try {
    // Show loading state
    tableBody.innerHTML = `
      <tr>
        <td colspan="100%" class="px-6 py-4 text-center text-gray-500">
          Carregando dados...
        </td>
      </tr>
    `;

    // Start building the Supabase query
    let query = supabase.from('ordens_servico').select(
      COLUMNS.filter(column => column.checked).map(column => column.id).join(',') || '*' // Select all if none checked
    );

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
      // Adjust this logic based on the actual data types and desired matching for dynamic fields
      query = query.ilike(filterState.dynamicField, `%${filterState.dynamicValue}%`);
    }

    // Execute the query
    const { data, error } = await query;

    console.log('Supabase query data:', data);
    console.log('Type of data:', typeof data);

    if (error) {
      throw new Error(error.message);
    }

    // Explicitly type the data variable
    const serviceOrders: ServiceOrder[] = data || [];

    // Update the table header
    updateTableHeader();

    // Populate the table
    populateTable(serviceOrders);

  } catch (error: any) { // Explicitly type error for better handling
    console.error('Error fetching data:', error);

    // Show error message
    tableBody.innerHTML = `
      <tr>
        <td colspan="100%" class="px-6 py-4 text-center text-red-500">
          Erro ao buscar dados. Por favor, verifique a configuração do Supabase e tente novamente.
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
  
  // Create a row for each service order
  data.forEach(order => {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-gray-50';
    
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
}

// Initialize the page - first time setup
updateTableHeader();
toggleCustomDateRange();
