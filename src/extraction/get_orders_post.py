import json
import requests
import sys

# Load the access token from the token file
try:
    with open('tiny_token.json', 'r') as f:
        token_data = json.load(f)
    access_token = token_data.get('access_token')
    if not access_token:
        print("Error: No access token found in tiny_token.json")
        sys.exit(1)
except Exception as e:
    print(f"Error loading token file: {e}")
    sys.exit(1)

# Try different API endpoints
endpoints = [
    "https://api.tiny.com.br/api2/ordens.servico.pesquisa.php",
    "https://api.tiny.com.br/api2/ordem.servico.pesquisa.php",
    "https://api.tiny.com.br/api2/ordem.servico.obter.php",
    "https://api.tiny.com.br/api2/ordem.servico.listar.php"
]

# Try different request formats
for endpoint in endpoints:
    print(f"\nTrying endpoint: {endpoint}")
    
    # Format 1: Token in request body
    data = {
        "token": access_token,
        "situacao": "3 - Finalizada",
        "formato": "JSON",
        "limite": 10
    }
    
    try:
        print("Making POST request with token in body...")
        response = requests.post(endpoint, data=data)
        
        # Check if the response is valid JSON
        try:
            result = response.json()
            print("Received valid JSON response!")
            
            # Save the full JSON response to a file
            with open('latest_10_orders.json', 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Full JSON response saved to latest_10_orders.json")
            
            # Print a summary of the orders
            print("\nSummary of the 10 most recent closed/finished orders:")
            print("=" * 80)
            
            # Try to extract order information based on different possible response structures
            if 'retorno' in result and 'ordens_servico' in result['retorno']:
                orders = result['retorno']['ordens_servico']
                print(f"{'Order Number':<15} {'Client Name':<30} {'Completion Date':<20}")
                print("-" * 80)
                for order in orders:
                    order_number = order.get('numeroOrdemServico', 'N/A')
                    client_name = order.get('nomeContato', 'N/A')
                    completion_date = order.get('dataConclusao', 'N/A')
                    print(f"{order_number:<15} {client_name:<30} {completion_date:<20}")
            elif 'retorno' in result and 'ordem_servico' in result['retorno']:
                order = result['retorno']['ordem_servico']
                print(f"{'Order Number':<15} {'Client Name':<30} {'Completion Date':<20}")
                print("-" * 80)
                order_number = order.get('numeroOrdemServico', 'N/A')
                client_name = order.get('nomeContato', 'N/A')
                completion_date = order.get('dataConclusao', 'N/A')
                print(f"{order_number:<15} {client_name:<30} {completion_date:<20}")
            elif 'itens' in result:
                orders = result['itens']
                print(f"{'Order Number':<15} {'Client Name':<30} {'Completion Date':<20}")
                print("-" * 80)
                for order in orders:
                    order_number = order.get('numeroOrdemServico', 'N/A')
                    client_name = order.get('nomeContato', 'N/A')
                    completion_date = order.get('dataConclusao', 'N/A')
                    print(f"{order_number:<15} {client_name:<30} {completion_date:<20}")
            else:
                print("Unexpected response format. Check the JSON file for details.")
                print(json.dumps(result, indent=2))
            
            # If we got a successful response, exit the loop
            sys.exit(0)
            
        except json.JSONDecodeError:
            print(f"Response is not valid JSON: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response text: {e.response.text}")

# If all endpoints fail, exit with an error
print("\nAll API endpoints failed. Please check your token and try again.")
sys.exit(1)
