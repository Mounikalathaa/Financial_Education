"""Admin Review Agent for human oversight of feedback and bias detection."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from pathlib import Path

from models import QuizFeedback, BiasAnalysis, AdminReview, ReviewAction

logger = logging.getLogger(__name__)

class AdminReviewAgent:
    """
    Agent responsible for:
    1. Managing admin review queue
    2. Processing admin interventions
    3. Overriding AI bias detection
    4. Manual bias flagging and content updates
    5. Tracking admin actions and decisions
    """

    def __init__(self, rag_service, feedback_agent):
        """Initialize the admin review agent."""
        self.rag_service = rag_service
        self.feedback_agent = feedback_agent
        self.review_queue_file = Path("./data/admin_review_queue.json")
        self.review_history_file = Path("./data/admin_review_history.json")
        self.review_queue_file.parent.mkdir(parents=True, exist_ok=True)
        logger.info("Admin Review Agent initialized")

    def add_to_review_queue(
        self,
        feedback: QuizFeedback,
        reason: str,
        priority: str = "medium"
    ) -> str:
        """
        Add feedback to admin review queue.

        Args:
            feedback: QuizFeedback object
            reason: Why it needs review
            priority: "low", "medium", "high", "urgent"

        Returns:
            Review ID
        """
        logger.info(f"Adding feedback {feedback.feedback_id} to review queue")

        review_item = {
            "review_id": f"review_{datetime.now().timestamp()}",
            "feedback": feedback.model_dump(mode='json'),
            "reason": reason,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "reviewed_at": None,
            "reviewed_by": None,
            "admin_decision": None
        }

        # Load existing queue
        queue = self._load_review_queue()
        queue.append(review_item)

        # Sort by priority (urgent > high > medium > low)
        priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
        queue.sort(key=lambda x: priority_order.get(x["priority"], 2))

        # Save queue
        self._save_review_queue(queue)

        logger.info(f"Review item added: {review_item['review_id']} (Priority: {priority})")
        return review_item['review_id']

    def get_review_queue(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get items from review queue with optional filters.

        Args:
            status: Filter by status (pending/reviewed/dismissed)
            priority: Filter by priority

        Returns:
            List of review items
        """
        queue = self._load_review_queue()

        # Apply filters
        if status:
            queue = [item for item in queue if item["status"] == status]
        if priority:
            queue = [item for item in queue if item["priority"] == priority]

        return queue

    async def process_admin_review(
        self,
        review_id: str,
        admin_id: str,
        decision: str,
        admin_notes: Optional[str] = None,
        bias_override: Optional[Dict[str, Any]] = None,
        force_update: bool = False
    ) -> AdminReview:
        """
        Process admin review decision.

        Args:
            review_id: Review identifier
            admin_id: Admin who reviewed
            decision: "approve", "reject", "flag_bias", "update_content", "dismiss"
            admin_notes: Optional admin comments
            bias_override: Manual bias detection override
            force_update: Force knowledge base update

        Returns:
            AdminReview object
        """
        logger.info(f"Processing admin review: {review_id} by {admin_id}")

        # Find review item in queue
        queue = self._load_review_queue()
        review_item = next((item for item in queue if item["review_id"] == review_id), None)

        if not review_item:
            raise ValueError(f"Review item {review_id} not found")

        # Create admin review record
        admin_review = AdminReview(
            review_id=review_id,
            feedback_id=review_item["feedback"]["feedback_id"],
            admin_id=admin_id,
            decision=ReviewAction(decision),
            admin_notes=admin_notes,
            bias_override=bias_override,
            reviewed_at=datetime.now()
        )

        # Process based on decision
        actions_taken = []

        if decision == "approve":
            # AI decision was correct, no action needed
            actions_taken.append("ai_decision_approved")
            logger.info("Admin approved AI decision")

        elif decision == "reject":
            # AI was wrong, revert any changes
            actions_taken.append("ai_decision_rejected")
            logger.warning("Admin rejected AI decision")

        elif decision == "flag_bias":
            # Admin manually flagged bias that AI missed
            if bias_override:
                logger.warning("Admin flagged bias that AI missed!")
                actions_taken.append("manual_bias_flagged")

                # Create new BiasAnalysis from admin override
                manual_bias = BiasAnalysis(
                    has_bias=True,
                    bias_types=bias_override.get("bias_types", []),
                    severity=bias_override.get("severity", "medium"),
                    specific_issues=bias_override.get("specific_issues", []),
                    recommendations=bias_override.get("recommendations", []),
                    confidence_score=1.0,  # Admin confidence is 100%
                    analyzed_at=datetime.now()
                )

                # Update feedback with manual bias analysis
                feedback_data = QuizFeedback(**review_item["feedback"])
                feedback_data.bias_analysis = manual_bias

                # Update knowledge base with error handling
                try:
                    logger.info(f"Attempting to update KB for concept: {feedback_data.concept}")
                    await self.feedback_agent.update_knowledge_base_for_bias(
                        concept=feedback_data.concept,
                        bias_analysis=manual_bias
                    )
                    actions_taken.append("knowledge_base_updated_by_admin")
                    logger.info("✅ Knowledge base successfully updated")
                except Exception as e:
                    logger.error(f"❌ Failed to update knowledge base: {str(e)}")
                    actions_taken.append("knowledge_base_update_failed")
                    # Re-raise to let admin know it failed
                    raise Exception(f"Failed to update knowledge base: {str(e)}")

        elif decision == "update_content":
            # Admin wants to force content update
            if force_update:
                logger.info("Admin forcing content update")
                feedback_data = QuizFeedback(**review_item["feedback"])

                # Use existing bias analysis or create from override
                bias_analysis = feedback_data.bias_analysis
                if bias_override:
                    bias_analysis = BiasAnalysis(
                        has_bias=True,
                        bias_types=bias_override.get("bias_types", []),
                        severity=bias_override.get("severity", "high"),
                        specific_issues=bias_override.get("specific_issues", []),
                        recommendations=bias_override.get("recommendations", []),
                        confidence_score=1.0,
                        analyzed_at=datetime.now()
                    )

                try:
                    logger.info(f"Forcing KB update for concept: {feedback_data.concept}")
                    await self.feedback_agent.update_knowledge_base_for_bias(
                        concept=feedback_data.concept,
                        bias_analysis=bias_analysis
                    )
                    actions_taken.append("forced_content_update")
                    logger.info("✅ Forced update successful")
                except Exception as e:
                    logger.error(f"❌ Forced update failed: {str(e)}")
                    actions_taken.append("forced_update_failed")
                    raise Exception(f"Failed to force update knowledge base: {str(e)}")

        elif decision == "dismiss":
            # False alarm, no action needed
            actions_taken.append("review_dismissed")
            logger.info("Admin dismissed review")

        # Update review item status
        review_item["status"] = "reviewed"
        review_item["reviewed_at"] = datetime.now().isoformat()
        review_item["reviewed_by"] = admin_id
        review_item["admin_decision"] = decision
        review_item["actions_taken"] = actions_taken

        # Save updated queue
        self._save_review_queue(queue)

        # Add to review history
        self._add_to_history(review_item, admin_review)

        admin_review.actions_taken = actions_taken
        logger.info(f"Admin review complete: {actions_taken}")

        return admin_review

    def get_statistics(self) -> Dict[str, Any]:
        """Get admin review statistics."""
        queue = self._load_review_queue()
        history = self._load_review_history()

        total_reviews = len(queue)
        pending_reviews = len([item for item in queue if item["status"] == "pending"])
        reviewed = len([item for item in queue if item["status"] == "reviewed"])

        # Priority breakdown
        priority_breakdown = {
            "urgent": len([item for item in queue if item["priority"] == "urgent" and item["status"] == "pending"]),
            "high": len([item for item in queue if item["priority"] == "high" and item["status"] == "pending"]),
            "medium": len([item for item in queue if item["priority"] == "medium" and item["status"] == "pending"]),
            "low": len([item for item in queue if item["priority"] == "low" and item["status"] == "pending"])
        }

        # Decision breakdown
        decisions = [item.get("admin_decision") for item in queue if item.get("admin_decision")]
        decision_breakdown = {
            "approve": decisions.count("approve"),
            "reject": decisions.count("reject"),
            "flag_bias": decisions.count("flag_bias"),
            "update_content": decisions.count("update_content"),
            "dismiss": decisions.count("dismiss")
        }

        # Manual bias flagged by admins
        manual_bias_flags = len([
            item for item in queue
            if item.get("admin_decision") == "flag_bias"
        ])

        # AI accuracy (approved / total reviewed)
        ai_accuracy = (decision_breakdown["approve"] / reviewed * 100) if reviewed > 0 else 0

        return {
            "total_reviews": total_reviews,
            "pending_reviews": pending_reviews,
            "reviewed": reviewed,
            "priority_breakdown": priority_breakdown,
            "decision_breakdown": decision_breakdown,
            "manual_bias_flags": manual_bias_flags,
            "ai_accuracy_percentage": round(ai_accuracy, 2),
            "total_history_records": len(history)
        }

    def flag_bias_manually(
        self,
        quiz_id: str,
        user_id: str,
        concept: str,
        admin_id: str,
        bias_types: List[str],
        severity: str,
        specific_issues: List[str],
        recommendations: List[str],
        admin_notes: Optional[str] = None
    ) -> str:
        """
        Allow admin to manually flag bias without waiting for user feedback.

        Args:
            quiz_id: Quiz with biased content
            user_id: User who took quiz
            concept: Financial concept
            admin_id: Admin flagging the bias
            bias_types: Types of bias detected
            severity: Bias severity
            specific_issues: Detailed issues
            recommendations: How to fix
            admin_notes: Admin comments

        Returns:
            Review ID
        """
        logger.warning(f"Admin {admin_id} manually flagging bias in quiz {quiz_id}")

        # Create manual bias analysis
        manual_bias = BiasAnalysis(
            has_bias=True,
            bias_types=bias_types,
            severity=severity,
            specific_issues=specific_issues,
            recommendations=recommendations,
            confidence_score=1.0,  # Admin confidence
            analyzed_at=datetime.now()
        )

        # Create synthetic feedback for tracking
        manual_feedback = QuizFeedback(
            feedback_id=f"manual_{datetime.now().timestamp()}",
            quiz_id=quiz_id,
            user_id=user_id,
            concept=concept,
            rating=1,  # Low rating for biased content
            comments=f"Manual bias flag by admin: {admin_notes or 'No notes'}",
            difficulty_perception="just_right",
            relevance_score=1,
            bias_analysis=manual_bias,
            created_at=datetime.now(),
            processed=True
        )

        # Add to review queue with urgent priority
        review_id = self.add_to_review_queue(
            feedback=manual_feedback,
            reason=f"Manual bias flag by admin {admin_id}",
            priority="urgent"
        )

        # Automatically process as "flag_bias"
        # This will update the knowledge base immediately

        return review_id

    def _load_review_queue(self) -> List[Dict[str, Any]]:
        """Load review queue from file."""
        if self.review_queue_file.exists():
            with open(self.review_queue_file, 'r') as f:
                return json.load(f)
        return []

    def _save_review_queue(self, queue: List[Dict[str, Any]]):
        """Save review queue to file."""
        with open(self.review_queue_file, 'w') as f:
            json.dump(queue, f, indent=2)

    def _load_review_history(self) -> List[Dict[str, Any]]:
        """Load review history from file."""
        if self.review_history_file.exists():
            with open(self.review_history_file, 'r') as f:
                return json.load(f)
        return []

    def _add_to_history(self, review_item: Dict[str, Any], admin_review: AdminReview):
        """Add completed review to history."""
        history = self._load_review_history()

        history_entry = {
            **review_item,
            "admin_review": admin_review.model_dump(mode='json')
        }

        history.append(history_entry)

        with open(self.review_history_file, 'w') as f:
            json.dump(history, f, indent=2)

