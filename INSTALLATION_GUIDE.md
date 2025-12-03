# 🚀 Installation & Setup Guide

## Quick Start (Recommended)

### One-Command Setup

```bash
chmod +x setup_and_run.sh && ./setup_and_run.sh
```

This will automatically:
- ✅ Check all system requirements
- ✅ Create Python virtual environment
- ✅ Install all Python dependencies
- ✅ Set up `.env` configuration file
- ✅ Initialize the database
- ✅ Load knowledge base
- ✅ Install Angular dependencies (if Node.js available)
- ✅ Start all services (MCP Server, Streamlit UI, Angular App)

## Prerequisites

### Required
- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **OpenAI API Key** - [Get API Key](https://platform.openai.com/api-keys)

### Optional
- **Node.js 18+** - [Download Node.js](https://nodejs.org/) (for Angular frontend)

## Manual Setup

### Step 1: Clone or Download the Project

```bash
cd /path/to/Financial_Education
```

### Step 2: Run the Setup Script

```bash
chmod +x start.sh
./start.sh
```

The script will guide you through:

1. **Environment Setup**: Creates a `.env` file if not present
2. **API Configuration**: Prompts you to add your OpenAI API key
3. **Dependency Installation**: Installs all Python packages
4. **Database Initialization**: Sets up SQLite database
5. **Knowledge Base**: Loads financial education content
6. **Service Startup**: Starts all required services

### Step 3: Configure API Keys

When prompted, edit the `.env` file and add your API key:

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

## What Gets Installed

### Python Packages
- `streamlit` - Web UI framework
- `openai` - OpenAI API client
- `agno` - AI agent framework
- `faiss-cpu` - Vector database
- `sentence-transformers` - Embeddings
- `fastapi` - MCP Server API
- `langchain` - LLM orchestration
- And more (see `requirements.txt`)

### Angular App (Optional)
- Angular 17 framework
- RxJS for reactive programming
- TypeScript compiler

## Services & Ports

After successful setup, the following services will be running:

| Service | URL | Description |
|---------|-----|-------------|
| **Streamlit UI** | http://localhost:8501 | Main web interface |
| **MCP Server** | http://localhost:8000 | API backend |
| **Angular App** | http://localhost:4200 | Detective-themed frontend (optional) |

## Log Files

All services generate log files for debugging:

- `mcp_server.log` - MCP Server logs
- `streamlit_app.log` - Streamlit application logs
- `angular_app.log` - Angular app logs (if applicable)

## Stopping the Application

Press `Ctrl+C` in the terminal where you ran the script. This will:
- Stop all running services
- Clean up background processes
- Release all ports

## Troubleshooting

### Port Already in Use

If you get port conflicts, kill existing processes:

```bash
# Kill processes on specific ports
lsof -ti:8000 | xargs kill -9  # MCP Server
lsof -ti:8501 | xargs kill -9  # Streamlit
lsof -ti:4200 | xargs kill -9  # Angular
```

### Python Virtual Environment Issues

```bash
# Remove and recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Missing API Key

Edit the `.env` file:

```bash
nano .env
# or
vim .env
# or
open .env  # macOS default editor
```

### Knowledge Base Not Loading

Manually initialize:

```bash
source venv/bin/activate
python scripts/load_knowledge_base.py
```

### Angular Dependencies Issues

```bash
cd finance-detective-app
rm -rf node_modules package-lock.json
npm install
cd ..
```

## Development Mode

### Running Only Python Backend

```bash
source venv/bin/activate
python mcp_server.py &
streamlit run app.py
```

### Running Only Angular Frontend

```bash
cd finance-detective-app
npm run start
```

### Running Tests

```bash
source venv/bin/activate
pytest
```

## Environment Variables

All available environment variables in `.env`:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
ANTHROPIC_API_KEY=your_anthropic_api_key_here
MCP_SERVER_URL=http://localhost:8000
MCP_SERVER_PORT=8000
STREAMLIT_PORT=8501
DATABASE_PATH=data/quiz_data.db
LOG_LEVEL=INFO
```

## System Requirements

### Minimum
- CPU: 2 cores
- RAM: 4GB
- Storage: 2GB free space
- OS: macOS, Linux, or Windows (WSL)

### Recommended
- CPU: 4+ cores
- RAM: 8GB+
- Storage: 5GB+ free space
- Internet connection for API calls

## Next Steps

1. Open your browser to http://localhost:8501
2. Create a user profile
3. Start learning with AI-generated quizzes!

## Getting Help

- Check log files for error details
- Review `PROJECT_SUMMARY.md` for architecture details
- See `QUICK_REFERENCE.md` for API documentation

---

**Happy Learning! 🎓💰**

