import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME", "shop_db"),
        user=os.getenv("DB_USER", "pyagent_user"),
        password=os.getenv("DB_PASSWORD", "your_secure_password"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        cursor_factory=RealDictCursor
    )
    return conn

def init_db():
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r") as f:
        schema_sql = f.read()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(schema_sql)
    conn.commit()
    cursor.close()
    conn.close()