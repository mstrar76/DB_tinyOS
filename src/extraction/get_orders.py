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

# API endpoint and parameters
# Try different base URLs and endpoint formats
endpoints = [
    "https://api.tiny.com.br/api3/ordem-servico",
    "https://api.tiny.com.br/api2/ordem-servico",
    "https://erp.tiny.com.br/api3/ordem-servico",
    "https://erp.tiny.com.br/api2/ordem-servico",
    "https://api.tiny.com.br/api2/ordem-servico.listar.php",
    "https://api.tiny.com.br/api2/ordem-servico.obter.php"
]

# Try different authentication methods
auth_methods = [
    # Method 1: Bearer token in Authorization header
    {"headers": {"Authorization": f"Bearer {access_token}"}, "params": {}},
    # Method 2: Token in query parameters
    {"headers": {}, "params": {"token": access_token}}
]

success = False

for url in endpoints:
    print(f"\nTrying URL: {url}")
    
    for auth_method in auth_methods:
        print(f"Trying authentication method: {auth_method}")
        
        # Combine the authentication parameters with the search parameters
        headers = auth_method["headers"]
        params = {
            **auth_method["params"],
            "situacao": "3 - Finalizada",
            "limit": "10",
            "orderBy": "desc"
        }

        # Make the API request
        try:
            print("Making API request...")
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            # Parse the JSON response
            data = response.json()
            
            # Save the full JSON response to a file
            with open('latest_10_orders.json', 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Full JSON response saved to latest_10_orders.json")
            
            # Print a summary of the orders
            print("\nSummary of the 10 most recent closed/finished orders:")
            print("=" * 80)
            print(f"{'Order Number':<15} {'Client Name':<30} {'Completion Date':<20}")
            print("-" * 80)
            
            # Check if the response has the expected structure
            if 'itens' in data:
                orders = data['itens']
                for order in orders:
                    order_number = order.get('numeroOrdemServico', 'N/A')
                    client_name = order.get('nomeContato', 'N/A')
                    completion_date = order.get('dataConclusao', 'N/A')
                    print(f"{order_number:<15} {client_name:<30} {completion_date:<20}")
            elif 'retorno' in data and 'ordens_servico' in data['retorno']:
                orders = data['retorno']['ordens_servico']
                for order in orders:
                    order_number = order.get('numeroOrdemServico', 'N/A')
                    client_name = order.get('nomeContato', 'N/A')
                    completion_date = order.get('dataConclusao', 'N/A')
                    print(f"{order_number:<15} {client_name:<30} {completion_date:<20}")
            else:
                print("Unexpected response format. Check the JSON file for details.")
            
            # If we get a successful response, mark success and break the loop
            success = True
            break
            
        except requests.exceptions.RequestException as e:
            print(f"API request error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status code: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            # Continue to the next authentication method if this one fails
            continue
        except Exception as e:
            print(f"Error: {e}")
            # Continue to the next authentication method if this one fails
            continue
    
    # If we got a successful response, break the outer loop too
    if success:
        break

# If all URLs fail, exit with an error
if not success:
    print("\nAll API endpoints failed. Please check your token and try again.")
