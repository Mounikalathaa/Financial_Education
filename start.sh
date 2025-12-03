#!/bin/bash

# Comprehensive Startup Script for Financial Education Quiz Engine
# This script handles all dependencies and starts all services

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Cleanup function
cleanup() {
    echo ""
    print_info "Stopping services..."
    if [ ! -z "$MCP_PID" ]; then
        kill $MCP_PID 2>/dev/null || true
    fi
    if [ ! -z "$ANGULAR_PID" ]; then
        kill $ANGULAR_PID 2>/dev/null || true
    fi
    # Kill any remaining processes on our ports
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:8501 | xargs kill -9 2>/dev/null || true
    lsof -ti:4200 | xargs kill -9 2>/dev/null || true
    print_success "All services stopped"
    exit 0
}

# Set up trap to catch Ctrl+C
trap cleanup SIGINT SIGTERM

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀 Financial Education Quiz Engine Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1: Check system dependencies
print_info "Checking system dependencies..."

if ! command_exists python3; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
print_success "Python $PYTHON_VERSION found"

if ! command_exists node; then
    print_warning "Node.js is not installed. Angular app will not be available."
    print_info "To install Node.js, visit: https://nodejs.org/"
    NODE_AVAILABLE=false
else
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION found"
    NODE_AVAILABLE=true
fi

# Step 2: Set up Python virtual environment
print_info "Setting up Python virtual environment..."

if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate

# Step 3: Check and create .env file
print_info "Checking environment configuration..."

if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating template..."
    cat > .env << EOF
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API Configuration (optional)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Server Configuration
MCP_SERVER_URL=http://localhost:8000
MCP_SERVER_PORT=8000
STREAMLIT_PORT=8501

# Database Configuration
DATABASE_PATH=data/quiz_data.db

# Logging
LOG_LEVEL=INFO
EOF
    print_error "Please edit .env file and add your API keys!"
    print_info "Opening .env file..."
    ${EDITOR:-nano} .env

    # Check if user added API key
    if grep -q "your_openai_api_key_here" .env; then
        print_error "OpenAI API key not set in .env file. Please add it and run the script again."
        exit 1
    fi
else
    print_success ".env file exists"

    # Validate API key is set
    if grep -q "your_openai_api_key_here" .env || ! grep -q "OPENAI_API_KEY=" .env; then
        print_error "OpenAI API key not properly set in .env file."
        print_info "Please edit .env and add your OpenAI API key"
        exit 1
    fi
fi

# Step 4: Install Python dependencies
print_info "Installing Python dependencies..."

if [ -f "requirements.txt" ]; then
    pip install --upgrade pip -q
    print_info "This may take a few minutes on first run..."
    pip install -r requirements.txt
    print_success "Python dependencies installed"
else
    print_error "requirements.txt not found!"
    exit 1
fi

# Step 5: Set up database
print_info "Setting up database..."

if [ ! -d "data" ]; then
    mkdir -p data
fi

if [ ! -f "data/quiz_data.db" ]; then
    print_info "Initializing database..."
    python3 -c "import database; database.init_database()"
    print_success "Database initialized"
else
    print_success "Database already exists"
fi

# Step 6: Initialize knowledge base
print_info "Checking knowledge base..."

if [ ! -d "data/vector_store" ] || [ -z "$(ls -A data/vector_store 2>/dev/null)" ]; then
    print_info "Initializing knowledge base (this may take a few minutes)..."
    if [ -f "scripts/load_knowledge_base.py" ]; then
        python scripts/load_knowledge_base.py
        print_success "Knowledge base initialized"
    else
        print_warning "Knowledge base loader not found. Will initialize on first run."
    fi
else
    print_success "Knowledge base already exists"
fi

# Step 7: Set up Angular app (if Node.js is available)
if [ "$NODE_AVAILABLE" = true ] && [ -d "finance-detective-app" ]; then
    print_info "Setting up Angular application..."
    cd finance-detective-app

    if [ ! -d "node_modules" ]; then
        print_info "Installing Angular dependencies (this may take a few minutes)..."
        npm install
        print_success "Angular dependencies installed"
    else
        print_success "Angular dependencies already installed"
    fi

    cd ..
fi

# Step 8: Verify installation
print_info "Verifying installation..."

if [ -f "verify_installation.py" ]; then
    python verify_installation.py
    if [ $? -eq 0 ]; then
        print_success "Installation verified"
    else
        print_warning "Some components may need attention"
    fi
fi

echo ""
print_success "Setup complete!"
echo ""
print_info "Starting services..."
echo ""

# Step 9: Start MCP Server
print_info "Starting MCP Server on port 8000..."
python mcp_server.py > mcp_server.log 2>&1 &
MCP_PID=$!

# Wait for MCP server to be ready
sleep 2
if ps -p $MCP_PID > /dev/null; then
    print_success "MCP Server started (PID: $MCP_PID)"
else
    print_error "MCP Server failed to start. Check mcp_server.log"
    cat mcp_server.log
    exit 1
fi

# Step 10: Start Angular app (if available)
if [ "$NODE_AVAILABLE" = true ] && [ -d "finance-detective-app" ]; then
    print_info "Starting Angular app on port 4200..."
    cd finance-detective-app
    npm run start > ../angular_app.log 2>&1 &
    ANGULAR_PID=$!
    cd ..
    print_success "Angular app starting (PID: $ANGULAR_PID)"
fi

# Step 11: Start Streamlit app
sleep 2
print_info "Starting Streamlit UI on port 8501..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🎓 Financial Education Quiz Engine"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  📱 Streamlit UI:  http://localhost:8501"
echo "  🔌 MCP Server:    http://localhost:8000"
if [ "$NODE_AVAILABLE" = true ] && [ -d "finance-detective-app" ]; then
    echo "  🎮 Angular App:   http://localhost:4200"
fi
echo ""
echo "  📋 Logs:"
echo "    - MCP Server: mcp_server.log"
echo "    - Streamlit:  streamlit_app.log"
if [ "$NODE_AVAILABLE" = true ] && [ -d "finance-detective-app" ]; then
    echo "    - Angular:    angular_app.log"
fi
echo ""
echo "  Press Ctrl+C to stop all services"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

streamlit run app.py 2>&1 | tee streamlit_app.log

# This will only execute when streamlit stops
cleanup
