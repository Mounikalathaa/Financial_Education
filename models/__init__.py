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

class EducationalStory(BaseModel):
    """Educational story model."""
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
    story: EducationalStory
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

class BiasAnalysis(BaseModel):
    """Analysis of potential bias in content."""
    has_bias: bool
    bias_types: List[str] = []  # e.g., ["gender", "cultural", "economic"]
    severity: str = "low"  # "low", "medium", "high"
    specific_issues: List[str] = []
    recommendations: List[str] = []
    confidence_score: float = 0.0
    analyzed_at: datetime = Field(default_factory=datetime.now)

class QuizFeedback(BaseModel):
    """Enhanced feedback model with bias analysis."""
    feedback_id: str
    quiz_id: str
    user_id: str
    concept: str
    rating: int = Field(ge=1, le=5)
    comments: Optional[str] = None
    difficulty_perception: Optional[str] = None  # "too_easy", "just_right", "too_hard"
    relevance_score: Optional[int] = Field(None, ge=1, le=5)
    bias_analysis: Optional[BiasAnalysis] = None
    created_at: datetime = Field(default_factory=datetime.now)
    processed: bool = False

class ReviewAction(str, Enum):
    """Admin review action types."""
    APPROVE = "approve"  # AI decision was correct
    REJECT = "reject"  # AI decision was wrong
    FLAG_BIAS = "flag_bias"  # Admin found bias AI missed
    UPDATE_CONTENT = "update_content"  # Force content update
    DISMISS = "dismiss"  # False alarm, no action needed

class AdminReview(BaseModel):
    """Admin review of feedback and bias detection."""
    review_id: str
    feedback_id: str
    admin_id: str
    decision: ReviewAction
    admin_notes: Optional[str] = None
    bias_override: Optional[Dict[str, Any]] = None
    actions_taken: List[str] = []
    reviewed_at: datetime = Field(default_factory=datetime.now)

