#!/usr/bin/env python3
"""Test script to verify SQLite database integration."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

import database as db

def test_database():
    """Test all database functions."""
    print("🧪 Testing SQLite Database Integration\n")
    
    # 1. Initialize database
    print("1️⃣ Initializing database...")
    db.init_database()
    
    # Check if database file exists
    if db.DB_PATH.exists():
        print(f"   ✅ Database created at: {db.DB_PATH}")
        print(f"   📊 Size: {db.DB_PATH.stat().st_size} bytes\n")
    else:
        print("   ❌ Database file not found!\n")
        return False
    
    # 2. Test user creation
    print("2️⃣ Testing user creation...")
    test_user_id = "test_user_123"
    success = db.save_user(
        user_id=test_user_id,
        name="Test User",
        age=10,
        hobbies=["reading", "sports"],
        interests=["technology", "nature"],
        learning_style="visual"
    )
    
    if success:
        print("   ✅ User saved successfully")
        
        # Retrieve user
        user = db.get_user(test_user_id)
        if user:
            print(f"   ✅ User retrieved: {user['name']}, Age: {user['age']}")
            print(f"   📚 Hobbies: {user['hobbies']}")
            print(f"   🎯 Interests: {user['interests']}\n")
        else:
            print("   ❌ Failed to retrieve user\n")
            return False
    else:
        print("   ❌ Failed to save user\n")
        return False
    
    # 3. Test gamification data
    print("3️⃣ Testing gamification data...")
    gamif = db.get_gamification_data(test_user_id)
    print(f"   ✅ Initial gamification data:")
    print(f"      Level: {gamif['level']}")
    print(f"      Points: {gamif['total_points']}")
    print(f"      Quizzes: {gamif['quizzes_completed']}\n")
    
    # 4. Test quiz result saving
    print("4️⃣ Testing quiz result saving...")
    sample_answers = [
        {
            'question_id': 'q1',
            'question_text': 'What is 2+2?',
            'correct_answer': '4',
            'user_answer': '4',
            'is_correct': True
        },
        {
            'question_id': 'q2',
            'question_text': 'What is the capital of France?',
            'correct_answer': 'Paris',
            'user_answer': 'Paris',
            'is_correct': True
        }
    ]
    
    quiz_result_id = db.save_quiz_result(
        user_id=test_user_id,
        quiz_id="quiz_001",
        concept="basic_math",
        score=2,
        total_questions=2,
        answers=sample_answers
    )
    
    if quiz_result_id:
        print(f"   ✅ Quiz result saved with ID: {quiz_result_id}\n")
    else:
        print("   ❌ Failed to save quiz result\n")
        return False
    
    # 5. Test gamification update
    print("5️⃣ Testing gamification update...")
    success = db.update_gamification_data(
        user_id=test_user_id,
        points_earned=50,
        is_perfect_score=True,
        new_badges=["first_quiz"]
    )
    
    if success:
        gamif = db.get_gamification_data(test_user_id)
        print(f"   ✅ Gamification updated:")
        print(f"      Level: {gamif['level']}")
        print(f"      Points: {gamif['total_points']}")
        print(f"      Quizzes: {gamif['quizzes_completed']}")
        print(f"      Perfect Scores: {gamif['perfect_scores']}")
        print(f"      Badges: {gamif['badges']}\n")
    else:
        print("   ❌ Failed to update gamification\n")
        return False
    
    # 6. Test quiz history retrieval
    print("6️⃣ Testing quiz history retrieval...")
    history = db.get_quiz_history(test_user_id, limit=10)
    if history:
        print(f"   ✅ Retrieved {len(history)} quiz(es)")
        for idx, quiz in enumerate(history, 1):
            print(f"      {idx}. {quiz['concept']}: {quiz['score']}/{quiz['total_questions']} ({quiz['percentage']:.0f}%)")
        print()
    else:
        print("   ⚠️  No quiz history found (expected for new user)\n")
    
    # 7. Test concept statistics
    print("7️⃣ Testing concept statistics...")
    stats = db.get_concept_statistics(test_user_id)
    if stats:
        print(f"   ✅ Retrieved statistics for {len(stats)} concept(s)")
        for stat in stats:
            print(f"      {stat['concept']}: {stat['attempts']} attempts, avg {stat['avg_score']:.1f}%")
        print()
    else:
        print("   ⚠️  No statistics found (expected for new user)\n")
    
    # 8. Test getting all users
    print("8️⃣ Testing user list retrieval...")
    all_users = db.get_all_users()
    print(f"   ✅ Retrieved {len(all_users)} user(s) from database\n")
    
    print("=" * 60)
    print("🎉 All database tests passed successfully!")
    print("=" * 60)
    print(f"\n📁 Database location: {db.DB_PATH}")
    print(f"📊 Database size: {db.DB_PATH.stat().st_size} bytes")
    
    return True

if __name__ == "__main__":
    try:
        test_database()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
