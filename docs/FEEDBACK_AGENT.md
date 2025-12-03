# 🔄 Feedback Agent - Bias Detection & Knowledge Base Improvement

## Overview

The Feedback Agent is an intelligent system that collects user feedback after quiz completion, analyzes it for potential biases, and automatically updates the knowledge base to ensure inclusive, high-quality educational content.

## 🎯 Key Features

### 1. **Comprehensive Feedback Collection**
- **Rating System**: 1-5 star overall rating
- **Difficulty Perception**: Too easy, just right, or too hard
- **Relevance Score**: How well the story related to user interests (1-5)
- **Open Comments**: Free-form text feedback

### 2. **Intelligent Bias Detection**
The agent uses GPT-4 to analyze feedback for multiple types of bias:
- **Gender Bias**: Stereotyping or gender exclusion
- **Cultural Bias**: Cultural insensitivity or exclusion
- **Age Appropriateness**: Content suitability issues
- **Stereotypes**: Harmful stereotyping
- **Accessibility**: Content accessibility concerns
- **Economic Bias**: Assumptions about economic backgrounds

### 3. **Automated Knowledge Base Updates**
When bias is detected with medium or high severity:
- Generates improved, inclusive content using AI
- Addresses all identified bias types
- Creates content for all difficulty levels
- Automatically adds to the vector store
- Saves changes permanently

### 4. **Actionable Insights**
The system takes specific actions based on feedback:
- `flagged_for_review`: Low ratings (<= 2 stars)
- `urgent_bias_review`: Medium/high severity bias detected
- `knowledge_base_updated`: Content automatically improved
- `difficulty_adjustment_needed`: Difficulty perception mismatches
- `personalization_improvement_needed`: Low relevance scores

## 📋 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Submits Quiz                     │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Feedback Collection Form                    │
│  • Overall Rating (1-5)                                  │
│  • Difficulty Perception                                 │
│  • Relevance Score (1-5)                                 │
│  • Comments (optional)                                   │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                   Feedback Agent                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │  1. Collect Feedback → QuizFeedback Model         │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  2. Analyze Bias (GPT-4)                          │  │
│  │     • Gender, Cultural, Economic, etc.            │  │
│  │     • Severity: Low/Medium/High                   │  │
│  │     • Specific Issues & Recommendations           │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  3. Process Feedback                              │  │
│  │     • Check for low ratings                       │  │
│  │     • Check for bias                              │  │
│  │     • Check difficulty/relevance mismatches       │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  4. Update Knowledge Base (if needed)             │  │
│  │     • Generate bias-free content                  │  │
│  │     • Add to FAISS vector store                   │  │
│  │     • Save permanently                            │  │
│  └───────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              User Sees Results & Actions                 │
│  • Bias analysis (if any)                                │
│  • Actions taken                                         │
│  • Knowledge base updated confirmation                   │
└─────────────────────────────────────────────────────────┘
```

## 💻 Usage

### In the Application

After completing a quiz, users are automatically presented with a feedback form:

```python
# The feedback form appears in the results screen
# Users can:
1. Rate the quiz (1-5 stars)
2. Indicate difficulty perception
3. Rate story relevance
4. Provide optional comments

# Upon submission:
- Feedback is analyzed for bias
- Knowledge base is updated if needed
- User sees transparent results
```

### Viewing Insights

Run the insights script to see aggregated feedback data:

```bash
python scripts/view_feedback_insights.py
```

This displays:
- Overall statistics
- Rating distribution
- Bias detection summary
- Difficulty perception analysis
- Concept-level feedback
- Recent comments

## 🔧 Technical Implementation

### Models

**BiasAnalysis**
```python
class BiasAnalysis(BaseModel):
    has_bias: bool
    bias_types: List[str]  # ["gender", "cultural", etc.]
    severity: str  # "low", "medium", "high"
    specific_issues: List[str]
    recommendations: List[str]
    confidence_score: float
    analyzed_at: datetime
