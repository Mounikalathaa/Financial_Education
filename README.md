# Financial Education: Agentic Personalized Quiz Engine

A sophisticated AI-powered educational platform that generates personalized financial education content using a Hierarchical Multi-Agent System (HMAS).

## 🌟 Features

### Core Capabilities
- **🤖 Multi-Agent Architecture**: Hierarchical system with specialized agents for personalization, content generation, quiz creation, evaluation, and gamification
- **📚 RAG-Powered Knowledge**: FAISS vector store with financial education knowledge base
- **🎯 Personalization**: Content tailored to user age, interests, hobbies, and past performance
- **🎮 Gamification**: Points, levels, badges, and streak tracking
- **🔄 MCP Integration**: Multi-Controller Proxy server for user data management
- **📱 Mobile-Friendly UI**: Responsive Streamlit interface with onboarding flow

### Agent System
1. **Orchestrator Agent**: Coordinates all sub-agents and manages workflow
2. **Personalization Agent**: Gathers user context from MCP server
3. **Content Generation Agent**: Creates age-appropriate educational stories
4. **Quiz Generation Agent**: Generates contextual questions
5. **Evaluation Agent**: Grades responses and provides feedback
6. **Gamification Agent**: Manages points, levels, and badges

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Streamlit UI Layer                     │
│              (Mobile-Friendly Interface)                 │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────┐
│              Orchestrator Agent (HMAS)                   │
│  ┌──────────┬──────────┬──────────┬──────────────────┐ │
│  │Personal- │ Content  │   Quiz   │  Evaluation &    │ │
│  │ization   │Generation│Generation│  Gamification    │ │
│  └────┬─────┴────┬─────┴────┬─────┴────┬────────────┘ │
└───────┼──────────┼──────────┼──────────┼──────────────┘
        │          │          │          │
    ┌───┴───┐  ┌───┴───┐  ┌───┴───┐  ┌──┴───┐
    │ MCP   │  │  RAG  │  │  RAG  │  │ MCP  │
    │Server │  │Service│  │Service│  │Server│
    └───────┘  └───────┘  └───────┘  └──────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- OpenAI API key

### Installation

1. **Clone and navigate to project:**
```bash
cd IntelliSpend/financial_education
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
Create a `.env` file:
```bash
OPENAI_API_KEY=your_openai_api_key_here
MCP_SERVER_URL=http://localhost:8000
```

5. **Initialize knowledge base:**
```bash
python scripts/load_knowledge_base.py
```

### Running the Application

1. **Start MCP Server (Terminal 1):**
```bash
python mcp_server.py
```

2. **Start Streamlit App (Terminal 2):**
```bash
streamlit run app.py
```

3. **Access the app:**
Open browser to `http://localhost:8501`

## 📖 Usage Flow

### 1. Onboarding
- Enter name and age
- Select hobbies and interests
- System creates personalized profile

### 2. Dashboard
- View gamification stats (points, level, badges, streak)
- Browse available financial concepts
- Select topic to start quiz

### 3. Quiz Taking
- Read personalized educational story
- Answer contextual questions
- Submit for evaluation

### 4. Results & Feedback
- View score and detailed feedback
- See correct/incorrect answers with explanations
- Earn points and badges
- Provide feedback on content

## 🎮 Gamification System

### Points
- **10 points** per correct answer
- **50 points** completion bonus per quiz

### Levels
1. **Beginner** (0-100 points)
2. **Explorer** (101-300 points)
3. **Learner** (301-600 points)
4. **Expert** (601-1000 points)
5. **Master** (1001+ points)

### Badges
- 🏅 **First Steps**: Complete first quiz
- 🏅 **Perfect!**: Get 100% on a quiz
- 🏅 **Weekly Warrior**: 7-day streak
- 🏅 **Savings Star**: Master savings quizzes

## 🧠 Financial Concepts Covered

1. **Saving Money**: Importance and strategies for saving
2. **Budgeting**: Planning and managing spending
3. **Needs vs Wants**: Distinguishing essential from optional
4. **Earning Money**: Understanding income sources
5. **Compound Interest**: How money grows over time
6. **Risk & Reward**: Understanding financial risks

## 🔧 Configuration

Edit `config.yaml` to customize:
- LLM settings (model, temperature)
- Gamification rules
- Age group definitions
- Financial concepts
- MCP endpoints

## 📊 Observability

The system includes comprehensive logging:
```python
# Logs show agent orchestration flow:
INFO - Starting quiz generation for user X
INFO - Step 1: Gathering personalization context
INFO - Step 2: Generating educational story
INFO - Step 3: Generating quiz questions
INFO - Quiz evaluation complete. Score: 80%
```

## 🎯 Success Criteria Met

✅ **End-to-End Autonomous System**: Complete quiz generation and evaluation
✅ **Data Integration**: MCP server provides user profiles, transactions, quiz history
✅ **Gamification Framework**: Points, levels, badges with achievement tracking
✅ **Accuracy**: RAG-based knowledge retrieval prevents hallucinations
✅ **Bias & Fairness**: Age-appropriate, unbiased content generation
✅ **Scalability**: Modular agent architecture for easy extension

## 🎁 Bonus Features

✅ **RAG Contextualization**: FAISS vector store with educational knowledge
✅ **UI Onboarding**: Complete onboarding flow captures user persona
✅ **Basic Observability**: Comprehensive logging of agent orchestration
✅ **Feedback Loop**: Users can provide feedback on generated content

## 📁 Project Structure

```
financial_education/
├── agents/
│   ├── orchestrator.py          # Main orchestrator
│   ├── personalization_agent.py # User context gathering
│   ├── content_generation_agent.py # Story generation
│   ├── quiz_generation_agent.py    # Question generation
│   ├── evaluation_agent.py         # Answer evaluation
│   └── gamification_agent.py       # Points & badges
├── services/
│   ├── mcp_client.py            # MCP server client
│   └── rag_service.py           # Vector store & RAG
├── models/
│   └── __init__.py              # Pydantic data models
├── config/
│   └── __init__.py              # Configuration management
├── data/
│   ├── sample_users.json        # Sample user data
│   └── vector_store/            # FAISS index storage
├── scripts/
│   └── load_knowledge_base.py   # Initialize vector store
├── app.py                       # Streamlit UI
├── mcp_server.py               # FastAPI MCP server
├── config.yaml                 # Configuration file
└── requirements.txt            # Dependencies
```

## 🔐 Security Considerations

- Never commit `.env` files
- API keys stored in environment variables
- User data isolated per user_id
- Input validation on all endpoints

## 🚀 Deployment & Scalability

### Target Architecture for Production:

1. **Frontend**: Deploy Streamlit on cloud platform (Streamlit Cloud, Heroku)
2. **MCP Server**: Deploy FastAPI with proper database (PostgreSQL)
3. **Vector Store**: Use managed vector DB (Pinecone, Weaviate)
4. **LLM**: Use API-based LLM (OpenAI, Anthropic)
5. **Caching**: Redis for session management
6. **Monitoring**: Application Insights, CloudWatch
7. **Scaling**: Kubernetes for horizontal scaling

## 🤝 Contributing

This is a hackathon project demonstrating HMAS concepts for educational technology.

## 📄 License

MIT License - Feel free to use for educational purposes

## 🎓 Educational Value

This system demonstrates:
- Agentic AI architecture patterns
- RAG implementation
- Multi-agent coordination
- Personalization at scale
- Gamification in education
- API design (MCP pattern)

---

**Built with ❤️ for financial education**
