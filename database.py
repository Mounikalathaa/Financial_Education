"""SQLite database module for persistent storage of users, quizzes, and gamification data."""

import sqlite3
import json
from datetime import datetime, date
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, List, Dict, Any

# Database file location
DB_PATH = Path(__file__).parent / "data" / "quiz_data.db"


@contextmanager
def get_db_connection():
    """Context manager for database connections with automatic commit/rollback."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_database():
    """Initialize the database with all required tables and indexes."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER,
                hobbies TEXT,  -- JSON array
                interests TEXT,  -- JSON array
                learning_style TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Quiz results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                quiz_id TEXT NOT NULL,
                concept TEXT NOT NULL,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                percentage REAL NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Quiz answers table (detailed answer tracking)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_result_id INTEGER NOT NULL,
                question_id TEXT NOT NULL,
                question_text TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                user_answer TEXT,
                is_correct BOOLEAN NOT NULL,
                answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (quiz_result_id) REFERENCES quiz_results(id)
            )
        """)
        
        # Gamification table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gamification (
                user_id TEXT PRIMARY KEY,
                total_points INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                quizzes_completed INTEGER DEFAULT 0,
                streak_days INTEGER DEFAULT 0,
                perfect_scores INTEGER DEFAULT 0,
                badges TEXT,  -- JSON array
                last_activity_date DATE,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Create indexes for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_quiz_results_user 
            ON quiz_results(user_id, completed_at DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_quiz_answers_result 
            ON quiz_answers(quiz_result_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_quiz_results_concept 
            ON quiz_results(user_id, concept)
        """)


def save_user(user_id: str, name: str, age: Optional[int] = None, 
              hobbies: Optional[List[str]] = None, interests: Optional[List[str]] = None,
              learning_style: Optional[str] = None) -> bool:
    """Save or update user profile in the database."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Convert lists to JSON strings
            hobbies_json = json.dumps(hobbies) if hobbies else None
            interests_json = json.dumps(interests) if interests else None
            
            cursor.execute("""
                INSERT INTO users (user_id, name, age, hobbies, interests, learning_style, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    name = excluded.name,
                    age = excluded.age,
                    hobbies = excluded.hobbies,
                    interests = excluded.interests,
                    learning_style = excluded.learning_style,
                    updated_at = CURRENT_TIMESTAMP
            """, (user_id, name, age, hobbies_json, interests_json, learning_style))
            
            # Initialize gamification data if new user
            cursor.execute("""
                INSERT OR IGNORE INTO gamification (user_id)
                VALUES (?)
            """, (user_id,))
            
        return True
    except Exception as e:
        print(f"Error saving user: {e}")
        return False


def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve user profile from the database."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, name, age, hobbies, interests, learning_style, 
                       created_at, updated_at
                FROM users
                WHERE user_id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'user_id': row['user_id'],
                    'name': row['name'],
                    'age': row['age'],
                    'hobbies': json.loads(row['hobbies']) if row['hobbies'] else [],
                    'interests': json.loads(row['interests']) if row['interests'] else [],
                    'learning_style': row['learning_style'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
            return None
    except Exception as e:
        print(f"Error retrieving user: {e}")
        return None


def get_all_users() -> List[Dict[str, Any]]:
    """Retrieve all users from the database."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, name, age, hobbies, interests, learning_style
                FROM users
                ORDER BY name
            """)
            
            users = []
            for row in cursor.fetchall():
                users.append({
                    'user_id': row['user_id'],
                    'name': row['name'],
                    'age': row['age'],
                    'hobbies': json.loads(row['hobbies']) if row['hobbies'] else [],
                    'interests': json.loads(row['interests']) if row['interests'] else [],
                    'learning_style': row['learning_style']
                })
            return users
    except Exception as e:
        print(f"Error retrieving users: {e}")
        return []


def save_quiz_result(user_id: str, quiz_id: str, concept: str, score: int, 
                     total_questions: int, answers: List[Dict[str, Any]]) -> Optional[int]:
    """Save quiz result and detailed answers to the database."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Calculate percentage
            percentage = (score / total_questions * 100) if total_questions > 0 else 0
            
            # Insert quiz result
            cursor.execute("""
                INSERT INTO quiz_results 
                (user_id, quiz_id, concept, score, total_questions, percentage)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, quiz_id, concept, score, total_questions, percentage))
            
            quiz_result_id = cursor.lastrowid
            
            # Insert detailed answers
            for answer in answers:
                cursor.execute("""
                    INSERT INTO quiz_answers 
                    (quiz_result_id, question_id, question_text, correct_answer, 
                     user_answer, is_correct)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    quiz_result_id,
                    answer.get('question_id', ''),
                    answer.get('question_text', ''),
                    answer.get('correct_answer', ''),
                    answer.get('user_answer', ''),
                    answer.get('is_correct', False)
                ))
            
            return quiz_result_id
    except Exception as e:
        print(f"Error saving quiz result: {e}")
        return None


