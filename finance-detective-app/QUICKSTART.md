# 🚀 Quick Start Guide - Finance Detective App

## Prerequisites Check

```bash
# Check Node.js version (need v18+)
node --version

# Check npm version
npm --version

# Install Angular CLI globally
npm install -g @angular/cli

# Verify Angular installation
ng version
```

## Setup Steps

### 1. Install Dependencies

```bash
cd finance-detective-app
npm install
```

This will install all required packages (~500MB).

### 2. Start MCP Server

In the parent directory:

```bash
cd ..
python mcp_server.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
MCP Server started successfully
```

### 3. Start Angular App

In a new terminal:

```bash
cd finance-detective-app
npm start
```

Wait for:
```
✔ Browser application bundle generation complete.
** Angular Live Development Server is listening on localhost:4200
```

### 4. Open Browser

Navigate to: `http://localhost:4200`

## First Time Setup

1. **Create Your Detective Profile**
   - Enter your name
   - Select your age (6-18)
   - Choose hobbies and interests
   - Click "Start Investigation"

2. **Explore Detective HQ**
   - View your stats
   - Check available cases
   - Navigate using the top menu

3. **Start Your First Case**
   - Click on any case card
   - Read the financial mystery
   - Answer questions
   - Earn your first badges!

## Common Commands

```bash
# Start development server
npm start

# Stop server (Ctrl+C in terminal)

# Build for production
npm run build

# Clean install
rm -rf node_modules package-lock.json
npm install
```

## Troubleshooting

### Port 4200 in use
```bash
lsof -ti:4200 | xargs kill -9
npm start
```

### MCP Server not responding
```bash
# Check if server is running
curl http://localhost:8000

# Restart server
python mcp_server.py
```

### npm install fails
```bash
# Clear npm cache
npm cache clean --force

# Try again
npm install
```

## Development Tips

- **Auto-reload**: Changes to files trigger automatic reload
- **DevTools**: Press F12 to see console logs and network requests
- **API Calls**: Check Network tab to debug MCP server communication

## Next Steps

1. Complete your first quiz
2. Earn 100 points to rank up
3. Unlock all badges
4. Become a Legendary Detective!

---

**Ready to solve financial mysteries? Let's go! 🕵️**
