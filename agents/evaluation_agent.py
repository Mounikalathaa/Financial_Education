"""Evaluation agent for grading quiz responses."""

import logging
import os
from typing import Dict, Any
from openai import AsyncAzureOpenAI
from models import Quiz, QuizResponse, QuizResult

logger = logging.getLogger(__name__)

class EvaluationAgent:
    """Agent responsible for evaluating quiz responses."""
    
    def __init__(self):
        """Initialize evaluation agent."""
        self.client = AsyncAzureOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            api_version=os.getenv("MODEL_API_VERSION", "2024-02-01"),
            azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
            timeout=60.0
        )
    
    async def generate_adaptive_explanation(
        self,
        question: str,
        correct_answer: str,
        user_answer: str,
        user_age: int,
        concept: str
    ) -> str:
        """
        Generate personalized explanation for wrong answers using AI.
        
        Args:
            question: The quiz question
            correct_answer: The correct answer
            user_answer: What the user selected
            user_age: User's age
            concept: Financial concept
            
        Returns:
            Personalized explanation
        """
        try:
            explain_prompt = f"""Help a {user_age}-year-old understand why their answer was incorrect.

Question: {question}
Their answer: {user_answer}
Correct answer: {correct_answer}
Concept: {concept}

Provide a kind, encouraging explanation (max 3 sentences) that:
1. Explains the correct concept simply
2. Uses age-appropriate language
3. Ends with encouragement

Explanation:"""
            
            response = await self.client.chat.completions.create(
                model=os.getenv("MODEL_NAME", "gpt-4o"),
                messages=[
                    {"role": "system", "content": "You are a supportive teacher who helps children learn from mistakes."},
                    {"role": "user", "content": explain_prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return f"The correct answer is {correct_answer}. Let's review this concept together!"
    
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
