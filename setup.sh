#!/bin/bash

# Financial Education Quiz Engine - Setup Script
# This script sets up the complete environment

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  Financial Education Quiz Engine - Setup                     ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then 
    echo -e "${RED}✗ Python 3.9+ required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"
echo ""

# Create virtual environment
echo "Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠ Virtual environment already exists${NC}"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Check .env file
echo "Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo -e "${RED}✗ .env file not found${NC}"
    echo ""
    echo "Please create a .env file with your Azure OpenAI credentials:"
    echo ""
    cat << EOF
# Azure OpenAI Configuration
OPENAI_API_KEY=your_azure_openai_api_key_here
MODEL_API_VERSION=2024-02-01
MODEL_NAME=gpt-4o
OPENAI_ENDPOINT=https://your-resource.openai.azure.com

# Optional
GOOGLE_API_KEY=your_google_api_key_here
MCP_SERVER_URL=http://localhost:8000
CLASSIFIER_MODEL_PROVIDER='openai'
EOF
    echo ""
    exit 1
fi
echo -e "${GREEN}✓ .env file exists${NC}"
echo ""

# Initialize knowledge base
echo "Initializing knowledge base..."
if [ ! -f "data/vector_store/education.index" ]; then
    python scripts/load_knowledge_base.py
    echo -e "${GREEN}✓ Knowledge base initialized${NC}"
else
    echo -e "${YELLOW}⚠ Knowledge base already exists${NC}"
    read -p "Reinitialize? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python scripts/load_knowledge_base.py
        echo -e "${GREEN}✓ Knowledge base reinitialized${NC}"
    fi
fi
echo ""

# Run verification
echo "Running verification checks..."
python verify_installation.py
echo ""

# Setup complete
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  Setup Complete!                                              ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "To start the application:"
echo ""
echo "  ${GREEN}bash start.sh${NC}"
echo ""
echo "Or manually:"
echo ""
echo "  ${GREEN}source venv/bin/activate${NC}"
echo "  ${GREEN}python mcp_server.py &${NC}"
echo "  ${GREEN}streamlit run app.py${NC}"
echo ""
echo "Access the app at: ${GREEN}http://localhost:8501${NC}"
echo ""
