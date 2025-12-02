"""Content generation agent for creating personalized educational stories."""

import logging
import os
from typing import Dict, Any
from openai import AsyncAzureOpenAI
from models import EducationalStory, DifficultyLevel
from config import config

logger = logging.getLogger(__name__)

class ContentGenerationAgent:
    """Agent responsible for generating personalized educational stories."""
    
    def __init__(self, rag_service):
        """Initialize with RAG service and LLM client."""
        self.rag_service = rag_service
        self.client = AsyncAzureOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            api_version=os.getenv("MODEL_API_VERSION", "2024-02-01"),
            azure_endpoint=os.getenv("OPENAI_ENDPOINT")
        )
    
    async def generate_story(
        self,
        concept: str,
        user_context: Dict[str, Any],
        difficulty: DifficultyLevel
    ) -> EducationalStory:
        """
        Generate a personalized educational story.
        
        Args:
            concept: Financial concept to teach
            user_context: User personalization context
            difficulty: Target difficulty level
            
        Returns:
            EducationalStory object with personalized content
        """
        logger.info(f"Generating story for concept: {concept}, difficulty: {difficulty}")
        
        try:
            # Retrieve relevant educational content from RAG
            knowledge = await self.rag_service.retrieve_knowledge(
                concept=concept,
                difficulty=difficulty.value,
                age=user_context.get("age")
            )
            
            # Build personalization prompt
            prompt = self._build_story_prompt(concept, user_context, difficulty, knowledge)
            
            # Generate story using LLM
            response = await self.client.chat.completions.create(
                model=os.getenv("MODEL_NAME", "gpt-4o"),
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(user_context["age"])
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=config.llm.temperature,
                max_tokens=config.llm.max_tokens
            )
            
            story_content = response.choices[0].message.content
            
            # Extract title (first line) and content
            lines = story_content.strip().split('\n', 1)
            title = lines[0].replace('Title:', '').replace('#', '').strip()
            content = lines[1].strip() if len(lines) > 1 else story_content
            
            story = EducationalStory(
                story_id=f"story_{concept}_{user_context.get('user_profile').user_id if user_context.get('user_profile') else 'default'}",
                title=title,
                content=content,
                concept=concept,
                personalization_elements=self._extract_personalization_elements(user_context)
            )
            
            logger.info(f"Story generated successfully: {story.title}")
            return story
            
        except Exception as e:
            logger.error(f"Error generating story: {str(e)}", exc_info=True)
            raise
    
    def _build_story_prompt(
        self,
        concept: str,
        user_context: Dict[str, Any],
        difficulty: DifficultyLevel,
        knowledge: str
    ) -> str:
        """Build the story generation prompt."""
        age = user_context.get("age", 10)
        hobbies = user_context.get("hobbies", [])
        interests = user_context.get("interests", [])
        spending_patterns = user_context.get("spending_patterns", {})
        
        personalization_hints = []
        if hobbies:
            personalization_hints.append(f"The child enjoys: {', '.join(hobbies)}")
        if interests:
            personalization_hints.append(f"They are interested in: {', '.join(interests)}")
        if spending_patterns.get("top_category"):
            personalization_hints.append(
                f"They often spend money on: {spending_patterns['top_category']}"
            )
        
        prompt = f"""Create an engaging educational story that teaches the financial concept of "{concept}" to a {age}-year-old child.

**Knowledge Base Context:**
{knowledge}

**Personalization Details:**
{chr(10).join(personalization_hints) if personalization_hints else "No specific personalization available"}

**Requirements:**
- Difficulty Level: {difficulty.value}
- Age-appropriate language and scenarios for {age}-year-old
- Include relatable characters and situations
- Make it engaging and fun
- Incorporate the child's interests where possible
- Story should be 200-400 words
- Ensure financial accuracy based on the knowledge base
- Avoid any gender, age, or socioeconomic bias

**Format:**
Title: [Creative title]
[Story content]

Generate the story now:"""
        
        return prompt
    
    def _get_system_prompt(self, age: int) -> str:
        """Get the system prompt for story generation."""
        age_group = config.get_age_group(age)
        
        return f"""You are an expert financial educator specialized in creating engaging, 
age-appropriate educational content for children. You excel at making complex financial 
concepts simple and relatable through storytelling.

Your stories are:
- Educational and accurate
- Engaging and fun
- Age-appropriate for {age_group['name'] if age_group else 'children'}
- Personalized to the child's interests
- Free from bias or stereotypes
- Based strictly on provided knowledge (no hallucinations)

Always maintain a positive, encouraging tone that makes learning about money fun and accessible."""
    
    def _extract_personalization_elements(self, user_context: Dict[str, Any]) -> list:
        """Extract personalization elements used in the story."""
        elements = []
        
        if user_context.get("hobbies"):
            elements.extend(user_context["hobbies"])
        if user_context.get("interests"):
            elements.extend(user_context["interests"])
        if user_context.get("spending_patterns", {}).get("top_category"):
            elements.append(user_context["spending_patterns"]["top_category"])
        
        return elements[:5]  # Limit to top 5 elements
