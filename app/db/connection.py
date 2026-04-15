import psycopg

def get_db_connection() -> psycopg.Connection:
    
    conn = psycopg.connect(
        host="localhost",
        port=5432,
        dbname="app_db",
        user="app_user",
        password="app_password"
    )
    return conn