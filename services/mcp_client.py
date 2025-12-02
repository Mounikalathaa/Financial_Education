"""MCP Client for communicating with the Multi-Controller Proxy server."""

import logging
import httpx
from typing import List, Optional, Dict, Any
from models import UserProfile, Transaction, QuizHistory, GamificationData
from config import config
from datetime import datetime

logger = logging.getLogger(__name__)

class MCPClient:
    """Client for MCP server communication."""
    
    def __init__(self, base_url: Optional[str] = None):
        """Initialize MCP client."""
        self.base_url = base_url or config.mcp.base_url
        self.timeout = config.mcp.timeout
        self.endpoints = config.mcp.endpoints
    
    async def get_user_profile(self, user_id: str) -> UserProfile:
        """Retrieve user profile from MCP."""
        logger.info(f"🔧 [MCP TOOL] Fetching user profile for {user_id}")
        logger.debug(f"   → URL: {self.base_url}{self.endpoints['user_profile']}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}{self.endpoints['user_profile']}",
                    params={"user_id": user_id}
                )
                response.raise_for_status()
                data = response.json()
                profile = UserProfile(**data)
                
                logger.info(f"✓ [MCP OUTPUT] Profile retrieved: {profile.name}, age {profile.age}")
                logger.debug(f"   → Hobbies: {profile.hobbies[:2]}...")
                logger.debug(f"   → Interests: {profile.interests[:2]}...")
                
                return profile
        except Exception as e:
            logger.error(f"✗ [MCP ERROR] Error fetching user profile: {str(e)}")
            # Return default profile on error
            default_profile = UserProfile(
                user_id=user_id,
                name="User",
                age=10,
                hobbies=[],
                interests=[]
            )
            logger.warning(f"   → Using default profile")
            return default_profile
    
    async def get_recent_transactions(
        self, 
        user_id: str, 
        limit: int = 10
    ) -> List[Transaction]:
        """Retrieve recent transactions from MCP."""
        logger.info(f"Fetching transactions for {user_id}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}{self.endpoints['transactions']}",
                    params={"user_id": user_id, "limit": limit}
                )
                response.raise_for_status()
                data = response.json()
                return [Transaction(**txn) for txn in data.get("transactions", [])]
        except Exception as e:
            logger.error(f"Error fetching transactions: {str(e)}")
            return []
    
    async def get_quiz_history(self, user_id: str) -> List[QuizHistory]:
        """Retrieve quiz history from MCP."""
        logger.info(f"Fetching quiz history for {user_id}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}{self.endpoints['quiz_history']}",
                    params={"user_id": user_id}
                )
                response.raise_for_status()
                data = response.json()
                return [QuizHistory(**quiz) for quiz in data.get("history", [])]
        except Exception as e:
            logger.error(f"Error fetching quiz history: {str(e)}")
            return []
    
    async def get_gamification_data(self, user_id: str) -> GamificationData:
        """Retrieve gamification data from MCP."""
        logger.info(f"Fetching gamification data for {user_id}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}{self.endpoints['gamification']}",
                    params={"user_id": user_id}
                )
                response.raise_for_status()
                data = response.json()
                return GamificationData(**data)
        except Exception as e:
            logger.error(f"Error fetching gamification data: {str(e)}")
            # Return default gamification data
            return GamificationData(
                user_id=user_id,
                total_points=0,
                level="Beginner",
                badges=[],
                streak_days=0,
                quizzes_completed=0,
                perfect_scores=0
            )
    
    async def update_gamification_data(
        self, 
        user_id: str, 
        gamif_data: GamificationData
    ) -> bool:
        """Update gamification data via MCP."""
        logger.info(f"Updating gamification data for {user_id}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}{self.endpoints['update_gamification']}",
                    json=gamif_data.model_dump(mode='json')
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Error updating gamification data: {str(e)}")
            print(f"❌ ERROR in update_gamification_data: {str(e)}")
            return False
    
    async def save_quiz_result(
        self, 
        user_id: str, 
        quiz_id: str,
        concept: str,
        score: int,
        total: int
    ) -> bool:
        """Save quiz result to history."""
        logger.info(f"Saving quiz result for {user_id}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/user/quiz-history",
                    json={
                        "user_id": user_id,
                        "quiz_id": quiz_id,
                        "concept": concept,
                        "score": score,
                        "total_questions": total,
                        "completed_at": datetime.now().isoformat()
                    }
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Error saving quiz result: {str(e)}")
            return False
