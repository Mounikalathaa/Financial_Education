"""Feedback Agent for collecting, analyzing, and processing user feedback."""

import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from openai import AzureOpenAI
from config import config
from models import QuizFeedback, BiasAnalysis

logger = logging.getLogger(__name__)

class FeedbackAgent:
    """
    Agent responsible for:
    1. Collecting user feedback after quiz completion
    2. Analyzing feedback for potential bias
    3. Identifying areas for knowledge base improvement
    4. Updating knowledge base based on feedback
    """

    def __init__(self, rag_service):
        """Initialize the feedback agent."""
        self.rag_service = rag_service
        self.openai_client = AzureOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            api_version=os.getenv("MODEL_API_VERSION", "2024-02-01"),
            azure_endpoint=os.getenv("OPENAI_ENDPOINT")
        )
        logger.info("Feedback Agent initialized with Azure OpenAI")

    async def collect_feedback(
        self,
        quiz_id: str,
        user_id: str,
        concept: str,
        rating: int,
        comments: Optional[str] = None,
        difficulty_perception: Optional[str] = None,
        relevance_score: Optional[int] = None
    ) -> QuizFeedback:
        """
        Collect structured feedback from the user.

        Args:
            quiz_id: Quiz identifier
            user_id: User identifier
            concept: Financial concept covered
            rating: Overall rating (1-5)
            comments: Optional text feedback
            difficulty_perception: "too_easy", "just_right", "too_hard"
            relevance_score: How relevant was the story (1-5)

        Returns:
            QuizFeedback object
        """
        logger.info(f"Collecting feedback for quiz {quiz_id} from user {user_id}")

        feedback = QuizFeedback(
            feedback_id=f"feedback_{quiz_id}_{datetime.now().timestamp()}",
            quiz_id=quiz_id,
            user_id=user_id,
            concept=concept,
            rating=rating,
            comments=comments,
            difficulty_perception=difficulty_perception,
            relevance_score=relevance_score,
            created_at=datetime.now()
        )

        # Analyze feedback for bias
        if comments:
            bias_analysis = await self.analyze_bias(
                feedback_text=comments,
                concept=concept,
                user_id=user_id
            )
            feedback.bias_analysis = bias_analysis

        logger.info(f"Feedback collected: rating={rating}, has_comments={bool(comments)}")
        return feedback

    async def analyze_bias(
        self,
        feedback_text: str,
        concept: str,
        user_id: str
    ) -> BiasAnalysis:
        """
        Analyze feedback for potential biases in the content.

        Checks for:
        - Gender bias
        - Cultural bias
        - Age appropriateness issues
        - Stereotypes
        - Accessibility concerns

        Args:
            feedback_text: User's text feedback
            concept: Financial concept
            user_id: User identifier

        Returns:
            BiasAnalysis object with findings
        """
        logger.info(f"Analyzing feedback for bias: {concept}")

        prompt = f"""You are an expert in educational content bias detection. Analyze the following user feedback about a financial education quiz for children.

Concept: {concept}
User Feedback: {feedback_text}

Analyze for the following types of bias:
1. Gender bias - Does the content stereotype or exclude any gender?
2. Cultural bias - Is the content culturally insensitive or exclusive?
3. Age appropriateness - Is the content suitable for the age group?
4. Stereotypes - Does the content perpetuate harmful stereotypes?
5. Accessibility - Are there concerns about content accessibility?
6. Economic bias - Does it assume certain economic backgrounds?

Provide your analysis in JSON format:
{{
    "has_bias": true/false,
    "bias_types": ["gender", "cultural", etc.],
    "severity": "low/medium/high",
    "specific_issues": ["detailed description of each issue"],
    "recommendations": ["specific suggestions to fix the bias"],
    "confidence_score": 0.0-1.0
}}"""

        try:
            model_name = os.getenv("MODEL_NAME", "gpt-4o")
            logger.info(f"Calling Azure OpenAI API for bias analysis with model: {model_name}")
            response = self.openai_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are an educational content bias expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            import json
            response_content = response.choices[0].message.content
            logger.info(f"Received response from OpenAI: {response_content[:200]}...")

            analysis_data = json.loads(response_content)

            bias_analysis = BiasAnalysis(
                has_bias=analysis_data.get("has_bias", False),
                bias_types=analysis_data.get("bias_types", []),
                severity=analysis_data.get("severity", "low"),
                specific_issues=analysis_data.get("specific_issues", []),
                recommendations=analysis_data.get("recommendations", []),
                confidence_score=analysis_data.get("confidence_score", 0.5),
                analyzed_at=datetime.now()
            )

            logger.info(f"Bias analysis complete: has_bias={bias_analysis.has_bias}, severity={bias_analysis.severity}, confidence={bias_analysis.confidence_score}")
            return bias_analysis

        except Exception as e:
            logger.error(f"Error analyzing bias: {type(e).__name__}: {str(e)}", exc_info=True)
            # Return a result that indicates AI failed but still triggers human review
            return BiasAnalysis(
                has_bias=False,
                bias_types=[],
                severity="low",
                specific_issues=[f"AI analysis failed: {str(e)}"],
                recommendations=["Manual review recommended"],
                confidence_score=0.0,
                analyzed_at=datetime.now()
            )

    async def process_feedback(
        self,
        feedback: QuizFeedback,
        admin_review_agent=None
    ) -> Dict[str, Any]:
        """
        Process feedback and determine actions.

        Args:
            feedback: QuizFeedback object
            admin_review_agent: Optional AdminReviewAgent for queueing reviews

        Returns:
            Dictionary with processing results and actions taken
        """
        logger.info(f"Processing feedback {feedback.feedback_id}")

        actions_taken = []
        requires_admin_review = False
        review_priority = None
        review_reason = None

        # Check for low ratings or negative feedback
        if feedback.rating <= 2:
            actions_taken.append("flagged_for_review")
            requires_admin_review = True
            review_priority = "high"
            review_reason = f"Low rating detected: {feedback.rating}/5"
            logger.warning(f"Low rating detected: {feedback.rating}")

        # Check for bias
        if feedback.bias_analysis and feedback.bias_analysis.has_bias:
            severity = feedback.bias_analysis.severity

            if severity in ["high", "medium"]:
                actions_taken.append("urgent_bias_review")
                logger.warning(f"Bias detected with {severity} severity")

                # Update knowledge base to address bias
                await self.update_knowledge_base_for_bias(
                    concept=feedback.concept,
                    bias_analysis=feedback.bias_analysis
                )
                actions_taken.append("knowledge_base_updated")

                # Add to admin review queue for verification
                requires_admin_review = True
                review_priority = "urgent" if severity == "high" else "high"
                review_reason = f"AI detected {severity} severity bias: {', '.join(feedback.bias_analysis.bias_types)}"

        # Check for low AI confidence (potential missed bias)
        if feedback.bias_analysis and not feedback.bias_analysis.has_bias:
            if feedback.bias_analysis.confidence_score < 0.6:
                requires_admin_review = True
                review_priority = "medium"
                review_reason = f"Low AI confidence ({feedback.bias_analysis.confidence_score:.2%}) - potential missed bias"
                actions_taken.append("low_confidence_flagged")

        # Check difficulty perception mismatch
        if feedback.difficulty_perception in ["too_easy", "too_hard"]:
            actions_taken.append("difficulty_adjustment_needed")
            logger.info(f"Difficulty mismatch: {feedback.difficulty_perception}")

        # Check relevance
        if feedback.relevance_score and feedback.relevance_score <= 2:
            actions_taken.append("personalization_improvement_needed")
            logger.info(f"Low relevance score: {feedback.relevance_score}")

        # Check for concerning keywords in comments
        if feedback.comments:
            concerning_keywords = ["biased", "offensive", "inappropriate", "stereotype",
                                 "racist", "sexist", "discriminat", "exclusive", "unfair"]
            if any(keyword in feedback.comments.lower() for keyword in concerning_keywords):
                requires_admin_review = True
                review_priority = "urgent" if not review_priority else review_priority
                review_reason = "User feedback contains concerning keywords"
                actions_taken.append("concerning_keywords_detected")

        # Add to admin review queue if needed
        if requires_admin_review and admin_review_agent:
            review_id = admin_review_agent.add_to_review_queue(
                feedback=feedback,
                reason=review_reason or "Requires admin review",
                priority=review_priority or "medium"
            )
            actions_taken.append("added_to_admin_queue")
            logger.info(f"Added to admin review queue: {review_id}")

        return {
            "feedback_id": feedback.feedback_id,
            "actions_taken": actions_taken,
            "requires_human_review": requires_admin_review,
            "review_priority": review_priority,
            "review_reason": review_reason,
            "timestamp": datetime.now().isoformat()
        }

    async def update_knowledge_base_for_bias(
        self,
        concept: str,
        bias_analysis: BiasAnalysis
    ):
        """
        Update knowledge base with inclusive, unbiased content.

        Args:
            concept: Financial concept to update
            bias_analysis: Analysis of detected bias
        """
        logger.info(f"Updating knowledge base for concept: {concept}")

        prompt = f"""You are an expert in creating inclusive, unbiased educational content for children.

A bias has been detected in educational content about: {concept}

Bias Details:
- Types: {', '.join(bias_analysis.bias_types)}
- Severity: {bias_analysis.severity}
- Issues: {', '.join(bias_analysis.specific_issues)}
- Recommendations: {', '.join(bias_analysis.recommendations)}

Create improved, bias-free educational content about {concept} that:
1. Is inclusive of all genders, cultures, and backgrounds
2. Avoids stereotypes
3. Uses diverse examples and characters
4. Is accessible to all learners
5. Maintains age-appropriate language

Provide content for three difficulty levels:
- Beginner (ages 6-9)
- Intermediate (ages 10-12)
- Advanced (ages 13-17)

Format each section clearly with the difficulty level as a header."""

        try:
            model_name = os.getenv("MODEL_NAME", "gpt-4o")
            response = self.openai_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are an expert in inclusive education."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            improved_content = response.choices[0].message.content

            # Add the improved content to the knowledge base
            await self.rag_service.add_documents(
                documents=[improved_content],
                metadata=[{
                    "concept": concept,
                    "bias_corrected": True,
                    "bias_types_addressed": bias_analysis.bias_types,
                    "updated_at": datetime.now().isoformat()
                }]
            )

            logger.info(f"Knowledge base updated with bias-free content for {concept}")

        except Exception as e:
            logger.error(f"Error updating knowledge base: {str(e)}")

    async def generate_feedback_insights(
        self,
        feedbacks: List[QuizFeedback]
    ) -> Dict[str, Any]:
        """
        Generate insights from multiple feedback entries.

        Args:
            feedbacks: List of QuizFeedback objects

        Returns:
            Dictionary with aggregated insights
        """
        if not feedbacks:
            return {"message": "No feedback available"}

        total_feedbacks = len(feedbacks)
        avg_rating = sum(f.rating for f in feedbacks) / total_feedbacks

        bias_count = sum(1 for f in feedbacks if f.bias_analysis and f.bias_analysis.has_bias)

        difficulty_feedback = {
            "too_easy": sum(1 for f in feedbacks if f.difficulty_perception == "too_easy"),
            "just_right": sum(1 for f in feedbacks if f.difficulty_perception == "just_right"),
            "too_hard": sum(1 for f in feedbacks if f.difficulty_perception == "too_hard")
        }

        concepts_needing_improvement = []
        concept_ratings = {}

        for f in feedbacks:
            if f.concept not in concept_ratings:
                concept_ratings[f.concept] = []
            concept_ratings[f.concept].append(f.rating)

        for concept, ratings in concept_ratings.items():
            avg = sum(ratings) / len(ratings)
            if avg < 3.5:
                concepts_needing_improvement.append({
                    "concept": concept,
                    "average_rating": avg,
                    "feedback_count": len(ratings)
                })

        return {
            "total_feedbacks": total_feedbacks,
            "average_rating": round(avg_rating, 2),
            "bias_detected_count": bias_count,
            "bias_percentage": round((bias_count / total_feedbacks) * 100, 1),
            "difficulty_distribution": difficulty_feedback,
            "concepts_needing_improvement": concepts_needing_improvement,
            "overall_health": "good" if avg_rating >= 4.0 and bias_count == 0 else "needs_attention"
        }

