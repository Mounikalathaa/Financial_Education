# System Flow Diagrams

## 1. Quiz Generation Flow

```
┌─────────────┐
│    User     │
│  Selects    │
│  Concept    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│      Orchestrator Agent                 │
│  generate_personalized_quiz()           │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│   Step 1: Personalization Agent         │
│   gather_user_context()                 │
└──────┬──────────────────────────────────┘
       │
       ├─────► MCP Client.get_user_profile()
       │         └─► MCP Server: GET /api/user/profile
       │
       ├─────► MCP Client.get_recent_transactions()
       │         └─► MCP Server: GET /api/user/transactions
       │
       └─────► MCP Client.get_quiz_history()
                 └─► MCP Server: GET /api/user/quiz-history
       │
       ▼
┌─────────────────────────────────────────┐
│   Context Dictionary Created            │
│   • user_profile                        │
│   • age, hobbies, interests             │
│   • recent_transactions                 │
│   • quiz_history                        │
│   • concept_performance                 │
│   • spending_patterns                   │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│   Step 2: Content Generation Agent      │
│   generate_story()                      │
└──────┬──────────────────────────────────┘
       │
       ├─────► RAG Service.retrieve_knowledge()
       │         │
       │         ├─► Embed query using SentenceTransformer
       │         ├─► Search FAISS index
       │         └─► Return top-K documents
       │
       ▼
┌─────────────────────────────────────────┐
│   Build Story Prompt                    │
│   • Concept + Knowledge Base            │
│   • User Context (age, hobbies)         │
│   • Difficulty Level                    │
│   • Personalization Hints               │
└──────┬──────────────────────────────────┘
       │
       ├─────► OpenAI API (GPT-4 Turbo)
       │         └─► Generate personalized story
       │
       ▼
┌─────────────────────────────────────────┐
│   Educational Story Created             │
│   • Title                               │
│   • Content (200-400 words)             │
│   • Personalization elements            │
│   • Age-appropriate language            │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│   Step 3: Quiz Generation Agent         │
│   generate_questions()                  │
└──────┬──────────────────────────────────┘
       │
       ├─────► RAG Service.retrieve_knowledge()
       │         └─► Get concept-specific content
       │
       ▼
┌─────────────────────────────────────────┐
│   Build Question Prompt                 │
│   • Story content                       │
│   • Knowledge base                      │
│   • Number of questions (age-based)     │
│   • Difficulty level                    │
└──────┬──────────────────────────────────┘
       │
       ├─────► OpenAI API (JSON mode)
       │         └─► Generate questions array
       │
       ▼
┌─────────────────────────────────────────┐
│   Quiz Questions Created                │
│   • 3-5 questions (age-dependent)       │
│   • 4 options each (A, B, C, D)         │
│   • Correct answer marked               │
│   • Explanation for each                │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│   Step 4: Assemble Complete Quiz        │
│   Quiz Object:                          │
│   • quiz_id                             │
│   • user_id                             │
│   • concept                             │
│   • story (EducationalStory)            │
│   • questions (List[QuizQuestion])      │
│   • difficulty                          │
│   • created_at                          │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│   Return Quiz to UI                     │
└─────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│   Streamlit Displays:                   │
│   • Story in styled box                 │
│   • Questions with radio buttons        │
│   • Submit button                       │
└─────────────────────────────────────────┘
```

## 2. Quiz Evaluation Flow

