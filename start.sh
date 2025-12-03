#!/bin/bash

# Startup script for Financial Education Quiz Engine

echo "🚀 Starting Financial Education Quiz Engine..."
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

echo ""
echo "✅ Setup complete!"
echo ""
echo "Starting services..."
echo ""

# Start MCP server in background
echo "🔌 Starting MCP Server on port 8000..."
python mcp_server.py &
MCP_PID=$!

# Wait for MCP server to start
sleep 3

# Start Streamlit app
echo "🎨 Starting Streamlit UI on port 8501..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🎓 Financial Education Quiz Engine"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  📱 UI: http://localhost:8501"
echo "  🔌 MCP Server: http://localhost:8000"
echo ""
echo "  Press Ctrl+C to stop all services"
echo ""
streamlit run app.py

# Cleanup on exit
echo ""
echo "🛑 Stopping services..."
kill $MCP_PID 2>/dev/null
echo "✅ All services stopped"
