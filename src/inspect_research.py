import sqlite3
import sys

def dump_db():
    try:
        conn = sqlite3.connect('research.db')
        cursor = conn.cursor()
        
        # Get schema of tables
        print("--- Table Schemas ---")
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
        for table in cursor.fetchall():
            print(f"Table: {table[0]}")
            print(f"Schema: {table[1]}\n")

        # Sample research_logs
        print("--- Sample research_logs ---")
        cursor.execute("SELECT * FROM research_logs LIMIT 10;")
        for row in cursor.fetchall():
            # Convert row to string safely
            print(f"Row: {[str(col) for col in row]}")

        # Sample chat_logs
        print("\n--- Sample chat_logs ---")
        cursor.execute("SELECT * FROM chat_logs LIMIT 10;")
        for row in cursor.fetchall():
            print(f"Row: {[str(col) for col in row]}")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Ensure stdout handles utf-8
    sys.stdout.reconfigure(encoding='utf-8')
    dump_db()
