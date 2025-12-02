# Testing Guide

## Manual Testing Checklist

### 1. Environment Setup Testing

- [ ] Virtual environment activates successfully
- [ ] All dependencies install without errors
- [ ] `.env` file is properly configured
- [ ] Knowledge base loads successfully (10 documents)
- [ ] MCP server starts on port 8000
- [ ] Streamlit app starts on port 8501

### 2. Onboarding Flow Testing

#### Test Case 1: New User Registration
**Steps:**
1. Open app in browser
2. Enter name: "TestUser"
3. Select age: 12
4. Choose hobbies: "Video Games", "Sports"
5. Choose interests: "Technology", "Space"
6. Click "Start Learning!"

**Expected Results:**
- ✅ User profile created successfully
- ✅ Redirected to dashboard
- ✅ Level shows "Beginner"
- ✅ Points show 0
- ✅ Name displays correctly

#### Test Case 2: Invalid Input Handling
**Steps:**
1. Leave name blank
2. Try to submit

**Expected Results:**
- ✅ Form validation prevents submission
- ✅ Error message displayed

### 3. Dashboard Testing

#### Test Case 3: Dashboard Display
**Steps:**
1. After onboarding, view dashboard

**Expected Results:**
- ✅ User name displayed in greeting
- ✅ Level badge shows "Beginner"
- ✅ Four metric cards display (Points, Quizzes, Streak, Perfect)
- ✅ Six concept cards displayed
- ✅ All cards clickable

#### Test Case 4: Concept Selection
**Steps:**
1. Click "Start Quiz: Saving Money"

**Expected Results:**
- ✅ Loading spinner appears
- ✅ Quiz generation takes 10-15 seconds
- ✅ Redirected to quiz interface

### 4. Quiz Generation Testing

#### Test Case 5: Personalized Story Generation
**Steps:**
1. Generate quiz for user with hobbies "video games"
2. Read story content

**Expected Results:**
- ✅ Story mentions video games or related themes
- ✅ Story is age-appropriate for selected age
- ✅ Story teaches the selected financial concept
- ✅ Title is creative and relevant
- ✅ Content is 200-400 words

#### Test Case 6: Question Generation
**Steps:**
1. View questions after story

**Expected Results:**
- ✅ 3-5 questions displayed (based on age)
- ✅ Each question has 4 options (A, B, C, D)
- ✅ Questions relate to story and concept
- ✅ Language is age-appropriate
- ✅ Questions are clear and unambiguous

### 5. Quiz Taking Testing

#### Test Case 7: Answer Selection
**Steps:**
1. Select answers for all questions
2. Verify submit button enables

**Expected Results:**
- ✅ Radio buttons work correctly
- ✅ Selected answers highlighted
- ✅ Submit button disabled until all answered
- ✅ Submit button enables when complete

#### Test Case 8: Quiz Submission
**Steps:**
1. Answer all questions (mix of correct/incorrect)
2. Click "Submit Quiz"

**Expected Results:**
- ✅ Loading spinner appears
- ✅ Evaluation completes in < 5 seconds
- ✅ Redirected to results screen

### 6. Results & Evaluation Testing

#### Test Case 9: Score Display
**Steps:**
1. View results after submission

**Expected Results:**
- ✅ Score displayed (e.g., "3/5")
- ✅ Percentage calculated correctly
- ✅ Points earned displayed
- ✅ Feedback message appropriate to score

#### Test Case 10: Perfect Score
**Steps:**
1. Take quiz and answer all correctly

**Expected Results:**
- ✅ Score shows 100%
- ✅ Feedback: "Perfect score! Financial superstar!"
- ✅ "Perfect!" badge earned
- ✅ Celebration effect (balloons)

#### Test Case 11: Level Up
**Steps:**
1. Complete multiple quizzes to reach 101 points

**Expected Results:**
- ✅ Level up notification displayed
- ✅ Level badge changes to "Explorer"
- ✅ Celebration effect shown

#### Test Case 12: Streak Tracking
**Steps:**
1. Complete quiz today
2. Check streak counter
3. Complete another quiz next day

