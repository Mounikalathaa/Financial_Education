#!/bin/bash

# Finance Detective - Startup Script
# This script helps you start all required services

echo "🕵️ Finance Detective - Starting Services..."
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

# Check if Angular CLI is installed
if ! command -v ng &> /dev/null; then
    echo "⚠️  Angular CLI not found. Installing globally..."
    npm install -g @angular/cli
fi

# Check if dependencies are installed
if [ ! -d "finance-detective-app/node_modules" ]; then
    echo "📦 Installing dependencies..."
    cd finance-detective-app
    npm install
    cd ..
fi

echo ""
echo "✅ All checks passed!"
echo ""
echo "Starting services in 3 seconds..."
sleep 3

# Start MCP Server
echo ""
echo "🚀 Starting MCP Server (Port 8000)..."
python mcp_server.py &
MCP_PID=$!
sleep 3

# Check if MCP server started successfully
if curl -s http://localhost:8000 > /dev/null; then
    echo "✅ MCP Server started successfully!"
else
    echo "❌ MCP Server failed to start"
    kill $MCP_PID 2>/dev/null
    exit 1
fi

# Start Angular App
echo ""
echo "🎨 Starting Angular App (Port 4200)..."
cd finance-detective-app
npm start &
ANGULAR_PID=$!

echo ""
echo "================================================"
echo "🎉 Finance Detective Services Started!"
echo "================================================"
echo ""
echo "📍 Access URLs:"
echo "   🕵️  Angular App:    http://localhost:4200"
echo "   🔌 MCP Server:     http://localhost:8000"
echo ""
echo "⚡ Process IDs:"
echo "   MCP Server: $MCP_PID"
echo "   Angular:    $ANGULAR_PID"
echo ""
echo "📝 To stop all services, press Ctrl+C"
echo ""
echo "================================================"

# Handle cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $MCP_PID 2>/dev/null
    kill $ANGULAR_PID 2>/dev/null
    echo "✅ All services stopped. Goodbye!"
    exit 0
}

trap cleanup INT TERM

# Keep script running
wait
