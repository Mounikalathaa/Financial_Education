#!/bin/bash

# Quick demo script for Financial Education Quiz Engine

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Financial Education Quiz Engine - Quick Demo          ║"
echo "║  Agentic AI for Personalized Learning                  ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check if running in correct directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the financial_education directory"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "✓ Virtual environment found"
else
    echo "⚠ Virtual environment not found"
    echo "  Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✓ Activating virtual environment"
source venv/bin/activate

# Check if dependencies are installed
if python -c "import streamlit" 2>/dev/null; then
    echo "✓ Dependencies installed"
else
    echo "⚠ Installing dependencies..."
    pip install -q -r requirements.txt
    echo "✓ Dependencies installed"
fi

# Check ..env file
if [ -f ".env" ]; then
    echo "✓ Environment configuration found"
else
    echo "❌ Error: .env file not found"
    echo ""
    echo "Please create a .env file with:"
    echo "OPENAI_API_KEY=your_openai_api_key_here"
    echo "MCP_SERVER_URL=http://localhost:8000"
    exit 1
fi

# Check vector store
if [ -f "data/vector_store/education.index" ]; then
    echo "✓ Knowledge base initialized"
else
    echo "⚠ Initializing knowledge base..."
    python scripts/load_knowledge_base.py
    echo "✓ Knowledge base ready"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  System Check Complete - Starting Demo                 ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Start MCP server
echo "🔌 Starting MCP Server..."
python mcp_server.py > /dev/null 2>&1 &
MCP_PID=$!
sleep 3

# Check if MCP server is running
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✓ MCP Server running on port 8000"
else
    echo "❌ Failed to start MCP Server"
    kill $MCP_PID 2>/dev/null
    exit 1
fi

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Starting Streamlit Application                        ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "  🎓 Financial Education Quiz Engine"
echo ""
echo "  📱 UI:         http://localhost:8501"
echo "  🔌 MCP Server: http://localhost:8000"
echo "  📚 API Docs:   http://localhost:8000/docs"
echo ""
echo "  Demo Users:"
echo "    • Alex (age 12)  - Tech enthusiast"
echo "    • Sarah (age 9)  - Art lover"
echo "    • Mike (age 15)  - Science geek"
echo ""
echo "  Financial Concepts:"
echo "    1. Saving Money"
echo "    2. Budgeting"
echo "    3. Needs vs Wants"
echo "    4. Earning Money"
echo "    5. Compound Interest"
echo "    6. Risk & Reward"
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Press Ctrl+C to stop all services                     ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Start Streamlit
streamlit run app.py

# Cleanup on exit
echo ""
echo "🛑 Stopping services..."
kill $MCP_PID 2>/dev/null
echo "✓ All services stopped"
echo ""
echo "Thank you for trying Financial Education Quiz Engine! 💰🎓"
