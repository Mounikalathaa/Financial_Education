"""Gamification agent for managing points, levels, and badges."""

import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from models import QuizResult, GamificationData
from config import config

logger = logging.getLogger(__name__)

class GamificationAgent:
    """Agent responsible for gamification logic."""
    
    def __init__(self, mcp_client):
        """Initialize with MCP client."""
        self.mcp_client = mcp_client
    
    async def update_after_quiz(
        self,
        user_id: str,
        quiz_result: QuizResult,
        concept: str
    ) -> Dict[str, Any]:
        """
        Update gamification data after quiz completion.
        
        Args:
            user_id: User identifier
            quiz_result: Quiz evaluation result
            concept: Financial concept
            
        Returns:
            Dictionary with gamification updates
        """
        logger.info(f"Updating gamification for user {user_id}")
        
        try:
            # Get current gamification data
            gamif_data = await self.mcp_client.get_gamification_data(user_id)
            print(f"🔍 DEBUG: Current gamification data: {gamif_data}")
            
            # Calculate points earned
            points_for_correct = quiz_result.score * config.gamification.points_per_correct
            completion_bonus = config.gamification.points_per_quiz
            total_points_earned = points_for_correct + completion_bonus
            print(f"💰 DEBUG: Points calculation: {quiz_result.score} correct × {config.gamification.points_per_correct} + {completion_bonus} bonus = {total_points_earned} points")
            
            # Update points
            old_total = gamif_data.total_points
            new_total = old_total + total_points_earned
            print(f"📊 DEBUG: Points update: {old_total} + {total_points_earned} = {new_total}")
            
            # Check for level up
            old_level = config.get_level_for_points(old_total)
            new_level = config.get_level_for_points(new_total)
            level_up = old_level["name"] != new_level["name"]
            print(f"🏆 DEBUG: Level: {old_level['name']} → {new_level['name']} (level_up: {level_up})")
            
            # Update streak
            new_streak = self._calculate_streak(gamif_data)
            print(f"🔥 DEBUG: Streak: {gamif_data.streak_days} → {new_streak}")
            
            # Check for new badges
            new_badges = await self._check_new_badges(
                user_id, gamif_data, quiz_result, new_streak, concept
            )
            print(f"🎖️ DEBUG: New badges: {new_badges}")
            
            # Update gamification data
            gamif_data.total_points = new_total
            gamif_data.level = new_level["name"]
            gamif_data.quizzes_completed += 1
            gamif_data.streak_days = new_streak
            gamif_data.last_quiz_date = datetime.now()
            
            if quiz_result.percentage == 100:
                gamif_data.perfect_scores += 1
            
            # Add new badges
            for badge_id in new_badges:
                if badge_id not in gamif_data.badges:
                    gamif_data.badges.append(badge_id)
            
            print(f"✅ DEBUG: Updated gamification data: points={gamif_data.total_points}, level={gamif_data.level}, quizzes={gamif_data.quizzes_completed}, streak={gamif_data.streak_days}, perfect={gamif_data.perfect_scores}")
            
            # Save updated data
            update_result = await self.mcp_client.update_gamification_data(user_id, gamif_data)
            print(f"💾 DEBUG: Update result: {update_result}")
            
            return {
                "points_earned": total_points_earned,
                "new_total_points": new_total,
                "level_up": level_up,
                "new_level": new_level["name"] if level_up else None,
                "new_badges": new_badges,
                "streak_days": new_streak
            }
            
        except Exception as e:
            logger.error(f"Error updating gamification: {str(e)}", exc_info=True)
            return {
                "points_earned": 0,
                "level_up": False,
                "new_badges": []
            }
    
    def _calculate_streak(self, gamif_data: GamificationData) -> int:
        """Calculate current streak in days."""
        if not gamif_data.last_quiz_date:
            return 1
        
        days_since_last = (datetime.now() - gamif_data.last_quiz_date).days
        
        if days_since_last == 0:
            # Same day, maintain streak
            return gamif_data.streak_days
        elif days_since_last == 1:
            # Next day, increment streak
            return gamif_data.streak_days + 1
        else:
            # Streak broken, restart
            return 1
    
    async def _check_new_badges(
        self,
        user_id: str,
        gamif_data: GamificationData,
        quiz_result: QuizResult,
        streak: int,
        concept: str
    ) -> list:
        """Check if user earned any new badges."""
        new_badges = []
        
        for badge in config.gamification.badges:
            # Skip if already earned
            if badge["id"] in gamif_data.badges:
                continue
            
            # Evaluate badge criteria
            earned = self._evaluate_badge_criteria(
                badge["criteria"],
                gamif_data,
                quiz_result,
                streak,
                concept
            )
            
            if earned:
                new_badges.append(badge["id"])
                logger.info(f"User {user_id} earned badge: {badge['name']}")
        
        return new_badges
    
    def _evaluate_badge_criteria(
        self,
        criteria: str,
        gamif_data: GamificationData,
        quiz_result: QuizResult,
        streak: int,
        concept: str
    ) -> bool:
        """Evaluate if badge criteria is met."""
        # Simple criteria evaluation
        # In production, this could be more sophisticated
        
        try:
            # Create evaluation context
            context = {
                "quizzes_completed": gamif_data.quizzes_completed,
                "perfect_scores": gamif_data.perfect_scores,
                "streak_days": streak,
                "savings_quizzes": gamif_data.quizzes_completed if concept == "saving" else 0
            }
            
            # Evaluate criteria
            return eval(criteria, {"__builtins__": {}}, context)
        except Exception as e:
            logger.error(f"Error evaluating badge criteria: {str(e)}")
            return False