**Expected Results:**
- ✅ Streak shows 1 on first day
- ✅ Streak increments to 2 on consecutive day
- ✅ Streak resets if day is skipped

### 7. Gamification Testing

#### Test Case 13: Points Calculation
**Steps:**
1. Answer quiz with 3/5 correct

**Expected Results:**
- ✅ Points earned: (3 × 10) + 50 = 80 points
- ✅ Total points updated in dashboard
- ✅ Calculation shown in results

#### Test Case 14: Badge Awards
**Steps:**
1. Complete first quiz → Check for "First Steps" badge
2. Get 100% score → Check for "Perfect!" badge

**Expected Results:**
- ✅ Badges awarded immediately
- ✅ Badge notification shown
- ✅ Badges visible in dashboard

### 8. MCP Server Testing

#### Test Case 15: User Profile API
**Steps:**
```bash
curl "http://localhost:8000/api/user/profile?user_id=test_user"
```

**Expected Results:**
- ✅ Returns user profile JSON
- ✅ Status code: 200
- ✅ Contains user_id, name, age, hobbies

#### Test Case 16: Transactions API
**Steps:**
```bash
curl "http://localhost:8000/api/user/transactions?user_id=test_user&limit=5"
```

**Expected Results:**
- ✅ Returns transactions array
- ✅ Status code: 200
- ✅ Auto-generates if none exist

#### Test Case 17: Gamification API
**Steps:**
```bash
curl "http://localhost:8000/api/user/gamification?user_id=test_user"
```

**Expected Results:**
- ✅ Returns gamification data
- ✅ Includes points, level, badges, streak

### 9. RAG System Testing

#### Test Case 18: Knowledge Retrieval
**Steps:**
1. Generate quiz for "Saving Money" concept
2. Check story includes accurate information

**Expected Results:**
- ✅ Story includes facts from knowledge base
- ✅ No hallucinated information
- ✅ Concepts explained correctly

#### Test Case 19: Vector Store Loading
**Steps:**
```bash
python scripts/load_knowledge_base.py
```

**Expected Results:**
- ✅ Loads 10 documents
- ✅ Creates FAISS index
- ✅ Saves to disk successfully
- ✅ No errors during embedding

### 10. Error Handling Testing

#### Test Case 20: MCP Server Down
**Steps:**
1. Stop MCP server
2. Try to generate quiz

**Expected Results:**
- ✅ System uses fallback data
- ✅ Error logged but doesn't crash
- ✅ User sees graceful error message

#### Test Case 21: Invalid API Key
**Steps:**
1. Set invalid OpenAI API key
2. Try to generate quiz

**Expected Results:**
- ✅ Error caught and logged
- ✅ User-friendly error message
- ✅ System doesn't crash

#### Test Case 22: Network Timeout
**Steps:**
1. Simulate slow network
2. Generate quiz

**Expected Results:**
- ✅ Loading indicator shows
- ✅ Request eventually completes or times out gracefully
- ✅ Clear error message if timeout

### 11. Feedback System Testing

#### Test Case 23: Feedback Submission
**Steps:**
1. Complete quiz
2. Rate 5 stars
3. Select "Just Right" difficulty
4. Enter comments
5. Submit feedback

**Expected Results:**
- ✅ Feedback saved successfully
- ✅ Success message displayed
- ✅ Feedback stored in data/feedback.json

### 12. Multi-User Testing

#### Test Case 24: Multiple Users
**Steps:**
1. Create user "Alice", age 8
2. Complete quiz
3. Logout
4. Create user "Bob", age 15
5. Complete quiz

**Expected Results:**
- ✅ Each user has separate profile
- ✅ Points tracked separately
- ✅ Story difficulty differs (age-based)
- ✅ Question count differs (3 for Alice, 5 for Bob)

### 13. Performance Testing

#### Test Case 25: Quiz Generation Time
**Steps:**
1. Generate 5 quizzes in sequence
2. Measure time for each

**Expected Results:**
- ✅ Each quiz generates in 10-15 seconds
- ✅ No degradation over multiple requests
- ✅ Memory usage remains stable

