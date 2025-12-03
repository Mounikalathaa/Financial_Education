# Bias Checking Agent Documentation

## Overview

The Bias Checking Agent is an automated system that validates all AI-generated content for fairness, inclusivity, and cultural sensitivity. It ensures that educational materials are appropriate and unbiased across multiple dimensions.

## Purpose

The agent helps maintain high standards of content quality by:
- Detecting potential biases in generated stories, questions, hints, and explanations
- Providing actionable recommendations for improvement
- Automatically improving content when bias scores are too low
- Ensuring age-appropriate and culturally sensitive educational materials

## Bias Detection Dimensions

The agent evaluates content across **8 key dimensions**:

### 1. **Gender Bias**
- Checks for stereotypical gender role assignments
- Ensures balanced gender representation
- Validates pronoun usage and assumptions

**Example Issues Detected:**
- "The nurse (she) helped..." - assumes gender
- Male characters always in leadership roles
- Female characters only in supportive roles

### 2. **Cultural Sensitivity**
- Detects cultural stereotypes or assumptions
- Validates diverse cultural representation
- Ensures respectful treatment of traditions

**Example Issues Detected:**
- Assuming Western cultural norms as universal
- Stereotypical names or scenarios
- Excluding non-Western perspectives

### 3. **Socioeconomic Assumptions**
- Identifies assumptions about wealth or access
- Validates inclusive economic scenarios
- Ensures representation of different economic backgrounds

**Example Issues Detected:**
- "Everyone has a credit card..."
- Assuming access to banks or financial institutions
- Wealth-centric examples

### 4. **Ability and Accessibility**
- Checks for ableist language or assumptions
- Validates inclusive scenarios
- Ensures consideration of different abilities

**Example Issues Detected:**
- "Just look at the graph..." - assumes visual ability
- Physical activity requirements without alternatives
- Language implying disability as limitation

### 5. **Age Appropriateness**
- Validates complexity for target age group
- Ensures developmentally appropriate content
- Checks vocabulary and concept difficulty

**Example Issues Detected:**
- Advanced financial concepts for young learners
- Patronizing language for older students
- Inappropriate complexity levels

### 6. **Name Diversity**
- Validates representation of diverse names
- Checks for stereotypical name choices
- Ensures global name representation

**Example Issues Detected:**
- Only Western names used
- Stereotypical name-culture associations
- Lack of name diversity in examples

### 7. **Scenario Representation**
- Checks for diverse life situations
- Validates inclusive contexts
- Ensures varied family structures and backgrounds

**Example Issues Detected:**
- Always nuclear family scenarios
- Urban-centric situations
- Single lifestyle representation

### 8. **Language Inclusivity**
- Detects exclusive or discriminatory language
- Validates neutral terminology
- Ensures respectful phrasing

**Example Issues Detected:**
- Gendered language (e.g., "guys" for mixed groups)
- Exclusionary terms
- Culturally insensitive expressions

## Integration Points

The Bias Checking Agent is integrated at **4 key points** in the content generation pipeline:

### 1. Quiz Generation
**Location:** `agents/team_orchestrator.py` - `generate_personalized_quiz()`

**Process:**
- Case brief is checked after generation
- Quiz questions and options are validated
- Content is auto-improved if bias score < 7/10

**Logging:**
```
[Bias Check] Case brief passed (score: 8.5/10)
[Bias Check] Quiz passed (score: 9.0/10)
```

### 2. Hint Generation
**Location:** `mcp_server.py` - `/api/quiz/hint` endpoint

**Process:**
- AI-generated hints are checked before returning to user
- Low-scoring hints are automatically improved
- Bias reports are logged to console

**Logging:**
```
✅ [Bias Check] Hint passed (score: 8.2/10)
⚠️ [Bias Check] Hint has bias issues (score: 6.5/10)
[Bias Check] Auto-improving hint...
```

### 3. Explanation Generation
**Location:** `mcp_server.py` - `/api/quiz/explanation` endpoint

**Process:**
- Wrong answer explanations are validated
- Improvements suggested if needed
- Console logs show bias check results

### 4. Future Integration: Real-time Validation
- Additional checkpoints can be added easily
- Modular design allows flexible integration
- Any content type can be validated

## Scoring System

### Bias Score (0-10)
- **9-10**: Excellent - highly inclusive and unbiased
- **7-8**: Good - acceptable with minor improvements possible
- **5-6**: Fair - has issues, improvements recommended
- **0-4**: Poor - significant bias detected, requires improvement

### Auto-Improvement Threshold
- **Score < 7**: Content is automatically improved
- **Score ≥ 7**: Content passes, logged for monitoring

### Acceptability
- `is_acceptable: true` - Content can be used as-is
- `is_acceptable: false` - Issues detected, review recommended

## Agent Response Format

```python
{
    "bias_score": 8.5,  # 0-10 scale
    "is_acceptable": True,  # Boolean flag
    "issues_found": [
        "Minor gender assumption in hint",
        "Name diversity could be improved"
    ],
    "recommendations": [
        "Use neutral pronouns consistently",
        "Include names from various cultural backgrounds",
        "Add examples from different economic contexts"
    ],
    "bias_details": {
        "gender_bias": "Low",
        "cultural_sensitivity": "High",
        "socioeconomic_assumptions": "Medium",
        # ... other dimensions
    }
}
```

