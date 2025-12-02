"""Feedback processing and storage."""

import json
from pathlib import Path
from typing import List
from datetime import datetime
from models import Feedback

class FeedbackProcessor:
    """Process and store user feedback."""
    
    def __init__(self, feedback_file: str = "./data/feedback.json"):
        self.feedback_file = Path(feedback_file)
        self.feedback_file.parent.mkdir(parents=True, exist_ok=True)
        self.feedback_data = self._load_feedback()
    
    def _load_feedback(self) -> List[dict]:
        """Load existing feedback from file."""
        if self.feedback_file.exists():
            with open(self.feedback_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_feedback(self):
        """Save feedback to file."""
        with open(self.feedback_file, 'w') as f:
            json.dump(self.feedback_data, f, indent=2)
    
    def add_feedback(self, feedback: Feedback):
        """Add new feedback entry."""
        self.feedback_data.append(feedback.model_dump(mode='json'))
        self._save_feedback()
    
    def get_quiz_feedback(self, quiz_id: str) -> List[Feedback]:
        """Get all feedback for a specific quiz."""
        return [
            Feedback(**fb) for fb in self.feedback_data 
            if fb.get('quiz_id') == quiz_id
        ]
    
    def get_user_feedback(self, user_id: str) -> List[Feedback]:
        """Get all feedback from a specific user."""
        return [
            Feedback(**fb) for fb in self.feedback_data 
            if fb.get('user_id') == user_id
        ]
    
    def get_concept_feedback(self, concept: str) -> List[Feedback]:
        """Get feedback for quizzes about a specific concept."""
        # Would need to join with quiz data to filter by concept
        # Simplified version for now
        return [Feedback(**fb) for fb in self.feedback_data]
    
    def get_average_rating(self, concept: str = None) -> float:
        """Get average rating, optionally filtered by concept."""
        ratings = [fb.get('rating', 0) for fb in self.feedback_data]
        return sum(ratings) / len(ratings) if ratings else 0.0
    
    def get_difficulty_feedback(self) -> dict:
        """Get distribution of difficulty ratings."""
        distribution = {"too_easy": 0, "just_right": 0, "too_hard": 0}
        for fb in self.feedback_data:
            diff = fb.get('difficulty_rating')
            if diff and diff in distribution:
                distribution[diff] += 1
        return distribution
