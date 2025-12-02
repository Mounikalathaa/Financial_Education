"""Test script to demonstrate agent tracing functionality."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.orchestrator import OrchestratorAgent
from services.mcp_client import MCPClient
from services.rag_service import RAGService
from models import DifficultyLevel
from utils.logging_utils import setup_logging

async def main():
    """Run a test quiz generation with full tracing."""
    
    # Setup logging with DEBUG level to see all details
    setup_logging(log_level="INFO")
    
    print("\n" + "="*80)
    print("AGENT TRACING DEMONSTRATION")
    print("="*80 + "\n")
    print("This will generate a quiz and show the complete execution trace:")
    print("  • Orchestrator decisions")
    print("  • Tool calls (MCP, RAG, OpenAI)")
    print("  • Tool outputs")
    print("  • Agent reasoning")
    print("\n" + "="*80 + "\n")
    
    # Initialize services
    mcp_client = MCPClient()
    rag_service = RAGService()
    
    # Initialize orchestrator
    orchestrator = OrchestratorAgent(mcp_client, rag_service)
    
    # Generate a quiz
    try:
        quiz = await orchestrator.generate_personalized_quiz(
            user_id="user_john",
            concept="Saving Money",
            difficulty=DifficultyLevel.BEGINNER
        )
        
        print("\n" + "="*80)
        print("QUIZ GENERATION RESULTS")
        print("="*80)
        print(f"Quiz ID: {quiz.quiz_id}")
        print(f"Concept: {quiz.concept}")
        print(f"Story Title: {quiz.story.title}")
        print(f"Questions: {len(quiz.questions)}")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\nError during quiz generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
