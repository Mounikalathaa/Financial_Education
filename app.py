"""Main Streamlit application for Financial Education Quiz Engine."""

import streamlit as st
import asyncio
from datetime import datetime
from typing import Optional
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from models import (
    UserProfile, Quiz, QuizResponse, DifficultyLevel
)
from agents.team_orchestrator import TeamOrchestrator
from services.mcp_client import MCPClient
from services.rag_service import RAGService
from config import config
import database as db

# Initialize database
db.init_database()

# Page configuration
st.set_page_config(
    page_title="💰 Financial Education Quiz",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for mobile-friendly design
st.markdown("""
<style>
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-15px); }
    }
    
    @keyframes rainbow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .main {
        padding: 1rem;
    }
    
    .welcome-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-size: 200% 200%;
        animation: rainbow 8s ease infinite;
        padding: 3rem 2rem;
        border-radius: 30px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    }
    
    .welcome-title {
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        animation: bounce 2s infinite;
    }
    
    .welcome-subtitle {
        font-size: 1.5rem;
        margin-bottom: 1rem;
        opacity: 0.95;
    }
    
    .fun-emoji {
        font-size: 4rem;
        display: inline-block;
        animation: float 3s ease-in-out infinite;
        margin: 0 0.5rem;
    }
    
    .user-card {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        padding: 1.5rem;
        border-radius: 20px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        cursor: pointer;
        border: 3px solid transparent;
    }
    
    .user-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        border-color: #FFD700;
    }
    
    .user-card-emoji {
        font-size: 3rem;
        display: inline-block;
        margin-right: 1rem;
    }
    
    .user-card-name {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
    }
    
    .user-card-details {
        font-size: 1rem;
        color: #34495e;
        margin-top: 0.5rem;
    }
    
    .create-user-box {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 2rem;
        border-radius: 25px;
        margin-top: 2rem;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    .section-header {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 15px;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 1.5rem 0 1rem 0;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    
    .hobby-chip {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.3rem;
        font-size: 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 1rem;
        font-size: 1.3rem;
        font-weight: bold;
        border-radius: 15px;
        border: none;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.6);
        animation: pulse 0.5s ease;
    }
    
    .quiz-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        background-color: #FFD700;
        color: #000;
        border-radius: 20px;
        margin: 0.25rem;
        font-weight: bold;
    }
    
    .level-badge {
        font-size: 1.5rem;
        padding: 0.5rem 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 25px;
        display: inline-block;
        margin: 1rem 0;
    }
    
    .points-display {
        font-size: 2rem;
        font-weight: bold;
        color: #4CAF50;
    }
    
    .story-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffe8a1 100%);
        padding: 2rem;
        border-left: 8px solid #ffc107;
        border-radius: 20px;
        margin: 1.5rem 0;
        font-size: 1.2rem;
        line-height: 1.8;
        box-shadow: 0 4px 15px rgba(255, 193, 7, 0.3);
        border: 2px solid #ffd54f;
    }
    
    .story-title {
        font-size: 1.8rem;
        font-weight: bold;
        color: #ff6f00;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .question-card {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 2rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        border: 3px solid #42a5f5;
        transition: transform 0.3s ease;
    }
    
    .question-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .question-number {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 25px;
        font-size: 1.2rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 1rem;
        box-shadow: 0 3px 10px rgba(238, 90, 111, 0.4);
    }
    
    .question-text {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1976d2;
        margin: 1rem 0;
        line-height: 1.6;
    }
    
    .progress-bar-container {
        background-color: #e0e0e0;
        border-radius: 25px;
        height: 30px;
        margin: 1rem 0;
        overflow: hidden;
        box-shadow: inset 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .progress-bar {
        background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%);
        height: 100%;
        border-radius: 25px;
        transition: width 0.5s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 1rem;
    }
    
    .result-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 2.5rem;
        border-radius: 30px;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        text-align: center;
        border: 4px solid #ff6b9d;
    }
    
    .score-circle {
        width: 200px;
        height: 200px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin: 2rem auto;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
        border: 6px solid white;
    }
    
    .score-number {
        font-size: 3.5rem;
        font-weight: bold;
        color: white;
    }
    
    .score-label {
        font-size: 1.2rem;
        color: white;
        opacity: 0.9;
    }
    
    .feedback-box {
        background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
        padding: 2rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        border: 3px solid #fdcb6e;
        box-shadow: 0 5px 15px rgba(253, 203, 110, 0.4);
    }
    
    .star-rating {
        font-size: 3rem;
        cursor: pointer;
        transition: transform 0.2s ease;
    }
    
    .star-rating:hover {
        transform: scale(1.2);
    }
    
    .emoji-rating {
        font-size: 4rem;
        cursor: pointer;
        display: inline-block;
        margin: 0 1rem;
        transition: transform 0.3s ease;
        filter: grayscale(50%);
    }
    
    .emoji-rating:hover {
        transform: scale(1.3) rotate(10deg);
        filter: grayscale(0%);
    }
    
    .emoji-rating.selected {
        transform: scale(1.2);
        filter: grayscale(0%);
        animation: bounce 0.5s ease;
    }
    
    .answer-option {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem 1.5rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        border: 3px solid transparent;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .answer-option:hover {
        border-color: #667eea;
        transform: translateX(10px);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .correct-answer {
        background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%);
        border-color: #4CAF50;
        color: white;
    }
    
    .incorrect-answer {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        border-color: #ff6b6b;
        color: white;
    }
    
    .review-card {
        background: linear-gradient(135deg, #ffeaa7 0%, #fff 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 6px solid;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
    }
    
    .confetti {
        position: fixed;
        width: 10px;
        height: 10px;
        background-color: #f0f;
        position: absolute;
        animation: confetti-fall 3s linear infinite;
    }
    
    @keyframes confetti-fall {
        to {
            transform: translateY(100vh) rotate(360deg);
        }
    }
    
    .divider {
        height: 3px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        margin: 2rem 0;
        border-radius: 10px;
    }
    
    .quiz-layout {
        display: flex;
        gap: 2rem;
        margin: 2rem 0;
    }
    
    .questions-column {
        flex: 1;
        background: linear-gradient(135deg, #ffeaa7 0%, #fff5dc 100%);
        padding: 2rem;
        border-radius: 25px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        border: 3px solid #ffd93d;
    }
    
    .answers-column {
        flex: 1;
        background: linear-gradient(135deg, #a8edea 0%, #dff5f7 100%);
        padding: 2rem;
        border-radius: 25px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        border: 3px solid #6bcfdb;
    }
    
    .column-header {
        font-size: 1.8rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1.5rem;
        padding: 1rem;
        border-radius: 15px;
        background: white;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
    }
    
    .question-box {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 6px solid #ffc107;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .question-box:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    .question-box-number {
        display: inline-block;
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 1rem;
        font-weight: bold;
        margin-bottom: 0.8rem;
    }
    
    .question-box-text {
        font-size: 1.2rem;
        font-weight: 600;
        color: #2c3e50;
        line-height: 1.6;
    }
    
    .answer-box {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 3px solid #e0e0e0;
        transition: all 0.3s ease;
        cursor: pointer;
        text-align: center;
        font-size: 1.1rem;
        font-weight: 500;
        color: #2c3e50;
    }
    
    .answer-box:hover {
        transform: scale(1.05);
        border-color: #667eea;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
        background: linear-gradient(135deg, #f0f4ff 0%, #e8f0fe 100%);
    }
    
    .answer-box-selected {
        border-color: #4CAF50;
        background: linear-gradient(135deg, #d4f4dd 0%, #c8f7dc 100%);
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
        transform: scale(1.05);
    }
    
    .answer-label {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.9rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .match-indicator {
        display: inline-block;
        font-size: 1.5rem;
        margin-left: 0.5rem;
    }
    
    .answer-choice-box {
        background: white;
        padding: 1.2rem;
        border-radius: 15px;
        margin: 0.8rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 3px solid #6bcfdb;
        transition: all 0.3s ease;
        cursor: pointer;
        text-align: center;
        font-size: 1.1rem;
        font-weight: 500;
        color: #2c3e50;
        position: relative;
    }
    
    .answer-choice-box:hover {
        transform: scale(1.03);
        border-color: #667eea;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #f0f4ff 0%, #e8f0fe 100%);
    }
    
    .answer-choice-box.matched {
        border-color: #4CAF50;
        background: linear-gradient(135deg, #d4f4dd 0%, #c8f7dc 100%);
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.5);
    }
    
    .answer-choice-box.matched::before {
        content: "✓";
        position: absolute;
        top: -10px;
        right: -10px;
        background: #4CAF50;
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 1.2rem;
        box-shadow: 0 2px 8px rgba(76, 175, 80, 0.5);
    }
    
    .match-line {
        position: relative;
    }
    
    .connection-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-left: 0.5rem;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Initialize services
@st.cache_resource
def initialize_services():
    """Initialize MCP client, RAG service, and Team orchestrator."""
    mcp_client = MCPClient()
    rag_service = RAGService()
    orchestrator = TeamOrchestrator(mcp_client, rag_service)
    return orchestrator, mcp_client

def get_services():
    """Get initialized services (lazy loading)."""
    if 'services_initialized' not in st.session_state:
        st.session_state.services_initialized = False
    
    if not st.session_state.services_initialized:
        orchestrator, mcp_client = initialize_services()
        st.session_state.orchestrator = orchestrator
        st.session_state.mcp_client = mcp_client
        st.session_state.services_initialized = True
    
    return st.session_state.orchestrator, st.session_state.mcp_client

# Session state initialization
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = None
if 'current_quiz' not in st.session_state:
    st.session_state.current_quiz = None
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'quiz_result' not in st.session_state:
    st.session_state.quiz_result = None
if 'onboarding_complete' not in st.session_state:
    st.session_state.onboarding_complete = False
if 'gamification_data' not in st.session_state:
    st.session_state.gamification_data = None

def run_async(coro):
    """Helper to run async functions."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

def load_existing_users():
    """Load existing users from database."""
    return db.get_all_users()

def onboarding_flow():
    """User onboarding flow."""
    
    # Animated welcome header
    st.markdown("""
    <div class="welcome-container">
        <div class="welcome-title">
            <span class="fun-emoji">🎉</span>
            Welcome to Learning Adventure!
            <span class="fun-emoji">🚀</span>
        </div>
        <div class="welcome-subtitle">
            Get ready for an amazing journey of learning and fun!
        </div>
        <div style="font-size: 2rem; margin-top: 1rem;">
            🌟 ⭐ 💫 ✨ 🎯
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Load existing users from database
    existing_users = load_existing_users()
    
    # Option to select existing user
    if existing_users:
        st.markdown('<div class="section-header">👥 Welcome Back, Friends!</div>', unsafe_allow_html=True)
        st.markdown("##### Click on your profile to continue:")
        
        # Display user cards
        cols = st.columns(min(3, len(existing_users)))
        for idx, user in enumerate(existing_users):
            with cols[idx % 3]:
                # Assign fun emojis based on user index
                emoji_list = ["🦁", "🐼", "🦊", "🐨", "🐯", "🦄", "🐸", "🐙"]
                user_emoji = emoji_list[idx % len(emoji_list)]
                
                st.markdown(f"""
                <div class="user-card">
                    <div class="user-card-emoji">{user_emoji}</div>
                    <div class="user-card-name">{user['name']}</div>
                    <div class="user-card-details">Age: {user['age']} years old</div>
                    <div class="user-card-details">🏆 Ready to learn!</div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Let's Go! 🚀", key=f"user_{idx}", use_container_width=True):
                    # Create profile from selected user
                    profile = UserProfile(
                        user_id=user['user_id'],
                        name=user['name'],
                        age=user['age'],
                        hobbies=user.get('hobbies', []),
                        interests=user.get('interests', []),
                        preferred_learning_style=user.get('preferred_learning_style', 'visual')
                    )
                    
                    # Save user to database
                    db.save_user(
                        user_id=profile.user_id,
                        name=profile.name,
                        age=profile.age,
                        hobbies=profile.hobbies,
                        interests=profile.interests,
                        learning_style=profile.preferred_learning_style
                    )
                    
                    # Update session state
                    st.session_state.user_profile = profile
                    st.session_state.onboarding_complete = True
                    
                    # Gamification data will be loaded lazily in dashboard
                    st.balloons()
                    st.success(f"🎊 Welcome back, {profile.name}! Let's have fun learning! 🎉")
                    st.rerun()
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Create new user form
    st.markdown('<div class="section-header">🌟 New Here? Join the Fun!</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="create-user-box">', unsafe_allow_html=True)
    
    with st.form("onboarding_form"):
        st.markdown("### 📝 Tell us about yourself!")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            name = st.text_input("✨ What's your awesome name?", placeholder="Enter your name here")
        with col2:
            age = st.number_input("🎂 How old are you?", min_value=6, max_value=17, value=10)
        
        st.markdown("---")
        st.markdown("### 🎨 What makes you happy?")
        st.caption("Pick as many as you like!")
        
        hobbies = st.multiselect(
            "Your favorite activities:",
            ["Reading 📚", "Sports ⚽", "Video Games 🎮", "Music 🎵", "Art 🎨", 
             "Science 🔬", "Cooking 🍳", "Dancing 💃", "Building 🏗️", "Animals 🐾"],
            help="Choose what you love to do!"
        )
        
        st.markdown("### 🌈 What interests you?")
        st.caption("Select the topics you find exciting!")
        
        interests = st.multiselect(
            "Topics you're curious about:",
            ["Technology 💻", "Nature 🌿", "Space 🚀", "Animals 🦁", "History 🏰", 
             "Adventure 🗺️", "Fashion 👗", "Building 🏗️", "Sports 🏅", "Magic ✨"],
            help="Pick what you want to learn about!"
        )
        
        st.markdown("---")
        
        submitted = st.form_submit_button("🎉 Start My Learning Adventure!", use_container_width=True)
        
        if submitted and name:
            # Create user profile
            user_id = f"user_{name.lower().replace(' ', '_')}"
            
            # Clean up hobby and interest strings (remove emojis)
            clean_hobbies = [h.split()[0].lower() if h else h for h in hobbies]
            clean_interests = [i.split()[0].lower() if i else i for i in interests]
            
            profile = UserProfile(
                user_id=user_id,
                name=name,
                age=age,
                hobbies=clean_hobbies,
                interests=clean_interests
            )
            
            # Save user to database
            db.save_user(
                user_id=profile.user_id,
                name=profile.name,
                age=profile.age,
                hobbies=profile.hobbies,
                interests=profile.interests
            )
            
            # Update session state
            st.session_state.user_profile = profile
            st.session_state.onboarding_complete = True
            
            # Services and gamification data will be loaded lazily in dashboard
            st.balloons()
            st.success(f"🎊 Awesome! Welcome to the adventure, {name}! 🎉")
            st.markdown("### 🚀 Get ready for amazing quizzes and fun learning!")
            st.rerun()
        elif submitted and not name:
            st.error("🤔 Oops! Please tell us your name so we can get started!")
    
    st.markdown('</div>', unsafe_allow_html=True)

def dashboard():
    """User dashboard."""
    profile = st.session_state.user_profile
    
    # Get services
    orchestrator, mcp_client = get_services()
    
    # Load gamification data from database
    gamif = db.get_gamification_data(profile.user_id)
    st.session_state.gamification_data = gamif
    
    # Header
    col1, col2 = st.columns([2, 1])
    with col1:
        st.title(f"👋 Hi, {profile.name}!")
    with col2:
        if st.button("🚪 Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Gamification display
    if gamif:
        st.markdown(f'<div class="level-badge">🏆 Level: {gamif["level"]}</div>', unsafe_allow_html=True)
        
        cols = st.columns(4)
        with cols[0]:
            st.metric("💎 Points", gamif["total_points"])
        with cols[1]:
            st.metric("📚 Quizzes", gamif["quizzes_completed"])
        with cols[2]:
            st.metric("🔥 Streak", f"{gamif['streak_days']} days")
        with cols[3]:
            st.metric("⭐ Perfect", gamif["perfect_scores"])
        
        # Badges
        if gamif["badges"]:
            st.markdown("### 🎖️ Your Badges")
            badge_html = ""
            for badge_id in gamif["badges"]:
                badge = next((b for b in config.gamification.badges if b["id"] == badge_id), None)
                if badge:
                    badge_html += f'<span class="badge" title="{badge["description"]}">🏅 {badge["name"]}</span>'
            st.markdown(badge_html, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quiz History Section
    st.markdown("### 📊 Your Quiz History")
    # Load quiz history from database
    quiz_history_data = db.get_quiz_history(profile.user_id, limit=50)
    # Convert to quiz objects for compatibility
    from types import SimpleNamespace
    quiz_history = [
        SimpleNamespace(
            quiz_id=q['quiz_id'],
            concept=q['concept'],
            score=q['score'],
            total_questions=q['total_questions'],
            completed_at=q['completed_at']
        )
        for q in quiz_history_data
    ]
    
    if quiz_history:
        # Create tabs for different views
        tab1, tab2 = st.tabs(["Recent Quizzes", "Performance by Topic"])
        
        with tab1:
            # Show last 5 quizzes
            st.markdown("#### 🕐 Recent Activity")
            for quiz in quiz_history[-5:]:
                percentage = (quiz.score / quiz.total_questions * 100) if quiz.total_questions > 0 else 0
                
                # Color based on score
                if percentage >= 80:
                    emoji = "🌟"
                    color = "#4CAF50"
                elif percentage >= 60:
                    emoji = "👍"
                    color = "#FFA726"
                else:
                    emoji = "📖"
                    color = "#FF7043"
                
                st.markdown(f"""
                <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 5px solid {color};">
                    {emoji} <b>{quiz.concept.replace('_', ' ').title()}</b><br/>
                    Score: {quiz.score}/{quiz.total_questions} ({percentage:.0f}%)<br/>
                    <small>Completed: {quiz.completed_at.strftime('%b %d, %Y at %I:%M %p')}</small>
                </div>
                """, unsafe_allow_html=True)
        
        with tab2:
            # Analyze performance by concept
            st.markdown("#### 📈 Performance Analysis")
            
            # Group by concept
            concept_stats = {}
            for quiz in quiz_history:
                concept = quiz.concept
                if concept not in concept_stats:
                    concept_stats[concept] = {"total": 0, "correct": 0, "count": 0}
                concept_stats[concept]["total"] += quiz.total_questions
                concept_stats[concept]["correct"] += quiz.score
                concept_stats[concept]["count"] += 1
            
            # Display stats
            for concept, stats in concept_stats.items():
                avg_percentage = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
                
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    st.write(f"**{concept.replace('_', ' ').title()}**")
                with col2:
                    st.write(f"{stats['count']} quiz{'zes' if stats['count'] != 1 else ''}")
                with col3:
                    st.write(f"{stats['correct']}/{stats['total']}")
                with col4:
                    if avg_percentage >= 80:
                        st.write(f"🌟 {avg_percentage:.0f}%")
                    elif avg_percentage >= 60:
                        st.write(f"👍 {avg_percentage:.0f}%")
                    else:
                        st.write(f"📖 {avg_percentage:.0f}%")
    else:
        st.info("📝 No quiz history yet. Start your first quiz below!")
    
    st.markdown("---")
    
    # Quiz selection
    st.markdown("### 📖 Choose a Topic to Learn")
    
    concepts = config.financial_concepts
    
    # Check if quiz is being generated
    if 'generating_quiz' not in st.session_state:
        st.session_state.generating_quiz = False
    if 'selected_concept' not in st.session_state:
        st.session_state.selected_concept = None
    
    # Show loading message at the top if generating
    if st.session_state.generating_quiz:
        st.info("🎨 Creating your personalized quiz... Please wait! This may take a few moments.")
    
    # Create a container to maintain stable layout
    quiz_container = st.container()
    
    with quiz_container:
        cols = st.columns(3)
        for idx, concept in enumerate(concepts):
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="quiz-card">
                    <h4>{concept['name']}</h4>
                    <p>{concept['description']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Determine button state
                is_generating = st.session_state.generating_quiz
                is_this_concept_selected = (st.session_state.selected_concept == concept['id'])
                
                # Button label and state
                if is_generating and is_this_concept_selected:
                    button_label = f"⏳ Generating..."
                    button_disabled = True
                elif is_generating:
                    button_label = f"Start Quiz: {concept['name']}"
                    button_disabled = True
                else:
                    button_label = f"Start Quiz: {concept['name']}"
                    button_disabled = False
                
                if st.button(button_label, key=f"quiz_{concept['id']}", disabled=button_disabled):
                    # Set generating flag and store selected concept
                    st.session_state.generating_quiz = True
                    st.session_state.selected_concept = concept['id']
                    st.rerun()  # Rerun to show loading message
    
    # Handle quiz generation after button press
    if st.session_state.generating_quiz and st.session_state.selected_concept:
        # Get services
        orchestrator, _ = get_services()
        
        concept_id = st.session_state.selected_concept
        
        # Generate quiz
        try:
            quiz = run_async(orchestrator.generate_personalized_quiz(
                user_id=profile.user_id,
                concept=concept_id
            ))
            st.session_state.current_quiz = quiz
            st.session_state.user_answers = {}
            st.session_state.quiz_result = None
            st.session_state.generating_quiz = False
            st.session_state.selected_concept = None
            st.rerun()
        except Exception as e:
            st.session_state.generating_quiz = False
            st.session_state.selected_concept = None
            st.error(f"⚠️ Oops! Something went wrong: {str(e)}")
            st.info("💡 Please try again or choose a different topic!")

def quiz_interface():
    """Quiz taking interface."""
    quiz = st.session_state.current_quiz
    
    if not quiz:
        st.error("No quiz loaded!")
        return
    
    # Back button
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("⬅️ Back", use_container_width=True):
            st.session_state.current_quiz = None
            st.session_state.user_answers = {}
            st.session_state.quiz_result = None
            st.rerun()
    
    # Title with emoji
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem;">
        <h1 style="color: #667eea;">📚 {quiz.concept.replace('_', ' ').title()} Quiz</h1>
        <p style="font-size: 1.2rem; color: #666;">Read the story and answer the questions! 🌟</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress bar
    answered = len(st.session_state.user_answers)
    total = len(quiz.questions)
    progress = (answered / total * 100) if total > 0 else 0
    
    st.markdown(f"""
    <div class="progress-bar-container">
        <div class="progress-bar" style="width: {progress}%;">
            {answered}/{total} Questions Answered
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Display story with enhanced styling
    st.markdown("### 📖 Story Time! Listen Carefully...")
    st.markdown(f"""
    <div class="story-box">
        <div class="story-title">✨ {quiz.story.title} ✨</div>
        <p>{quiz.story.content}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Display questions and answers in side-by-side layout
    st.markdown("### 🎯 Match Questions with Answers!")
    st.markdown("<p style='text-align: center; font-size: 1.1rem; color: #666;'>Click a question first, then click the matching answer! 🎨</p>", unsafe_allow_html=True)
    
    # Initialize shuffled answers in session state if not exists
    if 'shuffled_answers' not in st.session_state or st.session_state.get('current_quiz_id') != quiz.quiz_id:
        import random
        # Get all correct answers
        correct_answers = [q.correct_answer for q in quiz.questions]
        # Shuffle them
        shuffled = correct_answers.copy()
        random.shuffle(shuffled)
        st.session_state.shuffled_answers = shuffled
        st.session_state.current_quiz_id = quiz.quiz_id
        # Initialize matching state
        st.session_state.selected_question = None  # Which question is selected
        st.session_state.answer_matches = {}  # Maps question_id to selected answer
    
    # Create two columns for questions and answers
    col_q, col_a = st.columns([1, 1], gap="large")
    
    with col_q:
        st.markdown("""
        <div class="column-header" style="background: linear-gradient(135deg, #ffd93d 0%, #ffe57f 100%); color: #2c3e50;">
            📝 Questions (Click to Select)
        </div>
        """, unsafe_allow_html=True)
        
        # Show instruction if question is selected
        if st.session_state.selected_question:
            selected_q_num = next((idx + 1 for idx, q in enumerate(quiz.questions) if q.question_id == st.session_state.selected_question), 0)
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                 color: white; padding: 1rem; border-radius: 15px; margin-bottom: 1rem; text-align: center; animation: pulse 1s infinite;">
                <strong>✨ Selected Question {selected_q_num}</strong><br/>
                <small>👉 Now click an answer on the right to match!</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Display all questions as clickable boxes
        for idx, question in enumerate(quiz.questions):
            # Check if this question has been matched
            is_matched = question.question_id in st.session_state.answer_matches
            matched_answer = st.session_state.answer_matches.get(question.question_id, "")
            # Clean matched answer display
            import re
            clean_matched = re.sub(r'^[A-D]\)\s*', '', matched_answer) if matched_answer else ""
            is_selected = st.session_state.selected_question == question.question_id
            
            # Show question box with match indicator
            border_style = ""
            if is_matched:
                border_style = "border-color: #4CAF50; background: linear-gradient(135deg, #d4f4dd 0%, #e8f5e9 100%);"
            elif is_selected:
                border_style = "border-color: #667eea; background: linear-gradient(135deg, #e8f0fe 0%, #f0f4ff 100%); box-shadow: 0 0 20px rgba(102, 126, 234, 0.5);"
            
            st.markdown(f"""
            <div class="question-box" style="{border_style}">
                <div class="question-box-text">{question.question_text}</div>
                {f'<div style="margin-top: 0.8rem; padding: 0.5rem; background: white; border-radius: 10px; border-left: 4px solid #4CAF50;"><strong style="color: #4CAF50;">✓ Matched:</strong> {clean_matched}</div>' if is_matched else ''}
            </div>
            """, unsafe_allow_html=True)
            
            # Button to select this question (only if not already matched)
            if not is_matched:
                button_label = "✓ Question Selected!" if is_selected else f"📌 Select Question"
                button_type = "primary" if is_selected else "secondary"
                
                if st.button(button_label, key=f"select_q_{question.question_id}", use_container_width=True, type=button_type):
                    if is_selected:
                        # Deselect
                        st.session_state.selected_question = None
                    else:
                        # Select this question
                        st.session_state.selected_question = question.question_id
                    st.rerun()
            else:
                # Button to unmatch if already matched
                if st.button(f"🔄 Change Answer", key=f"change_ans_{question.question_id}", use_container_width=True):
                    del st.session_state.answer_matches[question.question_id]
                    if question.question_id in st.session_state.user_answers:
                        del st.session_state.user_answers[question.question_id]
                    st.rerun()
    
    with col_a:
        st.markdown("""
        <div class="column-header" style="background: linear-gradient(135deg, #6bcfdb 0%, #a8edea 100%); color: #2c3e50;">
            💡 Answer Boxes (Click to Match)
        </div>
        """, unsafe_allow_html=True)
        
        # Display shuffled answers as clickable boxes
        for idx, answer in enumerate(st.session_state.shuffled_answers):
            # Check if this answer has already been matched
            is_used = answer in st.session_state.answer_matches.values()
            
            # Determine box style
            box_class = "answer-choice-box"
            if is_used:
                box_class += " matched"
            
            # Show answer box (plain text, clean up any A), B), C) prefixes)
            clean_answer = answer
            # Remove A), B), C), D) type prefixes if they exist
            import re
            clean_answer = re.sub(r'^[A-D]\)\s*', '', answer)
            
            st.markdown(f"""
            <div class="{box_class}" style="{'opacity: 0.5; cursor: not-allowed;' if is_used else ''}">
                <div>{clean_answer}</div>
                {f'<span class="connection-badge">✓ Used</span>' if is_used else ''}
            </div>
            """, unsafe_allow_html=True)
            
            # Button to match this answer to the selected question
            if not is_used and st.session_state.selected_question:
                if st.button(f"✓ Match This Answer", key=f"match_ans_{idx}", use_container_width=True, type="primary"):
                    # Match this answer to the selected question
                    st.session_state.answer_matches[st.session_state.selected_question] = answer
                    st.session_state.user_answers[st.session_state.selected_question] = answer
                    st.session_state.selected_question = None
                    st.rerun()
            elif is_used:
                st.markdown("<div style='text-align: center; color: #4CAF50; font-weight: bold; padding: 0.5rem;'>✓ Already Matched</div>", unsafe_allow_html=True)
            elif not st.session_state.selected_question:
                st.markdown("<div style='text-align: center; color: #999; font-size: 0.9rem; padding: 0.5rem;'>👈 Select a question first</div>", unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Submit button with status
    if len(st.session_state.user_answers) == len(quiz.questions):
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
             border-radius: 20px; margin: 1rem 0;">
            <h3 style="color: #667eea;">🎉 All questions answered! Ready to submit?</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎯 Submit My Answers!", type="primary", use_container_width=True):
                # Get services
                orchestrator, mcp_client = get_services()
                
                # Create quiz response
                response = QuizResponse(
                    quiz_id=quiz.quiz_id,
                    user_id=quiz.user_id,
                    answers=st.session_state.user_answers
                )
                
                # Evaluate quiz
                with st.spinner("🔮 Checking your answers... This is exciting!"):
                    result = run_async(orchestrator.evaluate_quiz(quiz, response))
                    st.session_state.quiz_result = result
                    
                    # Prepare detailed answers for database
                    detailed_answers = []
                    for q in quiz.questions:
                        user_answer = st.session_state.user_answers.get(q.question_id, "")
                        is_correct = q.question_id in result.correct_questions
                        detailed_answers.append({
                            'question_id': q.question_id,
                            'question_text': q.question_text,
                            'correct_answer': q.correct_answer,
                            'user_answer': user_answer,
                            'is_correct': is_correct
                        })
                    
                    # Save quiz result to database
                    db.save_quiz_result(
                        user_id=quiz.user_id,
                        quiz_id=quiz.quiz_id,
                        concept=quiz.concept,
                        score=result.score,
                        total_questions=result.total_questions,
                        answers=detailed_answers
                    )
                    
                    # Update gamification data in database
                    is_perfect = result.score == result.total_questions
                    db.update_gamification_data(
                        user_id=quiz.user_id,
                        points_earned=result.points_earned,
                        is_perfect_score=is_perfect,
                        new_badges=result.new_badges
                    )
                    
                    # Also save to MCP for backward compatibility
                    run_async(mcp_client.save_quiz_result(
                        user_id=quiz.user_id,
                        quiz_id=quiz.quiz_id,
                        concept=quiz.concept,
                        score=result.score,
                        total=result.total_questions
                    ))
                    
                    # Refresh gamification data from database
                    st.session_state.gamification_data = db.get_gamification_data(quiz.user_id)
                    
                    st.rerun()
    else:
        remaining = total - answered
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
             border-radius: 20px; margin: 1rem 0;">
            <h3 style="color: #d63031;">📝 {remaining} more question{'s' if remaining != 1 else ''} to go!</h3>
            <p style="color: #2d3436;">You've answered {answered} out of {total} questions. Keep going! 💪</p>
        </div>
        """, unsafe_allow_html=True)

def results_screen():
    """Display quiz results."""
    result = st.session_state.quiz_result
    quiz = st.session_state.current_quiz
    profile = st.session_state.user_profile
    
    if not result:
        return
    
    # Animated header
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1 style="color: #667eea; font-size: 3rem; animation: bounce 1s infinite;">🎉 Your Results Are In! 🎉</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Score display in a circular badge
    percentage = result.percentage
    
    # Determine emoji and color based on score
    if percentage >= 90:
        emoji = "🌟"
        color = "#4CAF50"
        message = "Outstanding! You're a superstar!"
    elif percentage >= 80:
        emoji = "🎯"
        color = "#2196F3"
        message = "Excellent work! Keep it up!"
    elif percentage >= 70:
        emoji = "👍"
        color = "#FF9800"
        message = "Great job! You're doing well!"
    elif percentage >= 60:
        emoji = "💪"
        color = "#FFC107"
        message = "Good effort! Keep learning!"
    else:
        emoji = "📚"
        color = "#9C27B0"
        message = "Keep practicing! You'll get better!"
    
    st.markdown(f"""
    <div class="result-card">
        <div style="font-size: 4rem; margin-bottom: 1rem;">{emoji}</div>
        <div class="score-circle" style="background: linear-gradient(135deg, {color} 0%, {color}dd 100%);">
            <div class="score-number">{result.score}/{result.total_questions}</div>
            <div class="score-label">{percentage:.0f}%</div>
        </div>
        <h2 style="color: #667eea; margin-top: 1rem;">{message}</h2>
        <p style="font-size: 1.3rem; color: #2d3436; margin-top: 1rem;">{result.feedback}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Points earned animation
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
             padding: 1.5rem; border-radius: 20px; text-align: center; color: white;">
            <div style="font-size: 2rem;">💎</div>
            <div style="font-size: 2rem; font-weight: bold;">+{result.points_earned}</div>
            <div>Points Earned</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
             padding: 1.5rem; border-radius: 20px; text-align: center; color: white;">
            <div style="font-size: 2rem;">✅</div>
            <div style="font-size: 2rem; font-weight: bold;">{result.score}</div>
            <div>Correct Answers</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%); 
             padding: 1.5rem; border-radius: 20px; text-align: center; color: white;">
            <div style="font-size: 2rem;">📊</div>
            <div style="font-size: 2rem; font-weight: bold;">{percentage:.0f}%</div>
            <div>Success Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Level up notification
    if result.level_up:
        st.balloons()
        st.success("🎊 Congratulations! You leveled up!")
    
    # New badges
    if result.new_badges:
        st.markdown("### 🎖️ New Badges Earned!")
        for badge_id in result.new_badges:
            badge = next((b for b in config.gamification.badges if b["id"] == badge_id), None)
            if badge:
                st.markdown(f"**🏅 {badge['name']}** - {badge['description']}")
    
    # Show updated gamification stats
    gamif = st.session_state.gamification_data
    if gamif:
        st.markdown("---")
        st.markdown("### 📊 Your Current Stats")
        cols = st.columns(4)
        with cols[0]:
            st.metric("💎 Total Points", gamif["total_points"])
        with cols[1]:
            st.metric("🏆 Level", gamif["level"])
        with cols[2]:
            st.metric("📚 Quizzes Completed", gamif["quizzes_completed"])
        with cols[3]:
            st.metric("🔥 Streak", f"{gamif['streak_days']} days")
    
    st.markdown("---")
    
    # Show correct/incorrect questions with enhanced styling
    st.markdown('<div class="section-header">📝 Let\'s Review Your Answers!</div>', unsafe_allow_html=True)
    
    for idx, question in enumerate(quiz.questions):
        user_answer = st.session_state.user_answers.get(question.question_id)
        is_correct = question.question_id in result.correct_questions
        
        # Color and emoji based on correctness
        if is_correct:
            border_color = "#4CAF50"
            status_emoji = "✅"
            status_text = "Correct!"
            bg_gradient = "linear-gradient(135deg, #d4f4dd 0%, #a8e6cf 100%)"
        else:
            border_color = "#ff6b6b"
            status_emoji = "❌"
            status_text = "Not quite"
            bg_gradient = "linear-gradient(135deg, #ffd3d3 0%, #ffb3b3 100%)"
        
        with st.expander(f"{status_emoji} Question {idx + 1}: {status_text}", expanded=False):
            st.markdown(f"""
            <div class="review-card" style="border-color: {border_color}; background: {bg_gradient};">
                <h4 style="color: #2d3436;">{question.question_text}</h4>
                <div style="margin: 1rem 0; padding: 1rem; background: white; border-radius: 10px;">
                    <p><strong>Your answer:</strong> <span style="color: {border_color}; font-weight: bold;">{user_answer}</span></p>
                    <p><strong>Correct answer:</strong> <span style="color: #4CAF50; font-weight: bold;">{question.correct_answer}</span></p>
                </div>
                <div style="background: #fff3cd; padding: 1rem; border-radius: 10px; border-left: 4px solid #ffc107;">
                    <p style="margin: 0;"><strong>💡 Explanation:</strong></p>
                    <p style="margin: 0.5rem 0 0 0;">{question.explanation}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Enhanced Feedback section
    st.markdown("""
    <div class="section-header">💬 Tell Us What You Think!</div>
    <div style="text-align: center; margin: 1rem 0;">
        <p style="font-size: 1.2rem; color: #666;">Your feedback helps us make quizzes even better! 🌈</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for emoji rating
    if 'emoji_rating' not in st.session_state:
        st.session_state.emoji_rating = None
    
    with st.form("feedback_form"):
        st.markdown('<div class="feedback-box">', unsafe_allow_html=True)
        
        # Emoji-based rating
        st.markdown("#### 😊 How did you feel about this quiz?")
        st.markdown('<div style="text-align: center; padding: 1rem;">', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        emojis = ["😢", "😕", "😐", "😊", "🤩"]
        labels = ["Sad", "Meh", "Okay", "Happy", "Amazing!"]
        
        emoji_rating = st.radio(
            "Select how you feel:",
            options=list(range(5)),
            format_func=lambda x: f"{emojis[x]} {labels[x]}",
            horizontal=True,
            label_visibility="collapsed"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Star rating
        st.markdown("#### ⭐ Rate this quiz (1-5 stars)")
        star_rating = st.select_slider(
            "Star Rating",
            options=[1, 2, 3, 4, 5],
            value=3,
            format_func=lambda x: "⭐" * x,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Difficulty rating with emojis
        st.markdown("#### 🎯 Was the difficulty level right for you?")
        difficulty_rating = st.radio(
            "Difficulty Level:",
            ["😴 Too Easy", "🎯 Just Right", "😰 Too Hard"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # What did you learn?
        st.markdown("#### 🧠 What did you learn today?")
        learning = st.text_area(
            "Share something new you learned:",
            placeholder="I learned that...",
            height=80,
            label_visibility="collapsed"
        )
        
        # Comments
        st.markdown("#### 💭 Any other thoughts?")
        comments = st.text_area(
            "Your comments:",
            placeholder="Tell us anything else you'd like to share!",
            height=100,
            label_visibility="collapsed"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Submit button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("✨ Send Feedback ✨", use_container_width=True)
        
        if submitted:
            # Show appreciation message
            st.balloons()
            st.markdown("""
            <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                 padding: 2rem; border-radius: 25px; text-align: center; margin: 1rem 0;
                 box-shadow: 0 8px 20px rgba(0,0,0,0.15);">
                <h2 style="color: #667eea;">🎉 Thank You!</h2>
                <p style="font-size: 1.2rem; color: #2d3436;">
                    Your feedback helps us make learning more fun for everyone! 💖
                </p>
                <div style="font-size: 2rem; margin-top: 1rem;">
                    🌟 ⭐ 💫 ✨ 🎯
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 Try Another Quiz"):
            st.session_state.current_quiz = None
            st.session_state.user_answers = {}
            st.session_state.quiz_result = None
            st.rerun()
    with col2:
        if st.button("🔄 Retake This Quiz"):
            st.session_state.user_answers = {}
            st.session_state.quiz_result = None
            st.rerun()

# Main app logic
def main():
    """Main application flow."""
    
    # Check if onboarding is complete
    if not st.session_state.onboarding_complete:
        onboarding_flow()
        return
    
    # Check if quiz is active
    if st.session_state.current_quiz:
        if st.session_state.quiz_result:
            results_screen()
        else:
            quiz_interface()
    else:
        dashboard()

if __name__ == "__main__":
    main()
