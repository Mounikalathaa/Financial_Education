"""Evaluation agent for grading quiz responses."""

import logging
from typing import Dict, Any
from models import Quiz, QuizResponse, QuizResult

logger = logging.getLogger(__name__)

class EvaluationAgent:
    """Agent responsible for evaluating quiz responses."""
    
    def __init__(self):
        """Initialize evaluation agent."""
        pass
    
    async def evaluate(self, quiz: Quiz, response: QuizResponse) -> QuizResult:
        """
        Evaluate user's quiz responses.
        
        Args:
            quiz: Original quiz object
            response: User's submitted answers
            
        Returns:
            QuizResult with scoring and feedback
        """
        logger.info(f"Evaluating quiz {quiz.quiz_id}")
        
        correct_questions = []
        incorrect_questions = []
        
        # Grade each question
        for question in quiz.questions:
            user_answer = response.answers.get(question.question_id)
            
            if user_answer and user_answer.strip() == question.correct_answer.strip():
                correct_questions.append(question.question_id)
            else:
                incorrect_questions.append(question.question_id)
        
        # Calculate score
        score = len(correct_questions)
        total = len(quiz.questions)
        percentage = (score / total * 100) if total > 0 else 0
        
        # Generate feedback
        feedback = self._generate_feedback(score, total, percentage, quiz.difficulty.value)
        
        result = QuizResult(
            quiz_id=quiz.quiz_id,
            user_id=response.user_id,
            score=score,
            total_questions=total,
            percentage=percentage,
            correct_questions=correct_questions,
            incorrect_questions=incorrect_questions,
            points_earned=0,  # Will be set by gamification agent
            feedback=feedback
        )
        
        logger.info(f"Quiz evaluated: {score}/{total} ({percentage:.1f}%)")
        return result
    
    def _generate_feedback(
        self, 
        score: int, 
        total: int, 
        percentage: float,
        difficulty: str
    ) -> str:
        """Generate encouraging feedback based on performance."""
        if percentage == 100:
            return "🌟 Perfect score! You're a financial superstar! Keep up the amazing work!"
        elif percentage >= 80:
            return "🎉 Excellent work! You really understand this concept. Just a few more details to master!"
        elif percentage >= 60:
            return "👍 Good job! You're on the right track. Review the questions you missed and try again!"
        elif percentage >= 40:
            return "💪 Nice effort! This is a challenging topic. Take your time to review and you'll get better!"
        else:
            return "🌱 Great start! Learning takes time. Review the material and don't give up - you've got this!"
