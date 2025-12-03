"""Data models for the Financial Education Quiz Engine."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class DifficultyLevel(str, Enum):
    """Quiz difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class UserProfile(BaseModel):
    """User profile model."""
    user_id: str
    name: str
    age: int
    hobbies: List[str] = []
    interests: List[str] = []
    preferred_learning_style: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class Transaction(BaseModel):
    """Transaction model."""
    transaction_id: str
    user_id: str
    amount: float
    category: str
    merchant: str
    description: Optional[str] = None
    timestamp: datetime

class QuizHistory(BaseModel):
    """Quiz history entry."""
    quiz_id: str
    user_id: str
    concept: str
    score: int
    total_questions: int
    completed_at: datetime
    time_taken_seconds: Optional[int] = None

class GamificationData(BaseModel):
    """User gamification data."""
    user_id: str
    total_points: int = 0
    level: str = "Beginner"
    badges: List[str] = []
    streak_days: int = 0
    quizzes_completed: int = 0
    perfect_scores: int = 0
    last_quiz_date: Optional[datetime] = None

class QuizQuestion(BaseModel):
    """Individual quiz question."""
    question_id: str
    question_text: str
    options: List[str]
    correct_answer: str
    explanation: str
    difficulty: DifficultyLevel

class CaseBrief(BaseModel):
    """Interactive case brief for detective-style learning."""
    case_id: str
    title: str
    mission: str  # Short, engaging mission statement (1-2 sentences)
    clues: List[str]  # 3-5 key clues/facts about the concept
    scenario: str  # Brief scenario (2-3 sentences)
    concept: str
    age_appropriate: bool = True
    personalization_elements: List[str] = []
    image_url: Optional[str] = None  # AI-generated detective scene image

class EducationalStory(BaseModel):
    """Educational story model (deprecated, use CaseBrief)."""
    story_id: str
    title: str
    content: str
    concept: str
    age_appropriate: bool = True
    personalization_elements: List[str] = []

class Quiz(BaseModel):
    """Complete quiz model."""
    quiz_id: str
    user_id: str
    concept: str
    case_brief: Optional[CaseBrief] = None
    story: Optional[EducationalStory] = None  # Deprecated, use case_brief
    questions: List[QuizQuestion]
    created_at: datetime = Field(default_factory=datetime.now)
    difficulty: DifficultyLevel

class QuizResponse(BaseModel):
    """User's response to a quiz."""
    quiz_id: str
    user_id: str
    answers: Dict[str, str]  # question_id -> selected_answer
    submitted_at: datetime = Field(default_factory=datetime.now)

class QuizResult(BaseModel):
    """Quiz evaluation result."""
    quiz_id: str
    user_id: str
    score: int
    total_questions: int
    percentage: float
    correct_questions: List[str]
    incorrect_questions: List[str]
    points_earned: int
    level_up: bool = False
    new_badges: List[str] = []
    feedback: str

class Feedback(BaseModel):
    """User feedback on quiz content."""
    feedback_id: str = Field(default_factory=lambda: f"fb_{datetime.now().timestamp()}")
    quiz_id: str
    user_id: str
    rating: int = Field(ge=1, le=5)  # 1-5 stars
    comments: Optional[str] = None
    difficulty_rating: Optional[str] = None  # "too_easy", "just_right", "too_hard"
    engagement_rating: Optional[int] = None  # 1-5
    submitted_at: datetime = Field(default_factory=datetime.now)
