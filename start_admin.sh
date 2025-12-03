#!/bin/bash

# Startup script for Financial Education Admin Dashboard

echo "🛡️  Starting Financial Education Admin Dashboard..."
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

# Check if MCP server is running
echo "🔍 Checking if MCP server is running..."
if ! curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo ""
    echo "⚠️  Warning: MCP Server is not running on port 8000"
    echo ""
    echo "The admin dashboard requires the MCP server to be running."
    echo "Please start the main application first using:"
    echo "  ./start.sh"
    echo ""
    echo "Or start just the MCP server:"
    echo "  python mcp_server.py"
    echo ""
    read -p "Do you want to start MCP server now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔌 Starting MCP Server on port 8000..."
        python mcp_server.py &
        MCP_PID=$!
        sleep 3
        echo "✅ MCP Server started"
    else
        echo "❌ Cannot start admin dashboard without MCP server"
        exit 1
    fi
fi

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

# Start Admin Dashboard
echo "🛡️  Starting Admin Dashboard on port 8502..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🛡️  Financial Education Admin Dashboard"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  🛡️  Admin Dashboard: http://localhost:8502"
echo "  🔌 MCP Server: http://localhost:8000"
echo "  📱 Main UI: http://localhost:8501"
echo ""
echo "  📋 Admin Login:"
echo "     Username: admin@example.com"
echo "     Password: admin123"
echo "     ⚠️  Change these in production!"
echo ""
echo "  Press Ctrl+C to stop"
echo ""
streamlit run admin_dashboard.py --server.port 8502

# Cleanup on exit
if [ ! -z "$MCP_PID" ]; then
    echo ""
    echo "🛑 Stopping MCP server..."
    kill $MCP_PID 2>/dev/null
fi
echo "✅ Admin dashboard stopped"