#### Test Case 26: Concurrent Users
**Steps:**
1. Open app in 3 browser tabs
2. Create different users in each
3. Generate quizzes simultaneously

**Expected Results:**
- ✅ All quizzes generate successfully
- ✅ No conflicts or errors
- ✅ Data isolated per user

## Automated Testing

### Unit Tests

Create `tests/test_agents.py`:

```python
import pytest
from agents.evaluation_agent import EvaluationAgent
from models import Quiz, QuizResponse, QuizQuestion, DifficultyLevel

def test_evaluation_agent():
    agent = EvaluationAgent()
    
    # Create mock quiz
    quiz = Quiz(
        quiz_id="test_quiz",
        user_id="test_user",
        concept="saving",
        story=None,
        questions=[
            QuizQuestion(
                question_id="q1",
                question_text="Test?",
                options=["A) 1", "B) 2"],
                correct_answer="A) 1",
                explanation="Because",
                difficulty=DifficultyLevel.BEGINNER
            )
        ],
        difficulty=DifficultyLevel.BEGINNER
    )
    
    # Create response
    response = QuizResponse(
        quiz_id="test_quiz",
        user_id="test_user",
        answers={"q1": "A) 1"}
    )
    
    # Evaluate
    result = await agent.evaluate(quiz, response)
    
    assert result.score == 1
    assert result.percentage == 100.0
    assert len(result.correct_questions) == 1
```

### Integration Tests

Create `tests/test_integration.py`:

```python
import pytest
from agents.team_orchestrator import TeamOrchestrator
from services.mcp_client import MCPClient
from services.rag_service import RAGService

@pytest.mark.asyncio
async def test_full_quiz_flow():
    mcp_client = MCPClient()
    rag_service = RAGService()
    orchestrator = TeamOrchestrator(mcp_client, rag_service)
    
    # Generate quiz
    quiz = await orchestrator.generate_personalized_quiz(
        user_id="test_user",
        concept="saving"
    )
    
    assert quiz is not None
    assert quiz.concept == "saving"
    assert len(quiz.questions) > 0
    assert quiz.story is not None
```

### Run Tests

```bash
# Install pytest
pip install pytest pytest-asyncio

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_agents.py -v

# Run with coverage
pytest tests/ --cov=agents --cov=services
```

## Load Testing

### Using Locust

Create `locustfile.py`:

```python
from locust import HttpUser, task, between

class QuizUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def get_profile(self):
        self.client.get("/api/user/profile?user_id=test_user")
    
    @task
    def get_transactions(self):
        self.client.get("/api/user/transactions?user_id=test_user&limit=10")
```

Run load test:
```bash
locust -f locustfile.py --host=http://localhost:8000
```

## Regression Testing Checklist

Before each release:

- [ ] All manual test cases pass
- [ ] Unit tests pass (100% of existing tests)
- [ ] Integration tests pass
- [ ] No new errors in logs
- [ ] Performance benchmarks met
- [ ] Security scan clean
- [ ] Documentation updated

## Known Issues & Limitations

1. **In-Memory Storage**: Data lost on server restart (by design for demo)
2. **No Authentication**: Anyone can access any user's data
3. **Rate Limiting**: Not implemented (could hit OpenAI limits)
4. **Error Recovery**: Some edge cases may not be handled
5. **Offline Mode**: Requires internet connection

## Bug Reporting Template

When reporting issues:

```markdown
**Title**: Brief description

**Environment**:
- OS: macOS/Windows/Linux
- Python version: 3.11
- Browser: Chrome 120

**Steps to Reproduce**:
1. Step one
2. Step two
3. Step three

**Expected Behavior**:
What should happen

**Actual Behavior**:
What actually happened

**Screenshots**:
If applicable

**Logs**:
Relevant error messages
```

## Testing Best Practices

1. **Test Early**: Start testing as you build
2. **Test Often**: Run tests after each change
3. **Test Realistically**: Use real user scenarios
4. **Test Edge Cases**: Empty inputs, max values, etc.
5. **Document Issues**: Track bugs systematically
6. **Automate**: Use automated tests where possible

---

**Happy Testing! 🧪**
