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

# API endpoint for Tiny ERP API v3
base_url = "https://api.tiny.com.br/public-api/v3"
endpoint = f"{base_url}/ordem-servico"

# Set up headers with the access token
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# --- Fetch detailed data for orders listed in latest_10_orders.json ---

# Load the IDs from the previously fetched list
try:
    with open('latest_10_orders.json', 'r') as f:
        initial_data = json.load(f)
    
    # Extract order IDs - handle potential structure variations
    order_ids = []
    if 'itens' in initial_data:
        order_ids = [order.get('id') for order in initial_data['itens'] if order.get('id')]
    elif 'retorno' in initial_data and 'ordens_servico' in initial_data['retorno']:
         order_ids = [order.get('id') for order in initial_data['retorno']['ordens_servico'] if order.get('id')]
    else:
        print("Could not find order IDs in latest_10_orders.json. Unexpected format.")
        print(json.dumps(initial_data, indent=2))
        sys.exit(1)
        
    if not order_ids:
        print("No valid order IDs found in latest_10_orders.json.")
        sys.exit(1)
        
    print(f"Found {len(order_ids)} order IDs to fetch details for.")

except FileNotFoundError:
    print("Error: latest_10_orders.json not found. Please run the script first without modifications to generate it.")
    sys.exit(1)
except Exception as e:
    print(f"Error reading or parsing latest_10_orders.json: {e}")
    sys.exit(1)

# List to store detailed order data
detailed_orders_data = []

# Loop through each order ID and fetch its details
print("\nFetching detailed data for each order...")
for order_id in order_ids:
    order_endpoint = f"{base_url}/ordem-servico/{order_id}"
    try:
        print(f"  Fetching details for Order ID: {order_id}...")
        response = requests.get(order_endpoint, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the JSON response
        order_details = response.json()
        
        # Extract the relevant order data based on observed actual response
        # Check if 'id' exists as a basic validation it's order data
        if 'id' in order_details and order_details['id'] == order_id: 
            detailed_orders_data.append(order_details)
            print(f"    Successfully fetched details for Order ID: {order_id}")
        else:
            # It might be an error response or unexpected format
            print(f"    Warning: Unexpected response format or missing ID for Order ID {order_id}.")
            print(f"    Response: {json.dumps(order_details, indent=2)}")
            
    except requests.exceptions.RequestException as e:
        print(f"    Error fetching details for Order ID {order_id}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"    Response status code: {e.response.status_code}")
            print(f"    Response text: {e.response.text}")
        # Continue to the next order even if one fails
    except Exception as e:
        print(f"    An unexpected error occurred for Order ID {order_id}: {e}")
        # Continue to the next order

# Save the collected detailed data to a new file
output_filename = 'detailed_10_orders.json'
try:
    with open(output_filename, 'w') as f:
        json.dump({"detailed_orders": detailed_orders_data}, f, indent=2)
    print(f"\nSuccessfully saved detailed data for {len(detailed_orders_data)} orders to {output_filename}")
    
    # Optional: Print a summary if needed
    # print("\nSummary of fetched detailed orders:")
    # for order in detailed_orders_data:
    #     print(f"  Order {order.get('numeroOrdemServico', 'N/A')}: {len(order.get('itens', []))} items")

except Exception as e:
    print(f"Error saving detailed data to {output_filename}: {e}")
    sys.exit(1)

# --- Original code for fetching the list is now replaced by the detailed fetch ---

# Original exception handling (can be kept or merged if needed)
# except requests.exceptions.RequestException as e:
#     print(f"API request error: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response status code: {e.response.status_code}")
        print(f"Response text: {e.response.text}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
