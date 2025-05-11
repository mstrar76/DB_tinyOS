DOntimport json
import csv
import sys

# Load the JSON data
try:
    with open('latest_10_orders.json', 'r') as f:
        data = json.load(f)
except Exception as e:
    print(f"Error loading JSON file: {e}")
    sys.exit(1)

# Check if the data has the expected structure
if 'itens' not in data:
    print("Unexpected JSON structure. 'itens' field not found.")
    sys.exit(1)

# Extract the orders
orders = data['itens']

# Define the CSV file path
csv_file = 'latest_10_orders.csv'

# Define the fields to include in the CSV
fields = [
    'id', 'numeroOrdemServico', 'situacao', 'data', 'dataPrevista', 'valor',
    'cliente_id', 'cliente_nome', 'cliente_codigo', 'cliente_fantasia', 'cliente_tipoPessoa',
    'cliente_cpfCnpj', 'cliente_inscricaoEstadual', 'cliente_rg', 'cliente_telefone',
    'cliente_celular', 'cliente_email',
    'cliente_endereco', 'cliente_numero', 'cliente_complemento', 'cliente_bairro',
    'cliente_municipio', 'cliente_cep', 'cliente_uf', 'cliente_pais',
    'marcadores'
]

# Write the data to a CSV file
try:
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        
        for order in orders:
            # Extract client information
            cliente = order.get('cliente', {})
            endereco = cliente.get('endereco', {})
            
            # Extract marcadores (tags)
            marcadores = order.get('marcadores', [])
            marcadores_str = ', '.join([m.get('descricao', '') for m in marcadores])
            
            # Create a row for the CSV
            row = {
                'id': order.get('id', ''),
                'numeroOrdemServico': order.get('numeroOrdemServico', ''),
                'situacao': order.get('situacao', ''),
                'data': order.get('data', ''),
                'dataPrevista': order.get('dataPrevista', ''),
                'valor': order.get('valor', ''),
                'cliente_id': cliente.get('id', ''),
                'cliente_nome': cliente.get('nome', ''),
                'cliente_codigo': cliente.get('codigo', ''),
                'cliente_fantasia': cliente.get('fantasia', ''),
                'cliente_tipoPessoa': cliente.get('tipoPessoa', ''),
                'cliente_cpfCnpj': cliente.get('cpfCnpj', ''),
                'cliente_inscricaoEstadual': cliente.get('inscricaoEstadual', ''),
                'cliente_rg': cliente.get('rg', ''),
                'cliente_telefone': cliente.get('telefone', ''),
                'cliente_celular': cliente.get('celular', ''),
                'cliente_email': cliente.get('email', ''),
                'cliente_endereco': endereco.get('endereco', ''),
                'cliente_numero': endereco.get('numero', ''),
                'cliente_complemento': endereco.get('complemento', ''),
                'cliente_bairro': endereco.get('bairro', ''),
                'cliente_municipio': endereco.get('municipio', ''),
                'cliente_cep': endereco.get('cep', ''),
                'cliente_uf': endereco.get('uf', ''),
                'cliente_pais': endereco.get('pais', ''),
                'marcadores': marcadores_str
            }
            
            writer.writerow(row)
    
    print(f"CSV file created successfully: {csv_file}")
    
except Exception as e:
    print(f"Error creating CSV file: {e}")
    sys.exit(1)
