"""MCP Server for providing user data via API."""

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import json
from pathlib import Path
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from models import (
    UserProfile, Transaction, QuizHistory, 
    GamificationData, Quiz, QuizResponse, DifficultyLevel
)
from services.rag_service import RAGService
from services.mcp_client import MCPClient
from agents.team_orchestrator import TeamOrchestrator
from utils import database as db
import asyncio

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

# Initialize services
rag_service = None
mcp_client = None
orchestrator = None

# Load data on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and services."""
    global rag_service, mcp_client, orchestrator
    
    # Initialize database
    db.init_database()
    
    # Initialize services for quiz generation
    try:
        rag_service = RAGService()
        mcp_client = MCPClient()
        orchestrator = TeamOrchestrator(mcp_client, rag_service)
        print("✅ Quiz generation services initialized")
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize quiz services: {e}")
        print("   Quiz generation will not be available")
    
    print("🚀 MCP Server started successfully")

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
    user_data = db.get_user(user_id)
    
    if user_data:
        return user_data
    
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/api/user/profile")
async def create_user_profile(profile: UserProfile):
    """Create or update user profile."""
    success = db.create_user(
        user_id=profile.user_id,
        name=profile.name,
        age=profile.age,
        hobbies=profile.hobbies,
        interests=profile.interests
    )
    
    if success:
        return {"status": "success", "user_id": profile.user_id}
    else:
        raise HTTPException(status_code=400, detail="User already exists or error creating user")

@app.post("/api/user/login")
async def login_user(request: dict):
    """Login user by name."""
    name = request.get("name")
    
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")
    
    user_data = db.get_user_by_name(name)
    
    if user_data:
        return {"status": "success", "user": user_data, "is_existing": True}
    else:
        return {"status": "success", "is_existing": False}

@app.get("/api/user/transactions")
async def get_transactions(
    user_id: str = Query(..., description="User ID"),
    limit: int = Query(10, description="Number of transactions")
):
    """Get user transactions."""
    user_txns = db.get_transactions(user_id, limit)
    
    # Generate sample transactions if none exist
    if not user_txns and db.get_user(user_id):
        generate_sample_transactions(user_id)
        user_txns = db.get_transactions(user_id, limit)
    
    return {"transactions": user_txns}

@app.get("/api/user/quiz-history")
async def get_quiz_history(user_id: str = Query(..., description="User ID")):
    """Get quiz history for user."""
    history = db.get_quiz_history(user_id)
    return {"history": history}

@app.post("/api/user/quiz-history")
async def save_quiz_result(quiz_data: dict):
    """Save quiz result to history."""
    success = db.add_quiz_history(
        user_id=quiz_data["user_id"],
        quiz_id=quiz_data["quiz_id"],
        concept=quiz_data["concept"],
        score=quiz_data["score"],
        total_questions=quiz_data["total_questions"]
    )
    
    if success:
        return {"status": "success"}
    else:
        raise HTTPException(status_code=500, detail="Error saving quiz history")

@app.get("/api/user/gamification")
async def get_gamification_data(user_id: str = Query(..., description="User ID")):
    """Get gamification data for user."""
    gamif_data = db.get_gamification(user_id)
    
    if not gamif_data:
        raise HTTPException(status_code=404, detail="User gamification data not found")
    
    return gamif_data

@app.post("/api/user/gamification/update")
async def update_gamification_data(gamif_data: GamificationData):
    """Update gamification data."""
    print(f"🔄 MCP SERVER: Received gamification update for user {gamif_data.user_id}")
    print(f"   Points: {gamif_data.total_points}, Level: {gamif_data.level}, Quizzes: {gamif_data.quizzes_completed}")
    
    success = db.update_gamification(gamif_data.user_id, gamif_data.model_dump())
    
    if success:
        print(f"✅ MCP SERVER: Updated successfully")
        return {"status": "success"}
    else:
        raise HTTPException(status_code=500, detail="Error updating gamification data")

