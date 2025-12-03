"""Tools for integrating agents with Team Orchestrator framework."""

import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from models import (
    UserProfile, Quiz, QuizResponse, QuizResult,
    EducationalStory, CaseBrief, QuizQuestion, DifficultyLevel
)
from agents.personalization_agent import PersonalizationAgent
from agents.content_generation_agent import ContentGenerationAgent
from agents.quiz_generation_agent import QuizGenerationAgent
from agents.evaluation_agent import EvaluationAgent
from agents.gamification_agent import GamificationAgent
from services.mcp_client import MCPClient
from services.rag_service import RAGService

logger = logging.getLogger(__name__)


class PersonalizationTools:
    """Tools for gathering user context and personalization data."""
    
    def __init__(self, mcp_client: MCPClient):
        self.agent = PersonalizationAgent(mcp_client)
        logger.info("PersonalizationTools initialized")
    
    async def gather_user_context(
        self, 
        user_id: str, 
        concept: str
    ) -> Dict[str, Any]:
        """
        Gather comprehensive user context including profile, history, and preferences.
        
        Args:
            user_id: User identifier
            concept: Financial concept to teach
            
        Returns:
            Dictionary containing user_profile, quiz_history, gamification_data
        """
        logger.info(f"[PersonalizationTools] Gathering context for user {user_id}, concept: {concept}")
        return await self.agent.gather_user_context(user_id, concept)


class ContentGenerationTools:
    """Tools for generating educational content (case briefs and stories)."""
    
    def __init__(self, rag_service: RAGService):
        self.agent = ContentGenerationAgent(rag_service)
        logger.info("ContentGenerationTools initialized")
    
    async def generate_case_brief(
        self,
        concept: str,
        user_context: Dict[str, Any],
        difficulty: DifficultyLevel
    ) -> CaseBrief:
        """
        Generate interactive detective-style case brief for engaging learning.
        
        Args:
            concept: Financial concept to teach
            user_context: User profile and preferences
            difficulty: Content difficulty level
            
        Returns:
            CaseBrief object with mission, clues, and scenario
        """
        logger.info(f"[ContentGenerationTools] Generating case brief for concept: {concept}, difficulty: {difficulty}")
        return await self.agent.generate_case_brief(concept, user_context, difficulty)
    
    async def generate_story(
        self,
        concept: str,
        user_context: Dict[str, Any],
        difficulty: DifficultyLevel
    ) -> EducationalStory:
        """
        Generate personalized educational story (legacy method).
        
        Args:
            concept: Financial concept to teach
            user_context: User profile and preferences
            difficulty: Story difficulty level
            
        Returns:
            EducationalStory object with title and content
        """
        logger.info(f"[ContentGenerationTools] Generating story for concept: {concept}, difficulty: {difficulty}")
        return await self.agent.generate_story(concept, user_context, difficulty)


class QuizGenerationTools:
    """Tools for generating quiz questions."""
    
    def __init__(self, rag_service: RAGService):
        self.agent = QuizGenerationAgent(rag_service)
        logger.info("QuizGenerationTools initialized")
    
    async def generate_questions(
        self,
        concept: str,
        story: EducationalStory,
        difficulty: DifficultyLevel,
        user_context: Dict[str, Any]
    ) -> List[QuizQuestion]:
        """
        Generate quiz questions based on educational story.
        
        Args:
            concept: Financial concept being tested
            story: Educational story questions are based on
            difficulty: Question difficulty level
            user_context: User profile for personalization
            
        Returns:
            List of QuizQuestion objects
        """
        logger.info(f"[QuizGenerationTools] Generating questions for concept: {concept}")
        return await self.agent.generate_questions(concept, story, difficulty, user_context)


class EvaluationTools:
    """Tools for evaluating quiz responses."""
    
    def __init__(self):
        self.agent = EvaluationAgent()
        logger.info("EvaluationTools initialized")
    
    async def evaluate_quiz(
        self,
        quiz: Quiz,
        response: QuizResponse
    ) -> QuizResult:
        """
        Evaluate user's quiz responses and provide feedback.
        
        Args:
            quiz: Original quiz object
            response: User's answers
            
        Returns:
            QuizResult with score and feedback
        """
        logger.info(f"[EvaluationTools] Evaluating quiz {quiz.quiz_id}")
        return await self.agent.evaluate(quiz, response)


class GamificationTools:
    """Tools for updating gamification data."""
    
    def __init__(self, mcp_client: MCPClient):
        self.agent = GamificationAgent(mcp_client)
        logger.info("GamificationTools initialized")
    
    async def update_after_quiz(
        self,
        user_id: str,
        quiz_result: QuizResult,
        concept: str
    ) -> Dict[str, Any]:
        """
        Update user's gamification data after quiz completion.
        
        Args:
            user_id: User identifier
            quiz_result: Quiz result with score
            concept: Financial concept that was tested
            
        Returns:
            Dictionary with points_earned, level_up, new_badges
        """
        logger.info(f"[GamificationTools] Updating gamification for user {user_id}")
        return await self.agent.update_after_quiz(user_id, quiz_result, concept)


class AgnoToolkit:
    """
    Combined toolkit providing all tools needed for educational quiz generation.
    This is the main interface for Agno agents.
    """
    
    def __init__(self, mcp_client: MCPClient, rag_service: RAGService):
        """Initialize all tool categories."""
        self.personalization = PersonalizationTools(mcp_client)
        self.content = ContentGenerationTools(rag_service)
        self.quiz = QuizGenerationTools(rag_service)
        self.evaluation = EvaluationTools()
        self.gamification = GamificationTools(mcp_client)
        
        logger.info("AgnoToolkit initialized with all tools")
    
    def get_all_tools(self) -> List[Any]:
        """
        Get list of all tool instances for Agno agents.
        
        Returns:
            List of tool objects that can be used by Agno agents
        """
        return [
            self.personalization,
            self.content,
            self.quiz,
            self.evaluation,
            self.gamification
        ]
