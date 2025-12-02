# Agno Team Format Migration Guide

## Overview

This document explains the migration from custom orchestrator pattern to Agno's Team-based multi-agent framework.

## What is Agno?

Agno is a high-performance multi-agent framework that provides:
- **Team Structure**: Hierarchical agent coordination with team leaders
- **Agent Specialization**: Each agent has a specific role and responsibilities
- **Native Tools**: Built-in MCP support, RAG, memory, and 100+ toolkits
- **Production Runtime**: Ready-to-use FastAPI app (AgentOS) for serving agents
- **Performance**: 529× faster instantiation than LangGraph, 24× lower memory

## Team Structure

### Original Custom Orchestrator
```
OrchestratorAgent
├── PersonalizationAgent
├── ContentGenerationAgent
├── QuizGenerationAgent
├── EvaluationAgent
└── GamificationAgent
```

### Agno Team Structure
```
Educational Quiz Team (Team Leader - GPT-4)
├── Personalization Agent
│   └── Gathers user context and preferences
├── Content Generation Team (Sub-team)
│   ├── Story Generator Agent
│   │   └── Creates educational stories using RAG
│   └── Quiz Generator Agent
│       └── Generates quiz questions from stories
├── Evaluation Agent
│   └── Scores quiz and provides feedback
└── Gamification Agent
    └── Updates points, levels, badges
```

## Key Differences

### 1. Hierarchical Delegation

**Before (Custom):**
```python
# Direct sequential calls
context = await self.personalization_agent.gather_user_context(user_id, concept)
story = await self.content_agent.generate_story(concept, user_context, difficulty)
questions = await self.quiz_agent.generate_questions(concept, story, difficulty, user_context)
```

**After (Agno Team):**
```python
# Team leader delegates tasks to members
team = Team(
    name="Educational Quiz Team",
    members=[personalization_agent, content_team, evaluation_agent, gamification_agent],
    instructions="Coordinate quiz generation workflow..."
)

# Team automatically delegates based on agent roles
response = team.run(f"Generate quiz for user {user_id} on concept {concept}")
```

### 2. Agent Definition

**Before (Custom):**
```python
class PersonalizationAgent:
    def __init__(self, mcp_client):
        self.mcp_client = mcp_client
    
    async def gather_user_context(self, user_id, concept):
        # Implementation...
```

**After (Agno Agent):**
```python
personalization_agent = Agent(
    id="personalization-agent",
    name="Personalization Agent",
    role="Gather user profile, quiz history, and learning preferences",
    instructions="""
    You are responsible for:
    1. Fetching user profile data
    2. Retrieving quiz history
    3. Analyzing preferences
    4. Providing comprehensive user context
    """,
    tools=[MCPTools(url="http://localhost:8000")]  # MCP integration
)
```

### 3. Sub-Teams

**Agno Advantage:** You can create sub-teams for related functionality:

```python
content_generation_team = Team(
    name="Content Generation Team",
    members=[story_generator_agent, quiz_generator_agent],
    instructions="Coordinate story and quiz creation..."
)

# Use sub-team as a member of main team
main_team = Team(
    name="Educational Quiz Team",
    members=[personalization_agent, content_generation_team, evaluation_agent],
    ...
)
```

## Implementation Approaches

### Approach 1: Hybrid (Current Implementation)

Keep existing agent logic, wrap with Agno Team structure:

```python
class AgnoOrchestratorTeam:
    def __init__(self, mcp_client, rag_service):
        # Keep existing agents
        self.personalization_agent = PersonalizationAgent(mcp_client)
        self.content_agent = ContentGenerationAgent(rag_service)
        
        # Create Agno Team for structure/coordination
        self.team = Team(
            members=[agno_personalization, agno_content, ...],
            instructions="Coordinate workflow..."
        )
        
    async def generate_personalized_quiz(self, user_id, concept):
        # Still call existing agents directly
        # But log with [Agno Team] prefix for tracking
        context = await self.personalization_agent.gather_user_context(...)
```

**Pros:**
- Minimal changes to existing code
- Gradual migration path
- Team structure documented

**Cons:**
- Not using Agno's full capabilities
- Still manual coordination

### Approach 2: Full Agno Migration (Future)

Migrate all agent logic to Agno agents with tools:

```python
# Create tools for existing logic
class PersonalizationTools:
    @tool
    async def get_user_profile(self, user_id: str) -> UserProfile:
        """Fetch user profile from MCP server."""
        return await mcp_client.get_user_profile(user_id)
    
    @tool
    async def get_quiz_history(self, user_id: str) -> List[QuizHistory]:
        """Fetch user's quiz history."""
        return await mcp_client.get_quiz_history(user_id)

# Create Agno agent with tools
personalization_agent = Agent(
    name="Personalization Agent",
    role="Gather user context",
    tools=[PersonalizationTools()],
    instructions="Use tools to gather comprehensive user context..."
)

# Let team handle coordination
team = Team(members=[personalization_agent, ...])
result = team.run(f"Generate quiz for {user_id} on {concept}")
```

