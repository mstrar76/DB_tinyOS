import psycopg2
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

def get_db_connection():
    """Establishes and returns a connection to the PostgreSQL database using environment variables."""
    try:
        # Use environment variables for connection details
        # Ensure DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, and DB_PORT are set in the .env file or environment
        conn = psycopg2.connect(
            host=os.environ.get("DB_HOST"),
            database=os.environ.get("DB_NAME"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            port=os.environ.get("DB_PORT")
        )
        print("Database connection established.")
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to the database: {e}")
        print("Please ensure the environment variables DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, and DB_PORT are set correctly in the .env file or your environment.")
        return None

def close_db_connection(conn):
    """Closes the database connection."""
    if conn:
        conn.close()
        print("Database connection closed.")

if __name__ == '__main__':
    # Example usage (for testing the connection)
    conn = get_db_connection()
    if conn:
        # You can add a simple query here to test the connection
        # try:
        #     cur = conn.cursor()
        #     cur.execute("SELECT 1;")
        #     print("Database connection test successful.")
        #     cur.close()
        # except Exception as e:
        #     print(f"Database test query failed: {e}")
        close_db_connection(conn)
