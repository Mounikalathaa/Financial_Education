#!/bin/bash

# One-command setup and run script for Financial Education Quiz Engine
# This script performs a complete fresh installation and starts the application

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🎓 Financial Education Quiz Engine"
echo "  📦 Complete Setup & Installation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if we're in the correct directory
if [ ! -f "requirements.txt" ] || [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Make start.sh executable
chmod +x start.sh

# Run the main start script
./start.sh