def generate_sample_transactions(user_id: str):
    """Generate sample transactions for demo and save to database."""
    categories = ["Food", "Entertainment", "Savings", "Education", "Gifts"]
    merchants = {
        "Food": ["Local Cafe", "Pizza Place", "Ice Cream Shop"],
        "Entertainment": ["Movie Theater", "Arcade", "Bookstore"],
        "Savings": ["Piggy Bank", "Savings Account"],
        "Education": ["School Supply Store", "Online Course"],
        "Gifts": ["Toy Store", "Gift Shop"]
    }
    
    for i in range(15):
        category = random.choice(categories)
        merchant = random.choice(merchants[category])
        amount = random.uniform(5.0, 50.0)
        
        db.add_transaction(
            transaction_id=f"txn_{user_id}_{i}",
            user_id=user_id,
            amount=amount,
            category=category,
            merchant=merchant,
            description=f"Purchase at {merchant}"
        )

@app.post("/api/quiz/generate")
async def generate_quiz(request: dict):
    """Generate a personalized quiz using Team Orchestrator."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Quiz generation service not available")
    
    try:
        user_id = request.get("user_id")
        concept = request.get("concept")
        difficulty = request.get("difficulty", "beginner")
        
        if not user_id or not concept:
            raise HTTPException(status_code=400, detail="user_id and concept are required")
        
        # Get user profile from database
        user_profile = db.get_user(user_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Map difficulty string to enum
        difficulty_map = {
            "beginner": DifficultyLevel.BEGINNER,
            "intermediate": DifficultyLevel.INTERMEDIATE,
            "advanced": DifficultyLevel.ADVANCED
        }
        difficulty_level = difficulty_map.get(difficulty.lower(), DifficultyLevel.BEGINNER)
        
        # Generate quiz
        quiz = await orchestrator.generate_personalized_quiz(
            user_id=user_id,
            concept=concept,
            difficulty=difficulty_level
        )
        
        return quiz.model_dump(mode='json')
        
    except Exception as e:
        print(f"❌ Error generating quiz: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {str(e)}")

@app.post("/api/quiz/evaluate")
async def evaluate_quiz(request: dict):
    """Evaluate quiz responses and update gamification."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Quiz evaluation service not available")
    
    try:
        quiz_data = request.get("quiz")
        response_data = request.get("response")
        
        if not quiz_data or not response_data:
            raise HTTPException(status_code=400, detail="quiz and response are required")
        
        # Reconstruct quiz and response objects
        quiz = Quiz(**quiz_data)
        response = QuizResponse(**response_data)
        
        # Evaluate quiz
        result = await orchestrator.evaluate_quiz(quiz, response)
        
        # Update database
        user_id = response.user_id
        
        # Save quiz history
        db.add_quiz_history(
            user_id=user_id,
            quiz_id=quiz.quiz_id,
            concept=quiz.concept,
            score=result.score,
            total_questions=result.total_questions
        )
        
        # Update gamification data
        gamif_data = db.get_gamification(user_id)
        
        if not gamif_data:
            raise HTTPException(status_code=404, detail="User gamification data not found")
        
        gamif_data['total_points'] += result.points_earned
        gamif_data['quizzes_completed'] += 1
        
        # Update level based on points (using string levels for frontend compatibility)
        if gamif_data['total_points'] >= 1000:
            gamif_data['level'] = "Legendary Detective"
        elif gamif_data['total_points'] >= 750:
            gamif_data['level'] = "Chief Detective"
        elif gamif_data['total_points'] >= 500:
            gamif_data['level'] = "Senior Detective"
        elif gamif_data['total_points'] >= 300:
            gamif_data['level'] = "Detective"
        elif gamif_data['total_points'] >= 100:
            gamif_data['level'] = "Junior Detective"
        else:
            gamif_data['level'] = "Rookie Detective"
        
        # Add new badges
        for badge in result.new_badges:
            if badge not in gamif_data['badges']:
                gamif_data['badges'].append(badge)
        
        # Update streak
        gamif_data['current_streak'] += 1
        if gamif_data['current_streak'] > gamif_data['longest_streak']:
            gamif_data['longest_streak'] = gamif_data['current_streak']
        
        # Check for perfect score
        if result.score == result.total_questions:
            gamif_data['perfect_scores'] += 1
        
        db.update_gamification(user_id, gamif_data)
        
        return result.model_dump(mode='json')
        
    except Exception as e:
        print(f"❌ Error evaluating quiz: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error evaluating quiz: {str(e)}")

