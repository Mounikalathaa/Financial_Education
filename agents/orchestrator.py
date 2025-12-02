"""Agent orchestrator for coordinating the multi-agent system."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json

from models import (
    UserProfile, Quiz, QuizResponse, QuizResult, 
    EducationalStory, QuizQuestion, DifficultyLevel
)
from agents.personalization_agent import PersonalizationAgent
from agents.content_generation_agent import ContentGenerationAgent
from agents.quiz_generation_agent import QuizGenerationAgent
from agents.evaluation_agent import EvaluationAgent
from agents.gamification_agent import GamificationAgent
from services.mcp_client import MCPClient
from services.rag_service import RAGService
from config import config
from utils.logging_utils import AgentTracer

logger = logging.getLogger(__name__)

class OrchestratorAgent:
    """
    Hierarchical orchestrator that coordinates all agents to generate
    personalized educational quizzes.
    """
    
    def __init__(self, mcp_client: MCPClient, rag_service: RAGService):
        """Initialize the orchestrator with required services."""
        self.mcp_client = mcp_client
        self.rag_service = rag_service
        
        # Initialize sub-agents
        self.personalization_agent = PersonalizationAgent(mcp_client)
        self.content_agent = ContentGenerationAgent(rag_service)
        self.quiz_agent = QuizGenerationAgent(rag_service)
        self.evaluation_agent = EvaluationAgent()
        self.gamification_agent = GamificationAgent(mcp_client)
        
        # Initialize tracer
        self.tracer = AgentTracer(logger)
        
        logger.info("Orchestrator initialized with all sub-agents")
    
    async def generate_personalized_quiz(
        self, 
        user_id: str, 
        concept: str,
        difficulty: Optional[DifficultyLevel] = None
    ) -> Quiz:
        """
        Generate a complete personalized quiz for a user.
        
        Orchestration Flow:
        1. Personalization Agent: Gather user context
        2. Content Generation Agent: Create personalized story
        3. Quiz Generation Agent: Generate questions
        4. Package into Quiz object
        
        Args:
            user_id: User identifier
            concept: Financial concept to teach
            difficulty: Optional difficulty override
            
        Returns:
            Complete Quiz object with story and questions
        """
        logger.info(f"Starting quiz generation for user {user_id}, concept: {concept}")
        
        # Clear previous traces and start new trace session
        self.tracer.clear_traces()
        logger.info(f"\n{'='*80}")
        logger.info(f"🚀 STARTING QUIZ GENERATION")
        logger.info(f"User: {user_id} | Concept: {concept} | Difficulty: {difficulty}")
        logger.info(f"{'='*80}\n")
        
        try:
            # Step 1: Gather personalization context
            self.tracer.log_step(
                "Orchestrator", 
                "Initiating personalization phase",
                {"user_id": user_id, "concept": concept}
            )
            
            self.tracer.log_step(
                "PersonalizationAgent", 
                "Calling gather_user_context",
                {"tool": "MCP.get_user_profile", "status": "starting"}
            )
            
            context = await self.personalization_agent.gather_user_context(
                user_id, concept
            )
            
            self.tracer.log_step(
                "PersonalizationAgent",
                "Tool output received",
                {
                    "tool": "MCP.get_user_profile",
                    "output_summary": {
                        "age": context.get("age"),
                        "quiz_history_count": len(context.get("quiz_history", [])),
                        "has_transactions": len(context.get("transactions", [])) > 0
                    }
                }
            )
            
            # Determine difficulty if not provided
            if not difficulty:
                difficulty = self._determine_difficulty(context)
                self.tracer.log_step(
                    "Orchestrator",
                    "Reasoning: Difficulty determined",
                    {"difficulty": difficulty.value, "reason": "Based on age and quiz history"}
                )
            
            # Step 2: Generate educational story
            self.tracer.log_step(
                "Orchestrator",
                "Initiating content generation phase",
                {"concept": concept, "difficulty": difficulty.value}
            )
            
            self.tracer.log_step(
                "ContentGenerationAgent",
                "Calling generate_story",
                {"tool": "RAG.retrieve_knowledge + OpenAI.chat", "status": "starting"}
            )
            
            story = await self.content_agent.generate_story(
                concept=concept,
                user_context=context,
                difficulty=difficulty
            )
            
            self.tracer.log_step(
                "ContentGenerationAgent",
                "Tool output received",
                {
                    "tool": "OpenAI.chat",
                    "output_summary": {
                        "title": story.title,
                        "content_length": len(story.content),
                        "personalization_elements": len(story.personalization_elements)
                    }
                }
            )
            
            self.tracer.log_step(
                "ContentGenerationAgent",
                "Reasoning: Story personalized",
                {
                    "reason": f"Story tailored for age {context.get('age')} with interests: {context.get('interests', [])[:2]}"
                }
            )
            
            # Step 3: Generate quiz questions
            self.tracer.log_step(
                "Orchestrator",
                "Initiating quiz generation phase",
                {"concept": concept, "story_title": story.title}
            )
            
            self.tracer.log_step(
                "QuizGenerationAgent",
                "Calling generate_questions",
                {"tool": "RAG.retrieve_knowledge + OpenAI.chat", "status": "starting"}
            )
            
            questions = await self.quiz_agent.generate_questions(
                concept=concept,
                story=story,
                difficulty=difficulty,
                user_context=context
            )
            
            self.tracer.log_step(
                "QuizGenerationAgent",
                "Tool output received",
                {
                    "tool": "OpenAI.chat",
                    "output_summary": {
                        "question_count": len(questions),
                        "difficulty": difficulty.value
                    }
                }
            )
            
            self.tracer.log_step(
                "QuizGenerationAgent",
                "Reasoning: Questions validated",
                {"reason": f"Generated {len(questions)} questions matching difficulty {difficulty.value}"}
            )
            
            # Step 4: Create complete quiz
            quiz = Quiz(
                quiz_id=f"quiz_{user_id}_{datetime.now().timestamp()}",
                user_id=user_id,
                concept=concept,
                story=story,
                questions=questions,
                difficulty=difficulty
            )
            
            self.tracer.log_step(
                "Orchestrator",
                "Quiz assembly complete",
                {
                    "quiz_id": quiz.quiz_id,
                    "total_components": {
                        "story": 1,
                        "questions": len(questions),
                        "personalization_elements": len(story.personalization_elements)
                    }
                }
            )
            
            # Log complete trace
            logger.info(f"\n{'='*80}")
            logger.info(f"✅ QUIZ GENERATION COMPLETE")
            logger.info(f"Quiz ID: {quiz.quiz_id}")
            logger.info(f"{'='*80}\n")
            logger.info(self.tracer.get_trace_summary())
            
            return quiz
            
        except Exception as e:
            logger.error(f"Error generating quiz: {str(e)}", exc_info=True)
            raise
    
    async def evaluate_quiz(
        self, 
        quiz: Quiz, 
        response: QuizResponse
    ) -> QuizResult:
        """
        Evaluate a user's quiz responses and update gamification.
        
        Args:
            quiz: Original quiz object
            response: User's answers
            
        Returns:
            QuizResult with score and gamification updates
        """
        logger.info(f"Evaluating quiz {quiz.quiz_id} for user {response.user_id}")
        
        try:
            # Step 1: Evaluate answers
            result = await self.evaluation_agent.evaluate(quiz, response)
            
            # Step 2: Update gamification
            logger.info("Updating gamification data")
            gamification_update = await self.gamification_agent.update_after_quiz(
                user_id=response.user_id,
                quiz_result=result,
                concept=quiz.concept
            )
            
            # Merge gamification updates into result
            result.points_earned = gamification_update.get("points_earned", 0)
            result.level_up = gamification_update.get("level_up", False)
            result.new_badges = gamification_update.get("new_badges", [])
            
            logger.info(f"Quiz evaluation complete. Score: {result.percentage}%")
            return result
            
        except Exception as e:
            logger.error(f"Error evaluating quiz: {str(e)}", exc_info=True)
            raise
    
    def _determine_difficulty(self, context: Dict[str, Any]) -> DifficultyLevel:
        """Determine appropriate difficulty based on user context."""
        user_profile = context.get("user_profile")
        quiz_history = context.get("quiz_history", [])
        
        # Age-based baseline
        age = user_profile.age if user_profile else 10
        if age < 10:
            base_difficulty = DifficultyLevel.BEGINNER
        elif age < 14:
            base_difficulty = DifficultyLevel.INTERMEDIATE
        else:
            base_difficulty = DifficultyLevel.ADVANCED
        
        # Adjust based on performance
        if quiz_history:
            recent_scores = [q.score / q.total_questions for q in quiz_history[-5:]]
            avg_score = sum(recent_scores) / len(recent_scores)
            
            if avg_score > 0.9 and base_difficulty != DifficultyLevel.ADVANCED:
                # Increase difficulty if performing well
                if base_difficulty == DifficultyLevel.BEGINNER:
                    return DifficultyLevel.INTERMEDIATE
                else:
                    return DifficultyLevel.ADVANCED
            elif avg_score < 0.6 and base_difficulty != DifficultyLevel.BEGINNER:
                # Decrease difficulty if struggling
                if base_difficulty == DifficultyLevel.ADVANCED:
                    return DifficultyLevel.INTERMEDIATE
                else:
                    return DifficultyLevel.BEGINNER
        
        return base_difficulty
    
    async def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user dashboard data."""
        logger.info(f"Fetching dashboard data for user {user_id}")
        
        try:
            # Gather all user data in parallel
            user_profile = await self.mcp_client.get_user_profile(user_id)
            gamification = await self.mcp_client.get_gamification_data(user_id)
            quiz_history = await self.mcp_client.get_quiz_history(user_id)
            
            return {
                "user_profile": user_profile,
                "gamification": gamification,
                "quiz_history": quiz_history,
                "available_concepts": config.financial_concepts
            }
            
        except Exception as e:
            logger.error(f"Error fetching dashboard: {str(e)}", exc_info=True)
            raise
