#!/usr/bin/env python3
"""
Script to verify if knowledge base was updated after admin reviews.
Checks vector store modification times against admin review timestamps.
"""

import json
from pathlib import Path
from datetime import datetime
import os

def check_kb_updates():
    print("=" * 80)
    print("KNOWLEDGE BASE UPDATE VERIFICATION")
    print("=" * 80)
    print()

    # Check vector store files
    vector_store_path = Path("data/vector_store")
    index_file = vector_store_path / "education.index"
    metadata_file = vector_store_path / "metadata.pkl"

    print("📁 Vector Store Files:")
    print("-" * 80)

    if index_file.exists():
        index_mtime = os.path.getmtime(index_file)
        index_time = datetime.fromtimestamp(index_mtime)
        index_size = index_file.stat().st_size
        print(f"✅ education.index:")
        print(f"   Last Modified: {index_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Size: {index_size:,} bytes")
    else:
        print("❌ education.index: NOT FOUND")
        return

    if metadata_file.exists():
        meta_mtime = os.path.getmtime(metadata_file)
        meta_time = datetime.fromtimestamp(meta_mtime)
        meta_size = metadata_file.stat().st_size
        print(f"✅ metadata.pkl:")
        print(f"   Last Modified: {meta_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Size: {meta_size:,} bytes")
    else:
        print("❌ metadata.pkl: NOT FOUND")
        return

    print()
    print("=" * 80)

    # Load admin review history
    history_file = Path("data/admin_review_history.json")

    if not history_file.exists():
        print("❌ Admin review history not found")
        return

    with open(history_file, 'r') as f:
        history = json.load(f)

    # Find reviews that should have updated KB
    kb_updates = []
    for review in history:
        actions = review.get('actions_taken', [])
        if 'knowledge_base_updated_by_admin' in actions or 'forced_content_update' in actions:
            reviewed_at = review.get('reviewed_at')
            if reviewed_at:
                review_time = datetime.fromisoformat(reviewed_at)
                kb_updates.append({
                    'review_id': review.get('review_id'),
                    'time': review_time,
                    'concept': review.get('feedback', {}).get('concept'),
                    'decision': review.get('admin_decision'),
                    'bias_types': review.get('admin_review', {}).get('bias_override', {}).get('bias_types', []),
                    'actions': actions
                })

    print(f"📊 Admin Reviews with KB Updates: {len(kb_updates)}")
    print("-" * 80)

    if not kb_updates:
        print("⚠️  No KB update reviews found")
        return

    # Show recent KB updates
    kb_updates.sort(key=lambda x: x['time'], reverse=True)

    print("\n📝 Recent KB Updates (last 5):")
    print("-" * 80)
    for i, update in enumerate(kb_updates[:5], 1):
        print(f"\n{i}. Review ID: {update['review_id']}")
        print(f"   Time: {update['time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Concept: {update['concept']}")
        print(f"   Decision: {update['decision']}")
        print(f"   Bias Types: {', '.join(update['bias_types']) if update['bias_types'] else 'None specified'}")
        print(f"   Actions: {', '.join(update['actions'])}")

        # Check if KB files were modified after this review
        if update['time'] < index_time:
            print(f"   ✅ KB files modified AFTER this review")
        else:
            print(f"   ⚠️  KB files NOT modified after this review")

    print()
    print("=" * 80)

    # Compare most recent update with file modification
    most_recent_update = kb_updates[0]
    time_diff = (index_time - most_recent_update['time']).total_seconds()

    print("\n🔍 Analysis:")
    print("-" * 80)
    print(f"Most Recent Admin KB Update: {most_recent_update['time'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Vector Store Last Modified:  {index_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Time Difference: {abs(time_diff):.0f} seconds")
    print()

    if time_diff > 0 and time_diff < 300:  # Within 5 minutes
        print("✅ VERIFIED: Knowledge base was updated after the admin review!")
        print(f"   Update happened {time_diff:.0f} seconds after the review.")
    elif time_diff > 0:
        print("⚠️  WARNING: KB files are newer than review, but by more than 5 minutes.")
        print("   This could be from a different update.")
    else:
        print("❌ FAILED: Knowledge base files are OLDER than the admin review!")
        print(f"   KB is {abs(time_diff):.0f} seconds older than the review.")
        print("   The update may have failed silently.")

    print()
    print("=" * 80)

    # Show what to check
    print("\n💡 How to verify KB updates manually:")
    print("-" * 80)
    print("1. Check file timestamps:")
    print("   ls -lh data/vector_store/")
    print()
    print("2. Check file sizes (should grow after updates):")
    print(f"   Current size: {index_size:,} bytes")
    print()
    print("3. Run a quiz and see if content is different:")
    print("   The updated concepts should have more diverse content")
    print()
    print("4. Check review history for actions:")
    print("   Look for 'knowledge_base_updated_by_admin' in actions_taken")
    print()
    print("=" * 80)

if __name__ == "__main__":
    try:
        check_kb_updates()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

