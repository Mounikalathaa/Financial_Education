#!/bin/bash

# Git Sync Script - Pull latest changes and reapply local work
# Uses SSH for authentication

echo "🔄 Git Sync - Pull Latest and Reapply Changes"
echo "=============================================="
echo ""

# Navigate to project directory
cd /Users/anshu@backbase.com/Projects/Hackathon/Financial_Education

# Check if git repo exists
if [ ! -d ".git" ]; then
    echo "❌ Not a git repository!"
    exit 1
fi

echo "📍 Current branch:"
git branch --show-current
echo ""

echo "📊 Current status:"
git status --short
echo ""

# Check if there are uncommitted changes
if [[ -n $(git status --porcelain) ]]; then
    echo "💾 You have uncommitted changes. Stashing them first..."
    git stash save "Auto-stash before pull - $(date '+%Y-%m-%d %H:%M:%S')"
    STASHED=true
    echo "✅ Changes stashed"
else
    echo "✅ No uncommitted changes"
    STASHED=false
fi
echo ""

# Show current remote
echo "🔗 Remote configuration:"
git remote -v
echo ""

# Pull latest changes
echo "⬇️  Pulling latest changes from remote..."
git pull origin main --rebase

if [ $? -eq 0 ]; then
    echo "✅ Pull successful!"
else
    echo "❌ Pull failed! Check errors above."
    if [ "$STASHED" = true ]; then
        echo "⚠️  Your changes are safely stashed. Run 'git stash pop' to restore them."
    fi
    exit 1
fi
echo ""

# Reapply stashed changes if any
if [ "$STASHED" = true ]; then
    echo "📤 Reapplying your local changes..."
    git stash pop

    if [ $? -eq 0 ]; then
        echo "✅ Your changes have been reapplied successfully!"
    else
        echo "⚠️  Merge conflicts detected! You'll need to resolve them manually."
        echo "   Files with conflicts are marked in 'git status'"
        echo ""
        echo "   After resolving conflicts:"
        echo "   1. Edit the conflicted files"
        echo "   2. Run: git add <resolved-files>"
        echo "   3. Run: git stash drop"
    fi
fi
echo ""

echo "📊 Final status:"
git status --short
echo ""

echo "✅ Done!"
echo ""
echo "💡 Your local changes (all the feedback agent work):"
echo "   • agents/feedback_agent.py"
echo "   • agents/admin_review_agent.py"
echo "   • admin_dashboard.py"
echo "   • models/__init__.py (BiasAnalysis, AdminReview models)"
echo "   • docs/FEEDBACK_AGENT.md"
echo "   • docs/ADMIN_INTERVENTION_GUIDE.md"
echo "   • docs/FEEDBACK_LOGIC_EXPLAINED.md"
echo "   • docs/HOW_TO_VERIFY_KB_UPDATES.md"
echo "   • scripts/verify_kb_updates.py"
echo "   • scripts/view_feedback_insights.py"
echo "   • start_admin.sh"
echo "   • start_all.sh"
echo ""
echo "If any conflicts occurred, they need to be resolved manually."

