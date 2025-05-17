# TinyERP API Integration — Special Cases and Best Practices

## 1. Authentication and Tokens

- Use OAuth 2.0 to obtain the access token.
- Tokens are stored in `tiny_token.json` (NEVER version this file).
- Implement automatic token refresh logic on 401 errors.

## 2. Fetching Markers (`marcadores`)

- **Problem:** The OS detail endpoint (`/ordem-servico/{id}`) does NOT return markers.
- **Solution:** 
  - Use the listing endpoint (`/ordem-servico?dataInicialEmissao=...&dataFinalEmissao=...`) to get OS lists with markers.
  - Merge the markers from the listing with the detailed OS data in the database.
  - Affected scripts: `fetch_historical_orders.py`, `update_orders_with_tags.py`.
- **Recommendation:** Always run the marker update script after large historical loads.

## 3. Equipment Serial (`equipamentoSerie`)

- **Problem:** Field present in the API schema, but often returns empty.
- **Diagnosis:** Ticket opened with TinyERP support.
- **Workaround:** Preserve the existing value in the database if the field is empty in the API response.

## 4. Rate Limiting and Pagination

- **Limit:** 120 requests/minute (60 GET, 60 PUT).
- **Solution:** Use `time.sleep(1)` between requests and process in batches.
- **Pagination:** Use `limit` and `offset` parameters to fetch all results.

## 5. Handling 401 Errors (Authorization)

- **Cause:** Expired or invalid token.
- **Solution:** Detect 401 errors, refresh the token, and retry the request.

## 6. Other Problematic Fields

- **Example:** Custom or nested fields may change name or format without notice.
- **Recommendation:** Always validate field presence before accessing and use structured logging for troubleshooting.

---

## Marker Processing and Client Origin Extraction

After fetching markers for each OS, you should parse the marker list and, if any marker indicates the client origin (such as `"txmidia"`, `"cliente existente"`, `"indicação"`, `"origem:social"`, `"origem:gpt"`, `"origem:local"`), update the `origem_cliente` field in the database for that OS.

**Example code:**

```python
def update_client_origin_from_markers(conn, os_id, markers):
    # List of possible client origin markers (case-insensitive, accents ignored)
    origin_keywords = [
        "txmidia", "cliente existente", "indicação",
        "origem:social", "origem:gpt", "origem:local"
    ]
    # Normalize markers for comparison
    def normalize(s):
        import unicodedata
        return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII').lower()
    normalized_markers = [normalize(m) for m in markers]
    # Find the first marker that matches any origin keyword
    found = None
    for keyword in origin_keywords:
        for marker in normalized_markers:
            if keyword in marker:
                found = marker
                break
        if found:
            break
    if found:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE ordens_servico SET origem_cliente = %s WHERE id = %s""",
            (found, os_id)
        )
        conn.commit()
        cursor.close()
```

**Best practice:**  
- Run this logic after updating markers for each OS, or as a dedicated post-processing step.
- Always log updates and handle cases where multiple origin markers are present.

---

## Example: Fetching Markers

```python
def get_orders_with_tags(token, start_date, end_date):
    url = f"https://api.tiny.com.br/public-api/v3/ordem-servico"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "dataInicialEmissao": start_date,
        "dataFinalEmissao": end_date,
        "limit": 100,
        "offset": 0
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    # Each item in data['itens'] will have its markers in item['marcadores']
    return [(item['id'], item.get('marcadores', [])) for item in data.get('itens', [])]
```

---

## Best Practices

- Never overwrite existing values in the database with null values from the API.
- Always log update attempts and errors for problematic fields.
- Keep marker update scripts independent for easier maintenance and reprocessing.

---

*Last reviewed: 2025-05-12*
