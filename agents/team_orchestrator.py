"""
Team Orchestrator for coordinating the multi-agent system.

This module implements the Financial Education Quiz system using Agno's 
hierarchical Team framework for multi-agent coordination.

Team Structure:
    Educational Quiz Team (Leader - GPT-4)
    ├── Personalization Agent
    │   └── Gathers user context, profile, and learning history
    ├── Content Generation Team (Sub-team)
    │   ├── Story Generator Agent
    │   │   └── Creates personalized educational stories
    │   └── Quiz Generator Agent
    │       └── Generates quiz questions from stories
    ├── Evaluation Agent
    │   └── Scores quizzes and provides feedback
    └── Gamification Agent
        └── Updates points, levels, badges, and streaks

Features:
    - Hierarchical team structure with clear agent roles
    - Sub-teams for related functionality (Content Generation)
    - Age-based content retrieval and personalization
    - Comprehensive gamification system
    - RAG-powered knowledge retrieval

For more details, see: docs/AGNO_TEAM_MIGRATION.md
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from agno.team import Team
from agno.agent import Agent
from agno.models.openai import OpenAIChat

from models import (
    UserProfile, Quiz, QuizResponse, QuizResult, 
    EducationalStory, QuizQuestion, DifficultyLevel
)
from agents.personalization_agent import PersonalizationAgent
from agents.content_generation_agent import ContentGenerationAgent
from agents.quiz_generation_agent import QuizGenerationAgent
from agents.evaluation_agent import EvaluationAgent
from agents.gamification_agent import GamificationAgent
from agents.agno_tools import AgnoToolkit
from services.mcp_client import MCPClient
from services.rag_service import RAGService
from config import config

logger = logging.getLogger(__name__)


class TeamOrchestrator:
    """
    Team-based orchestrator that coordinates all agents to generate
    personalized educational quizzes using Agno's Team pattern.
    """
    
    def __init__(self, mcp_client: MCPClient, rag_service: RAGService):
        """Initialize the orchestrator with Agno Team structure."""
        self.mcp_client = mcp_client
        self.rag_service = rag_service
        
        # Initialize legacy agents (these wrap existing logic)
        self.personalization_agent = PersonalizationAgent(mcp_client)
        self.content_agent = ContentGenerationAgent(rag_service)
        self.quiz_agent = QuizGenerationAgent(rag_service)
        self.evaluation_agent = EvaluationAgent()
        self.gamification_agent = GamificationAgent(mcp_client)
        
        # Initialize Agno toolkit with all tools
        self.toolkit = AgnoToolkit(mcp_client, rag_service)
        
        # Create Agno Team structure
        self.team = self._create_team()
        
        logger.info("=" * 60)
        logger.info("Team Orchestrator initialized with all agents and tools")
        logger.info("Team Structure:")
        logger.info(self.get_team_structure())
        logger.info("=" * 60)
    
    def _create_team(self) -> Team:
        """
        Create Agno Team with specialized agent members.
        
        Team Structure:
        - Team Leader: Coordinates quiz generation workflow
        - Members:
          1. Personalization Agent: Gathers user context
          2. Content Generation Sub-Team:
             - Story Generator Agent
             - Quiz Generator Agent
          3. Evaluation Agent: Scores quiz responses
          4. Gamification Agent: Updates points and badges
        """
        
        # Create individual Agno agents
        personalization_agno = Agent(
            id="personalization-agent",
            name="Personalization Agent",
            role="Gather user profile, quiz history, and learning preferences to personalize educational content",
            instructions="""
            You are responsible for:
            1. Fetching user profile data (age, name, hobbies, interests)
            2. Retrieving quiz history and performance metrics
            3. Analyzing user preferences and learning patterns
            4. Providing comprehensive user context to other agents
            
            Return structured context including user_profile, quiz_history, and gamification_data.
            """,
        )
        
        story_generator_agno = Agent(
            id="story-generator-agent",
            name="Story Generator Agent",
            role="Create engaging, age-appropriate educational stories about financial concepts",
            instructions="""
            You are responsible for:
            1. Using RAG to retrieve relevant knowledge about the financial concept
            2. Creating personalized stories based on user's age, hobbies, and interests
            3. Adapting story complexity to match the difficulty level
            4. Ensuring stories are educational and engaging
            
            Generate stories that teach financial concepts through relatable scenarios.
            """,
        )
        
        quiz_generator_agno = Agent(
            id="quiz-generator-agent",
            name="Quiz Generator Agent",
            role="Generate quiz questions based on educational stories and financial concepts",
            instructions="""
            You are responsible for:
            1. Creating multiple-choice questions that test understanding
            2. Ensuring questions align with the story and concept
            3. Adjusting question difficulty based on user's level
            4. Providing clear explanations for correct answers
            
            Generate 3-5 questions per quiz with 4 options each.
            """,
        )
        
        evaluation_agno = Agent(
            id="evaluation-agent",
            name="Evaluation Agent",
            role="Score quiz responses and provide detailed feedback",
            instructions="""
            You are responsible for:
            1. Comparing user answers with correct answers
            2. Calculating score and percentage
            3. Identifying strengths and areas for improvement
            4. Providing constructive feedback
            
            Return QuizResult with score, feedback, and recommendations.
            """,
        )
        
        gamification_agno = Agent(
            id="gamification-agent",
            name="Gamification Agent",
            role="Update user points, levels, badges, and streaks based on quiz performance",
            instructions="""
            You are responsible for:
            1. Calculating points earned based on quiz score
            2. Checking for level-ups and milestone achievements
            3. Awarding appropriate badges (first_quiz, perfect_score, streak_master, etc.)
            4. Updating streak data and maintaining engagement metrics
            
            Return gamification updates including points_earned, level_up, and new_badges.
            """,
        )
        
        # Create Content Generation sub-team
        content_generation_team = Team(
            name="Content Generation Team",
            role="Generate personalized educational content including stories and quiz questions",
            members=[story_generator_agno, quiz_generator_agno],
            instructions="""
            Coordinate story generation and quiz creation:
            1. Story Generator creates the educational story first
            2. Quiz Generator creates questions based on the story
            3. Ensure consistency between story and questions
            """,
        )
        
        # Create main Educational Quiz Team
        educational_quiz_team = Team(
            name="Educational Quiz Team",
            role="Generate and evaluate personalized educational quizzes for financial literacy",
            members=[
                personalization_agno,
                content_generation_team,
                evaluation_agno,
                gamification_agno
            ],
            model=OpenAIChat(id="gpt-4o"),
            instructions="""
            You are the team leader coordinating educational quiz generation.
            
            Workflow:
            1. Delegate to Personalization Agent to gather user context
            2. Delegate to Content Generation Team to create story and questions
            3. After user completes quiz, delegate to Evaluation Agent to score
            4. Delegate to Gamification Agent to update progress
            
            Ensure smooth coordination and data flow between agents.
            Maintain user engagement and learning effectiveness.
            """,
        )
        
        return educational_quiz_team
    
    async def generate_personalized_quiz(
        self, 
        user_id: str, 
        concept: str,
        difficulty: Optional[DifficultyLevel] = None
    ) -> Quiz:
        """
        Generate a complete personalized quiz for a user using Agno Team.
        
        Note: This is a hybrid approach - we use the Agno Team structure
        but still call our existing agent logic directly for now.
        Future enhancement: Migrate all logic into Agno agents with tools.
        
        Args:
            user_id: User identifier
            concept: Financial concept to teach
            difficulty: Optional difficulty override
            
        Returns:
            Complete Quiz object with story and questions
        """
        logger.info(f"[Team] Starting quiz generation for user {user_id}, concept: {concept}")
        
        try:
            # Step 1: Gather personalization context
            logger.info("[Team] Step 1: Personalization Agent gathering user context")
            context = await self.personalization_agent.gather_user_context(
                user_id, concept
            )
            
            # Determine difficulty if not provided
            if not difficulty:
                difficulty = self._determine_difficulty(context)
            
            # Step 2: Content Generation Team - Case Brief Generator
            logger.info("[Team] Step 2: Content Generation Team - Creating interactive case brief")
            case_brief = await self.content_agent.generate_case_brief(
                concept=concept,
                user_context=context,
                difficulty=difficulty
            )
            
            # Step 3: Content Generation Team - Quiz Generator
            logger.info("[Team] Step 3: Content Generation Team - Quiz Generator creating questions")
            questions = await self.quiz_agent.generate_questions(
                concept=concept,
                story=case_brief,  # Pass case_brief as story for compatibility
                difficulty=difficulty,
                user_context=context
            )
            
            # Step 4: Create complete quiz with case_brief
            quiz = Quiz(
                quiz_id=f"quiz_{user_id}_{datetime.now().timestamp()}",
                user_id=user_id,
                concept=concept,
                case_brief=case_brief,
                story=None,  # Deprecated
                questions=questions,
                difficulty=difficulty
            )
            
            logger.info(f"[Team] Successfully generated quiz {quiz.quiz_id}")
            return quiz
            
        except Exception as e:
            logger.error(f"[Team] Error generating quiz: {str(e)}", exc_info=True)
            raise
    
    async def evaluate_quiz(
        self, 
        quiz: Quiz, 
        response: QuizResponse
    ) -> QuizResult:
        """
        Evaluate a user's quiz responses using Agno Team structure.
        
        Args:
            quiz: Original quiz object
            response: User's answers
            
        Returns:
            QuizResult with score and gamification updates
        """
        logger.info(f"[Team] Evaluating quiz {quiz.quiz_id} for user {response.user_id}")
        
        try:
            # Step 1: Evaluation Agent scores the quiz
            logger.info("[Team] Step 1: Evaluation Agent scoring quiz")
            result = await self.evaluation_agent.evaluate(quiz, response)
            
            # Step 2: Gamification Agent updates progress
            logger.info("[Team] Step 2: Gamification Agent updating user progress")
            gamification_update = await self.gamification_agent.update_after_quiz(
                user_id=response.user_id,
                quiz_result=result,
                concept=quiz.concept
            )
            
            # Merge gamification updates into result
            result.points_earned = gamification_update.get("points_earned", 0)
            result.level_up = gamification_update.get("level_up", False)
            result.new_badges = gamification_update.get("new_badges", [])
            
            logger.info(f"[Team] Quiz evaluation complete. Score: {result.percentage}%")
            return result
            
        except Exception as e:
            logger.error(f"[Team] Error evaluating quiz: {str(e)}", exc_info=True)
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
        logger.info(f"[Team] Fetching dashboard data for user {user_id}")
        
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
            logger.error(f"[Team] Error fetching dashboard: {str(e)}", exc_info=True)
            raise
    
    def get_team_structure(self) -> str:
        """Return a visual representation of the team structure."""
        structure = """
        Educational Quiz Team (Team Leader)
        ├── Personalization Agent
        │   └── Role: Gather user context and preferences
        ├── Content Generation Team (Sub-team)
        │   ├── Story Generator Agent
        │   │   └── Role: Create educational stories
        │   └── Quiz Generator Agent
        │       └── Role: Generate quiz questions
        ├── Evaluation Agent
        │   └── Role: Score quiz and provide feedback
        └── Gamification Agent
            └── Role: Update points, levels, badges
        """
        return structure
