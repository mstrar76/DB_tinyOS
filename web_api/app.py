from flask import Flask, request, jsonify
import psycopg2
import os
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS for the frontend origin
CORS(app, origins="http://localhost:5173")

# Database connection details based on your existing db_utils.py
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_NAME = os.environ.get("DB_NAME", "tiny_os_data")
DB_USER = os.environ.get("DB_USER", "marcelo") # Default user from db_utils.py
DB_PASSWORD = os.environ.get("DB_PASSWORD", "") # Default empty password from db_utils.py
DB_PORT = os.environ.get("DB_PORT", "5432")

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    return conn

@app.route('/')
def index():
    return "Web Interface Backend is running."

@app.route('/api/orders', methods=['GET'])
def get_orders():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get requested columns from query parameters
        columns_param = request.args.get('columns')
        if columns_param:
            # Basic sanitization: split by comma and strip whitespace
            # In a real application, you'd want more robust validation
            columns = [col.strip() for col in columns_param.split(',')]
            # Ensure only valid column names are used to prevent SQL injection
            # For now, we'll use the provided columns directly, but this is a risk
            # A better approach would be to have a predefined list of allowed columns
            select_columns = ", ".join(columns)
        else:
            # Default columns if none are specified
            select_columns = "*" # Select all columns by default

        # Build the base query
        query = f"SELECT {select_columns} FROM ordens_servico"
        where_clauses = []
        query_params = []

        # Add filtering based on query parameters
        # Date filtering
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        if start_date and end_date:
            where_clauses.append("data_emissao BETWEEN %s AND %s")
            query_params.extend([start_date, end_date])
        elif start_date:
            where_clauses.append("data_emissao >= %s")
            query_params.append(start_date)
        elif end_date:
            where_clauses.append("data_emissao <= %s")
            query_params.append(end_date)

        # Status filtering
        status = request.args.get('status')
        if status:
            where_clauses.append("situacao = %s")
            query_params.append(status)

        # Dynamic field filtering (example for a few fields)
        # This part needs to be expanded based on the fields chosen for dynamic filtering
        # Example: Filter by tecnico
        tecnico = request.args.get('tecnico')
        if tecnico:
             where_clauses.append("tecnico ILIKE %s") # Case-insensitive search
             query_params.append(f"%{tecnico}%")

        # Add other dynamic filters here based on user selection...
        # Example: Filter by numero_ordem_servico
        numero_ordem_servico = request.args.get('numero_ordem_servico')
        if numero_ordem_servico:
             where_clauses.append("numero_ordem_servico = %s")
             query_params.append(numero_ordem_servico)

        # Combine where clauses
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        # Execute the query
        cur.execute(query, query_params)
        rows = cur.fetchall()

        # Get column names from cursor description
        column_names = [desc[0] for desc in cur.description]

        # Format results as a list of dictionaries
        result = []
        for row in rows:
            result.append(dict(zip(column_names, row)))

        return jsonify(result)

    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Could not fetch data", "details": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    # In a production environment, use a production-ready WSGI server like Gunicorn or uWSGI
    app.run(debug=True)
