# 📘 Quick Reference - Financial Education Quiz Engine

## 🚀 Quick Start Commands

```bash
# One-time setup
bash setup.sh

# Start application
bash start.sh

# Or manually
python mcp_server.py &
streamlit run app.py

# Stop application
pkill -f "streamlit"
pkill -f "mcp_server"
```

## 📍 Important URLs

- **Application**: http://localhost:8501
- **MCP Server**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📂 Project Structure

```
FinancialEducationQuiz/
├── agents/              # 6 AI agents (orchestrator, personalization, etc.)
├── services/            # MCP client & RAG service
├── models/              # Pydantic data models
├── config/              # Configuration management
├── utils/               # Helper utilities
├── scripts/             # Setup & utility scripts
├── data/                # Data storage & vector store
├── docs/                # Documentation
├── app.py               # Streamlit UI (main entry point)
├── mcp_server.py        # FastAPI server
├── config.yaml          # App configuration
├── .env                 # Environment variables (sensitive)
└── requirements.txt     # Python dependencies
```

## 🔑 Key Files

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit application |
| `mcp_server.py` | FastAPI MCP server |
| `config.yaml` | Application settings |
| `.env` | API keys & credentials |
| `requirements.txt` | Python dependencies |
| `setup.sh` | One-time setup script |
| `start.sh` | Start application |
| `verify_installation.py` | Verify setup |

## 🔧 Configuration Files

### .env (Required)
```bash
OPENAI_API_KEY=your_azure_openai_api_key
MODEL_API_VERSION=2024-02-01
MODEL_NAME=gpt-4o
OPENAI_ENDPOINT=https://your-resource.openai.azure.com
```

### config.yaml (Customizable)
- LLM settings (temperature, tokens)
- Gamification rules (points, levels)
- Age groups & difficulty levels
- Financial concepts

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/user/profile/{user_id}` | Get user profile |
| GET | `/api/user/transactions/{user_id}` | Get transactions |
| GET | `/api/user/quiz-history/{user_id}` | Get quiz history |
| GET | `/api/user/gamification/{user_id}` | Get gamification data |
| POST | `/api/user/gamification/update` | Update gamification |

## 🎮 Gamification System

### Points
- Correct answer: **10 points**
- Quiz completion: **+50 bonus**

### Levels
1. Beginner (0-100)
2. Explorer (101-300)
3. Learner (301-600)
4. Expert (601-1000)
5. Master (1000+)

### Badges
- First Quiz Complete
- Streak Master (5 days)
- Perfect Score
- Concept Explorer

## 🧩 AI Agents

1. **Orchestrator** - Coordinates workflow
2. **Personalization** - Analyzes user context
3. **Content Generation** - Creates stories
4. **Quiz Generation** - Generates questions
5. **Evaluation** - Grades responses
6. **Gamification** - Manages achievements

## 📚 Financial Concepts

1. Saving Money
2. Budgeting Basics
3. Needs vs Wants
4. Earning Money
5. Banking Basics
6. Goal Setting
7. Smart Spending
8. Compound Interest
9. Risk and Reward
10. Giving and Charity

## 🔍 Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Kill process on port 8501
lsof -ti:8501 | xargs kill -9

# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

**Module Not Found**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

**API Key Error**
```bash
# Check ..env file
cat ..env

# Verify API key is valid
# Get new key from Azure Portal
```

**Vector Store Missing**
```bash
# Reinitialize knowledge base
python scripts/load_knowledge_base.py
```

**Services Not Starting**
```bash
# Check logs
tail -f mcp_server.log

# Verify installation
python verify_installation.py
```

## 🛠️ Development Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Install new dependency
pip install package-name
pip freeze > requirements.txt

# Update knowledge base
python scripts/load_knowledge_base.py

# Run verification
python verify_installation.py

# View logs
tail -f mcp_server.log

# Run tests (if available)
pytest
```

## 📦 Dependencies

**Core**
- streamlit ≥1.31.0
- openai ≥1.12.0
- faiss-cpu ≥1.9.0
- sentence-transformers ≥3.3.0

**Backend**
- fastapi ≥0.109.0
- uvicorn ≥0.27.0
- pydantic ≥2.6.0

**Data**
- pandas ≥2.2.0
- numpy ≥1.26.0

**AI/ML**
- langchain ≥0.3.0
- langchain-community ≥0.3.0
- langchain-openai ≥0.2.0

## 🌐 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | Azure OpenAI API key (required) |
| `MODEL_API_VERSION` | 2024-02-01 | API version |
| `MODEL_NAME` | gpt-4o | Model deployment name |
| `OPENAI_ENDPOINT` | - | Azure endpoint URL |
| `MCP_SERVER_URL` | http://localhost:8000 | MCP server URL |
| `CLASSIFIER_MODEL_PROVIDER` | openai | Model provider |

## 📖 Documentation

- **README_STANDALONE.md** - Complete project overview
- **DEPLOYMENT.md** - Deployment guide
- **GETTING_STARTED.md** - User guide
- **PROJECT_SUMMARY.md** - Technical summary
- **README_HACKATHON.md** - Hackathon presentation

## 🔗 Quick Links

- Azure OpenAI: https://portal.azure.com
- Streamlit Docs: https://docs.streamlit.io
- FastAPI Docs: https://fastapi.tiangolo.com
- Project Repo: [Your Git URL]

## 💡 Tips

1. **Always activate venv** before running commands
2. **Keep .env secure** - never commit to git
3. **Check logs** when troubleshooting
4. **Verify setup** after changes
5. **Stop services** properly before restarting
6. **Backup data/** directory regularly
7. **Update dependencies** periodically
8. **Monitor API usage** to control costs

## 🆘 Getting Help

1. Check this quick reference
2. Review relevant documentation
3. Check application logs
4. Run verification script
5. Consult troubleshooting section
6. Check Azure OpenAI status

---

**For detailed information, see:**
- `README_STANDALONE.md` - Full documentation
- `DEPLOYMENT.md` - Deployment guide
- `docs/` directory - Additional guides