**Pros:**
- Full Agno benefits (parallelization, smart delegation)
- Native MCP integration
- Built-in monitoring via AgentOS UI
- Better performance

**Cons:**
- Significant refactoring required
- Learning curve for team

## Migration Roadmap

### Phase 1: Structure (✅ Complete)
- [x] Install Agno framework
- [x] Create `orchestrator_agno.py` with Team structure
- [x] Define all agents with roles and instructions
- [x] Create Content Generation sub-team
- [x] Document team hierarchy

### Phase 2: Hybrid Implementation (Current)
- [x] Wrap existing agents with Agno Team
- [x] Add [Agno Team] logging for tracking
- [ ] Test quiz generation flow
- [ ] Verify all agents working correctly

### Phase 3: Tool Integration (Future)
- [ ] Create PersonalizationTools for MCP client
- [ ] Create RAGTools for knowledge retrieval
- [ ] Create EvaluationTools for scoring
- [ ] Create GamificationTools for updates
- [ ] Integrate MCP server as tool provider

### Phase 4: Full Migration (Future)
- [ ] Migrate PersonalizationAgent to pure Agno
- [ ] Migrate ContentGenerationAgent to pure Agno
- [ ] Migrate QuizGenerationAgent to pure Agno
- [ ] Migrate EvaluationAgent to pure Agno
- [ ] Migrate GamificationAgent to pure Agno
- [ ] Let Team handle full coordination

### Phase 5: Production (Future)
- [ ] Deploy with AgentOS runtime
- [ ] Connect AgentOS UI for monitoring
- [ ] Add team-level memory and knowledge
- [ ] Implement human-in-the-loop for quiz review
- [ ] Add guardrails for content safety

## Benefits of Agno Team Format

### 1. Clear Role Definition
Each agent has explicit `role` and `instructions` defining their responsibilities.

### 2. Automatic Delegation
Team leader automatically delegates tasks based on:
- Agent roles and capabilities
- User request intent
- Current context

### 3. Sub-Team Modularity
Group related agents (Story + Quiz Generator) into sub-teams for better organization.

### 4. Built-in Features
- **Memory**: Agents remember user interactions
- **Knowledge**: Integrated RAG with 20+ vector stores
- **MCP Tools**: First-class Model Context Protocol support
- **Monitoring**: AgentOS UI for real-time debugging
- **Performance**: Optimized for production scale

### 5. Production Ready
AgentOS provides:
- FastAPI app out of the box
- Stateless, horizontally scalable
- SSE-compatible streaming endpoints
- RBAC and access control
- Private by design (runs in your cloud)

## Usage Examples

### Generate Quiz with Agno Team

```python
from agents.orchestrator_agno import AgnoOrchestratorTeam

# Initialize team
team_orchestrator = AgnoOrchestratorTeam(mcp_client, rag_service)

# View team structure
print(team_orchestrator.get_team_structure())

# Generate quiz (hybrid approach)
quiz = await team_orchestrator.generate_personalized_quiz(
    user_id="user_123",
    concept="banking",
    difficulty=DifficultyLevel.INTERMEDIATE
)

# Evaluate quiz
result = await team_orchestrator.evaluate_quiz(quiz, response)
```

### Direct Team Interaction (Future)

```python
# Once fully migrated, use team.run() directly
team = team_orchestrator.team

# Team handles full workflow
response = team.run(
    f"Generate a personalized {difficulty} quiz about {concept} "
    f"for user {user_id} who is {age} years old and likes {hobbies}"
)

# Streaming support
for chunk in team.run(..., stream=True):
    print(chunk.content, end="", flush=True)
```

## Testing

### Current (Hybrid)
```bash
# Use existing test suite
python -m pytest tests/test_orchestrator.py

# Both orchestrators should work identically
from agents.orchestrator import OrchestratorAgent  # Original
from agents.orchestrator_agno import AgnoOrchestratorTeam  # Agno version
```

### Future (Full Agno)
```bash
# Use Agno's built-in testing
from agno.team import Team

team = Team(...)
team.print_response("Generate quiz about banking", show_members_responses=True)

# Monitor in AgentOS UI
# Visit: https://os.agno.com/
```

## Resources

- **Agno Documentation**: https://docs.agno.com/
- **Team Building Guide**: https://docs.agno.com/basics/teams/building-teams
- **Agno GitHub**: https://github.com/agno-agi/agno
- **Examples**: https://github.com/agno-agi/agno/tree/main/cookbook/teams
- **Community**: https://community.agno.com/
- **Discord**: https://discord.gg/4MtYHHrgA8

## Conclusion

The Agno Team format provides:
1. **Better organization** through hierarchical teams
2. **Clearer responsibilities** with explicit roles
3. **Production readiness** with AgentOS runtime
4. **Native integrations** (MCP, RAG, monitoring)
5. **Superior performance** (529× faster than alternatives)

Current hybrid approach maintains stability while documenting the team structure. Future full migration will unlock Agno's complete capabilities for production deployment.
