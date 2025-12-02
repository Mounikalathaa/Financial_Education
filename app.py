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
from agents.orchestrator import OrchestratorAgent
from services.mcp_client import MCPClient
from services.rag_service import RAGService
from config import config

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
    .main {
        padding: 1rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 0.75rem;
        font-size: 1.1rem;
        border-radius: 10px;
        border: none;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #45a049;
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
        background-color: #fff3cd;
        padding: 1.5rem;
        border-left: 5px solid #ffc107;
        border-radius: 10px;
        margin: 1rem 0;
        font-size: 1.1rem;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# Initialize services
@st.cache_resource
def initialize_services():
    """Initialize MCP client, RAG service, and orchestrator."""
    mcp_client = MCPClient()
    rag_service = RAGService()
    orchestrator = OrchestratorAgent(mcp_client, rag_service)
    return orchestrator, mcp_client

orchestrator, mcp_client = initialize_services()

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

def load_sample_users():
    """Load sample users from data file."""
    import json
    sample_file = Path(__file__).parent / "data" / "sample_users.json"
    try:
        with open(sample_file, 'r') as f:
            data = json.load(f)
            return data.get('users', [])
    except:
        return []

def onboarding_flow():
    """User onboarding flow."""
    st.title("🎓 Welcome to Financial Education!")
    st.markdown("### Let's get to know you!")
    
    # Load sample users
    sample_users = load_sample_users()
    
    # Option to select existing user
    if sample_users:
        st.markdown("#### 👥 Select an Existing User")
        user_options = ["Create New User"] + [f"{u['name']} (Age {u['age']})" for u in sample_users]
        selected = st.selectbox("Choose a user:", user_options)
        
        if selected != "Create New User":
            # Extract selected user
            selected_idx = user_options.index(selected) - 1
            selected_user = sample_users[selected_idx]
            
            if st.button("Login as " + selected_user['name'], type="primary"):
                # Create profile from selected user
                profile = UserProfile(
                    user_id=selected_user['user_id'],
                    name=selected_user['name'],
                    age=selected_user['age'],
                    hobbies=selected_user.get('hobbies', []),
                    interests=selected_user.get('interests', []),
                    preferred_learning_style=selected_user.get('preferred_learning_style', 'visual')
                )
                
                # Update session state
                st.session_state.user_profile = profile
                st.session_state.onboarding_complete = True
                
                # Load gamification data
                st.session_state.gamification_data = run_async(
                    mcp_client.get_gamification_data(profile.user_id)
                )
                
                st.success(f"Welcome back, {profile.name}! 🎉")
                st.rerun()
            
            st.markdown("---")
    
    # Create new user form
    st.markdown("#### 📝 Or Create New User")
    with st.form("onboarding_form"):
        name = st.text_input("What's your name?", placeholder="Enter your name")
        age = st.number_input("How old are you?", min_value=6, max_value=17, value=10)
        
        st.markdown("#### 🎨 What do you enjoy?")
        hobbies = st.multiselect(
            "Select your hobbies:",
            ["Reading", "Sports", "Video Games", "Music", "Art", "Science", "Cooking", "Dancing"]
        )
        
        interests = st.multiselect(
            "What interests you?",
            ["Technology", "Nature", "Space", "Animals", "History", "Adventure", "Fashion", "Building"]
        )
        
        submitted = st.form_submit_button("Start Learning! 🚀")
        
        if submitted and name:
            # Create user profile
            user_id = f"user_{name.lower().replace(' ', '_')}"
            profile = UserProfile(
                user_id=user_id,
                name=name,
                age=age,
                hobbies=[h.lower() for h in hobbies],
                interests=[i.lower() for i in interests]
            )
            
            # Save profile
            run_async(mcp_client.get_user_profile(user_id))  # This will create if not exists
            
            # Update session state
            st.session_state.user_profile = profile
            st.session_state.onboarding_complete = True
            
            # Load gamification data
            st.session_state.gamification_data = run_async(
                mcp_client.get_gamification_data(user_id)
            )
            
            st.success(f"Welcome, {name}! Let's start your financial learning journey! 🎉")
            st.rerun()

def dashboard():
    """User dashboard."""
    profile = st.session_state.user_profile
    gamif = st.session_state.gamification_data
    
    # Refresh gamification data
    if gamif:
        gamif = run_async(mcp_client.get_gamification_data(profile.user_id))
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
        st.markdown(f'<div class="level-badge">🏆 Level: {gamif.level}</div>', unsafe_allow_html=True)
        
        cols = st.columns(4)
        with cols[0]:
            st.metric("💎 Points", gamif.total_points)
        with cols[1]:
            st.metric("📚 Quizzes", gamif.quizzes_completed)
        with cols[2]:
            st.metric("🔥 Streak", f"{gamif.streak_days} days")
        with cols[3]:
            st.metric("⭐ Perfect", gamif.perfect_scores)
        
        # Badges
        if gamif.badges:
            st.markdown("### 🎖️ Your Badges")
            badge_html = ""
            for badge_id in gamif.badges:
                badge = next((b for b in config.gamification.badges if b["id"] == badge_id), None)
                if badge:
                    badge_html += f'<span class="badge" title="{badge["description"]}">🏅 {badge["name"]}</span>'
            st.markdown(badge_html, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quiz History Section
    st.markdown("### 📊 Your Quiz History")
    quiz_history = run_async(mcp_client.get_quiz_history(profile.user_id))
    
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
    
    cols = st.columns(3)
    for idx, concept in enumerate(concepts):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="quiz-card">
                <h4>{concept['name']}</h4>
                <p>{concept['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Start Quiz: {concept['name']}", key=f"quiz_{concept['id']}"):
                # Generate quiz
                with st.spinner("🎨 Creating your personalized quiz..."):
                    quiz = run_async(orchestrator.generate_personalized_quiz(
                        user_id=profile.user_id,
                        concept=concept['id']
                    ))
                    st.session_state.current_quiz = quiz
                    st.session_state.user_answers = {}
                    st.session_state.quiz_result = None
                    st.rerun()

def quiz_interface():
    """Quiz taking interface."""
    quiz = st.session_state.current_quiz
    
    if not quiz:
        st.error("No quiz loaded!")
        return
    
    # Back button
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.current_quiz = None
        st.session_state.user_answers = {}
        st.session_state.quiz_result = None
        st.rerun()
    
    st.title(f"📚 Quiz: {quiz.concept.replace('_', ' ').title()}")
    
    # Display story
    st.markdown("### 📖 Story Time!")
    st.markdown(f"""
    <div class="story-box">
        <h3>{quiz.story.title}</h3>
        <p>{quiz.story.content}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### ❓ Answer These Questions")
    
    # Display questions
    for idx, question in enumerate(quiz.questions):
        st.markdown(f"#### Question {idx + 1}")
        st.write(question.question_text)
        
        # Radio buttons for options
        answer = st.radio(
            "Select your answer:",
            question.options,
            key=f"q_{question.question_id}",
            index=None
        )
        
        if answer:
            st.session_state.user_answers[question.question_id] = answer
        
        st.markdown("---")
    
    # Submit button
    if len(st.session_state.user_answers) == len(quiz.questions):
        if st.button("🎯 Submit Quiz", type="primary"):
            # Create quiz response
            response = QuizResponse(
                quiz_id=quiz.quiz_id,
                user_id=quiz.user_id,
                answers=st.session_state.user_answers
            )
            
            # Evaluate quiz
            with st.spinner("📊 Evaluating your answers..."):
                result = run_async(orchestrator.evaluate_quiz(quiz, response))
                st.session_state.quiz_result = result
                
                # Save quiz result
                run_async(mcp_client.save_quiz_result(
                    user_id=quiz.user_id,
                    quiz_id=quiz.quiz_id,
                    concept=quiz.concept,
                    score=result.score,
                    total=result.total_questions
                ))
                
                # Refresh gamification data to show updated stats
                st.session_state.gamification_data = run_async(
                    mcp_client.get_gamification_data(quiz.user_id)
                )
                
                st.rerun()
    else:
        st.info(f"Please answer all questions ({len(st.session_state.user_answers)}/{len(quiz.questions)} answered)")

def results_screen():
    """Display quiz results."""
    result = st.session_state.quiz_result
    quiz = st.session_state.current_quiz
    profile = st.session_state.user_profile
    
    if not result:
        return
    
    st.title("🎉 Quiz Results")
    
    # Score display
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Score", f"{result.score}/{result.total_questions}")
    with col2:
        st.metric("Percentage", f"{result.percentage:.1f}%")
    with col3:
        st.metric("Points Earned", f"+{result.points_earned}")
    
    # Feedback
    st.markdown(f"### {result.feedback}")
    
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
            st.metric("💎 Total Points", gamif.total_points)
        with cols[1]:
            st.metric("🏆 Level", gamif.level)
        with cols[2]:
            st.metric("📚 Quizzes Completed", gamif.quizzes_completed)
        with cols[3]:
            st.metric("🔥 Streak", f"{gamif.streak_days} days")
    
    st.markdown("---")
    
    # Show correct/incorrect questions
    st.markdown("### 📝 Review Your Answers")
    
    for idx, question in enumerate(quiz.questions):
        user_answer = st.session_state.user_answers.get(question.question_id)
        is_correct = question.question_id in result.correct_questions
        
        with st.expander(f"Question {idx + 1}: {'✅ Correct' if is_correct else '❌ Incorrect'}"):
            st.write(f"**{question.question_text}**")
            st.write(f"Your answer: {user_answer}")
            st.write(f"Correct answer: {question.correct_answer}")
            st.info(f"💡 {question.explanation}")
    
    st.markdown("---")
    
    # Feedback form
    with st.form("feedback_form"):
        st.markdown("### 💬 How was this quiz?")
        rating = st.slider("Rate this quiz:", 1, 5, 3)
        difficulty_rating = st.radio(
            "Was this quiz...",
            ["Too Easy", "Just Right", "Too Hard"]
        )
        comments = st.text_area("Any comments?")
        
        if st.form_submit_button("Submit Feedback"):
            st.success("Thank you for your feedback! 🙏")
    
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
