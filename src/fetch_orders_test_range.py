import requests
import json
import time
# Removed db_utils import as we are saving to local file

API_BASE = "https://api.tiny.com.br/public-api/v3"
TOKEN_FILE = "tiny_token.json"
TOKEN_FILE = "tiny_token.json"
# OUTPUT_FILE = "orders_test_range.json" # Temporary output file - Removed

def get_access_token():
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("access_token")

def fetch_order_ids(token, data_inicial, data_final):
    """Fetch order IDs for a specific date range using pagination."""
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "situacao": "3",  # Finalizada - assuming we test with finalized orders
        "dataInicialEmissao": data_inicial,
        "dataFinalEmissao": data_final,
        "limit": 100,
        "offset": 0
    }
    all_ids = []

    print(f"Fetching orders for {data_inicial} to {data_final}...")

    while True:
        resp = requests.get(f"{API_BASE}/ordem-servico", headers=headers, params=params)
        if resp.status_code != 200:
            print(f"Failed to fetch order list for {data_inicial} to {data_final}: {resp.status_code} {resp.text}")
            break
        data = resp.json()
        items = data.get("itens", [])
        if not items:
            break
        current_page_ids = [item["id"] for item in items if "id" in item]
        all_ids.extend(current_page_ids)
        print(f"Fetched {len(current_page_ids)} order IDs for {data_inicial} to {data_final} (total so far: {len(all_ids)})")

        if len(items) < params["limit"]:
            break
        params["offset"] += params["limit"]
        time.sleep(1) # Respect API rate limits for listing

    return all_ids

def fetch_order_details(token, order_ids):
    """Fetch detailed data for each order ID."""
    headers = {"Authorization": f"Bearer {token}"}
    detailed_orders = []
    for idx, order_id in enumerate(order_ids):
        url = f"{API_BASE}/ordem-servico/{order_id}"
        try:
            resp = requests.get(url, headers=headers)
            resp.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            order_data = resp.json()

            if isinstance(order_data, dict) and "id" in order_data:
                 detailed_orders.append(order_data)
            else:
                 print(f"Warning: Unexpected detail format for order {order_id}. Skipping.")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching details for Order ID {order_id}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status code: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            # Continue to the next order even if fetching one fails
        except Exception as e:
            print(f"An unexpected error occurred fetching details for Order ID {order_id}: {e}")
            # Continue to the next order

        time.sleep(1) # Increased delay to respect API rate limits

    return detailed_orders

def main():
    token = get_access_token()
    if not token:
        print("No access token found.")
        return

    # Set the specific date range for testing
    test_data_inicial = "2023-01-01"
    test_data_final = "2023-03-31"
    output_filename = "orders_jan_mar_2023.json"

    print(f"Fetching order IDs for {test_data_inicial} to {test_data_final}...")
    order_ids = fetch_order_ids(token, test_data_inicial, test_data_final)

    print(f"Total order IDs fetched: {len(order_ids)}")
    print("Fetching detailed data for each order...")
    detailed_orders = fetch_order_details(token, order_ids)

    print(f"Saving {len(detailed_orders)} detailed orders to {output_filename}")
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump({"detailed_orders": detailed_orders}, f, ensure_ascii=False, indent=2)
    print("Done.")

if __name__ == "__main__":
    main()
