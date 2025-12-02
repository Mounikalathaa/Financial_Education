# Agent Tracing Documentation

## Overview

This project implements comprehensive tracing for the multi-agent quiz generation system. The tracing shows the complete execution flow: Orchestrator → Tool → Tool Output → Reasoning.

## Features

### 1. **Orchestrator-Level Tracing**
The `OrchestratorAgent` uses `AgentTracer` to log each phase of quiz generation:
- Phase initiation
- Agent coordination
- Reasoning and decision-making

### 2. **Tool Call Logging**
Each tool call is clearly marked with:
- 🔧 `[TOOL]` - Tool invocation
- ✓ `[OUTPUT]` - Tool results
- 🎯 `[REASONING]` - Agent reasoning based on output

### 3. **Supported Tools**
- **MCP Tools**: User profile, transactions, quiz history
- **RAG Tools**: Knowledge retrieval from vector store
- **OpenAI Tools**: Story generation, question generation

## Trace Format

Each trace entry includes:
```
[TIMESTAMP] [AGENT_NAME] Action
   → Details: {context_information}
```

### Example Trace Output

```
================================================================================
🚀 STARTING QUIZ GENERATION
User: user_john | Concept: Saving Money | Difficulty: BEGINNER
================================================================================

[Orchestrator] Initiating personalization phase | {'user_id': 'user_john', 'concept': 'Saving Money'}

🔧 [MCP TOOL] Fetching user profile for user_john
   → URL: http://localhost:8000/api/user/profile
✓ [MCP OUTPUT] Profile retrieved: John Doe, age 12
   → Hobbies: ['gaming', 'reading']
   → Interests: ['technology', 'sports']

[PersonalizationAgent] Tool output received | {'tool': 'MCP.get_user_profile', 'output_summary': {...}}

[Orchestrator] Reasoning: Difficulty determined | {'difficulty': 'beginner', 'reason': 'Based on age and quiz history'}

[Orchestrator] Initiating content generation phase | {'concept': 'Saving Money', 'difficulty': 'beginner'}

🔧 [RAG TOOL] Retrieving knowledge for: Saving Money
   → Difficulty: beginner, Age: 12
✓ [RAG OUTPUT] Retrieved 3 knowledge chunks

🔧 [OpenAI TOOL] Generating personalized story
   → Model: gpt-4o
   → Temperature: 0.7
✓ [OpenAI OUTPUT] Story generated (2847 characters)
   → Tokens used: 1234

🎯 [REASONING] Story personalized with elements: ['gaming', 'technology']

[QuizGenerationAgent] Calling generate_questions | {'tool': 'RAG.retrieve_knowledge + OpenAI.chat'}

🔧 [RAG TOOL] Retrieving knowledge for: Saving Money
✓ [RAG OUTPUT] Retrieved 3 knowledge chunks

🔧 [OpenAI TOOL] Generating 5 questions
   → Model: gpt-4o
   → Temperature: 0.7
✓ [OpenAI OUTPUT] Received 5 questions
   → Tokens used: 987

🎯 [REASONING] Successfully validated 5 questions for beginner difficulty

[Orchestrator] Quiz assembly complete | {'quiz_id': 'quiz_user_john_1234567890', 'total_components': {...}}

================================================================================
✅ QUIZ GENERATION COMPLETE
Quiz ID: quiz_user_john_1234567890
================================================================================
```

## Usage

### Viewing Traces in the Application UI

When you complete a quiz, the execution trace is automatically displayed in the results screen:

1. **Take a quiz** in the application
2. **Submit your answers**
3. **View results** - You'll see a new section called **"🔍 Behind the Scenes: How Your Quiz Was Generated"**
4. **Expand the section** to see:
   - Step-by-step agent execution flow
   - Tool calls (MCP, RAG, OpenAI)
   - Tool outputs with details
   - Agent reasoning
   - Summary metrics (total steps, agents involved, tool calls)

Each trace step shows:
- **Icon** indicating type (🔧 Tool, ✓ Output, 🎯 Reasoning, 🎭 Orchestrator)
- **Agent name** (e.g., ContentGenerationAgent, QuizGenerationAgent)
- **Action** description
- **Details** (JSON format with parameters and results)
- **Timestamp**

### Running with Tracing

1. **Via Test Script:**
   ```bash
   python test_tracing.py
   ```

2. **In Application:**
   The tracing is automatically enabled when you generate a quiz through the app.

### Viewing Trace Summary

The complete trace summary is logged at the end of quiz generation:
```python
logger.info(orchestrator.tracer.get_trace_summary())
```

### Adjusting Log Level

Control verbosity in your code:
```python
from utils.logging_utils import setup_logging

# Show all details including tool parameters
setup_logging(log_level="DEBUG")

# Show only main steps and outputs
setup_logging(log_level="INFO")
```

Or set in environment:
```bash
export LOG_LEVEL=DEBUG
python app.py
```

## Trace Components

### 1. Orchestrator Actions
- Phase initiation
- Agent coordination
- Final assembly

### 2. Tool Invocations
Each tool call logs:
- Tool name and purpose
- Input parameters
- Execution status

### 3. Tool Outputs
Results include:
- Output summary
- Key metrics (token usage, count, etc.)
- Success/error status

### 4. Reasoning
Agent decisions based on outputs:
- Why this tool was called
- How output influenced next steps
- Validation results

## Benefits

1. **Transparency**: See exactly what each agent does in both logs and UI
2. **Debugging**: Identify where issues occur with detailed trace
3. **Performance**: Track token usage and timing for optimization
4. **Understanding**: Learn how the multi-agent system works
5. **Auditing**: Complete execution history for every quiz
6. **User Education**: Show users the AI workflow in an accessible way
7. **Trust Building**: Demonstrate the sophistication of the system

## Implementation Details

### AgentTracer Class
Located in `utils/logging_utils.py`:
- `log_step()`: Record an execution step
- `get_trace_summary()`: Format complete trace
- `clear_traces()`: Reset for new session

### Integration Points
- **Orchestrator**: Main coordination logging
- **MCP Client**: External API calls
- **Content Agent**: Story generation
- **Quiz Agent**: Question generation
- **RAG Service**: Knowledge retrieval

## Best Practices

1. **Use structured logging**: Include context in details dict
2. **Mark tool boundaries**: Clear start/end of tool calls
3. **Log reasoning**: Explain why decisions were made
4. **Include metrics**: Token counts, timing, etc.
5. **Handle errors**: Log failures with context

## Future Enhancements

- [ ] Export traces to JSON for analysis
- [ ] Add timing information for each step
- [ ] Visual trace viewer in UI
- [ ] Performance metrics dashboard
- [ ] Trace comparison for optimization