@app.post("/api/quiz/hint")
async def get_ai_hint(request: dict):
    """Get AI-generated personalized hint for a question."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Hint service not available")
    
    try:
        question = request.get("question")
        user_id = request.get("user_id")
        concept = request.get("concept")
        
        if not all([question, user_id, concept]):
            raise HTTPException(status_code=400, detail="question, user_id, and concept are required")
        
        # Get user context
        user_data = db.get_user(user_id)
        user_context = {
            "age": user_data.get("age", 10),
            "hobbies": user_data.get("hobbies", [])
        }
        
        # Generate personalized hint
        hint = await orchestrator.content_agent.generate_personalized_hint(
            question=question,
            user_context=user_context,
            concept=concept
        )
        
        # Check hint for bias
        hint_content = {"hint": hint}
        bias_check = await orchestrator.bias_checking_agent.check_content_bias(
            content=hint_content,
            content_type="hint",
            user_age=user_context["age"]
        )
        
        # Log bias check results
        if not bias_check["is_acceptable"]:
            print(f"⚠️ [Bias Check] Hint has bias issues (score: {bias_check['bias_score']}/10)")
            print(f"⚠️ [Bias Check] Issues: {bias_check['issues_found']}")
            # Auto-improve if bias score is low
            if bias_check["bias_score"] < 7:
                print("[Bias Check] Auto-improving hint...")
                improved_hint = await orchestrator.bias_checking_agent.suggest_improvements(
                    content=hint_content,
                    bias_analysis=bias_check,
                    content_type="hint"
                )
                if improved_hint and isinstance(improved_hint, dict) and "hint" in improved_hint:
                    hint = improved_hint["hint"]
                    print("[Bias Check] Hint improved successfully")
        else:
            print(f"✅ [Bias Check] Hint passed (score: {bias_check['bias_score']}/10)")
        
        return {"hint": hint}
        
    except Exception as e:
        print(f"❌ Error generating hint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating hint: {str(e)}")

@app.post("/api/quiz/explanation")
async def get_ai_explanation(request: dict):
    """Get AI-generated explanation for wrong answer."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Explanation service not available")
    
    try:
        question = request.get("question")
        correct_answer = request.get("correct_answer")
        user_answer = request.get("user_answer")
        user_id = request.get("user_id")
        concept = request.get("concept")
        
        if not all([question, correct_answer, user_answer, user_id, concept]):
            raise HTTPException(status_code=400, detail="All fields are required")
        
        # Get user age
        user_data = db.get_user(user_id)
        user_age = user_data.get("age", 10)
        
        # Generate explanation
        explanation = await orchestrator.evaluation_agent.generate_adaptive_explanation(
            question=question,
            correct_answer=correct_answer,
            user_answer=user_answer,
            user_age=user_age,
            concept=concept
        )
        
        # Check explanation for bias
        explanation_content = {"explanation": explanation}
        bias_check = await orchestrator.bias_checking_agent.check_content_bias(
            content=explanation_content,
            content_type="explanation",
            user_age=user_age
        )
        
        # Log bias check results
        if not bias_check["is_acceptable"]:
            print(f"⚠️ [Bias Check] Explanation has bias issues (score: {bias_check['bias_score']}/10)")
            print(f"⚠️ [Bias Check] Issues: {bias_check['issues_found']}")
            # Auto-improve if bias score is low
            if bias_check["bias_score"] < 7:
                print("[Bias Check] Auto-improving explanation...")
                improved_explanation = await orchestrator.bias_checking_agent.suggest_improvements(
                    content=explanation_content,
                    bias_analysis=bias_check,
                    content_type="explanation"
                )
                if improved_explanation and isinstance(improved_explanation, dict) and "explanation" in improved_explanation:
                    explanation = improved_explanation["explanation"]
                    print("[Bias Check] Explanation improved successfully")
        else:
            print(f"✅ [Bias Check] Explanation passed (score: {bias_check['bias_score']}/10)")
        
        return {"explanation": explanation}
        
    except Exception as e:
        print(f"❌ Error generating explanation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating explanation: {str(e)}")

