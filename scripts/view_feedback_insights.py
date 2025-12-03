"""Script to view aggregated feedback insights and bias analysis."""

import sys
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from models import QuizFeedback, BiasAnalysis
from utils.feedback_processor import FeedbackProcessor
from datetime import datetime

def display_feedback_insights():
    """Display aggregated feedback insights."""

    feedback_file = Path(__file__).parent.parent / "data" / "feedback.json"

    if not feedback_file.exists():
        print("📭 No feedback data available yet.")
        return

    # Load feedback data
    with open(feedback_file, 'r') as f:
        feedback_data = json.load(f)

    if not feedback_data:
        print("📭 No feedback entries found.")
        return

    print("=" * 80)
    print("📊 FEEDBACK INSIGHTS DASHBOARD")
    print("=" * 80)
    print()

    # Overall statistics
    total_feedbacks = len(feedback_data)
    ratings = [f.get('rating', 0) for f in feedback_data]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0

    print(f"📈 Overall Statistics:")
    print(f"   Total Feedbacks: {total_feedbacks}")
    print(f"   Average Rating: {avg_rating:.2f}/5.0")
    print()

    # Rating distribution
    rating_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for r in ratings:
        if r in rating_dist:
            rating_dist[r] += 1

    print(f"⭐ Rating Distribution:")
    for rating, count in sorted(rating_dist.items(), reverse=True):
        bar = "█" * count
        print(f"   {rating} stars: {bar} ({count})")
    print()

    # Bias analysis
    bias_detected_count = 0
    bias_by_severity = {"low": 0, "medium": 0, "high": 0}
    bias_types_count = {}

    for f in feedback_data:
        bias = f.get('bias_analysis')
        if bias and bias.get('has_bias'):
            bias_detected_count += 1
            severity = bias.get('severity', 'low')
            if severity in bias_by_severity:
                bias_by_severity[severity] += 1

            for bias_type in bias.get('bias_types', []):
                bias_types_count[bias_type] = bias_types_count.get(bias_type, 0) + 1

    print(f"⚠️  Bias Detection:")
    print(f"   Bias Detected: {bias_detected_count}/{total_feedbacks} ({(bias_detected_count/total_feedbacks)*100:.1f}%)")

    if bias_detected_count > 0:
        print(f"   By Severity:")
        for severity, count in bias_by_severity.items():
            if count > 0:
                print(f"      {severity.capitalize()}: {count}")

        if bias_types_count:
            print(f"   By Type:")
            for bias_type, count in sorted(bias_types_count.items(), key=lambda x: x[1], reverse=True):
                print(f"      {bias_type}: {count}")
    print()

    # Difficulty perception
    difficulty_perception = {"too_easy": 0, "just_right": 0, "too_hard": 0}
    for f in feedback_data:
        perception = f.get('difficulty_perception')
        if perception in difficulty_perception:
            difficulty_perception[perception] += 1

    print(f"📊 Difficulty Perception:")
    for perception, count in difficulty_perception.items():
        if count > 0:
            percentage = (count / total_feedbacks) * 100
            bar = "█" * int(percentage / 5)
            print(f"   {perception.replace('_', ' ').title()}: {bar} {count} ({percentage:.1f}%)")
    print()

    # Concepts feedback
    concepts_ratings = {}
    for f in feedback_data:
        concept = f.get('concept', 'unknown')
        rating = f.get('rating', 0)
        if concept not in concepts_ratings:
            concepts_ratings[concept] = []
        concepts_ratings[concept].append(rating)

    print(f"📚 Feedback by Concept:")
    for concept, ratings in sorted(concepts_ratings.items()):
        avg = sum(ratings) / len(ratings)
        status = "✅" if avg >= 4.0 else "⚠️" if avg >= 3.0 else "❌"
        print(f"   {status} {concept}: {avg:.2f}/5.0 ({len(ratings)} responses)")
    print()

    # Recent feedback with comments
    recent_with_comments = [
        f for f in feedback_data
        if f.get('comments') and f.get('created_at')
    ]
    recent_with_comments.sort(key=lambda x: x.get('created_at', ''), reverse=True)

    if recent_with_comments:
        print(f"💬 Recent Feedback Comments (Top 5):")
        for i, f in enumerate(recent_with_comments[:5], 1):
            rating = f.get('rating', 0)
            comment = f.get('comments', '')
            concept = f.get('concept', 'unknown')
            timestamp = f.get('created_at', '')

            print(f"   {i}. [{concept}] ⭐{rating}/5")
            print(f"      \"{comment[:100]}{'...' if len(comment) > 100 else ''}\"")
            print(f"      Time: {timestamp}")

            # Show bias if detected
            bias = f.get('bias_analysis')
            if bias and bias.get('has_bias'):
                print(f"      ⚠️ Bias detected: {', '.join(bias.get('bias_types', []))}")
            print()

    print("=" * 80)
    print(f"✨ Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

if __name__ == "__main__":
    display_feedback_insights()

