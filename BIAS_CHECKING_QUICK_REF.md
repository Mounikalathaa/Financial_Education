# Bias Checking Agent - Quick Reference

## What It Does
Automatically validates all AI-generated content (stories, questions, hints, explanations) for fairness, inclusivity, and cultural sensitivity across 8 dimensions.

## 8 Bias Dimensions Checked
1. **Gender Bias** - Stereotypes, balanced representation
2. **Cultural Sensitivity** - Stereotypes, diverse representation
3. **Socioeconomic Assumptions** - Wealth assumptions, access
4. **Ability & Accessibility** - Ableist language, inclusive scenarios
5. **Age Appropriateness** - Complexity, vocabulary, concepts
6. **Name Diversity** - Global representation, stereotypes
7. **Scenario Representation** - Life situations, family structures
8. **Language Inclusivity** - Exclusive terms, neutral language

## Scoring
- **9-10**: Excellent ✅
- **7-8**: Good ✅ 
- **5-6**: Fair ⚠️ (auto-improved)
- **0-4**: Poor ⚠️ (auto-improved)

**Auto-Improvement Threshold:** Score < 7

## Where It's Integrated
1. **Quiz Generation** - Case briefs and questions validated
2. **Hint Generation** - AI hints checked before delivery
3. **Explanations** - Wrong answer explanations validated

## Sample Logs

### Passed Content
```
✅ [Bias Check] Case brief passed (score: 8.5/10)
✅ [Bias Check] Quiz passed (score: 9.0/10)
✅ [Bias Check] Hint passed (score: 8.2/10)
```

### Issues Detected & Auto-Improved
```
⚠️ [Bias Check] Hint has bias issues (score: 6.5/10)
⚠️ [Bias Check] Issues: ['Gender assumption in example']
[Bias Check] Auto-improving hint...
[Bias Check] Hint improved successfully
```

## Response Format
```python
{
    "bias_score": 8.5,
    "is_acceptable": True,
    "issues_found": ["List of issues"],
    "recommendations": ["List of recommendations"]
}
```

## Quick Usage

### Check Content
```python
bias_result = await bias_checking_agent.check_content_bias(
    content={"story": "Once upon a time..."},
    content_type="story",
    user_age=10
)
```

### Auto-Improve
```python
if bias_result["bias_score"] < 7:
    improved = await bias_checking_agent.suggest_improvements(
        content=original_content,
        bias_analysis=bias_result,
        content_type="story"
    )
```

## Configuration
Uses same environment variables as other agents:
- `OPENAI_API_KEY`
- `OPENAI_ENDPOINT`
- `MODEL_API_VERSION`
- `MODEL_NAME`

## Files Modified
- **New:** `agents/bias_checking_agent.py` (296 lines)
- **Updated:** `agents/team_orchestrator.py` (added initialization + integration)
- **Updated:** `mcp_server.py` (added bias checks to hint and explanation endpoints)
- **New:** `docs/BIAS_CHECKING.md` (comprehensive documentation)

## Test It
1. Generate a quiz in the app
2. Request a hint
3. Check console logs for bias check results
4. Look for ✅ (passed) or ⚠️ (improved) markers

---
For detailed information, see `docs/BIAS_CHECKING.md`
