# Project Summary: TinyERP Service Order Analysis & Local DB

## Objective
The primary goal is to extract detailed service order data from TinyERP via its API v3 and store it in a local, robust database (PostgreSQL). This database will serve as a foundation for analysis, reporting (dashboards), CRM integration, and other applications, with the capability to be containerized using Docker in the future.

## Constraints & Key Information
- **API Rate Limit:** TinyERP API has a limit of 120 requests per minute (60 GET, 60 PUT).
- **Data Volume:** Target is to extract and maintain ~31,000+ service orders, with daily updates.
- **Data Structure:** The database must handle relationships (Orders, Contacts, Addresses, etc.) and allow for custom categorization fields.
- **Relevant Fields:** A comprehensive list of fields to extract from the API is documented in `docs/conhecimento.txt`. Specific attention needed for `equipamentoSerie` and `marcadores`.
- **Service Order Statuses:** Various statuses exist (e.g., Finalizada, Em andamento, Aprovada).
- **Documentation:** API documentation is available in the `/docs` folder (`Tiny_API_Documentation.md`, `doc_TinyAPI_v3.md`).
- **Unicode:** Data must be handled correctly (UTF-8) to preserve special characters and accents.

## Progress So Far
- **Authentication:** Successfully authenticated with the TinyERP API using OAuth 2.0 (`src/tiny_auth_server.py`, `tiny_token.json`).
- **Initial Data Fetch:** Scripts (`src/get_orders.py`, `src/get_orders_post.py`, `src/get_orders_v3.py`, `src/fetch_orders_april.py`) developed to fetch service orders.
- **Basic Order List:** Successfully retrieved a list of the latest 10 service orders (`latest_10_orders.json`).
- **Detailed Order Fetch:** Script `src/get_orders_v3.py` successfully fetches detailed data for specific order IDs using `GET /ordem-servico/{idOrdemServico}` and saves to `detailed_10_orders.json`.
- **API Field Investigation:**
    - Confirmed `equipamentoSerie` is in the API response schema but returned empty in tests.
    - Confirmed `marcadores` is *not* in the standard response schema for `GET /ordem-servico/{idOrdemServico}`.
    - Generated a report (`report_tiny_support.txt`) for Tiny ERP support regarding these field issues.
- **Knowledge Base:** Created `docs/conhecimento.txt` to document project details, API fields, and statuses.
- **Version Control:** Initialized a Git repository in the project directory.
- **Database Setup (Local PostgreSQL):**
    - Installed PostgreSQL using Homebrew.
    - Started the PostgreSQL service.
    - Created the `tiny_os_data` database.
    - Installed `psycopg2-binary` Python dependency.
    - Defined the database schema in `db/schema.sql` and created the tables.
    - Created `src/db_utils.py` for database connection handling.
    - Created `src/process_data.py` with logic to read JSON data and insert/update into the database.
- **Data Import:** Successfully extracted 120 finalized service orders from April 2025 using `src/fetch_orders_april.py` and saved to `orders_april_finalizadas.json`. These orders were then successfully processed and inserted into the PostgreSQL database using `src/process_data.py`.
- **Web Interface Data Display:** Successfully configured the web interface (`web_interface/`) to connect to and display April service orders from the Supabase PostgreSQL database.

## Current Plan & Next Steps

1.  **Full Extraction & Database Completion:**
    *   Modify the script to capture all service orders from 2013 to today to complete the database.
    *   Adapt scripts to handle API pagination and rate limits to fetch *all* 31k+ orders.
    *   Set up a mechanism (e.g., `cron`) for daily data updates.
2.  **Optimize Report Access Interface:**
    *   Optimize the web interface for efficient access and display of the full report data.
3.  **Dockerization:**
    *   Create `Dockerfile` for the Python application.
    *   Create `docker-compose.yml` to manage the Python app and PostgreSQL containers.
4.  **Address `marcadores` and `equipamentoSerie`:**
    *   Follow up on the support ticket with Tiny ERP regarding the API issues with these fields.
    *   Once a solution is available, update the extraction and processing scripts to correctly handle this data.

## Web Interface Plan (Supabase Backend)

5.  **Web Interface Development:**
    *   **Purpose:** Create a web interface to view, filter, and customize the display of service orders, connecting directly to the Supabase PostgreSQL database.
    *   **Backend:** **Supabase PostgreSQL Database** (replaces local Flask backend).
        *   Database schema replicated and initial data populated.
        *   Row Level Security (RLS) configured for read access.
        *   Frontend will interact directly with the Supabase API.
    *   **Frontend:** Use Vite + TypeScript + Tailwind CSS located in the `web_interface/` directory.
        *   `@supabase/supabase-js` client library installed and configured.
        *   Implemented data fetching and filtering logic using Supabase query methods.
        *   Implemented column selection using Supabase's `.select()` method.
        *   UI for filter inputs, column selection (checkboxes/multi-select), and dynamic data table rendering is in place.
        *   **Recent Improvements (July 2025):**
            *   Redesigned column selection UI to use buttons for better visualization.
            *   Configured table columns to update immediately upon column selection changes.
            *   Added functionality for users to adjust table column widths by dragging headers.
            *   Ensured 'ID' column is not displayed and 'Número OS' is always visible.
    *   **Build Tool:** Vite for frontend development and build process.

---

## [Error Log] Frontend Environment Issue (April/May 2025)

### Problem
Persistent error: **"npm error could not determine executable to run"** when running `npx tailwindcss init -p` in `web_interface`, even after cleaning and reinstalling dependencies.

### Troubleshooting Steps Attempted
1. Verified Node.js and npm installation (Node v22.14.0, npm v10.9.2).
2. Checked PATH and nvm configuration.
3. Cleaned npm cache.
4. Deleted and reinstalled node_modules and package-lock.json.
5. Reinstalled tailwindcss locally and globally.
6. Confirmed tailwindcss is present in package.json but not in node_modules/.bin.
7. Global tailwindcss binary not found in PATH after global install.
8. `npm bin -g` not recognized; `which tailwindcss` returns not found.
9. npx cannot find the executable to run.

### Analysis
- The issue is likely due to a misconfiguration or corruption in npm, nvm, or Node.js installation, or a problem with how binaries are linked on this system.
- The problem persists across both local and global installs, and even after full cleanups.

### Recommendations & Next Steps
- Consider switching to a stable LTS Node.js version (e.g., Node 20.x) using nvm.
- Reinstall Node.js and npm completely to ensure a clean environment.
- Ensure the global npm bin directory is in your PATH.
- Consult npm/nvm documentation for fixing global/local binary linking issues.
- If the problem persists, seek help on Stack Overflow or npm GitHub issues with the full error log.

---

*(Next immediate action: Resolve the npm/tailwindcss environment issue before proceeding with web interface development. All troubleshooting steps and findings are documented here for future reference.)*