## Methods

### `check_content_bias(content, content_type, user_age)`
Analyzes content and returns bias analysis.

**Parameters:**
- `content`: Dictionary or string containing the content
- `content_type`: One of "story", "quiz", "hint", "explanation"
- `user_age`: Target age for appropriateness checking

**Returns:** Bias analysis dictionary with score and recommendations

### `suggest_improvements(content, bias_analysis, content_type)`
Generates improved version of content based on bias analysis.

**Parameters:**
- `content`: Original content that needs improvement
- `bias_analysis`: Result from `check_content_bias()`
- `content_type`: Type of content being improved

**Returns:** Improved content with bias issues addressed

### `get_bias_report(bias_analysis)`
Creates human-readable report from bias analysis.

**Parameters:**
- `bias_analysis`: Result from `check_content_bias()`

**Returns:** Formatted string report for logging or display

## Configuration

### Environment Variables
The agent uses the same Azure OpenAI credentials as other agents:

```bash
OPENAI_API_KEY=<your-azure-openai-key>
OPENAI_ENDPOINT=<your-azure-endpoint>
MODEL_API_VERSION=2024-02-01
MODEL_NAME=gpt-4
```

### Initialization
The agent is initialized in `team_orchestrator.py`:

```python
from agents.bias_checking_agent import BiasCheckingAgent

self.bias_checking_agent = BiasCheckingAgent()
```

## Monitoring and Logs

### Console Logs
All bias checks are logged to the console with clear indicators:

**Passed Checks:**
```
✅ [Bias Check] Case brief passed (score: 8.5/10)
✅ [Bias Check] Quiz passed (score: 9.0/10)
✅ [Bias Check] Hint passed (score: 8.2/10)
```

**Issues Detected:**
```
⚠️ [Bias Check] Case brief has bias issues (score: 6.5/10)
⚠️ [Bias Check] Issues: ['Gender assumption in example', 'Limited name diversity']
```

**Auto-Improvements:**
```
[Bias Check] Auto-improving case brief...
[Bias Check] Case brief improved successfully
```

### Log Levels
- `INFO`: Successful bias checks
- `WARNING`: Issues detected
- `ERROR`: Failures in bias checking process

## Benefits

### For Students
- More inclusive and relatable content
- Reduced stereotype exposure
- Culturally sensitive learning materials
- Age-appropriate complexity

### For Educators
- Automated quality assurance
- Consistent content standards
- Reduced manual review time
- Transparent bias reporting

### For System
- Improved content quality
- Automated bias mitigation
- Scalable validation
- Continuous monitoring

## Example Workflow

1. **Content Generation**
   - Quiz agent generates questions and case brief
   - Content sent to Bias Checking Agent

2. **Bias Analysis**
   - Agent evaluates across 8 dimensions
   - Calculates bias score (0-10)
   - Identifies specific issues

3. **Decision Making**
   - Score ≥ 7: Content passes ✅
   - Score < 7: Auto-improvement triggered ⚠️

4. **Auto-Improvement** (if needed)
   - Agent generates improved version
   - Re-validates improved content
   - Logs improvement success

5. **Delivery**
   - Validated/improved content returned to user
   - All checks logged for monitoring

## Future Enhancements

### Planned Features
- **Database Logging**: Store bias reports in database for analytics
- **Admin Dashboard**: View bias statistics and trends
- **Custom Rules**: Define organization-specific bias rules
- **Multi-language Support**: Detect bias in non-English content
- **Historical Analysis**: Track bias improvements over time
- **User Feedback Loop**: Incorporate user reports of bias

### Extensibility
The agent is designed for easy extension:
- Add new bias dimensions by updating the prompt
- Customize scoring thresholds per content type
- Integrate with additional content types
- Add custom validation rules

## Best Practices

### For Developers
1. Always call bias checking after content generation
2. Log bias scores for monitoring trends
3. Review auto-improved content periodically
4. Update bias detection prompts based on findings
5. Monitor false positives and adjust thresholds

### For Content Reviewers
1. Review flagged content (score < 7)
2. Provide feedback on false positives
3. Update bias dimension definitions as needed
4. Monitor log patterns for systematic issues
5. Celebrate improvements in bias scores

## Technical Details

### Dependencies
- `openai`: Azure OpenAI client for GPT-4 analysis
- `asyncio`: Asynchronous bias checking
- Standard library: `logging`, `typing`, `os`

### Performance
- **Latency**: ~2-3 seconds per check (GPT-4 analysis)
- **Caching**: Not implemented (each check is fresh)
- **Concurrent Checks**: Supported via async/await
- **Timeout**: 120 seconds for GPT-4 calls

### Error Handling
- Failed bias checks don't block content delivery
- Errors logged but content still returned
- Fallback to original content if improvement fails
- Network issues handled gracefully

## Conclusion

The Bias Checking Agent represents a significant step forward in automated content quality assurance. By systematically evaluating generated content across multiple dimensions, it helps ensure that our financial education platform provides inclusive, appropriate, and unbiased learning experiences for all students.

The automated nature of the checks, combined with auto-improvement capabilities, makes it scalable and maintainable while reducing the burden on human reviewers. The comprehensive logging provides transparency and accountability, enabling continuous improvement of the system.

---

**Last Updated:** January 2025  
**Version:** 1.0  
**Maintainer:** Financial Education Platform Team
