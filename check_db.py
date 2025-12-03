"""Quick script to check SQLite database tables and data."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "quiz_data.db"

def check_database():
    """Display all tables and their row counts."""
    if not DB_PATH.exists():
        print(f"❌ Database not found at: {DB_PATH}")
        return
    
    print(f"✅ Database found at: {DB_PATH}\n")
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print("=" * 60)
    print("DATABASE TABLES")
    print("=" * 60)
    
    for (table_name,) in tables:
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        print(f"\n📊 Table: {table_name}")
        print(f"   Rows: {count}")
        
        # Get column info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"   Columns: {', '.join([col[1] for col in columns])}")
        
        # Show sample data if exists
        if count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            rows = cursor.fetchall()
            print(f"   Sample data (first {min(3, count)} rows):")
            for row in rows:
                print(f"     {row}")
    
    print("\n" + "=" * 60)
    conn.close()

if __name__ == "__main__":
    check_database()