def get_quiz_history(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieve quiz history for a user."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, quiz_id, concept, score, total_questions, 
                       percentage, completed_at
                FROM quiz_results
                WHERE user_id = ?
                ORDER BY completed_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            history = []
            for row in cursor.fetchall():
                # Parse datetime string to datetime object
                completed_at = row['completed_at']
                if isinstance(completed_at, str):
                    try:
                        completed_at = datetime.fromisoformat(completed_at)
                    except:
                        completed_at = datetime.now()
                
                history.append({
                    'id': row['id'],
                    'quiz_id': row['quiz_id'],
                    'concept': row['concept'],
                    'score': row['score'],
                    'total_questions': row['total_questions'],
                    'percentage': row['percentage'],
                    'completed_at': completed_at
                })
            return history
    except Exception as e:
        print(f"Error retrieving quiz history: {e}")
        return []


def get_quiz_details(quiz_result_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve detailed quiz result including all answers."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get quiz result
            cursor.execute("""
                SELECT id, user_id, quiz_id, concept, score, total_questions, 
                       percentage, completed_at
                FROM quiz_results
                WHERE id = ?
            """, (quiz_result_id,))
            
            result_row = cursor.fetchone()
            if not result_row:
                return None
            
            # Get all answers
            cursor.execute("""
                SELECT question_id, question_text, correct_answer, 
                       user_answer, is_correct, answered_at
                FROM quiz_answers
                WHERE quiz_result_id = ?
                ORDER BY id
            """, (quiz_result_id,))
            
            answers = []
            for row in cursor.fetchall():
                answers.append({
                    'question_id': row['question_id'],
                    'question_text': row['question_text'],
                    'correct_answer': row['correct_answer'],
                    'user_answer': row['user_answer'],
                    'is_correct': bool(row['is_correct']),
                    'answered_at': row['answered_at']
                })
            
            return {
                'id': result_row['id'],
                'user_id': result_row['user_id'],
                'quiz_id': result_row['quiz_id'],
                'concept': result_row['concept'],
                'score': result_row['score'],
                'total_questions': result_row['total_questions'],
                'percentage': result_row['percentage'],
                'completed_at': result_row['completed_at'],
                'answers': answers
            }
    except Exception as e:
        print(f"Error retrieving quiz details: {e}")
        return None


def get_concept_statistics(user_id: str) -> List[Dict[str, Any]]:
    """Get aggregated statistics by concept for a user."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    concept,
                    COUNT(*) as attempts,
                    AVG(percentage) as avg_score,
                    MAX(percentage) as best_score,
                    MIN(percentage) as worst_score
                FROM quiz_results
                WHERE user_id = ?
                GROUP BY concept
                ORDER BY attempts DESC, avg_score DESC
            """, (user_id,))
            
            stats = []
            for row in cursor.fetchall():
                stats.append({
                    'concept': row['concept'],
                    'attempts': row['attempts'],
                    'avg_score': round(row['avg_score'], 1),
                    'best_score': round(row['best_score'], 1),
                    'worst_score': round(row['worst_score'], 1)
                })
            return stats
    except Exception as e:
        print(f"Error retrieving concept statistics: {e}")
        return []


def get_gamification_data(user_id: str) -> Dict[str, Any]:
    """Retrieve gamification data for a user."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT total_points, level, quizzes_completed, streak_days, 
                       perfect_scores, badges, last_activity_date
                FROM gamification
                WHERE user_id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'total_points': row['total_points'] or 0,
                    'level': row['level'] or 1,
                    'quizzes_completed': row['quizzes_completed'] or 0,
                    'streak_days': row['streak_days'] or 0,
                    'perfect_scores': row['perfect_scores'] or 0,
                    'badges': json.loads(row['badges']) if row['badges'] else [],
                    'last_activity_date': row['last_activity_date']
                }
            else:
                # Return default values if no record exists
                return {
                    'total_points': 0,
                    'level': 1,
                    'quizzes_completed': 0,
                    'streak_days': 0,
                    'perfect_scores': 0,
                    'badges': [],
                    'last_activity_date': None
                }
    except Exception as e:
        print(f"Error retrieving gamification data: {e}")
        return {
            'total_points': 0,
            'level': 1,
            'quizzes_completed': 0,
            'streak_days': 0,
            'perfect_scores': 0,
            'badges': [],
            'last_activity_date': None
        }


def update_gamification_data(user_id: str, points_earned: int, 
                            is_perfect_score: bool = False,
                            new_badges: Optional[List[str]] = None) -> bool:
    """Update gamification data after quiz completion."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get current data
            cursor.execute("""
                SELECT total_points, level, quizzes_completed, streak_days, 
                       perfect_scores, badges, last_activity_date
                FROM gamification
                WHERE user_id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            if not row:
                # Initialize if doesn't exist
                cursor.execute("""
                    INSERT INTO gamification (user_id)
                    VALUES (?)
                """, (user_id,))
                row = cursor.execute("""
                    SELECT total_points, level, quizzes_completed, streak_days, 
                           perfect_scores, badges, last_activity_date
                    FROM gamification
                    WHERE user_id = ?
                """, (user_id,)).fetchone()
            
            # Calculate new values
            total_points = (row['total_points'] or 0) + points_earned
            quizzes_completed = (row['quizzes_completed'] or 0) + 1
            perfect_scores = (row['perfect_scores'] or 0) + (1 if is_perfect_score else 0)
            
            # Calculate level (100 points per level)
            level = (total_points // 100) + 1
            
            # Calculate streak
            last_activity = row['last_activity_date']
            today = date.today()
            
            if last_activity:
                if isinstance(last_activity, str):
                    last_activity = date.fromisoformat(last_activity)
                
                days_diff = (today - last_activity).days
                if days_diff == 1:
                    # Consecutive day
                    streak_days = (row['streak_days'] or 0) + 1
                elif days_diff == 0:
                    # Same day
                    streak_days = row['streak_days'] or 1
                else:
                    # Streak broken
                    streak_days = 1
            else:
                streak_days = 1
            
            # Update badges
            current_badges = json.loads(row['badges']) if row['badges'] else []
            if new_badges:
                current_badges.extend(new_badges)
                current_badges = list(set(current_badges))  # Remove duplicates
            badges_json = json.dumps(current_badges)
            
            # Update database
            cursor.execute("""
                UPDATE gamification
                SET total_points = ?,
                    level = ?,
                    quizzes_completed = ?,
                    streak_days = ?,
                    perfect_scores = ?,
                    badges = ?,
                    last_activity_date = ?
                WHERE user_id = ?
            """, (total_points, level, quizzes_completed, streak_days, 
                  perfect_scores, badges_json, today.isoformat(), user_id))
            
        return True
    except Exception as e:
        print(f"Error updating gamification data: {e}")
        return False
