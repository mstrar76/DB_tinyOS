import requests
import json
import os
import logging
from datetime import datetime

API_BASE = "https://api.tiny.com.br/public-api/v3"
TOKEN_FILE = "tiny_token.json"
ORDER_IDS = [470608429, 470270569, 472283512, 504433724]
OUTPUT_DIR = "order_api_responses"

# Structured JSON logging setup
def setup_logger():
    logger = logging.getLogger("check_orders_api")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "service": "check_orders_api", "message": %(message)s}'
    )
    handler.setFormatter(formatter)
    logger.handlers = [handler]
    return logger

logger = setup_logger()

def get_access_token():
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("access_token")
    except Exception as e:
        logger.error(json.dumps({"error": f"Failed to read token: {e}"}))
        return None

def fetch_order(order_id, token):
    url = f"{API_BASE}/ordem-servico/{order_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response

def save_json(order_id, data):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    out_path = os.path.join(OUTPUT_DIR, f"order_{order_id}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(json.dumps({"order_id": order_id, "saved_to": out_path}))

def highlight_suspect_fields(order_data):
    # List of fields that are likely to be CHAR(1) in DB
    suspect_fields = ["status", "tipo", "tipo_frete", "cancelado", "devolvido", "tipo_desconto"]
    issues = []
    def check_field(obj, prefix=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in suspect_fields and isinstance(v, str) and len(v) > 1:
                    issues.append({"field": prefix + k, "value": v, "length": len(v)})
                check_field(v, prefix + k + ".")
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                check_field(item, prefix + f"[{idx}].")
    check_field(order_data)
    return issues

def main():
    token = get_access_token()
    if not token:
        logger.error(json.dumps({"error": "No access token found. Aborting."}))
        return
    for order_id in ORDER_IDS:
        logger.info(json.dumps({"action": "fetch_order", "order_id": order_id}))
        try:
            resp = fetch_order(order_id, token)
            if resp.status_code == 200:
                data = resp.json()
                save_json(order_id, data)
                issues = highlight_suspect_fields(data)
                if issues:
                    logger.warning(json.dumps({"order_id": order_id, "suspect_fields": issues}))
                else:
                    logger.info(json.dumps({"order_id": order_id, "message": "No suspect fields found."}))
            else:
                logger.error(json.dumps({"order_id": order_id, "status_code": resp.status_code, "response": resp.text}))
        except Exception as e:
            logger.error(json.dumps({"order_id": order_id, "error": str(e)}))

if __name__ == "__main__":
    main()