```

**QuizFeedback**
```python
class QuizFeedback(BaseModel):
    feedback_id: str
    quiz_id: str
    user_id: str
    concept: str
    rating: int  # 1-5
    comments: Optional[str]
    difficulty_perception: Optional[str]
    relevance_score: Optional[int]  # 1-5
    bias_analysis: Optional[BiasAnalysis]
    created_at: datetime
    processed: bool
```

### Key Methods

**collect_feedback()**
```python
await feedback_agent.collect_feedback(
    quiz_id=quiz.quiz_id,
    user_id=quiz.user_id,
    concept=quiz.concept,
    rating=4,
    comments="Great quiz but...",
    difficulty_perception="just_right",
    relevance_score=5
)
```

**analyze_bias()**
- Uses GPT-4 with specialized bias detection prompt
- Returns structured BiasAnalysis object
- Confidence scoring for reliability

**update_knowledge_base_for_bias()**
- Generates improved content addressing all bias types
- Creates content for all difficulty levels
- Adds to FAISS vector store with metadata
- Persists changes automatically

## 📊 Data Storage

Feedback is stored in:
```
data/
  feedback.json  # All feedback entries
  vector_store/  # Updated knowledge base
    education.index
    metadata.pkl
```

## 🎨 UI Integration

The feedback form is seamlessly integrated into the quiz results screen:

1. **Before Submission**: Interactive form with all fields
2. **During Processing**: Loading spinner with status
3. **After Processing**: 
   - Success message
   - Bias analysis details (if detected)
   - Actions taken
   - Transparent communication

## 🔒 Privacy & Ethics

- User feedback is stored securely
- Bias detection helps ensure inclusive content
- Transparent reporting to users
- Continuous improvement cycle
- Human review flagged for serious issues

## 📈 Impact Metrics

Track the effectiveness of the feedback system:
- **Average Rating**: Overall content quality
- **Bias Detection Rate**: How often bias is found
- **Knowledge Base Updates**: Number of improvements made
- **User Satisfaction**: Trend over time
- **Concept Health**: Which topics need attention

## 🚀 Future Enhancements

1. **Multi-language Bias Detection**: Support for multiple languages
2. **Sentiment Analysis**: Deeper emotional understanding
3. **Automated A/B Testing**: Test improved content effectiveness
4. **Real-time Alerts**: Notify team of urgent issues
5. **ML-based Predictions**: Predict content issues before feedback
6. **Parent/Teacher Dashboard**: Separate insights view

## 🤝 Integration with Other Agents

The Feedback Agent works with:
- **Orchestrator**: Coordinates feedback collection
- **RAG Service**: Updates knowledge base
- **Content Generation Agent**: Benefits from improved content
- **Personalization Agent**: Uses feedback for better targeting

## 📝 Example Flow

```
1. User completes quiz on "Saving Money"
2. User rates quiz 2/5, comments: "Examples were only about boys"
3. Feedback Agent analyzes comment
4. Detects: GENDER BIAS (High Severity)
5. Generates new inclusive content with diverse examples
6. Updates vector store automatically
7. User sees: "We detected gender bias and updated our content!"
8. Next user gets improved, inclusive content
```

## 🎯 Success Criteria

The Feedback Agent is successful when:
- ✅ Bias detection rate decreases over time
- ✅ Average ratings increase
- ✅ Knowledge base continuously improves
- ✅ Users feel heard and see changes
- ✅ Content becomes more inclusive
- ✅ All children see themselves represented

## 🔧 Configuration

The feedback agent uses these config settings:
```python
# config.yaml
llm:
  model: "gpt-4-turbo-preview"
  temperature: 0.3  # Low for consistent bias detection
  
vector_store:
  index_path: "./data/vector_store/education.index"
  metadata_path: "./data/vector_store/metadata.pkl"
```

## 📚 References

- Bias Detection in Educational Content: Best Practices
- Inclusive Design Principles for Children's Education
- RAG-based Knowledge Base Management
- Automated Content Improvement Systems

---

**Built with ❤️ for inclusive financial education**

