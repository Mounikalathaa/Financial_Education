# Architecture Documentation

## System Overview

The Financial Education Quiz Engine is built using a Hierarchical Multi-Agent System (HMAS) architecture, where specialized AI agents work together to create personalized educational experiences.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│                  (Streamlit Web Application)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ Onboarding   │  │  Dashboard   │  │   Quiz Interface     │ │
│  │   Flow       │  │   & Stats    │  │   & Results          │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────────┐
│                   ORCHESTRATOR AGENT                             │
│              (Coordinates All Sub-Agents)                        │
│                                                                   │
│  Responsibilities:                                                │
│  • Workflow coordination                                         │
│  • Agent communication                                           │
│  • Error handling                                                │
│  • Response assembly                                             │
└───┬───────────┬───────────┬────────────┬──────────┬────────────┘
    │           │           │            │          │
    ▼           ▼           ▼            ▼          ▼
┌────────┐ ┌────────┐ ┌─────────┐ ┌──────────┐ ┌─────────┐
│Personal│ │Content │ │  Quiz   │ │Evaluation│ │Gamifica │
│ization │ │  Gen   │ │   Gen   │ │  Agent   │ │  tion   │
│ Agent  │ │ Agent  │ │  Agent  │ │          │ │  Agent  │
└───┬────┘ └───┬────┘ └────┬────┘ └──────────┘ └────┬────┘
    │          │           │                          │
    ▼          ▼           ▼                          ▼
┌────────────────────────────────────────────────────────────┐
│                   SERVICE LAYER                             │
│  ┌──────────────┐    ┌─────────────────────────────────┐  │
│  │  MCP Client  │    │      RAG Service                │  │
│  │              │    │  ┌────────────┐  ┌───────────┐ │  │
│  │ • User Data  │    │  │   FAISS    │  │ Sentence  │ │  │
│  │ • Transactions│   │  │   Vector   │  │Transform  │ │  │
│  │ • History    │    │  │   Store    │  │   ers     │ │  │
│  │ • Gamification│   │  └────────────┘  └───────────┘ │  │
│  └──────┬───────┘    └─────────────────────────────────┘  │
└─────────┼──────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                   DATA LAYER                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ MCP Server   │  │  Vector DB   │  │   LLM API        │ │
│  │  (FastAPI)   │  │   (FAISS)    │  │  (OpenAI)        │ │
│  │              │  │              │  │                  │ │
│  │ • User DB    │  │ • Knowledge  │  │ • GPT-4 Turbo    │ │
│  │ • Transactions│ │ • Embeddings │  │ • Text Embedding │ │
│  │ • Quiz History│ │ • Metadata   │  │                  │ │
│  └──────────────┘  └──────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Agent Details

### 1. Orchestrator Agent

**Purpose**: Main coordinator that manages the entire quiz generation and evaluation pipeline.

**Responsibilities**:
- Receive user requests
- Coordinate sub-agents in proper sequence
- Handle errors and fallbacks
- Assemble final responses
- Manage state transitions

**Key Methods**:
- `generate_personalized_quiz()`: Main quiz generation workflow
- `evaluate_quiz()`: Quiz evaluation workflow
- `get_user_dashboard()`: Fetch comprehensive user data

### 2. Personalization Agent

**Purpose**: Gather and analyze user-specific context for personalization.

**Data Sources** (via MCP):
- User profile (age, hobbies, interests)
- Transaction history
- Quiz performance history
- Learning patterns

**Output**: Comprehensive user context dictionary used by other agents

**Key Features**:
- Performance analysis by concept
- Spending pattern analysis
- Mastery level determination
- Personalization vector creation

### 3. Content Generation Agent

**Purpose**: Create age-appropriate, personalized educational stories.

**Inputs**:
- Financial concept
- User context
- Difficulty level
- Knowledge base content (from RAG)

**Process**:
1. Retrieve relevant knowledge from RAG
2. Build personalized prompt with user context
3. Generate story using LLM
4. Validate age-appropriateness
5. Extract title and content

**Quality Assurance**:
- Age-appropriate vocabulary
- Bias-free content
- Accurate financial information
- Engaging narrative structure

### 4. Quiz Generation Agent

**Purpose**: Generate contextual, educational quiz questions.

**Inputs**:
- Educational story
- Financial concept
- Difficulty level
- User context

**Process**:
1. Retrieve knowledge base content
2. Analyze story for key concepts
3. Generate questions using LLM (JSON mode)
4. Validate question quality
5. Create QuizQuestion objects

**Question Types**:
- Story comprehension
- Concept application
- Scenario-based
- Definition/explanation

### 5. Evaluation Agent

