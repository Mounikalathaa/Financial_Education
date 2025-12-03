"""Content generation agent for creating personalized educational stories."""

import logging
import os
from typing import Dict, Any, Optional
from openai import AsyncAzureOpenAI
from models import EducationalStory, CaseBrief, DifficultyLevel
from config import config

logger = logging.getLogger(__name__)

class ContentGenerationAgent:
    """Agent responsible for generating personalized educational content."""
    
    def __init__(self, rag_service):
        """Initialize with RAG service and LLM client."""
        self.rag_service = rag_service
        self.client = AsyncAzureOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            api_version=os.getenv("MODEL_API_VERSION", "2024-02-01"),
            azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
            timeout=120.0  # Increase timeout to 120 seconds
        )
    
    async def generate_personalized_hint(
        self,
        question: str,
        user_context: Dict[str, Any],
        concept: str
    ) -> str:
        """
        Generate AI-powered personalized hints based on user's learning style.
        
        Args:
            question: The question user is struggling with
            user_context: User's profile and learning preferences
            concept: The financial concept being taught
            
        Returns:
            Personalized hint as a string
        """
        try:
            age = user_context.get("age", 10)
            hobbies = user_context.get("hobbies", [])
            
            hint_prompt = f"""You are a friendly detective mentor helping a {age}-year-old child understand {concept}.

Question they're struggling with: {question}

User's interests: {', '.join(hobbies) if hobbies else 'general learning'}

Provide a helpful hint that:
1. Doesn't give away the answer
2. Uses analogies related to their interests
3. Breaks down the concept into simpler parts
4. Encourages critical thinking
5. Is max 2-3 sentences

Hint:"""
            
            response = await self.client.chat.completions.create(
                model=os.getenv("MODEL_NAME", "gpt-4o"),
                messages=[
                    {"role": "system", "content": "You are an encouraging, patient teacher for children."},
                    {"role": "user", "content": hint_prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            hint = response.choices[0].message.content.strip()
            logger.info(f"Generated personalized hint for {concept}")
            return hint
            
        except Exception as e:
            logger.error(f"Error generating hint: {e}")
            return "Think about what you learned in the clues. What patterns do you notice?"
    
    async def generate_case_brief(
        self,
        concept: str,
        user_context: Dict[str, Any],
        difficulty: DifficultyLevel
    ) -> CaseBrief:
        """
        Generate an interactive case brief for detective-style learning.
        
        Args:
            concept: Financial concept to teach
            user_context: User personalization context
            difficulty: Target difficulty level
            
        Returns:
            CaseBrief object with mission, clues, and scenario
        """
        logger.info(f"Generating case brief for concept: {concept}, difficulty: {difficulty}")
        
        try:
            # Retrieve relevant educational content from RAG
            knowledge = await self.rag_service.retrieve_knowledge(
                concept=concept,
                difficulty=difficulty.value,
                age=user_context.get("age")
            )
            
            # Build case brief prompt
            prompt = self._build_case_brief_prompt(concept, user_context, difficulty, knowledge)
            
            # Generate case brief using LLM
            response = await self.client.chat.completions.create(
                model=os.getenv("MODEL_NAME", "gpt-4o"),
                messages=[
                    {
                        "role": "system",
                        "content": self._get_case_system_prompt(user_context["age"])
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=config.llm.temperature,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            
            # Parse the structured response
            case_brief = self._parse_case_brief(content, concept, user_context)
            
            logger.info(f"Case brief generated successfully: {case_brief.title}")
            
            # Image generation disabled - Azure OpenAI doesn't support DALL-E on standard endpoints
            # Future enhancement: Use OpenAI direct API or placeholder images
            logger.info("Image generation skipped (not available on Azure OpenAI standard endpoint)")
            
            return case_brief
            
        except Exception as e:
            logger.error(f"Error generating case brief: {str(e)}", exc_info=True)
            raise
    
    async def generate_personalized_hint(
        self,
        question: str,
        user_context: Dict[str, Any],
        concept: str
    ) -> str:
        """
        Generate AI-powered personalized hints based on user's learning style.
        
        Args:
            question: The question user is struggling with
            user_context: User's profile and learning preferences
            concept: The financial concept being taught
            
        Returns:
            Personalized hint as a string
        """
        try:
            age = user_context.get("age", 10)
            hobbies = user_context.get("hobbies", [])
            
            hint_prompt = f"""You are a friendly detective mentor helping a {age}-year-old child understand {concept}.

Question they're struggling with: {question}

User's interests: {', '.join(hobbies) if hobbies else 'general learning'}

Provide a helpful hint that:
1. Doesn't give away the answer directly
2. Uses simple analogies related to their interests
3. Breaks down the concept into simpler parts
4. Encourages critical thinking
5. Is max 2-3 sentences

Hint:"""
            
            response = await self.client.chat.completions.create(
                model=os.getenv("MODEL_NAME", "gpt-4o"),
                messages=[
                    {"role": "system", "content": "You are an encouraging, patient detective teacher for children."},
                    {"role": "user", "content": hint_prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            hint = response.choices[0].message.content.strip()
            logger.info(f"Generated personalized hint for {concept}")
            return hint
            
        except Exception as e:
            logger.error(f"Error generating hint: {e}")
            return "🔍 Think about what you learned in the clues. What patterns do you notice? Try breaking the problem into smaller parts!"
    
    async def generate_voice_script(
        self,
        text: str,
        context: str,
        user_age: int,
        personality: str = "detective",
        difficulty: str = "medium"
    ) -> str:
        """
        Generate AI-enhanced voice script with personality, emotion, and adaptive pacing.
        
        Args:
            text: The text to convert to voice script
            context: Context of the narration
            user_age: Age of the user
            personality: Voice personality (detective/teacher/friend/mentor)
            difficulty: Question difficulty for pacing
            
        Returns:
            Enhanced voice script with personality and emotion
        """
        try:
            # Define personality traits
            personalities = {
                "detective": {
                    "style": "mysterious, encouraging, uses detective metaphors",
                    "phrases": ["🔍 Interesting clue!", "Let's crack this case!", "Sharp detective work!"]
                },
                "teacher": {
                    "style": "patient, educational, breaks down concepts step-by-step",
                    "phrases": ["Great question!", "Let me explain this clearly", "You're learning so well!"]
                },
                "friend": {
                    "style": "casual, supportive, uses everyday examples",
                    "phrases": ["Hey buddy!", "You got this!", "That's awesome!"]
                },
                "mentor": {
                    "style": "wise, inspiring, encourages critical thinking",
                    "phrases": ["Think deeply about this", "You're capable of amazing things", "Trust your instincts"]
                }
            }
            
            persona = personalities.get(personality, personalities["detective"])
            
            # Adaptive pacing based on difficulty
            pacing_guide = {
                "easy": "quick, energetic, celebrate small wins",
                "medium": "steady, clear, encouraging",
                "hard": "slow, patient, break into tiny steps, very supportive"
            }
            
            pacing = pacing_guide.get(difficulty, pacing_guide["medium"])
            
            voice_prompt = f"""You are an AI voice script writer creating an extraordinary narration for a {user_age}-year-old.

🎭 PERSONALITY: {personality.upper()} - {persona['style']}
⚡ PACING: {pacing}
📝 ORIGINAL TEXT: {text}
🎯 CONTEXT: {context}

Your task:
1. Rewrite with the {personality} personality
2. Add emotional markers: [excited], [curious], [encouraging], [mysterious], [proud]
3. Insert natural pauses with ... or .
4. Use sound effect cues: *detective music*, *ding*, *celebration sounds*
5. Add personality catchphrases from: {', '.join(persona['phrases'])}
6. Make it feel like a conversation, not a lecture
7. For questions, build suspense before revealing options
8. For hints, sound like you're sharing a secret
9. For case briefs, narrate like an exciting story

✨ SPECIAL TOUCHES:
- Start with a hook that grabs attention
- Use the child's age-appropriate vocabulary
- Add a memorable ending phrase
- Make numbers and facts sound exciting

🎬 FORMAT EXAMPLE:
[excited] Hey there, super detective! *ding* Ready for something cool? ... Listen carefully. [mysterious] This case is unlike anything you've seen before ...

Now transform the text above into an amazing voice script. Only return the script, nothing else."""
            
            response = await self.client.chat.completions.create(
                model=os.getenv("MODEL_NAME", "gpt-4o"),
                messages=[
                    {
                        "role": "system", 
                        "content": f"You are a Tony Award-winning voice actor and children's audiobook narrator. Your specialty is bringing educational content to life with personality, emotion, and theatrical flair."
                    },
                    {"role": "user", "content": voice_prompt}
                ],
                temperature=0.85,  # Higher for more creativity
                max_tokens=400
            )
            
            enhanced_script = response.choices[0].message.content.strip()
            logger.info(f"Generated {personality} voice script with {difficulty} pacing")
            return enhanced_script
            
        except Exception as e:
            logger.error(f"Error generating voice script: {e}")
            return text
    
    async def analyze_emotion_for_voice(
        self,
        text: str,
        context: str
    ) -> Dict[str, Any]:
        """
        Analyze text to detect appropriate emotion, pacing, and pitch for voice.
        
        Returns:
            Dictionary with emotion, suggested_rate, suggested_pitch, sound_effects
        """
        try:
            analysis_prompt = f"""Analyze this educational content and determine the best voice settings:

Text: {text}
Context: {context}

Provide a JSON response with:
{{
  "emotion": "excited|curious|encouraging|mysterious|proud|neutral",
  "energy_level": "high|medium|low",
  "suggested_rate": 0.7-1.2,
  "suggested_pitch": 0.9-1.3,
  "sound_effects": ["effect1", "effect2"],
  "emotional_markers": ["word1", "word2"]
}}

Consider:
- Questions = curious, slightly mysterious
- Achievements = excited, proud
- Explanations = encouraging, patient
- Story openings = mysterious, engaging"""

            response = await self.client.chat.completions.create(
                model=os.getenv("MODEL_NAME", "gpt-4o"),
                messages=[
                    {"role": "system", "content": "You are an emotion analysis expert for voice synthesis."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Emotion analysis: {result['emotion']} with {result['energy_level']} energy")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing emotion: {e}")
            return {
                "emotion": "neutral",
                "energy_level": "medium",
                "suggested_rate": 0.9,
                "suggested_pitch": 1.0,
                "sound_effects": [],
                "emotional_markers": []
            }
    
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
    
    def _build_case_brief_prompt(
        self,
        concept: str,
        user_context: Dict[str, Any],
        difficulty: DifficultyLevel,
        knowledge: str
    ) -> str:
        """Build the case brief generation prompt."""
        age = user_context.get("age", 10)
        hobbies = user_context.get("hobbies", [])
        interests = user_context.get("interests", [])
        
        personalization = f"Age: {age}"
        if hobbies:
            personalization += f", Interests: {', '.join(hobbies[:2])}"
        
        # Add inclusivity requirements if provided
        inclusivity_section = ""
        if 'inclusivity_requirements' in user_context:
            inclusivity_section = f"\n\n**INCLUSIVITY REQUIREMENTS (MANDATORY):**\n{user_context['inclusivity_requirements']}"
            if 'bias_feedback' in user_context:
                inclusivity_section += f"\n\n**Apply these improvements:**\n" + "\n".join([f"- {rec}" for rec in user_context['bias_feedback']])
        
        return f"""Create an engaging detective-style case brief for a {age}-year-old to learn about "{concept}".

**Knowledge Base:**
{knowledge}

**Personalization:** {personalization}{inclusivity_section}

**Format (STRICTLY follow this structure):**
TITLE: [Creative case title with gender-neutral emoji, max 8 words]
MISSION: [1-2 exciting sentences about what detective needs to solve/learn]
CLUE1: [One key fact about the concept - use inclusive emoji]
CLUE2: [Second key fact - use inclusive emoji]
CLUE3: [Third key fact - use inclusive emoji]
CLUE4: [Fourth key fact - optional, use inclusive emoji]
SCENARIO: [2-3 sentences setting up a relatable situation where this concept matters]

**Requirements:**
- Make it fun and engaging for kids
- Use emojis to make it visually appealing (prefer gender-neutral emojis)
- Keep clues short (max 15 words each)
- Relate to child's interests when possible
- Be accurate based on knowledge base
- Difficulty: {difficulty.value}
- Use inclusive, diverse examples and scenarios
- Avoid stereotypes and assumptions about gender, culture, or economic status

Generate the case brief now:"""
    
    def _get_case_system_prompt(self, age: int) -> str:
        """Get system prompt for case brief generation."""
        return f"""You are a creative financial education expert who creates engaging detective-style 
learning experiences for {age}-year-olds. You make finance fun through mystery and discovery.

Your case briefs are:
- Short, punchy, and exciting
- Full of visual elements (emojis)
- Accurate and educational
- Age-appropriate and relatable
- Formatted EXACTLY as requested

Always use the exact format: TITLE:, MISSION:, CLUE1:, CLUE2:, CLUE3:, SCENARIO:"""
    
    def _parse_case_brief(self, content: str, concept: str, user_context: Dict[str, Any]) -> CaseBrief:
        """Parse LLM response into CaseBrief object."""
        lines = content.strip().split('\n')
        
        title = ""
        mission = ""
        clues = []
        scenario = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith("TITLE:"):
                title = line.replace("TITLE:", "").strip()
            elif line.startswith("MISSION:"):
                mission = line.replace("MISSION:", "").strip()
            elif line.startswith("CLUE"):
                clue_text = line.split(":", 1)[1].strip() if ":" in line else ""
                if clue_text:
                    clues.append(clue_text)
            elif line.startswith("SCENARIO:"):
                scenario = line.replace("SCENARIO:", "").strip()
        
        # Fallbacks if parsing fails
        if not title:
            title = f"🔍 The Case of {concept.title()}"
        if not mission:
            mission = f"Your mission: Learn about {concept} and solve the mystery!"
        if not clues:
            clues = ["📚 Learn the basics", "🔍 Investigate the details", "✅ Solve the case"]
        if not scenario:
            scenario = f"A mystery involving {concept} needs your detective skills!"
        
        return CaseBrief(
            case_id=f"case_{concept}_{user_context.get('user_id', 'default')}",
            title=title,
            mission=mission,
            clues=clues[:5],  # Limit to 5 clues max
            scenario=scenario,
            concept=concept,
            personalization_elements=self._extract_personalization_elements(user_context)
        )
