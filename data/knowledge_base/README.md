# Financial Education Knowledge Base

This directory contains the JSON knowledge base files used by the Financial Education Quiz Engine.

## Files

- `Class_6.json` - Financial concepts for Class 6 students (ages 11-12)
- `Class_7.json` - Financial concepts for Class 7 students (ages 12-13)
- `Class_8.json` - Financial concepts for Class 8 students (ages 13-14)
- `Class_9.json` - Financial concepts for Class 9 students (ages 14-15)
- `Class_10.json` - Financial concepts for Class 10 students (ages 15-16)

## Structure

Each JSON file contains:
```json
{
  "class": "6",
  "resource_type": "financial_education_knowledge_base",
  "topics": [
    {
      "topic_name": "Topic Name",
      "definition": "Clear definition of the concept",
      "key_points": ["Point 1", "Point 2", ...],
      "processes": ["Process 1", "Process 2", ...],
      "examples": ["Example 1", "Example 2", ...],
      "facts": ["Fact 1", "Fact 2", ...]
    }
  ]
}
```

## Topics Covered

### Class 6 (10 topics)
- Barter System
- Evolution of Money
- Needs and Wants
- Bill and Cash Memo
- Trade
- Benefits of Trade
- Budgeting and Saving
- Stories with Financial Lessons
- Taxation
- Money Growth and Savings Data

### Class 7 (10 topics)
- Need and Sources of Borrowing
- Role and Functions of the RBI
- Banking Operations
- Credit and Debit Cards
- Digital Payments
- And more...

### Class 8 (10 topics)
- Inflation and Purchasing Power
- Investment Basics
- Stock Market
- And more...

### Class 9 (11 topics)
- Advanced Banking Concepts
- Economic Indicators
- And more...

### Class 10 (15 topics)
- Complex Financial Instruments
- Economic Policies
- And more...

## Usage

The knowledge base is automatically loaded into the FAISS vector store when you run:

```bash
python scripts/load_knowledge_base.py
```

The system:
1. Reads all JSON files from this directory
2. Extracts topics with their definitions, key points, processes, examples, and facts
3. Creates structured documents for each topic
4. Indexes them in the vector store for RAG-powered retrieval
5. Maps topics to appropriate age groups and difficulty levels

## Adding New Content

To add new financial education content:

1. Follow the same JSON structure as existing files
2. Place the file in this directory
3. Update `scripts/load_knowledge_base.py` to include the new file in the `json_files` list
4. Run the load script to rebuild the index

## Automatic Mapping

The system automatically maps:
- **Class levels → Age groups & Difficulty**
  - Class 6-7 → Ages 6-9, Beginner
  - Class 8-9 → Ages 10-12, Intermediate  
  - Class 10+ → Ages 13-17, Advanced

- **Topics → Financial Concepts**
  - Saving-related topics → "saving"
  - Budget-related topics → "budgeting"
  - Needs/wants topics → "needs_vs_wants"
  - Earning topics → "earning"
  - Interest topics → "compound_interest"
  - Risk/investment topics → "risk_reward"
  - Money/trade topics → "money_basics"
  - Borrowing/loan topics → "borrowing"
  - Banking topics → "banking"
  - Tax topics → "taxation"
  - Others → "general_finance"
