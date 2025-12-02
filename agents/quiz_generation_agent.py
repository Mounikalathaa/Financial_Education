"""Quiz generation agent for creating questions based on educational content."""

import logging
import json
import os
from typing import List, Dict, Any
from openai import AsyncAzureOpenAI
from models import QuizQuestion, EducationalStory, DifficultyLevel
from config import config

logger = logging.getLogger(__name__)

class QuizGenerationAgent:
    """Agent responsible for generating quiz questions."""
    
    def __init__(self, rag_service):
        """Initialize with RAG service and LLM client."""
        self.rag_service = rag_service
        self.client = AsyncAzureOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            api_version=os.getenv("MODEL_API_VERSION", "2024-02-01"),
            azure_endpoint=os.getenv("OPENAI_ENDPOINT")
        )
    
    async def generate_questions(
        self,
        concept: str,
        story: EducationalStory,
        difficulty: DifficultyLevel,
        user_context: Dict[str, Any]
    ) -> List[QuizQuestion]:
        """
        Generate quiz questions based on the story and concept.
        
        Args:
            concept: Financial concept
            story: Generated educational story
            difficulty: Difficulty level
            user_context: User context for personalization
            
        Returns:
            List of QuizQuestion objects
        """
        logger.info(f"Generating questions for concept: {concept}")
        
        try:
            # Determine number of questions based on age/difficulty
            num_questions = self._get_question_count(
                user_context.get("age", 10), 
                difficulty
            )
            
            # Retrieve knowledge for question generation
            knowledge = await self.rag_service.retrieve_knowledge(
                concept=concept,
                difficulty=difficulty.value,
                age=user_context.get("age")
            )
            
            # Build question generation prompt
            prompt = self._build_question_prompt(
                concept, story, difficulty, num_questions, knowledge
            )
            
            # Generate questions using LLM
            response = await self.client.chat.completions.create(
                model=os.getenv("MODEL_NAME", "gpt-4o"),
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            questions_data = json.loads(response.choices[0].message.content)
            
            # Convert to QuizQuestion objects
            questions = []
            for idx, q_data in enumerate(questions_data.get("questions", [])):
                question = QuizQuestion(
                    question_id=f"q_{story.story_id}_{idx+1}",
                    question_text=q_data["question"],
                    options=q_data["options"],
                    correct_answer=q_data["correct_answer"],
                    explanation=q_data["explanation"],
                    difficulty=difficulty
                )
                questions.append(question)
            
            logger.info(f"Generated {len(questions)} questions successfully")
            return questions
            
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}", exc_info=True)
            raise
    
    def _build_question_prompt(
        self,
        concept: str,
        story: EducationalStory,
        difficulty: DifficultyLevel,
        num_questions: int,
        knowledge: str
    ) -> str:
        """Build the question generation prompt."""
        prompt = f"""Generate {num_questions} multiple-choice quiz questions based on the following educational story and knowledge base.

**Story:**
{story.title}
{story.content}

**Knowledge Base:**
{knowledge}

**Requirements:**
- Generate exactly {num_questions} questions
- Difficulty: {difficulty.value}
- Each question should have 4 options (A, B, C, D)
- Questions should test understanding of the "{concept}" concept
- Include both story-based and concept-based questions
- Ensure accuracy based on the knowledge base
- Age-appropriate language
- Provide clear explanations for correct answers

**Output Format (JSON):**
{{
  "questions": [
    {{
      "question": "Question text here?",
      "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
      "correct_answer": "A) Option 1",
      "explanation": "Explanation of why this is correct"
    }}
  ]
}}

Generate the questions now:"""
        
        return prompt
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for question generation."""
        return """You are an expert quiz designer for financial education. You create engaging,
accurate, and educational quiz questions that test understanding while being age-appropriate.

Your questions:
- Test real understanding, not just memorization
- Have one clear correct answer
- Include plausible distractors
- Are based strictly on provided knowledge
- Are free from bias
- Include helpful explanations

Always output valid JSON matching the specified format."""
    
    def _get_question_count(self, age: int, difficulty: DifficultyLevel) -> int:
        """Determine appropriate number of questions."""
        if age < 10:
            return 3
        elif age < 13:
            return 4
        else:
            return 5
