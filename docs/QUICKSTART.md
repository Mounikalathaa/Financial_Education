# Quick Start Guide

Get up and running with the Financial Education Quiz Engine in under 5 minutes!

## Prerequisites

- **Python 3.9 or higher**
- **OpenAI API key** (get one at [platform.openai.com](https://platform.openai.com))
- **Terminal/Command Line** access
- **Modern web browser**

## Installation Steps

### 1. Navigate to Project

```bash
cd IntelliSpend/financial_education
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR on Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Streamlit for UI
- OpenAI for LLM
- FAISS for vector store
- FastAPI for MCP server
- And more...

### 4. Configure Environment

Create a `.env` file in the project root:

```bash
touch .env
```

Add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
MCP_SERVER_URL=http://localhost:8000
```

### 5. Initialize Knowledge Base

Load financial education content into the vector store:

```bash
python scripts/load_knowledge_base.py
```

You should see:
```
Adding documents to vector store...
Saving index to disk...
✅ Successfully loaded 10 documents into vector store!
```

### 6. Start the Application

#### Option A: Manual Start (Recommended for first time)

**Terminal 1 - Start MCP Server:**
```bash
python mcp_server.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 - Start Streamlit UI:**
```bash
streamlit run app.py
```

The browser should automatically open to `http://localhost:8501`

#### Option B: Automated Start (macOS/Linux)

```bash
chmod +x start.sh
./start.sh
```

This script will:
- Check dependencies
- Start MCP server
- Start Streamlit UI
- Open browser automatically

## First Time Usage

### 1. Complete Onboarding

When you first open the app, you'll see the onboarding screen:

1. **Enter your name**: e.g., "Alex"
2. **Enter your age**: e.g., 12
3. **Select hobbies**: Choose from the list (e.g., "Video Games", "Sports")
4. **Select interests**: Choose topics you like (e.g., "Technology", "Space")
5. Click **"Start Learning! 🚀"**

### 2. Explore Dashboard

After onboarding, you'll see:
- Your level and points
- Number of quizzes completed
- Current streak
- Available badges
- Financial concepts to learn

### 3. Start Your First Quiz

1. Click on any concept card (e.g., "Saving Money")
2. Wait while the system generates your personalized quiz (~10-15 seconds)
3. Read the educational story
4. Answer all questions
5. Click "Submit Quiz"

### 4. View Results

After submitting:
- See your score
- Earn points and possibly level up!
- Review correct/incorrect answers
- Provide feedback
- Try another quiz or retake

## Troubleshooting

### Issue: "Import error" or "Module not found"

**Solution**: Make sure you activated the virtual environment and installed dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "Invalid API key"

**Solution**: Check your `.env` file has correct OpenAI API key:
```bash
cat .env  # Should show OPENAI_API_KEY=sk-...
```

### Issue: "Connection refused" or "MCP server not available"

**Solution**: Make sure MCP server is running:
```bash
# In Terminal 1
python mcp_server.py
```

Wait for "Uvicorn running on..." message before starting Streamlit.

### Issue: "No documents in index"

**Solution**: Run the knowledge base loader:
```bash
python scripts/load_knowledge_base.py
```

### Issue: Port already in use

**Solution**: Kill existing processes:
```bash
# Kill process on port 8000 (MCP server)
lsof -ti:8000 | xargs kill -9

# Kill process on port 8501 (Streamlit)
lsof -ti:8501 | xargs kill -9
```

## Testing the System

### Quick Test Flow

1. **Onboarding**: Create user "TestUser", age 10
2. **Dashboard**: Verify you see level "Beginner" with 0 points
3. **Quiz**: Select "Saving Money" concept
4. **Story**: Verify personalized story appears
5. **Questions**: Answer all questions (try getting some right and some wrong)
6. **Results**: Verify you see score, earned points, and feedback
7. **Dashboard**: Return to dashboard and verify points updated

### Expected Results

- Story should reference user's hobbies/interests if provided
- Questions should be age-appropriate (simpler for younger ages)
- Correct answers earn 10 points each
- Quiz completion earns 50 bonus points
- Perfect score earns "Perfect!" badge

## API Testing

You can test the MCP server directly:

```bash
# Test health check
curl http://localhost:8000/

# Test user profile
curl "http://localhost:8000/api/user/profile?user_id=test_user"

# Test transactions
curl "http://localhost:8000/api/user/transactions?user_id=test_user&limit=5"
```

## Next Steps

### Customize Content

1. **Add new financial concepts**: Edit `config.yaml`
2. **Add knowledge base content**: Edit `scripts/load_knowledge_base.py`
3. **Customize gamification**: Edit `config.yaml` gamification section
4. **Change UI styling**: Edit CSS in `app.py`

### Advanced Features

- **Add more agents**: Create new agent files in `agents/` directory
- **Integrate real databases**: Replace in-memory storage in MCP server
- **Add analytics**: Implement tracking in UI
- **Deploy to cloud**: Use Streamlit Cloud or Heroku

## Architecture Overview

```
User Browser
     ↓
Streamlit UI (Port 8501)
     ↓
Orchestrator Agent
     ↓
├─ Personalization Agent → MCP Server (Port 8000)
├─ Content Agent → RAG Service (FAISS)
├─ Quiz Agent → RAG Service (FAISS)
├─ Evaluation Agent
└─ Gamification Agent → MCP Server (Port 8000)
```

## Getting Help

### Check Logs

Logs appear in the terminal where you started each service. Look for:
- `ERROR` messages for problems
- `INFO` messages for normal operations
- `WARNING` messages for potential issues

### Common Questions

**Q: How long does quiz generation take?**
A: Typically 10-15 seconds. Depends on OpenAI API response time.

**Q: How many quizzes can I take?**
A: Unlimited! Each quiz is dynamically generated.

**Q: Are quizzes always different?**
A: Yes, quizzes are personalized based on your profile and performance.

**Q: What concepts are covered?**
A: Saving, Budgeting, Needs vs Wants, Earning, Compound Interest, Risk & Reward.

**Q: Can multiple users use the app?**
A: Yes, each user has separate profile and progress.

## Demo Mode

For quick demonstrations, sample users are pre-loaded:
- `user_demo` (Alex, age 12)
- `user_sarah` (Sarah, age 9)
- `user_mike` (Mike, age 15)

You can create new users through the onboarding flow.

## Performance Tips

1. **Pre-load knowledge base**: Run `load_knowledge_base.py` before demos
2. **Keep MCP server running**: Don't restart between quizzes
3. **Use consistent API key**: Avoid rate limits by using one key
4. **Clear browser cache**: If UI acts strangely, clear cache

## Production Considerations

Before deploying to production:

1. ✅ Replace in-memory storage with real database
2. ✅ Add authentication and authorization
3. ✅ Implement rate limiting
4. ✅ Add comprehensive error handling
5. ✅ Set up monitoring and alerting
6. ✅ Use environment-specific configs
7. ✅ Enable HTTPS
8. ✅ Add data backup strategy

## Success!

If you see the Streamlit UI with the onboarding screen, you're all set! 🎉

Enjoy teaching financial literacy with AI! 💰📚
