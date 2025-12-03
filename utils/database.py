"""
Database utilities for SQLite persistence.
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

DATABASE_PATH = Path(__file__).parent.parent / "data" / "quiz_data.db"

@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_database():
    """Initialize database tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER,
                hobbies TEXT,
                interests TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Quiz history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                concept TEXT NOT NULL,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Gamification table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gamification (
                user_id TEXT PRIMARY KEY,
                total_points INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                quizzes_completed INTEGER DEFAULT 0,
                perfect_scores INTEGER DEFAULT 0,
                streak_days INTEGER DEFAULT 0,
                current_streak INTEGER DEFAULT 0,
                longest_streak INTEGER DEFAULT 0,
                badges TEXT DEFAULT '[]',
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Migrate existing gamification table if needed
        try:
            cursor.execute("SELECT current_streak FROM gamification LIMIT 1")
        except Exception:
            # Column doesn't exist, add it
            cursor.execute("ALTER TABLE gamification ADD COLUMN current_streak INTEGER DEFAULT 0")
            cursor.execute("ALTER TABLE gamification ADD COLUMN longest_streak INTEGER DEFAULT 0")
            print("✅ Migrated gamification table with streak columns")
        
        # Fix NULL badges values
        cursor.execute("UPDATE gamification SET badges = '[]' WHERE badges IS NULL")
        cursor.execute("UPDATE gamification SET current_streak = 0 WHERE current_streak IS NULL")
        cursor.execute("UPDATE gamification SET longest_streak = 0 WHERE longest_streak IS NULL")
        
        # Transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                merchant TEXT NOT NULL,
                description TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        conn.commit()
        print("✅ Database tables initialized")

# User operations
def create_user(user_id: str, name: str, age: int, hobbies: List[str], interests: List[str]) -> bool:
    """Create a new user."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (user_id, name, age, hobbies, interests)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, name, age, json.dumps(hobbies), json.dumps(interests)))
            
            # Initialize gamification data
            cursor.execute("""
                INSERT INTO gamification (user_id)
                VALUES (?)
            """, (user_id,))
            
            return True
    except sqlite3.IntegrityError:
        return False

def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        
        if row:
            return {
                "user_id": row["user_id"],
                "name": row["name"],
                "age": row["age"],
                "hobbies": json.loads(row["hobbies"]),
                "interests": json.loads(row["interests"])
            }
        return None

def get_user_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Get user by name for login (case-insensitive)."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM users 
            WHERE LOWER(name) = LOWER(?)
            ORDER BY created_at DESC
            LIMIT 1
        """, (name,))
        row = cursor.fetchone()
        
        if row:
            return {
                "user_id": row["user_id"],
                "name": row["name"],
                "age": row["age"],
                "hobbies": json.loads(row["hobbies"]) if row["hobbies"] else [],
                "interests": json.loads(row["interests"]) if row["interests"] else []
            }
        return None

# Gamification operations
def get_gamification(user_id: str) -> Optional[Dict[str, Any]]:
    """Get gamification data for user."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM gamification WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        
        if row:
            badges_data = row["badges"]
            level_num = row["level"] or 1
            # Map integer level to string rank
            level_map = {
                1: "Rookie Detective",
                2: "Junior Detective",
                3: "Detective",
                4: "Senior Detective",
                5: "Chief Detective",
                6: "Legendary Detective"
            }
            return {
                "user_id": row["user_id"],
                "total_points": row["total_points"] or 0,
                "level": level_map.get(level_num, "Rookie Detective"),
                "quizzes_completed": row["quizzes_completed"] or 0,
                "perfect_scores": row["perfect_scores"] or 0,
                "streak_days": row["streak_days"] or 0,
                "current_streak": row["current_streak"] or 0,
                "longest_streak": row["longest_streak"] or 0,
                "badges": json.loads(badges_data) if badges_data else []
            }
        return None

def update_gamification(user_id: str, data: Dict[str, Any]) -> bool:
    """Update gamification data."""
    try:
        # Convert level from string to integer if needed
        level = data.get('level', 1)
        if isinstance(level, str):
            level_map = {
                "Rookie Detective": 1,
                "Junior Detective": 2,
                "Detective": 3,
                "Senior Detective": 4,
                "Chief Detective": 5,
                "Legendary Detective": 6
            }
            level = level_map.get(level, 1)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE gamification
                SET total_points = ?,
                    level = ?,
                    quizzes_completed = ?,
                    perfect_scores = ?,
                    streak_days = ?,
                    current_streak = ?,
                    longest_streak = ?,
                    badges = ?,
                    last_activity_date = CURRENT_DATE
                WHERE user_id = ?
            """, (
                data.get("total_points", 0),
                level,  # Use converted level integer
                data.get("quizzes_completed", 0),
                data.get("perfect_scores", 0),
                data.get("streak_days", 0),
                data.get("current_streak", 0),
                data.get("longest_streak", 0),
                json.dumps(data.get("badges", [])),
                user_id
            ))
            conn.commit()  # Explicitly commit the transaction
            print(f"✅ Updated gamification for {user_id}: {data.get('total_points')} points, {data.get('quizzes_completed')} quizzes")
            return True
    except Exception as e:
        print(f"❌ Error updating gamification: {str(e)}")
        return False

# Quiz history operations
def add_quiz_history(user_id: str, quiz_id: str, concept: str, score: int, total_questions: int) -> bool:
    """Add quiz completion to history."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO quiz_history (quiz_id, user_id, concept, score, total_questions)
                VALUES (?, ?, ?, ?, ?)
            """, (quiz_id, user_id, concept, score, total_questions))
            return True
    except Exception:
        return False

def get_quiz_history(user_id: str) -> List[Dict[str, Any]]:
    """Get quiz history for user."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM quiz_history
            WHERE user_id = ?
            ORDER BY completed_at DESC
        """, (user_id,))
        
        rows = cursor.fetchall()
        return [{
            "quiz_id": row["quiz_id"],
            "user_id": row["user_id"],
            "concept": row["concept"],
            "score": row["score"],
            "total_questions": row["total_questions"],
            "completed_at": row["completed_at"]
        } for row in rows]

# Transaction operations
def add_transaction(transaction_id: str, user_id: str, amount: float, category: str, 
                   merchant: str, description: str = "") -> bool:
    """Add a transaction."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (transaction_id, user_id, amount, category, merchant, description)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (transaction_id, user_id, amount, category, merchant, description))
            return True
    except sqlite3.IntegrityError:
        return False

def get_transactions(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get transactions for user."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM transactions
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (user_id, limit))
        
        rows = cursor.fetchall()
        return [{
            "transaction_id": row["transaction_id"],
            "user_id": row["user_id"],
            "amount": row["amount"],
            "category": row["category"],
            "merchant": row["merchant"],
            "description": row["description"],
            "timestamp": row["timestamp"]
        } for row in rows]