```
┌─────────────┐
│    User     │
│  Submits    │
│   Answers   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│   Create QuizResponse Object            │
│   • quiz_id                             │
│   • user_id                             │
│   • answers: {question_id: answer}      │
│   • submitted_at                        │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│      Orchestrator Agent                 │
│      evaluate_quiz()                    │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│   Step 1: Evaluation Agent              │
│   evaluate()                            │
└──────┬──────────────────────────────────┘
       │
       ├─► For each question:
       │    ├─► Compare user_answer to correct_answer
       │    ├─► Add to correct_questions OR incorrect_questions
       │    └─► Continue
       │
       ▼
┌─────────────────────────────────────────┐
│   Calculate Score & Metrics             │
│   • score = correct_count               │
│   • total = question_count              │
│   • percentage = (score/total) * 100    │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│   Generate Feedback                     │
│   Based on percentage:                  │
│   • 100%: "Perfect! Financial superstar"│
│   • 80%+: "Excellent work!"             │
│   • 60%+: "Good job!"                   │
│   • 40%+: "Nice effort!"                │
│   • <40%: "Great start!"                │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│   Create QuizResult Object              │
│   • quiz_id, user_id                    │
│   • score, total_questions              │
│   • percentage                          │
│   • correct_questions[]                 │
│   • incorrect_questions[]               │
│   • feedback                            │
│   • points_earned (to be set)           │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│   Step 2: Gamification Agent            │
│   update_after_quiz()                   │
└──────┬──────────────────────────────────┘
       │
       ├─────► MCP Client.get_gamification_data()
       │         └─► Get current points, level, badges
       │
       ▼
┌─────────────────────────────────────────┐
│   Calculate Points Earned               │
│   • points_for_correct =                │
│       score * 10 points                 │
│   • completion_bonus = 50 points        │
│   • total_earned = sum                  │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│   Check Level Progression               │
│   • old_level = get_level(old_points)   │
│   • new_points = old_points + earned    │
│   • new_level = get_level(new_points)   │
│   • level_up = (old != new)             │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│   Calculate Streak                      │
│   • If last_quiz_date is yesterday:     │
│       streak += 1                       │
│   • If today: maintain streak           │
│   • If gap > 1 day: reset to 1          │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│   Check Badge Criteria                  │
│   For each badge:                       │
│   • Evaluate criteria expression        │
│   • If met and not already earned:      │
│       Add to new_badges[]               │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│   Update Gamification Data              │
│   • total_points += earned              │
│   • level = new_level                   │
│   • quizzes_completed += 1              │
│   • streak_days = new_streak            │
│   • badges.extend(new_badges)           │
│   • last_quiz_date = now()              │
└──────┬──────────────────────────────────┘
       │
       ├─────► MCP Client.update_gamification_data()
       │         └─► POST updated data
       │
       └─────► MCP Client.save_quiz_result()
                 └─► POST quiz history entry
       │
       ▼
┌─────────────────────────────────────────┐
│   Return Gamification Updates           │
│   • points_earned                       │
│   • new_total_points                    │
│   • level_up (boolean)                  │
│   • new_level (if level_up)             │
│   • new_badges[]                        │
│   • streak_days                         │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│   Merge into QuizResult                 │
│   • points_earned                       │
│   • level_up                            │
│   • new_badges                          │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│   Return QuizResult to UI               │
└─────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│   Streamlit Results Screen              │
│   • Score metrics                       │
│   • Feedback message                    │
│   • Points earned display               │
│   • Level up notification (if any)      │
│   • New badges earned (if any)          │
│   • Question-by-question review         │
│   • Feedback form                       │
└─────────────────────────────────────────┘
```

## 3. Agent Communication Pattern

```
┌──────────────────────────────────────────────────────┐
│                  Orchestrator Agent                   │
│                                                       │
│  High-level workflow coordination                    │
│  Error handling and retry logic                      │
│  Response assembly                                   │
└───────────┬──────────────────────────────────────────┘
            │
            ├─────────────────────┬─────────────────────┬──────────────────┐
            │                     │                     │                  │
            ▼                     ▼                     ▼                  ▼
┌───────────────────┐  ┌──────────────────┐  ┌─────────────────┐  ┌──────────────┐
│  Personalization  │  │ Content          │  │  Quiz           │  │ Gamification │
│     Agent         │  │ Generation       │  │ Generation      │  │   Agent      │
│                   │  │   Agent          │  │   Agent         │  │              │
│ • Gather context  │  │ • Create story   │  │ • Create Qs     │  │ • Update pts │
│ • Analyze history │  │ • Personalize    │  │ • Validate      │  │ • Check lvl  │
│ • Build profile   │  │ • Ensure accuracy│  │ • Format        │  │ • Award badge│
└─────┬─────────────┘  └────┬─────────────┘  └────┬────────────┘  └──────┬───────┘
      │                     │                      │                       │
      ▼                     ▼                      ▼                       ▼
┌──────────────┐     ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  MCP Client  │     │ RAG Service  │      │ RAG Service  │      │  MCP Client  │
│              │     │              │      │              │      │              │
│ • User data  │     │ • Vector DB  │      │ • Vector DB  │      │ • Save state │
│ • Txns       │     │ • Embeddings │      │ • Knowledge  │      │ • Update DB  │
│ • History    │     │ • Retrieval  │      │ • Search     │      │              │
└──────────────┘     └──────────────┘      └──────────────┘      └──────────────┘
```

## 4. Data Flow: MCP Server

