"""Admin dashboard for reviewing feedback and managing bias detection."""

import streamlit as st
import asyncio
from datetime import datetime
from typing import Optional
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from models import QuizFeedback, BiasAnalysis, AdminReview, ReviewAction
from agents.admin_review_agent import AdminReviewAgent
from agents.orchestrator import OrchestratorAgent
from services.mcp_client import MCPClient
from services.rag_service import RAGService
from config import config

# Page configuration
st.set_page_config(
    page_title="🛡️ Admin Review Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .review-card {
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        margin: 10px 0;
        background: white;
    }
    .urgent { border-color: #ff4444; background: #fff5f5; }
    .high { border-color: #ff9800; background: #fff8f0; }
    .medium { border-color: #2196f3; background: #f0f8ff; }
    .low { border-color: #4caf50; background: #f0fff0; }

    .stat-card {
        padding: 15px;
        border-radius: 8px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
    }
    .bias-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 15px;
        margin: 5px;
        font-size: 12px;
        font-weight: bold;
    }
    .gender { background: #e91e63; color: white; }
    .cultural { background: #9c27b0; color: white; }
    .economic { background: #ff5722; color: white; }
    .stereotype { background: #795548; color: white; }
    .accessibility { background: #607d8b; color: white; }
</style>
""", unsafe_allow_html=True)

# Helper function for async operations
def run_async(coro):
    """Run async function in sync context."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# Initialize services
@st.cache_resource
def init_services():
    """Initialize all services."""
    mcp_client = MCPClient(base_url=config.mcp.base_url)
    rag_service = RAGService()
    orchestrator = OrchestratorAgent(mcp_client, rag_service)
    admin_agent = AdminReviewAgent(rag_service, orchestrator.feedback_agent)
    return admin_agent, orchestrator

admin_agent, orchestrator = init_services()

# Admin authentication (simplified)
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False
    st.session_state.admin_id = None

def login_page():
    """Simple admin login."""
    st.title("🛡️ Admin Login")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Enter Admin Credentials")
        admin_id = st.text_input("Admin ID", placeholder="admin@example.com")
        password = st.text_input("Password", type="password")

        if st.button("Login", type="primary"):
            # Simple authentication (in production, use proper auth)
            if admin_id and password == "admin123":  # Change this!
                st.session_state.admin_logged_in = True
                st.session_state.admin_id = admin_id
                st.rerun()
            else:
                st.error("Invalid credentials")

def main_dashboard():
    """Main admin dashboard."""

    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🛡️ Admin Review Dashboard")
        st.markdown(f"**Logged in as:** {st.session_state.admin_id}")
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.admin_logged_in = False
            st.session_state.admin_id = None
            st.rerun()

    st.markdown("---")

    # Statistics
    stats = admin_agent.get_statistics()

    st.markdown("### 📊 Overview Statistics")
    cols = st.columns(5)

    with cols[0]:
        st.markdown(f"""
        <div class="stat-card">
            <h2>{stats['pending_reviews']}</h2>
            <p>Pending Reviews</p>
        </div>
        """, unsafe_allow_html=True)

    with cols[1]:
        st.markdown(f"""
        <div class="stat-card">
            <h2>{stats['manual_bias_flags']}</h2>
            <p>Manual Flags</p>
        </div>
        """, unsafe_allow_html=True)

    with cols[2]:
        st.markdown(f"""
        <div class="stat-card">
            <h2>{stats['ai_accuracy_percentage']}%</h2>
            <p>AI Accuracy</p>
        </div>
        """, unsafe_allow_html=True)

    with cols[3]:
        st.markdown(f"""
        <div class="stat-card">
            <h2>{stats['reviewed']}</h2>
            <p>Reviewed</p>
        </div>
        """, unsafe_allow_html=True)

    with cols[4]:
        st.markdown(f"""
        <div class="stat-card">
            <h2>{stats['total_reviews']}</h2>
            <p>Total Items</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 Review Queue",
        "🚩 Manual Bias Flag",
        "📈 Statistics",
        "📜 Review History"
    ])

    with tab1:
        review_queue_tab()

    with tab2:
        manual_flag_tab()

    with tab3:
        statistics_tab(stats)

    with tab4:
        review_history_tab()

def review_queue_tab():
    """Review queue interface."""
    st.markdown("### 🔍 Pending Reviews")

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        priority_filter = st.selectbox(
            "Filter by Priority",
            ["All", "urgent", "high", "medium", "low"]
        )
    with col2:
        sort_by = st.selectbox(
            "Sort by",
            ["Priority", "Date (Newest)", "Date (Oldest)"]
        )

    # Get queue
    queue = admin_agent.get_review_queue(status="pending")

    if priority_filter != "All":
        queue = [item for item in queue if item["priority"] == priority_filter]

    if not queue:
        st.info("✅ No pending reviews! All caught up.")
        return

    st.markdown(f"**{len(queue)} items** need review")
    st.markdown("---")

    # Display each review item
    for item in queue:
        priority = item["priority"]
        feedback = QuizFeedback(**item["feedback"])

        with st.container():
            st.markdown(f"""
            <div class="review-card {priority}">
                <h4>🔔 Priority: {priority.upper()}</h4>
                <p><strong>Review ID:</strong> {item['review_id']}</p>
                <p><strong>Reason:</strong> {item['reason']}</p>
                <p><strong>Created:</strong> {item['created_at']}</p>
            </div>
            """, unsafe_allow_html=True)

            # Feedback details
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Feedback Details:**")
                st.write(f"- **Concept:** {feedback.concept}")
                st.write(f"- **Rating:** {'⭐' * feedback.rating} ({feedback.rating}/5)")
                st.write(f"- **Difficulty:** {feedback.difficulty_perception}")
                st.write(f"- **Relevance:** {feedback.relevance_score}/5")

                if feedback.comments:
                    st.markdown("**User Comments:**")
                    st.info(feedback.comments)

            with col2:
                st.markdown("**AI Bias Analysis:**")
                if feedback.bias_analysis:
                    bias = feedback.bias_analysis

                    if bias.has_bias:
                        st.warning(f"⚠️ Bias Detected: {bias.severity.upper()}")

                        st.markdown("**Bias Types:**")
                        for bias_type in bias.bias_types:
                            st.markdown(f'<span class="bias-badge {bias_type}">{bias_type}</span>', unsafe_allow_html=True)

                        with st.expander("View Details"):
                            st.markdown("**Issues:**")
                            for issue in bias.specific_issues:
                                st.write(f"- {issue}")

                            st.markdown("**Recommendations:**")
                            for rec in bias.recommendations:
                                st.write(f"✓ {rec}")

                            st.write(f"**AI Confidence:** {bias.confidence_score:.2%}")
                    else:
                        st.success("✅ No bias detected by AI")
                else:
                    st.info("No bias analysis available")

            # Admin action form
            st.markdown("### 🎯 Admin Action")

            with st.form(key=f"review_form_{item['review_id']}"):
                col1, col2 = st.columns(2)

                with col1:
                    decision = st.selectbox(
                        "Decision",
                        ["approve", "reject", "flag_bias", "update_content", "dismiss"],
                        format_func=lambda x: {
                            "approve": "✅ Approve (AI correct)",
                            "reject": "❌ Reject (AI wrong)",
                            "flag_bias": "🚩 Flag Bias (AI missed)",
                            "update_content": "✨ Update Content",
                            "dismiss": "👋 Dismiss"
                        }[x],
                        key=f"decision_{item['review_id']}"
                    )

                with col2:
                    force_update = st.checkbox("Force Knowledge Base Update", key=f"force_{item['review_id']}")

                admin_notes = st.text_area(
                    "Admin Notes",
                    placeholder="Optional notes about your decision...",
                    key=f"notes_{item['review_id']}"
                )

                # Bias override section - ALWAYS show for flag_bias and update_content
                bias_override = None
                bias_types = []
                severity = "medium"
                specific_issues = ""
                recommendations = ""

                if decision in ["flag_bias", "update_content"]:
                    st.markdown("---")
                    st.markdown("### ⚠️ REQUIRED: Manual Bias Details")
                    st.warning("Please fill in all fields below to update the knowledge base properly!")

                    col1, col2 = st.columns(2)
                    with col1:
                        bias_types = st.multiselect(
                            "Bias Types (Required)",
                            ["gender", "cultural", "economic", "stereotype", "accessibility", "age_appropriateness"],
                            help="Select at least one bias type",
                            key=f"bias_types_{item['review_id']}"
                        )
                        severity = st.select_slider(
                            "Severity",
                            ["low", "medium", "high"],
                            value="medium",
                            key=f"severity_{item['review_id']}"
                        )

                    with col2:
                        specific_issues = st.text_area(
                            "Specific Issues (Required - one per line)",
                            placeholder="Example:\nContent assumes middle-class background\nOnly shows one type of family structure\nLacks diverse representation",
                            height=100,
                            key=f"issues_{item['review_id']}"
                        )
                        recommendations = st.text_area(
                            "Recommendations (Required - one per line)",
                            placeholder="Example:\nInclude examples from various income levels\nShow diverse family types\nUse inclusive language",
                            height=100,
                            key=f"recs_{item['review_id']}"
                        )

                    # Build bias override
                    issues_list = [i.strip() for i in specific_issues.split('\n') if i.strip()]
                    recs_list = [r.strip() for r in recommendations.split('\n') if r.strip()]

                    bias_override = {
                        "bias_types": bias_types,
                        "severity": severity,
                        "specific_issues": issues_list,
                        "recommendations": recs_list
                    }

                st.markdown("---")

                # Submit button with validation
                submitted = st.form_submit_button("Submit Review", type="primary")

                if submitted:
                    # Validation
                    if decision in ["flag_bias", "update_content"]:
                        if not bias_types:
                            st.error("❌ Please select at least one bias type!")
                        elif not specific_issues.strip():
                            st.error("❌ Please describe the specific issues!")
                        elif not recommendations.strip():
                            st.error("❌ Please provide recommendations!")
                        else:
                            # All validations passed
                            with st.spinner("Processing admin review..."):
                                admin_review = run_async(
                                    admin_agent.process_admin_review(
                                        review_id=item['review_id'],
                                        admin_id=st.session_state.admin_id,
                                        decision=decision,
                                        admin_notes=admin_notes,
                                        bias_override=bias_override,
                                        force_update=force_update
                                    )
                                )

                                st.success(f"✅ Review processed! Actions: {', '.join(admin_review.actions_taken)}")
                                st.balloons()
                                st.rerun()
                    else:
                        # No validation needed for other decisions
                        with st.spinner("Processing admin review..."):
                            admin_review = run_async(
                                admin_agent.process_admin_review(
                                    review_id=item['review_id'],
                                    admin_id=st.session_state.admin_id,
                                    decision=decision,
                                    admin_notes=admin_notes,
                                    bias_override=bias_override,
                                    force_update=force_update
                                )
                            )

                            st.success(f"✅ Review processed! Actions: {', '.join(admin_review.actions_taken)}")
                            st.balloons()
                            st.rerun()

            st.markdown("---")

def manual_flag_tab():
    """Manual bias flagging interface."""
    st.markdown("### 🚩 Manually Flag Bias")
    st.info("Use this to flag bias you've identified that wasn't caught by the AI system.")

    with st.form("manual_flag_form"):
        col1, col2 = st.columns(2)

        with col1:
            quiz_id = st.text_input("Quiz ID", placeholder="quiz_123456")
            user_id = st.text_input("User ID", placeholder="user_123")
            concept = st.selectbox(
                "Concept",
                ["saving_money", "budgeting", "investing", "credit", "debt", "earning"]
            )

        with col2:
            bias_types = st.multiselect(
                "Bias Types",
                ["gender", "cultural", "economic", "stereotype", "accessibility", "age_appropriateness"],
                help="Select all that apply"
            )
            severity = st.select_slider("Severity", ["low", "medium", "high"], value="medium")

        specific_issues = st.text_area(
            "Specific Issues",
            placeholder="Describe the bias issues you found (one per line)",
            height=100
        )

        recommendations = st.text_area(
            "Recommendations",
            placeholder="How should this be fixed? (one per line)",
            height=100
        )

        admin_notes = st.text_area(
            "Admin Notes",
            placeholder="Additional context or notes",
            height=80
        )

        if st.form_submit_button("🚩 Flag Bias & Update Content", type="primary"):
            if not quiz_id or not user_id or not bias_types:
                st.error("Please fill in all required fields")
            else:
                with st.spinner("Flagging bias and updating content..."):
                    issues_list = [i.strip() for i in specific_issues.split('\n') if i.strip()]
                    recs_list = [r.strip() for r in recommendations.split('\n') if r.strip()]

                    review_id = admin_agent.flag_bias_manually(
                        quiz_id=quiz_id,
                        user_id=user_id,
                        concept=concept,
                        admin_id=st.session_state.admin_id,
                        bias_types=bias_types,
                        severity=severity,
                        specific_issues=issues_list,
                        recommendations=recs_list,
                        admin_notes=admin_notes
                    )

                    # Auto-process to update knowledge base
                    admin_review = run_async(
                        admin_agent.process_admin_review(
                            review_id=review_id,
                            admin_id=st.session_state.admin_id,
                            decision="flag_bias",
                            admin_notes=admin_notes,
                            bias_override={
                                "bias_types": bias_types,
                                "severity": severity,
                                "specific_issues": issues_list,
                                "recommendations": recs_list
                            },
                            force_update=True
                        )
                    )

                    st.success("✅ Bias flagged and content updated!")
                    st.balloons()
                    st.markdown(f"**Review ID:** {review_id}")
                    st.markdown(f"**Actions taken:** {', '.join(admin_review.actions_taken)}")

def statistics_tab(stats):
    """Statistics and analytics."""
    st.markdown("### 📈 Detailed Statistics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Priority Breakdown")
        priority_data = stats['priority_breakdown']
        for priority, count in priority_data.items():
            if count > 0:
                st.metric(f"{priority.capitalize()} Priority", count)

    with col2:
        st.markdown("#### Decision Breakdown")
        decision_data = stats['decision_breakdown']
        for decision, count in decision_data.items():
            if count > 0:
                st.metric(decision.replace('_', ' ').title(), count)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("AI Accuracy", f"{stats['ai_accuracy_percentage']}%")

    with col2:
        st.metric("Manual Bias Flags", stats['manual_bias_flags'])

    with col3:
        st.metric("Total History Records", stats['total_history_records'])

def review_history_tab():
    """Review history."""
    st.markdown("### 📜 Review History")

    queue = admin_agent.get_review_queue(status="reviewed")

    if not queue:
        st.info("No review history yet")
        return

    st.markdown(f"**{len(queue)} completed reviews**")

    for item in queue[-10:]:  # Show last 10
        with st.expander(f"Review {item['review_id']} - {item['admin_decision']}"):
            st.write(f"**Reviewed by:** {item['reviewed_by']}")
            st.write(f"**Reviewed at:** {item['reviewed_at']}")
            st.write(f"**Decision:** {item['admin_decision']}")
            st.write(f"**Actions:** {', '.join(item.get('actions_taken', []))}")

            feedback = QuizFeedback(**item["feedback"])
            st.write(f"**Concept:** {feedback.concept}")
            st.write(f"**Rating:** {feedback.rating}/5")
            if feedback.comments:
                st.info(f"Comment: {feedback.comments}")

# Main app
if not st.session_state.admin_logged_in:
    login_page()
else:
    main_dashboard()

