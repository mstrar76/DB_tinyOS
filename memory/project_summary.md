# Project Summary: TinyERP Service Order Analysis

## Objective
The primary goal is to create a local database containing detailed information from TinyERP service orders. This database will be used for generating reports and dashboards to analyze service order data.

## Constraints & Key Information
- **API Rate Limit:** TinyERP API has a limit of 120 requests per minute (60 GET, 60 PUT).
- **Data Structure:** The database must handle multiple items (products and services) per service order (1:N relationship).
- **Relevant Fields:** A comprehensive list of fields to extract from the API is documented in `docs/conhecimento.txt`.
- **Service Order Statuses:** Various statuses exist (e.g., Finalizada, Em andamento, Aprovada).
- **Documentation:** API documentation is available in the `/docs` folder.

## Progress So Far
- **Authentication:** Successfully authenticated with the TinyERP API using OAuth 2.0 (`tiny_auth_server.py`, `tiny_token.json`).
- **Initial Data Fetch:** Scripts (`get_orders.py`, `get_orders_post.py`, `get_orders_v3.py`) were developed to fetch service orders.
- **Basic Order Data:** Successfully retrieved a list of the latest 10 service orders, extracting initial fields (`id`, `numeroOrdemServico`, `data`, `situacao`) and saved them to `latest_10_orders.json`.
- **Knowledge Base:** Created `docs/conhecimento.txt` to document project details, API fields, and statuses.

## Next Steps
1.  Extract all remaining relevant fields (as listed in `docs/conhecimento.txt`) from the service orders already fetched in `latest_10_orders.json`.
2.  Modify the data fetching script (`get_orders_v3.py`) to retrieve all necessary fields in future requests.
3.  Develop functionality to store the extracted data in a structured format suitable for a local database (e.g., CSV, SQLite).
4.  Implement logic to handle pagination and API rate limits for fetching larger datasets.