```
┌─────────────────────────────────────────┐
│          MCP Server (FastAPI)           │
│          Port: 8000                     │
└──────────┬──────────────────────────────┘
           │
           ├─► GET /api/user/profile
           │    Input: user_id
           │    Output: UserProfile
           │    Source: users_db (in-memory)
           │
           ├─► POST /api/user/profile
           │    Input: UserProfile
           │    Output: success status
           │    Action: Create/update user
           │
           ├─► GET /api/user/transactions
           │    Input: user_id, limit
           │    Output: Transaction[]
           │    Source: transactions_db
           │    Note: Auto-generates if empty
           │
           ├─► GET /api/user/quiz-history
           │    Input: user_id
           │    Output: QuizHistory[]
           │    Source: quiz_history_db
           │
           ├─► POST /api/user/quiz-history
           │    Input: QuizHistory data
           │    Output: success status
           │    Action: Append to history
           │
           ├─► GET /api/user/gamification
           │    Input: user_id
           │    Output: GamificationData
           │    Source: gamification_db
           │    Note: Creates default if new
           │
           └─► POST /api/user/gamification/update
                Input: GamificationData
                Output: success status
                Action: Update state

┌─────────────────────────────────────────┐
│        In-Memory Data Stores            │
│  (Would be replaced with DB in prod)    │
└─────────────────────────────────────────┘
│
├─► users_db: Dict[user_id → UserProfile]
├─► transactions_db: Dict[user_id → Transaction[]]
├─► quiz_history_db: Dict[user_id → QuizHistory[]]
└─► gamification_db: Dict[user_id → GamificationData]
```

## 5. RAG Knowledge Retrieval

```
┌─────────────────────────────────────────┐
│    User Query: "saving beginner"        │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│   SentenceTransformer                   │
│   Model: all-MiniLM-L6-v2               │
│   Generate embedding vector (768-dim)   │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│   FAISS Index                           │
│   Type: IndexFlatL2                     │
│   Action: Similarity search             │
│   Return: top-K indices + distances     │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│   Retrieve Documents                    │
│   For each index:                       │
│   • Get document text                   │
│   • Get metadata (concept, difficulty)  │
│   • Filter by relevance                 │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│   Combine & Return                      │
│   Join documents with "\n\n"            │
│   Return knowledge string               │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│   Used by Content/Quiz Agents          │
│   To ground LLM generation              │
└─────────────────────────────────────────┘
```

## 6. Onboarding Flow

```
┌─────────────┐
│   User      │
│   Opens     │
│   App       │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│   Check Session State                   │
│   if not onboarding_complete:           │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│   Display Onboarding Form               │
│   • Name input                          │
│   • Age selector (6-17)                 │
│   • Hobbies multiselect                 │
│   • Interests multiselect               │
│   • Submit button                       │
└──────┬──────────────────────────────────┘
       │
       ▼ (User fills form)
┌─────────────────────────────────────────┐
│   Validate Input                        │
│   • Name not empty                      │
│   • Age in valid range                  │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│   Create UserProfile                    │
│   • user_id = "user_" + name.lower()    │
│   • Convert selections to lowercase     │
│   • Set created_at = now()              │
└──────┬──────────────────────────────────┘
       │
       ├─────► MCP Client.get_user_profile()
       │         └─► Creates profile if not exists
       │
       ▼
┌─────────────────────────────────────────┐
│   Initialize Gamification               │
│   If new user:                          │
│   • total_points = 0                    │
│   • level = "Beginner"                  │
│   • badges = []                         │
│   • streak_days = 0                     │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│   Update Session State                  │
│   • user_profile = profile              │
│   • gamification_data = gamif           │
│   • onboarding_complete = True          │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│   Redirect to Dashboard                 │
│   st.rerun()                            │
└─────────────────────────────────────────┘
```

## 7. Complete System Integration

```
                    ┌──────────────┐
                    │   Browser    │
                    │  localhost:  │
                    │     8501     │
                    └──────┬───────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │      Streamlit Application           │
        │  • Onboarding                        │
        │  • Dashboard                         │
        │  • Quiz Interface                    │
        │  • Results Display                   │
        └──────┬──────────────┬────────────────┘
               │              │
    ┌──────────▼────┐    ┌───▼──────────────┐
    │ Orchestrator  │    │   Session        │
    │    Agent      │    │   State          │
    └──────┬────────┘    └──────────────────┘
           │
    ┌──────┴──────────────────────────┐
    │                                  │
    ▼                                  ▼
┌─────────────────┐          ┌──────────────────┐
│  Agent Layer    │          │  Service Layer   │
│                 │          │                  │
│ • Personal.     │──────────│ • MCP Client     │
│ • Content       │          │ • RAG Service    │
│ • Quiz Gen      │          │                  │
│ • Evaluation    │          └────┬─────────────┘
│ • Gamification  │               │
└─────────────────┘               │
                      ┌───────────┴───────────┐
                      │                       │
                      ▼                       ▼
            ┌──────────────────┐    ┌──────────────────┐
            │   MCP Server     │    │  Vector Store    │
            │   (FastAPI)      │    │   (FAISS)        │
            │   Port: 8000     │    │                  │
            │                  │    │ • Education docs │
            │ • User DB        │    │ • Embeddings     │
            │ • Transactions   │    │ • Metadata       │
            │ • Quiz History   │    └──────────────────┘
            │ • Gamification   │
            └──────────────────┘
                      │
                      ▼
            ┌──────────────────┐
            │   External APIs  │
            │                  │
            │ • OpenAI GPT-4   │
            │ • Text Embeddings│
            └──────────────────┘
```
