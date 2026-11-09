import os
import glob
from db.connection import get_db_connection

def run_migrations():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Create migration tracking table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version VARCHAR(255) PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    # 2. Get already applied migrations
    cursor.execute("SELECT version FROM schema_migrations")
    applied_versions = {row["version"] for row in cursor.fetchall()}

    # 3. Find all migration files in the migrations folder
    migrations_dir = os.path.join(os.path.dirname(__file__), "../migrations")
    migration_files = sorted(glob.glob(os.path.join(migrations_dir, "*.sql")))

    # 4. Run pending migrations
    for filepath in migration_files:
        filename = os.path.basename(filepath)
        if filename not in applied_versions:
            print(f"[MIGRATION]: Applying {filename}...")
            with open(filepath, "r") as f:
                sql_script = f.read()
            
            cursor.execute(sql_script)
            cursor.execute(
                "INSERT INTO schema_migrations (version) VALUES (%s)", 
                (filename,)
            )
            conn.commit()
            print(f"[MIGRATION]: Successfully applied {filename}.")

    cursor.close()
    conn.close()