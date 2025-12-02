"""Personalization agent for gathering and analyzing user context."""

import logging
from typing import Dict, Any
from models import UserProfile, Transaction, QuizHistory

logger = logging.getLogger(__name__)

class PersonalizationAgent:
    """Agent responsible for gathering user-specific context for personalization."""
    
    def __init__(self, mcp_client):
        """Initialize with MCP client for data retrieval."""
        self.mcp_client = mcp_client
    
    async def gather_user_context(self, user_id: str, concept: str) -> Dict[str, Any]:
        """
        Gather comprehensive user context for personalization.
        
        Args:
            user_id: User identifier
            concept: Financial concept being taught
            
        Returns:
            Dictionary containing all relevant user context
        """
        logger.info(f"Gathering context for user {user_id}, concept: {concept}")
        
        try:
            # Retrieve user data from MCP
            user_profile = await self.mcp_client.get_user_profile(user_id)
            transactions = await self.mcp_client.get_recent_transactions(user_id, limit=10)
            quiz_history = await self.mcp_client.get_quiz_history(user_id)
            
            # Analyze context
            context = {
                "user_profile": user_profile,
                "age": user_profile.age,
                "hobbies": user_profile.hobbies,
                "interests": user_profile.interests,
                "recent_transactions": transactions,
                "quiz_history": quiz_history,
                "concept_performance": self._analyze_concept_performance(
                    quiz_history, concept
                ),
                "spending_patterns": self._analyze_spending(transactions)
            }
            
            logger.info(f"Context gathered successfully for user {user_id}")
            return context
            
        except Exception as e:
            logger.error(f"Error gathering user context: {str(e)}")
            # Return minimal context if data retrieval fails
            return {
                "user_profile": None,
                "age": 10,  # Default age
                "hobbies": [],
                "interests": [],
                "recent_transactions": [],
                "quiz_history": [],
                "concept_performance": None,
                "spending_patterns": {}
            }
    
    def _analyze_concept_performance(
        self, 
        quiz_history: list, 
        concept: str
    ) -> Dict[str, Any]:
        """Analyze user's past performance on this concept."""
        concept_quizzes = [q for q in quiz_history if q.concept == concept]
        
        if not concept_quizzes:
            return {"attempts": 0, "average_score": None, "mastery_level": "novice"}
        
        scores = [q.score / q.total_questions for q in concept_quizzes]
        avg_score = sum(scores) / len(scores)
        
        # Determine mastery level
        if avg_score >= 0.9:
            mastery = "expert"
        elif avg_score >= 0.7:
            mastery = "proficient"
        elif avg_score >= 0.5:
            mastery = "learning"
        else:
            mastery = "novice"
        
        return {
            "attempts": len(concept_quizzes),
            "average_score": avg_score,
            "mastery_level": mastery,
            "last_attempt_score": scores[-1] if scores else None
        }
    
    def _analyze_spending(self, transactions: list) -> Dict[str, Any]:
        """Analyze spending patterns from transactions."""
        if not transactions:
            return {}
        
        # Calculate category distribution
        categories = {}
        total_spent = 0
        
        for txn in transactions:
            categories[txn.category] = categories.get(txn.category, 0) + abs(txn.amount)
            total_spent += abs(txn.amount)
        
        return {
            "total_spent": total_spent,
            "category_distribution": categories,
            "top_category": max(categories.items(), key=lambda x: x[1])[0] if categories else None,
            "transaction_count": len(transactions)
        }