@app.get("/api/topics")
async def get_available_topics(user_id: str = Query(None, description="User ID for personalized topic filtering")):
    """Get available topics from knowledge base, filtered by user age if user_id provided"""
    try:
        import glob
        topics_list = []
        
        for file_path in sorted(glob.glob("data/knowledge_base/*.json")):
            with open(file_path, 'r') as f:
                data = json.load(f)
                class_level = data.get("class", "")
                
                for topic in data.get("topics", []):
                    topics_list.append({
                        "id": topic["topic_name"].lower().replace(" ", "_").replace("(", "").replace(")", ""),
                        "title": f"The Case of {topic['topic_name']}",
                        "concept": topic["topic_name"],
                        "class": class_level,
                        "difficulty": "beginner" if int(class_level) <= 7 else ("intermediate" if int(class_level) <= 9 else "advanced"),
                        "description": topic.get("definition", "")[:100] + "..." if len(topic.get("definition", "")) > 100 else topic.get("definition", ""),
                        "points": 100 if int(class_level) <= 7 else (120 if int(class_level) <= 9 else 150)
                    })
        
        # Filter by user age if user_id provided
        if user_id and orchestrator:
            user_data = db.get_user(user_id)
            if user_data:
                user_age = user_data.get("age", 10)
                topics_list = orchestrator.personalization_agent.filter_topics_by_age(topics_list, user_age)
                print(f"✅ Filtered topics for user {user_id} (age {user_age}): {len(topics_list)} topics")
        
        return {"topics": topics_list, "total": len(topics_list)}
        
    except Exception as e:
        print(f"❌ Error fetching topics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching topics: {str(e)}")

@app.post("/api/voice/script")
async def generate_voice_script(request: Request):
    """Generate AI-enhanced voice script with personality, emotion, and adaptive pacing"""
    try:
        data = await request.json()
        text = data.get("text")
        context = data.get("context", "general")
        user_age = data.get("user_age", 10)
        personality = data.get("personality", "detective")  # detective/teacher/friend/mentor
        difficulty = data.get("difficulty", "medium")  # easy/medium/hard
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Analyze emotion for voice settings
        emotion_data = await orchestrator.content_agent.analyze_emotion_for_voice(
            text=text,
            context=context
        )
        
        # Generate enhanced voice script with personality
        enhanced_script = await orchestrator.content_agent.generate_voice_script(
            text=text,
            context=context,
            user_age=user_age,
            personality=personality,
            difficulty=difficulty
        )
        
        return {
            "script": enhanced_script,
            "emotion": emotion_data.get("emotion", "neutral"),
            "rate": emotion_data.get("suggested_rate", 0.9),
            "pitch": emotion_data.get("suggested_pitch", 1.0),
            "sound_effects": emotion_data.get("sound_effects", []),
            "energy": emotion_data.get("energy_level", "medium")
        }
        
    except Exception as e:
        print(f"❌ Error generating voice script: {str(e)}")
        # Return original text as fallback
        return {
            "script": data.get("text", ""),
            "emotion": "neutral",
            "rate": 0.9,
            "pitch": 1.0,
            "sound_effects": [],
            "energy": "medium"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
