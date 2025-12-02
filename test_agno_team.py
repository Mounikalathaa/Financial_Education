"""Test script to verify Agno Team structure is working correctly."""

import asyncio
import logging
from agents.team_orchestrator import TeamOrchestrator
from services.mcp_client import MCPClient
from services.rag_service import RAGService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_team_initialization():
    """Test that the Agno Team initializes correctly."""
    print("\n" + "="*60)
    print("Testing Agno Team Initialization")
    print("="*60 + "\n")
    
    # Initialize services
    mcp_client = MCPClient()
    rag_service = RAGService()
    
    # Initialize Team orchestrator
    orchestrator = TeamOrchestrator(mcp_client, rag_service)
    
    print("\n✅ Agno Team initialized successfully!")
    print("\nTeam Members:")
    print(f"  - Team: {orchestrator.team.name}")
    print(f"  - Model: {orchestrator.team.model.id if orchestrator.team.model else 'Not specified'}")
    print(f"  - Number of members: {len(orchestrator.team.members)}")
    
    print("\nTeam Structure:")
    print(orchestrator.get_team_structure())
    
    print("\nToolkit Available:")
    print(f"  - Personalization Tools: {orchestrator.toolkit.personalization}")
    print(f"  - Content Tools: {orchestrator.toolkit.content}")
    print(f"  - Quiz Tools: {orchestrator.toolkit.quiz}")
    print(f"  - Evaluation Tools: {orchestrator.toolkit.evaluation}")
    print(f"  - Gamification Tools: {orchestrator.toolkit.gamification}")
    
    return orchestrator

async def test_quiz_generation_flow():
    """Test that quiz generation flow still works with Agno Team."""
    print("\n" + "="*60)
    print("Testing Quiz Generation Flow (Hybrid Mode)")
    print("="*60 + "\n")
    
    # Initialize
    mcp_client = MCPClient()
    rag_service = RAGService()
    orchestrator = TeamOrchestrator(mcp_client, rag_service)
    
    print("Attempting to generate quiz for test user...")
    print("User ID: user_test")
    print("Concept: banking")
    print("Difficulty: intermediate")
    
    try:
        # This will use the hybrid approach - Agno structure but legacy agents
        from models import DifficultyLevel
        quiz = await orchestrator.generate_personalized_quiz(
            user_id="user_test",
            concept="banking",
            difficulty=DifficultyLevel.INTERMEDIATE
        )
        
        print(f"\n✅ Quiz generated successfully!")
        print(f"  - Quiz ID: {quiz.quiz_id}")
        print(f"  - Concept: {quiz.concept}")
        print(f"  - Difficulty: {quiz.difficulty}")
        print(f"  - Story Title: {quiz.story.title}")
        print(f"  - Number of Questions: {len(quiz.questions)}")
        
        return quiz
        
    except Exception as e:
        print(f"\n❌ Error generating quiz: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Run all tests."""
    print("\n" + "🚀 "*30)
    print("Agno Team Migration Test Suite")
    print("🚀 "*30 + "\n")
    
    # Test 1: Initialization
    orchestrator = await test_team_initialization()
    
    # Test 2: Quiz Generation (will only work if API keys are configured)
    print("\n" + "-"*60 + "\n")
    print("⚠️  Note: Quiz generation test requires Azure OpenAI API keys")
    print("If not configured, this test will fail (expected)")
    print("-"*60 + "\n")
    
    await test_quiz_generation_flow()
    
    print("\n" + "="*60)
    print("Test Suite Complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
