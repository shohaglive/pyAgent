import os
import json
import glob
import sys
from db.connection import get_db_connection

SEEDS_DIR = os.path.join(os.path.dirname(__file__), "../seeds")

def run_seeds(target="all"):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Find all JSON files in the seeds directory
    pattern = os.path.join(SEEDS_DIR, "*.json")
    seed_files = sorted(glob.glob(pattern))

    for filepath in seed_files:
        filename = os.path.basename(filepath)
        table_name = os.path.splitext(filename)[0]  # e.g., 'customers.json' -> 'customers'

        # If target is specific (e.g., 'customers'), skip other files
        if target != "all" and target != table_name:
            continue

        print(f"[SEED]: Processing seed file for table '{table_name}'...")

        try:
            with open(filepath, "r") as f:
                records = json.load(f)

            if not isinstance(records, list) or len(records) == 0:
                print(f"[SEED]: Skipped {filename} (empty or not a JSON array).")
                continue

            for record in records:
                columns = list(record.keys())
                values = list(record.values())

                # Dynamically construct placeholders: (%s, %s, %s)
                placeholders = ", ".join(["%s"] * len(columns))
                cols_str = ", ".join(columns)

                # Build upsert query (assuming first column or primary key can conflict)
                # To make it robust, we use DO NOTHING on conflict
                query = f"""
                    INSERT INTO {table_name} ({cols_str})
                    VALUES ({placeholders})
                    ON CONFLICT DO NOTHING;
                """

                cursor.execute(query, values)

            conn.commit()
            print(f"[SEED]: Successfully seeded table '{table_name}'.")

        except Exception as e:
            conn.rollback()
            print(f"[SEED ERROR]: Failed to seed {filename}: {e}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    # Command-line usage: python3 -m db.seed_runner [all | customers | orders]
    target_arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    run_seeds(target_arg)