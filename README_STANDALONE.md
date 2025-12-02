# 🎓 Financial Education Quiz Engine

An AI-powered, personalized financial education platform for children (ages 6-17) featuring a Hierarchical Multi-Agent System (HMAS) for generating engaging, gamified quizzes.

## 🌟 Features

- **6 Specialized AI Agents** working together to create personalized content
- **RAG-Powered Knowledge Base** with 10+ financial education documents
- **Gamification System** with points, levels, badges, and streaks
- **Azure OpenAI Integration** for enterprise-grade AI capabilities
- **Mobile-Friendly UI** built with Streamlit
- **Real-time Evaluation** with personalized feedback
- **Age-Appropriate Content** tailored for different learning levels

## 🏗️ Architecture

### Multi-Agent System
1. **Orchestrator Agent** - Coordinates all agents and workflow
2. **Personalization Agent** - Analyzes user context and preferences
3. **Content Generation Agent** - Creates engaging educational stories
4. **Quiz Generation Agent** - Generates age-appropriate questions
5. **Evaluation Agent** - Grades responses and provides feedback
6. **Gamification Agent** - Manages points, levels, and achievements

### Technology Stack
- **Backend**: Python 3.9+, FastAPI (MCP Server)
- **AI/ML**: Azure OpenAI (GPT-4), Sentence Transformers, FAISS
- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy, Pydantic
- **Vector Store**: FAISS for semantic search

## 📋 Prerequisites

- Python 3.9 or higher
- Azure OpenAI access with valid API key
- 4GB RAM minimum
- Internet connection for AI model access

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or navigate to project directory
cd /Users/mounikas@backbase.com/Documents/FinancialEducationQuiz

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create or update your `.env` file with Azure OpenAI credentials:

```bash
# Azure OpenAI Configuration
OPENAI_API_KEY=your_azure_openai_api_key_here
MODEL_API_VERSION=2024-02-01
MODEL_NAME=gpt-4o
OPENAI_ENDPOINT=https://your-resource.openai.azure.com

# Optional: Google API Key for alternative models
GOOGLE_API_KEY=your_google_api_key_here

# MCP Server Configuration
MCP_SERVER_URL=http://localhost:8000

# Model Provider Selection
CLASSIFIER_MODEL_PROVIDER='openai'
```

### 3. Initialize Knowledge Base

```bash
# Load financial education documents into vector store
python scripts/load_knowledge_base.py
```

### 4. Verify Installation

```bash
# Run verification script
python verify_installation.py
```

### 5. Run the Application

**Option A: Use the Quick Start Script**
```bash
bash start.sh
```

**Option B: Manual Start**
```bash
# Terminal 1: Start MCP Server
python mcp_server.py

# Terminal 2: Start Streamlit UI
streamlit run app.py
```

### 6. Access the Application

Open your browser and navigate to:
- **Local**: http://localhost:8501
- **Network**: http://your-ip:8501

## 📖 User Guide

### Getting Started
1. **Onboarding**: Enter your name and age (6-17)
2. **Dashboard**: View your progress, points, and available concepts
3. **Take Quiz**: Select a financial concept to start learning
4. **Complete**: Answer questions and receive instant feedback
5. **Progress**: Track your levels, badges, and achievements

### Financial Concepts Covered
- Saving Money
- Budgeting Basics
- Needs vs Wants
- Earning Money
- Banking Basics
- Goal Setting
- Smart Spending
- Compound Interest
- Risk and Reward
- Giving and Charity

## 🎮 Gamification System

### Points
- **Correct Answer**: 10 points
- **Quiz Completion**: 50 points bonus

### Levels (5 Progressive Stages)
1. **Beginner** (0-100 points)
2. **Explorer** (101-300 points)
3. **Learner** (301-600 points)
4. **Expert** (601-1000 points)
5. **Master** (1000+ points)

### Badges & Achievements
- First Quiz Complete
- Streak Master (5 days)
- Perfect Score
- Concept Explorer
- And many more!

## 🛠️ Development

### Project Structure
```
FinancialEducationQuiz/
├── agents/              # AI agent implementations
│   ├── orchestrator.py
│   ├── personalization_agent.py
│   ├── content_generation_agent.py
│   ├── quiz_generation_agent.py
│   ├── evaluation_agent.py
│   └── gamification_agent.py
├── services/           # Backend services
│   ├── mcp_client.py
│   └── rag_service.py
├── models/            # Pydantic data models
├── config/            # Configuration management
├── utils/             # Helper utilities
├── scripts/           # Utility scripts
├── data/              # Data storage
│   └── vector_store/  # FAISS index
├── docs/              # Documentation
├── app.py             # Streamlit UI
├── mcp_server.py      # FastAPI MCP server
├── config.yaml        # App configuration
└── requirements.txt   # Python dependencies
```

### Key Files
- **app.py**: Main Streamlit application
- **mcp_server.py**: FastAPI server for data management
- **config.yaml**: Application settings and configurations
- **.env**: Sensitive credentials (not in git)

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

## 🔧 Configuration

### Age Groups
Defined in `config.yaml`:
- **Young Learners** (6-9): Simple language, basic concepts
- **Pre-teens** (10-12): Moderate complexity
- **Teenagers** (13-17): Advanced concepts

### Difficulty Levels
- **Easy**: Fundamental concepts
- **Medium**: Intermediate understanding
- **Hard**: Complex scenarios

### Customization
Edit `config.yaml` to customize:
- Points system
- Level thresholds
- Badge criteria
- Financial concepts
- Age group settings

## 📊 API Endpoints (MCP Server)

The MCP server provides RESTful APIs:

- `GET /api/user/profile/{user_id}` - Get user profile
- `GET /api/user/transactions/{user_id}` - Get transaction history
- `GET /api/user/quiz-history/{user_id}` - Get quiz history
- `GET /api/user/gamification/{user_id}` - Get gamification data
- `POST /api/user/gamification/update` - Update gamification data

## 🐛 Troubleshooting

### Common Issues

**Issue: API Authentication Error**
```
Error code: 401 - Invalid API key
```
**Solution**: Verify your Azure OpenAI API key in `.env` file

**Issue: Module Not Found**
```
ModuleNotFoundError: No module named 'agents'
```
**Solution**: Ensure all `__init__.py` files exist in subdirectories

**Issue: Vector Store Not Found**
```
Vector store not initialized
```
**Solution**: Run `python scripts/load_knowledge_base.py`

**Issue: Port Already in Use**
```
Address already in use: 8000
```
**Solution**: Kill existing process: `lsof -ti:8000 | xargs kill -9`

## 📝 License

This project is created for educational purposes as part of a hackathon.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Support

For issues or questions:
- Check the documentation in `/docs`
- Review troubleshooting guide above
- Open an issue on GitHub

## 🎯 Future Enhancements

- [ ] Multi-language support
- [ ] Parent dashboard
- [ ] Progress reports
- [ ] Social features (leaderboards)
- [ ] More financial concepts
- [ ] Video content integration
- [ ] Mobile app version
- [ ] Offline mode

## 🙏 Acknowledgments

- OpenAI for GPT-4 capabilities
- Streamlit for the amazing UI framework
- Sentence Transformers for embeddings
- FAISS for efficient vector search

---

**Built with ❤️ for financial literacy education**
