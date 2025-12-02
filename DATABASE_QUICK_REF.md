# Quick Database Reference

## Database Overview
**Location:** `data/quiz_data.db`  
**Type:** SQLite 3  
**Tables:** 4 main tables (users, quiz_results, quiz_answers, gamification)

## Quick Commands

### View Database Contents
```bash
# Open database in SQLite CLI
sqlite3 data/quiz_data.db

# Common queries
.tables                          # List all tables
.schema users                    # Show table schema
SELECT * FROM users;             # View all users
SELECT * FROM quiz_results;      # View all quiz results
SELECT * FROM gamification;      # View gamification data
.quit                            # Exit
```

### Python Usage
```python
import database as db

# Initialize database (run once at startup)
db.init_database()

# Save a user
db.save_user(
    user_id="alice_123",
    name="Alice",
    age=10,
    hobbies=["reading", "music"],
    interests=["science", "art"]
)

# Get user
user = db.get_user("alice_123")
print(f"Name: {user['name']}, Age: {user['age']}")

# Get all users
users = db.get_all_users()
print(f"Total users: {len(users)}")

# Save quiz result
answers = [
    {
        'question_id': 'q1',
        'question_text': 'What is 2+2?',
        'correct_answer': '4',
        'user_answer': '4',
        'is_correct': True
    }
]
db.save_quiz_result(
    user_id="alice_123",
    quiz_id="quiz_001",
    concept="math",
    score=1,
    total_questions=1,
    answers=answers
)

# Get quiz history
history = db.get_quiz_history("alice_123")
for quiz in history:
    print(f"{quiz['concept']}: {quiz['score']}/{quiz['total_questions']}")

# Get gamification data
gamif = db.get_gamification_data("alice_123")
print(f"Level: {gamif['level']}, Points: {gamif['total_points']}")

# Update gamification
db.update_gamification_data(
    user_id="alice_123",
    points_earned=50,
    is_perfect_score=True,
    new_badges=["first_quiz"]
)

# Get statistics by concept
stats = db.get_concept_statistics("alice_123")
for stat in stats:
    print(f"{stat['concept']}: {stat['avg_score']:.1f}% average")
```

## Testing
```bash
# Run comprehensive database tests
source venv/bin/activate
python test_database.py
```

## Common Queries

### Count Users
```sql
SELECT COUNT(*) FROM users;
```

### Get Top Performers
```sql
SELECT u.name, g.total_points, g.level 
FROM users u 
JOIN gamification g ON u.user_id = g.user_id 
ORDER BY g.total_points DESC 
LIMIT 10;
```

### Get Recent Quizzes
```sql
SELECT u.name, qr.concept, qr.score, qr.total_questions, qr.completed_at
FROM quiz_results qr
JOIN users u ON qr.user_id = u.user_id
ORDER BY qr.completed_at DESC
LIMIT 20;
```

### Performance by Concept
```sql
SELECT concept, 
       COUNT(*) as attempts, 
       AVG(percentage) as avg_score
FROM quiz_results
GROUP BY concept
ORDER BY avg_score DESC;
```

### Users with Streaks
```sql
SELECT u.name, g.streak_days, g.last_activity_date
FROM users u
JOIN gamification g ON u.user_id = g.user_id
WHERE g.streak_days > 0
ORDER BY g.streak_days DESC;
```

## Backup & Restore

### Backup Database
```bash
# Simple copy
cp data/quiz_data.db data/quiz_data_backup_$(date +%Y%m%d).db

# SQLite dump
sqlite3 data/quiz_data.db .dump > quiz_backup.sql
```

### Restore Database
```bash
# From backup copy
cp data/quiz_data_backup_20241202.db data/quiz_data.db

# From SQL dump
sqlite3 data/quiz_data.db < quiz_backup.sql
```

## Troubleshooting

### Database Locked Error
```python
# The database uses context managers to prevent this
# If you get this error, ensure you're using get_db_connection()
with db.get_db_connection() as conn:
    cursor = conn.cursor()
    # Your queries here
```

### Check Database Integrity
```bash
sqlite3 data/quiz_data.db "PRAGMA integrity_check;"
```

### View Database Size
```bash
ls -lh data/quiz_data.db
du -h data/quiz_data.db
```

### Reset Database (CAUTION: Deletes all data)
```bash
rm data/quiz_data.db
# Then restart app to recreate
```

## Database Maintenance

### Optimize Database
```bash
sqlite3 data/quiz_data.db "VACUUM;"
```

### Analyze Query Performance
```sql
EXPLAIN QUERY PLAN SELECT * FROM quiz_results WHERE user_id = 'alice_123';
```

### View Indexes
```sql
SELECT name, sql FROM sqlite_master WHERE type='index';
```

## Integration Points in App

1. **Startup** (`app.py` line ~20):
   ```python
   import database as db
   db.init_database()
   ```

2. **User Selection** (`onboarding_flow()`):
   - Calls `db.save_user()` for both new and existing users

3. **Dashboard** (`dashboard()`):
   - Calls `db.get_gamification_data()`
   - Calls `db.get_quiz_history()`

4. **Quiz Submission** (`quiz_interface()`):
   - Calls `db.save_quiz_result()`
   - Calls `db.update_gamification_data()`

5. **Results Screen** (`results_screen()`):
   - Displays gamification data from database

## Data Flow

```
User Action → Streamlit UI → database.py → SQLite DB
                                    ↓
                            Session State (in-memory)
                                    ↓
                            UI Update/Display
```

## Future Enhancements

- [ ] Add data export (CSV, JSON)
- [ ] Add admin dashboard
- [ ] Add database migrations
- [ ] Add data archival
- [ ] Add multi-user leaderboard
- [ ] Add quiz sharing/comparison
- [ ] Add parent/teacher reports

---

For more details, see `DATABASE_INTEGRATION.md`
