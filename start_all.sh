#!/bin/bash

# Complete startup script for Financial Education Platform
# Starts both Main App and Admin Dashboard

echo "🚀 Starting Complete Financial Education Platform..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if ..env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Please create .env file with your OpenAI API key"
    echo ""
    echo "Example .env content:"
    echo "OPENAI_API_KEY=your_openai_api_key_here"
    echo "MCP_SERVER_URL=http://localhost:8000"
    echo ""
    exit 1
fi

# Install dependencies if needed
echo "📚 Checking dependencies..."
pip install -q -r requirements.txt

# Check if vector store exists
if [ ! -f "data/vector_store/education.index" ]; then
    echo "🧠 Initializing knowledge base..."
    python scripts/load_knowledge_base.py
fi

# Create data directories if they don't exist
mkdir -p data

echo ""
echo "✅ Setup complete!"
echo ""
echo "Starting all services..."
echo ""

# Start MCP server in background
echo "🔌 Starting MCP Server on port 8000..."
python mcp_server.py > mcp_server.log 2>&1 &
MCP_PID=$!

# Wait for MCP server to start
sleep 3

# Start Main Streamlit app in background
echo "🎨 Starting Main UI on port 8501..."
streamlit run app.py --server.port 8501 > streamlit_app.log 2>&1 &
APP_PID=$!

# Wait a bit for main app to start
sleep 2

# Start Admin Dashboard
echo "🛡️  Starting Admin Dashboard on port 8502..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🎓 Financial Education Complete Platform"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  📱 Main UI:          http://localhost:8501"
echo "  🛡️  Admin Dashboard:  http://localhost:8502"
echo "  🔌 MCP Server:       http://localhost:8000"
echo ""
echo "  👥 For Students/Users → Visit Main UI"
echo "  🛡️  For Admins       → Visit Admin Dashboard"
echo ""
echo "  📋 Admin Login:"
echo "     Username: admin@example.com"
echo "     Password: admin123"
echo "     ⚠️  Change these in production!"
echo ""
echo "  📝 Logs:"
echo "     MCP Server:  mcp_server.log"
echo "     Main App:    streamlit_app.log"
echo ""
echo "  Press Ctrl+C to stop all services"
echo ""
streamlit run admin_dashboard.py --server.port 8502

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."

    # Kill MCP server
    if [ ! -z "$MCP_PID" ]; then
        kill $MCP_PID 2>/dev/null
        echo "  ✓ MCP Server stopped"
    fi

    # Kill main app
    if [ ! -z "$APP_PID" ]; then
        kill $APP_PID 2>/dev/null
        echo "  ✓ Main UI stopped"
    fi

    # Kill any remaining streamlit processes
    pkill -f "streamlit run" 2>/dev/null

    echo "✅ All services stopped"
    exit 0
}

# Trap Ctrl+C and cleanup
trap cleanup SIGINT SIGTERM

# Wait for admin dashboard to finish
wait

