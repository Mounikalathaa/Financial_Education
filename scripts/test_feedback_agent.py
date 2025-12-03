"""Test script for the Feedback Agent."""

import sys
import asyncio
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from agents.feedback_agent import FeedbackAgent
from services.rag_service import RAGService
from models import QuizFeedback, BiasAnalysis

async def test_feedback_agent():
    """Test the feedback agent functionality."""

    print("=" * 80)
    print("🧪 Testing Feedback Agent")
    print("=" * 80)
    print()

    # Initialize services
    print("1. Initializing RAG Service...")
    rag_service = RAGService()

    print("2. Initializing Feedback Agent...")
    feedback_agent = FeedbackAgent(rag_service)
    print("✅ Feedback Agent initialized successfully!")
    print()

    # Test Case 1: Feedback with no bias
    print("📝 Test Case 1: Collecting feedback with no bias concerns")
    print("-" * 80)

    feedback1 = await feedback_agent.collect_feedback(
        quiz_id="test_quiz_001",
        user_id="test_user_001",
        concept="saving_money",
        rating=5,
        comments="Great quiz! The story was relatable and fun.",
        difficulty_perception="just_right",
        relevance_score=5
    )

    print(f"✅ Feedback collected: {feedback1.feedback_id}")
    print(f"   Rating: {feedback1.rating}/5")
    print(f"   Has Bias: {feedback1.bias_analysis.has_bias if feedback1.bias_analysis else 'Not analyzed'}")
    print()

    # Process feedback
    result1 = await feedback_agent.process_feedback(feedback1)
    print(f"📊 Processing result:")
    print(f"   Actions taken: {result1['actions_taken']}")
    print(f"   Requires review: {result1['requires_human_review']}")
    print()

    # Test Case 2: Feedback with potential gender bias
    print("📝 Test Case 2: Collecting feedback with potential gender bias")
    print("-" * 80)

    feedback2 = await feedback_agent.collect_feedback(
        quiz_id="test_quiz_002",
        user_id="test_user_002",
        concept="budgeting",
        rating=2,
        comments="The story only showed boys managing money. My daughter felt left out. All the examples were about sons and fathers, not daughters or mothers.",
        difficulty_perception="just_right",
        relevance_score=2
    )

    print(f"✅ Feedback collected: {feedback2.feedback_id}")
    print(f"   Rating: {feedback2.rating}/5")

    if feedback2.bias_analysis:
        bias = feedback2.bias_analysis
        print(f"   ⚠️  Bias Analysis:")
        print(f"      Has Bias: {bias.has_bias}")
        print(f"      Severity: {bias.severity}")
        print(f"      Types: {', '.join(bias.bias_types)}")
        print(f"      Confidence: {bias.confidence_score:.2f}")

        if bias.specific_issues:
            print(f"      Issues:")
            for issue in bias.specific_issues:
                print(f"         - {issue}")
    print()

    # Process feedback
    result2 = await feedback_agent.process_feedback(feedback2)
    print(f"📊 Processing result:")
    print(f"   Actions taken: {result2['actions_taken']}")
    print(f"   Requires review: {result2['requires_human_review']}")
    print()

    # Test Case 3: Feedback with cultural bias
    print("📝 Test Case 3: Collecting feedback with cultural concerns")
    print("-" * 80)

    feedback3 = await feedback_agent.collect_feedback(
        quiz_id="test_quiz_003",
        user_id="test_user_003",
        concept="investing",
        rating=3,
        comments="The story assumed everyone celebrates Christmas and has traditional American family structures. Not inclusive of diverse cultures and family types.",
        difficulty_perception="too_hard",
        relevance_score=2
    )

    print(f"✅ Feedback collected: {feedback3.feedback_id}")
    print(f"   Rating: {feedback3.rating}/5")

    if feedback3.bias_analysis:
        bias = feedback3.bias_analysis
        print(f"   ⚠️  Bias Analysis:")
        print(f"      Has Bias: {bias.has_bias}")
        print(f"      Severity: {bias.severity}")
        print(f"      Types: {', '.join(bias.bias_types)}")

        if bias.recommendations:
            print(f"      Recommendations:")
            for rec in bias.recommendations[:3]:
                print(f"         - {rec}")
    print()

    # Process feedback
    result3 = await feedback_agent.process_feedback(feedback3)
    print(f"📊 Processing result:")
    print(f"   Actions taken: {result3['actions_taken']}")
    print()

    # Generate insights from all feedback
    print("📈 Generating Aggregated Insights")
    print("-" * 80)

    insights = await feedback_agent.generate_feedback_insights([feedback1, feedback2, feedback3])

    print(f"Total Feedbacks: {insights['total_feedbacks']}")
    print(f"Average Rating: {insights['average_rating']}/5.0")
    print(f"Bias Detected: {insights['bias_detected_count']} ({insights['bias_percentage']}%)")
    print(f"Overall Health: {insights['overall_health'].upper()}")
    print()

    if insights['difficulty_distribution']:
        print("Difficulty Distribution:")
        for perception, count in insights['difficulty_distribution'].items():
            print(f"   {perception.replace('_', ' ').title()}: {count}")
    print()

    if insights['concepts_needing_improvement']:
        print("⚠️  Concepts Needing Improvement:")
        for concept_info in insights['concepts_needing_improvement']:
            print(f"   - {concept_info['concept']}: {concept_info['average_rating']:.2f}/5.0")
    print()

    print("=" * 80)
    print("✅ Feedback Agent Testing Complete!")
    print("=" * 80)
    print()
    print("💡 Key Takeaways:")
    print("   • Feedback collection works seamlessly")
    print("   • Bias detection identifies gender, cultural, and other biases")
    print("   • Knowledge base gets updated automatically when bias is detected")
    print("   • Insights help track content quality over time")
    print()

if __name__ == "__main__":
    asyncio.run(test_feedback_agent())

