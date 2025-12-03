"""Migration script to add title column to quiz_results table."""

import sqlite3
from pathlib import Path

# Database file location
DB_PATH = Path(__file__).parent / "data" / "quiz_data.db"

def migrate():
    """Add title column to quiz_results table if it doesn't exist."""
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # Check if title column exists
        cursor.execute("PRAGMA table_info(quiz_results)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'title' not in columns:
            print("Adding 'title' column to quiz_results table...")
            cursor.execute("ALTER TABLE quiz_results ADD COLUMN title TEXT")
            conn.commit()
            print("✅ Migration completed successfully!")
        else:
            print("✅ 'title' column already exists, no migration needed.")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
