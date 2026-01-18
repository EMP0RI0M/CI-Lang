import sqlite3
import sys
from collections import Counter

def analyze_agents():
    try:
        conn = sqlite3.connect('research.db')
        cursor = conn.cursor()
        
        # 1. Look for repeated queries (potential swarm triggers)
        print("--- Parallel Query Distribution ---")
        cursor.execute("SELECT query, COUNT(*) as count FROM chat_logs GROUP BY query HAVING count > 1 ORDER BY count DESC;")
        for query_text, count in cursor.fetchall():
            print(f"{count:2d} instances | {query_text[:80]}...")

        # 2. Check for unique 'metadata' or 'media_meta' fingerprints in the parallel queries
        print("\n--- Inspecting Metadata Fingerprints ---")
        cursor.execute("""
            SELECT query, timestamp, media_meta 
            FROM chat_logs 
            WHERE query LIKE 'Summarize%' 
            ORDER BY timestamp ASC;
        """)
        for q, ts, meta in cursor.fetchall():
            print(f"{ts} | {meta[:100]}...")

        # 3. Search for the word 'agent' or 'spawn' in ALL text fields
        search_terms = ['agent', 'spawn', 'worker', 'node', 'instance']
        print("\n--- Semantic Search for Agent Terminology ---")
        for term in search_terms:
            cursor.execute(f"SELECT COUNT(*) FROM chat_logs WHERE query LIKE '%{term}%' OR response LIKE '%{term}%'")
            count = cursor.fetchone()[0]
            print(f"Term '{term}' found {count} times in chat_logs.")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    analyze_agents()
