#!/bin/bash

# Finance Detective App Startup Script
# This script starts both the MCP server and Angular app

echo "🕵️  Starting Finance Detective App..."
echo "======================================"

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    lsof -ti:$1 > /dev/null 2>&1
    return $?
}

# Function to kill process on port
kill_port() {
    echo -e "${YELLOW}⚠️  Killing existing process on port $1...${NC}"
    lsof -ti:$1 | xargs kill -9 2>/dev/null || true
    sleep 2
}

# Create logs directory if it doesn't exist
mkdir -p logs

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo -e "${BLUE}🐍 Activating virtual environment...${NC}"
    source venv/bin/activate
fi

# Check if agno is installed
if ! python -c "import agno" 2>/dev/null; then
    echo -e "${YELLOW}📦 Installing agno package...${NC}"
    pip install agno
fi

# Kill existing processes on ports 8000 and 4200
if check_port 8000; then
    kill_port 8000
fi

if check_port 4200; then
    kill_port 4200
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo "Please create a .env file with your OPENAI_API_KEY"
    echo "Example:"
    echo "OPENAI_API_KEY=your_key_here"
    exit 1
fi

# Check if database is initialized
if [ ! -f "data/quiz_data.db" ]; then
    echo -e "${YELLOW}🗄️  Initializing database (will be created automatically on first run)...${NC}"
    python -c "import database as db; db.init_database(); print('✅ Database initialized')"
fi

# Start MCP Server in background
echo -e "${GREEN}🚀 Starting MCP Server on port 8000...${NC}"
nohup uvicorn mcp_server:app --host 0.0.0.0 --port 8000 > logs/mcp_server.log 2>&1 &
MCP_PID=$!

# Wait for MCP server to start
echo "⏳ Waiting for MCP server to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/users > /dev/null 2>&1; then
        echo -e "${GREEN}✅ MCP Server is running!${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Failed to start MCP Server${NC}"
        echo "Check logs/mcp_server.log for errors"
        cat logs/mcp_server.log
        exit 1
    fi
    sleep 1
done

# Navigate to Angular app directory
cd finance-detective-app

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing Angular dependencies...${NC}"
    npm install
fi

# Start Angular app
echo ""
echo "======================================"
echo -e "${GREEN}✅ Both servers are starting!${NC}"
echo ""
echo "🌐 MCP Server:    http://localhost:8000"
echo "🕵️  Detective App:  http://localhost:4200"
echo ""
echo "📝 Logs:"
echo "   MCP Server:   logs/mcp_server.log"
echo "   Angular App:  Console output below"
echo ""
echo "💡 Press Ctrl+C to stop all services"
echo "======================================"
echo ""
echo -e "${GREEN}🎮 Starting Finance Detective Angular App on port 4200...${NC}"
echo ""

# Start Angular app (this will run in foreground and open browser)
npm start -- --open

# Cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stopping services...${NC}"
    kill $MCP_PID 2>/dev/null
    pkill -f "uvicorn mcp_server" 2>/dev/null
    echo -e "${GREEN}✅ All services stopped. Goodbye!${NC}"
    exit 0
}

trap cleanup INT TERM
