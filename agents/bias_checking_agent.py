"""Bias checking agent for validating generated content for fairness and inclusivity."""

import logging
from typing import Dict, Any, List
from openai import AsyncAzureOpenAI
import os

logger = logging.getLogger(__name__)

class BiasCheckingAgent:
    """Agent responsible for detecting and mitigating bias in generated content."""
    
    def __init__(self):
        """Initialize the bias checking agent with Azure OpenAI."""
        self.client = AsyncAzureOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            api_version=os.getenv("MODEL_API_VERSION", "2024-02-01"),
            azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
            timeout=120.0  # Increase timeout to 120 seconds
        )
        self.deployment_name = os.getenv("MODEL_NAME", "gpt-4")
    
    async def check_content_bias(
        self,
        content: Dict[str, Any],
        content_type: str,
        user_age: int
    ) -> Dict[str, Any]:
        """
        Check generated content for bias and provide recommendations.
        
        Args:
            content: The generated content (story, questions, options)
            content_type: Type of content ('story', 'quiz', 'hint', 'explanation')
            user_age: Age of the target user
            
        Returns:
            Dictionary with bias analysis and recommendations
        """
        logger.info(f"Checking bias for {content_type} content, target age: {user_age}")
        
        try:
            # Prepare content for analysis
            content_text = self._extract_text_from_content(content, content_type)
            
            # Create bias checking prompt
            prompt = self._create_bias_checking_prompt(content_text, content_type, user_age)
            
            # Call Azure OpenAI for bias analysis
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert bias detection and inclusivity consultant specializing in educational content for children. 
Your role is to identify potential biases related to gender, race, ethnicity, socioeconomic status, ability, religion, and other factors.
You also check for age-appropriateness, cultural sensitivity, and inclusive language.
Provide constructive feedback and specific recommendations for improvement."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            analysis_text = response.choices[0].message.content
            
            # Log raw response for debugging
            logger.info(f"[Bias Check] Raw AI response:\n{analysis_text[:500]}...")
            
            # Parse the analysis
            bias_result = self._parse_bias_analysis(analysis_text)
            
            logger.info(f"Bias check complete. Score: {bias_result['bias_score']}/10, Issues: {len(bias_result['issues_found'])}, Acceptable: {bias_result['is_acceptable']}")
            return bias_result
            
        except Exception as e:
            logger.error(f"Error in bias checking: {str(e)}", exc_info=True)
            return {
                "bias_score": 5,
                "is_acceptable": True,
                "issues_found": [],
                "recommendations": [],
                "analysis": "Bias check unavailable",
                "error": str(e)
            }
    
    def _extract_text_from_content(self, content: Dict[str, Any], content_type: str) -> str:
        """Extract text from different content types."""
        if content_type == 'story':
            # For story/case brief content
            if 'title' in content:
                text = f"Title: {content.get('title', '')}\n"
                text += f"Mission: {content.get('mission', '')}\n"
                text += f"Scenario: {content.get('scenario', '')}\n"
                if 'clues' in content:
                    text += f"Clues: {', '.join(content.get('clues', []))}\n"
                return text
            else:
                return f"{content.get('content', str(content))}"
        
        elif content_type == 'quiz':
            text = ""
            # Include case brief if provided
            if 'case_brief' in content:
                cb = content['case_brief']
                text += f"Case Brief Scenario: {cb.get('scenario', '')}\n\n"
            
            # Extract questions - handle both 'question' and 'question_text' keys
            for q in content.get('questions', []):
                question_text = q.get('question', q.get('question_text', ''))
                text += f"Question: {question_text}\n"
                options = q.get('options', [])
                if options:
                    text += f"Options: {', '.join(options)}\n"
                explanation = q.get('explanation', '')
                if explanation:
                    text += f"Explanation: {explanation}\n"
                text += "\n"
            return text
        
        elif content_type == 'hint':
            return content.get('hint', str(content))
        
        elif content_type == 'explanation':
            return content.get('explanation', str(content))
        
        else:
            return str(content)
    
    def _create_bias_checking_prompt(self, content_text: str, content_type: str, user_age: int) -> str:
        """Create a comprehensive bias checking prompt."""
        return f"""Analyze the following educational content for potential biases and inclusivity issues.

**Content Type:** {content_type}
**Target Age:** {user_age} years old

**Content to Analyze:**
{content_text}

**Please evaluate the content on the following dimensions:**

1. **Gender Bias**: Are all genders represented fairly? Are there stereotypical assumptions?
2. **Cultural & Ethnic Sensitivity**: Is the content culturally inclusive? Any stereotypes or assumptions?
3. **Socioeconomic Bias**: Does it assume a particular economic background? Is it accessible to all?
4. **Ability & Accessibility**: Is language inclusive of people with different abilities?
5. **Age Appropriateness**: Is the content suitable for a {user_age}-year-old? Too complex or too simple?
6. **Name Diversity**: Are names used diverse and culturally representative?
7. **Example Scenarios**: Do scenarios represent diverse family structures, communities, and contexts?
8. **Language Inclusivity**: Is the language neutral and inclusive?

**Provide your analysis in this format:**

BIAS_SCORE: [0-10, where 10 is completely unbiased and inclusive]
IS_ACCEPTABLE: [YES/NO - whether content meets inclusivity standards]

ISSUES_FOUND:
- [List specific issues, if any]

RECOMMENDATIONS:
- [Specific suggestions for improvement, if needed]

OVERALL_ASSESSMENT: [Brief summary]"""
    
    def _parse_bias_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Parse the AI's bias analysis into structured format."""
        result = {
            "bias_score": 7,  # Default moderate score
            "is_acceptable": True,
            "issues_found": [],
            "recommendations": [],
            "analysis": analysis_text
        }
        
        try:
            lines = analysis_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('BIAS_SCORE:'):
                    try:
                        score = int(line.split(':')[1].strip().split()[0])
                        result['bias_score'] = max(0, min(10, score))
                    except:
                        pass
                
                elif line.startswith('IS_ACCEPTABLE:'):
                    acceptable = line.split(':')[1].strip().upper()
                    result['is_acceptable'] = acceptable.startswith('YES')
                
                elif line.startswith('ISSUES_FOUND:'):
                    current_section = 'issues'
                
                elif line.startswith('RECOMMENDATIONS:'):
                    current_section = 'recommendations'
                
                elif line.startswith('OVERALL_ASSESSMENT:'):
                    current_section = 'assessment'
                
                elif current_section:
                    # Handle both "-" and numbered list formats (e.g., "1.", "2.", etc.)
                    if line.startswith('-') or (len(line) > 2 and line[0].isdigit() and line[1] == '.'):
                        # Remove the prefix (- or 1. 2. etc.)
                        if line.startswith('-'):
                            item = line[1:].strip()
                        else:
                            # Remove number and dot
                            item = line.split('.', 1)[1].strip() if '.' in line else line
                        
                        if item:
                            if current_section == 'issues':
                                result['issues_found'].append(item)
                            elif current_section == 'recommendations':
                                result['recommendations'].append(item)
            
        except Exception as e:
            logger.error(f"Error parsing bias analysis: {str(e)}", exc_info=True)
        
        return result
    
    async def suggest_improvements(
        self,
        content: Dict[str, Any],
        bias_analysis: Dict[str, Any],
        content_type: str
    ) -> Dict[str, Any]:
        """
        Generate improved version of content based on bias analysis.
        
        Args:
            content: Original content
            bias_analysis: Results from bias check
            content_type: Type of content
            
        Returns:
            Improved content suggestions
        """
        if bias_analysis['bias_score'] >= 8:
            logger.info("Content already highly inclusive, no improvements needed")
            return content
        
        try:
            content_text = self._extract_text_from_content(content, content_type)
            
            prompt = f"""The following content has been flagged for potential bias issues.

**Original Content:**
{content_text}

**Issues Identified:**
{chr(10).join(f"- {issue}" for issue in bias_analysis['issues_found'])}

**Recommendations:**
{chr(10).join(f"- {rec}" for rec in bias_analysis['recommendations'])}

**Please rewrite the content to address these issues while maintaining educational value and engagement.**
Ensure the improved version is:
1. Culturally inclusive and diverse
2. Free from gender stereotypes
3. Accessible to all socioeconomic backgrounds
4. Age-appropriate
5. Uses diverse names and scenarios

**Provide the improved version:**"""
            
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in creating inclusive, unbiased educational content."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            improved_text = response.choices[0].message.content
            
            return {
                "improved_content": improved_text,
                "original_bias_score": bias_analysis['bias_score'],
                "improvements_made": bias_analysis['recommendations']
            }
            
        except Exception as e:
            logger.error(f"Error generating improvements: {str(e)}")
            return content
    
    def get_bias_report(self, bias_analysis: Dict[str, Any]) -> str:
        """Generate a human-readable bias report."""
        score = bias_analysis['bias_score']
        status = "✅ EXCELLENT" if score >= 9 else "✓ GOOD" if score >= 7 else "⚠️ NEEDS REVIEW" if score >= 5 else "❌ REQUIRES REVISION"
        
        report = f"""
{'='*60}
BIAS & INCLUSIVITY ANALYSIS REPORT
{'='*60}

Overall Score: {score}/10 - {status}
Acceptable: {'YES' if bias_analysis['is_acceptable'] else 'NO'}

"""
        
        if bias_analysis['issues_found']:
            report += "Issues Found:\n"
            for issue in bias_analysis['issues_found']:
                report += f"  ⚠️ {issue}\n"
            report += "\n"
        
        if bias_analysis['recommendations']:
            report += "Recommendations:\n"
            for rec in bias_analysis['recommendations']:
                report += f"  💡 {rec}\n"
            report += "\n"
        
        report += f"{'='*60}\n"
        
        return report