**Purpose**: Grade quiz responses and provide feedback.

**Process**:
1. Compare user answers to correct answers
2. Calculate score and percentage
3. Identify correct/incorrect questions
4. Generate encouraging feedback
5. Create QuizResult object

**Feedback Strategy**:
- Always encouraging and constructive
- Specific to performance level
- Growth mindset focused
- Actionable next steps

### 6. Gamification Agent

**Purpose**: Manage points, levels, badges, and engagement mechanics.

**Responsibilities**:
- Calculate points earned
- Check for level progression
- Evaluate badge criteria
- Update streak tracking
- Persist gamification data

**Gamification Elements**:
- Points: Based on correct answers + completion
- Levels: Progressive skill tiers
- Badges: Achievement recognition
- Streaks: Consistency rewards

## Data Flow: Quiz Generation

```
1. User selects concept
         ↓
2. Orchestrator receives request
         ↓
3. Personalization Agent → MCP Server
         ↓ (user context)
4. Content Generation Agent → RAG Service → LLM
         ↓ (educational story)
5. Quiz Generation Agent → RAG Service → LLM
         ↓ (questions)
6. Orchestrator assembles Quiz
         ↓
7. UI displays story and questions
         ↓
8. User submits answers
         ↓
9. Evaluation Agent grades responses
         ↓
10. Gamification Agent updates stats → MCP Server
         ↓
11. UI displays results and feedback
```

## MCP Server Architecture

The Multi-Controller Proxy (MCP) server provides a clean API layer for all user data:

**Endpoints**:
- `GET /api/user/profile` - Get user profile
- `POST /api/user/profile` - Create/update profile
- `GET /api/user/transactions` - Get transaction history
- `GET /api/user/quiz-history` - Get quiz history
- `GET /api/user/gamification` - Get gamification data
- `POST /api/user/gamification/update` - Update gamification
- `POST /api/user/quiz-history` - Save quiz result

**Benefits**:
- Data abstraction layer
- Easy to swap data sources
- Centralized data management
- API-first design for future mobile apps

## RAG (Retrieval-Augmented Generation)

### Vector Store Architecture

**Components**:
1. **FAISS Index**: Efficient similarity search
2. **Sentence Transformers**: Generate embeddings
3. **Metadata Store**: Document metadata (concept, difficulty, age)

**Knowledge Base**:
- 10+ financial education documents
- Categorized by concept and difficulty
- Age-appropriate content levels
- Regularly updated and expanded

**Retrieval Process**:
1. User query → Embed query
2. Search FAISS index for similar documents
3. Retrieve top-K most relevant
4. Combine and return to agents

**Benefits**:
- Prevents LLM hallucinations
- Ensures accurate information
- Contextual content generation
- Scalable knowledge base

## Security Considerations

1. **API Keys**: Stored in environment variables
2. **User Data**: Isolated per user_id
3. **Input Validation**: All user inputs validated
4. **Error Handling**: Graceful fallbacks
5. **Rate Limiting**: Prevent abuse (production)

## Scalability Strategy

### Current Architecture (Prototype)
- Single server
- In-memory data storage
- Local vector store
- Synchronous processing

### Production Architecture
1. **Horizontal Scaling**:
   - Multiple Streamlit instances (load balanced)
   - Multiple MCP server instances
   - Distributed vector store (Pinecone, Weaviate)

2. **Data Layer**:
   - PostgreSQL for user data
   - Redis for caching
   - S3 for vector store backups

3. **Async Processing**:
   - Celery for background tasks
   - RabbitMQ message queue
   - Async LLM calls

4. **Monitoring**:
   - Application Insights
   - CloudWatch metrics
   - Error tracking (Sentry)
   - Performance monitoring

5. **CDN & Caching**:
   - Static assets via CDN
   - Response caching for common queries
   - Vector store query caching

## Technology Stack

- **Frontend**: Streamlit (Python)
- **Backend**: FastAPI (Python)
- **LLM**: OpenAI GPT-4 Turbo
- **Embeddings**: OpenAI text-embedding-3-small
- **Vector Store**: FAISS
- **Data Models**: Pydantic
- **Configuration**: YAML + Environment Variables
- **Logging**: Python logging + colorlog

## Extension Points

The architecture supports easy extension:

1. **New Agents**: Add specialized agents (e.g., AdaptiveDifficultyAgent)
2. **New Concepts**: Add financial concepts to knowledge base
3. **New Data Sources**: Implement new MCP endpoints
4. **New LLMs**: Swap OpenAI for Anthropic, etc.
5. **New UI**: Build mobile app using same MCP API
6. **A/B Testing**: Add experimentation framework
7. **Analytics**: Add comprehensive tracking
