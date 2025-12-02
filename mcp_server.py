"""MCP Server for providing user data via API."""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import json
from pathlib import Path
from datetime import datetime, timedelta
import random

from models import (
    UserProfile, Transaction, QuizHistory, 
    GamificationData
)

app = FastAPI(
    title="Financial Education MCP Server",
    description="Multi-Controller Proxy for user data",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory data storage (in production, use a real database)
users_db = {}
transactions_db = {}
quiz_history_db = {}
gamification_db = {}

def load_sample_data():
    """Load sample data for demo purposes."""
    data_path = Path(__file__).parent.parent / "data" / "sample_users.json"
    if data_path.exists():
        with open(data_path, 'r') as f:
            data = json.load(f)
            # Load users
            for user_data in data.get("users", []):
                user = UserProfile(**user_data)
                users_db[user.user_id] = user
            print(f"Loaded {len(users_db)} users")

# Load data on startup
@app.on_event("startup")
async def startup_event():
    """Initialize sample data."""
    load_sample_data()
    print("MCP Server started successfully")

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Financial Education MCP Server",
        "version": "1.0.0"
    }

@app.get("/api/user/profile")
async def get_user_profile(user_id: str = Query(..., description="User ID")):
    """Get user profile."""
    if user_id in users_db:
        return users_db[user_id].model_dump()
    
    # Return default user if not found
    default_user = UserProfile(
        user_id=user_id,
        name="New User",
        age=10,
        hobbies=["reading", "games"],
        interests=["technology", "sports"]
    )
    users_db[user_id] = default_user
    return default_user.model_dump()

@app.post("/api/user/profile")
async def create_user_profile(profile: UserProfile):
    """Create or update user profile."""
    users_db[profile.user_id] = profile
    
    # Initialize gamification data
    if profile.user_id not in gamification_db:
        gamification_db[profile.user_id] = GamificationData(
            user_id=profile.user_id
        )
    
    return {"status": "success", "user_id": profile.user_id}

@app.get("/api/user/transactions")
async def get_transactions(
    user_id: str = Query(..., description="User ID"),
    limit: int = Query(10, description="Number of transactions")
):
    """Get user transactions."""
    user_txns = transactions_db.get(user_id, [])
    
    # Generate sample transactions if none exist
    if not user_txns and user_id in users_db:
        user_txns = generate_sample_transactions(user_id)
        transactions_db[user_id] = user_txns
    
    return {"transactions": [txn.model_dump() for txn in user_txns[:limit]]}

@app.get("/api/user/quiz-history")
async def get_quiz_history(user_id: str = Query(..., description="User ID")):
    """Get quiz history for user."""
    history = quiz_history_db.get(user_id, [])
    return {"history": [quiz.model_dump() for quiz in history]}

@app.post("/api/user/quiz-history")
async def save_quiz_result(quiz_data: dict):
    """Save quiz result to history."""
    user_id = quiz_data["user_id"]
    
    quiz_entry = QuizHistory(
        quiz_id=quiz_data["quiz_id"],
        user_id=user_id,
        concept=quiz_data["concept"],
        score=quiz_data["score"],
        total_questions=quiz_data["total_questions"],
        completed_at=datetime.fromisoformat(quiz_data["completed_at"])
    )
    
    if user_id not in quiz_history_db:
        quiz_history_db[user_id] = []
    
    quiz_history_db[user_id].append(quiz_entry)
    
    return {"status": "success"}

@app.get("/api/user/gamification")
async def get_gamification_data(user_id: str = Query(..., description="User ID")):
    """Get gamification data for user."""
    if user_id not in gamification_db:
        gamification_db[user_id] = GamificationData(user_id=user_id)
    
    return gamification_db[user_id].model_dump()

@app.post("/api/user/gamification/update")
async def update_gamification_data(gamif_data: GamificationData):
    """Update gamification data."""
    gamification_db[gamif_data.user_id] = gamif_data
    return {"status": "success"}

def generate_sample_transactions(user_id: str) -> List[Transaction]:
    """Generate sample transactions for demo."""
    categories = ["Food", "Entertainment", "Savings", "Education", "Gifts"]
    merchants = {
        "Food": ["Local Cafe", "Pizza Place", "Ice Cream Shop"],
        "Entertainment": ["Movie Theater", "Arcade", "Bookstore"],
        "Savings": ["Piggy Bank", "Savings Account"],
        "Education": ["School Supply Store", "Online Course"],
        "Gifts": ["Toy Store", "Gift Shop"]
    }
    
    transactions = []
    for i in range(15):
        category = random.choice(categories)
        merchant = random.choice(merchants[category])
        amount = round(random.uniform(5, 50), 2)
        
        txn = Transaction(
            transaction_id=f"txn_{user_id}_{i}",
            user_id=user_id,
            amount=amount,
            category=category,
            merchant=merchant,
            description=f"Purchase at {merchant}",
            timestamp=datetime.now() - timedelta(days=random.randint(0, 30))
        )
        transactions.append(txn)
    
    return sorted(transactions, key=lambda x: x.timestamp, reverse=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
