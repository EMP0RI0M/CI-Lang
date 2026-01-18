import sqlite3
import sys

def analyze_swarm():
    try:
        conn = sqlite3.connect('research.db')
        cursor = conn.cursor()
        
        # Look for the period of high activity identified in chat_logs
        query = """
        SELECT timestamp, topic, source_mode, metadata 
        FROM research_logs 
        WHERE timestamp >= '2026-01-16 10:30:00' 
        AND timestamp <= '2026-01-16 10:45:00'
        ORDER BY timestamp ASC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        print(f"Found {len(rows)} research events in swarm window.")
        for row in rows:
            print(f"{row[0]} | {row[1]} | {row[2]} | {row[3][:100]}...")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    analyze_swarm()
