"""Script to populate the vector store with financial education knowledge."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from services.rag_service import RAGService

def load_knowledge_base():
    """Load financial education knowledge into vector store."""
    
    rag_service = RAGService()
    
    documents = [
        # Saving Money
        """
        Saving Money - Beginner Level
        
        Saving money is one of the most important financial skills you can learn. When you save money, you're putting some aside instead of spending it all right away. This helps you:
        - Buy bigger things you really want
        - Be prepared for emergencies
        - Feel proud of yourself
        - Learn to be patient
        
        How to start saving:
        1. Get a piggy bank or savings jar
        2. Decide to save a little bit each time you get money
        3. Think about what you're saving for
        4. Don't touch your savings unless it's really important
        
        Example: If you get $10 for your birthday, you could save $5 and spend $5. After a few months, you'll have enough to buy something special!
        """,
        
        """
        Saving Money - Intermediate Level
        
        Saving money is about making smart choices today so you can have what you want tomorrow. It's not just about putting money in a piggy bank - it's about planning and setting goals.
        
        Different types of savings:
        - Short-term savings: For things you want soon (like a new game)
        - Long-term savings: For bigger things (like a bicycle)
        - Emergency savings: For unexpected needs
        
        The 50-30-20 rule (simplified for kids):
        - 50% for things you need (saved by parents)
        - 30% for things you want
        - 20% goes into savings
        
        Tips for successful saving:
        - Set specific goals with amounts and dates
        - Track your progress
        - Celebrate milestones
        - Don't get discouraged if you slip up
        """,
        
        """
        Saving Money - Advanced Level
        
        Understanding compound interest and long-term wealth building.
        
        Advanced saving concepts:
        - Interest: Money that grows your savings
        - Compound interest: When your interest earns interest
        - Savings accounts vs. investment accounts
        - The power of starting early
        
        Real-world example: If you save $10 per month starting at age 10, by age 18 you'll have saved $960. With just 3% annual interest, you'll actually have over $1,000!
        
        Advanced strategies:
        - Automate your savings
        - Use multiple accounts for different goals
        - Review and adjust your savings plan quarterly
        - Learn about different savings vehicles
        """,
        
        # Budgeting
        """
        Budgeting - Beginner Level
        
        A budget is a plan for your money. It helps you make sure you have enough for what you need and want.
        
        Simple budgeting steps:
        1. Know how much money you have
        2. List what you want to buy
        3. Make sure you don't spend more than you have
        4. Save some for later
        
        Example budget for $20 allowance:
        - Save: $5
        - Spend on needs: $10
        - Spend on wants: $5
        
        Why budgeting matters:
        - You won't run out of money
        - You can save for bigger things
        - You learn to make smart choices
        - You feel in control
        """,
        
        """
        Budgeting - Intermediate Level
        
        Creating and following a personal budget plan.
        
        Budget categories:
        - Fixed expenses: Things that stay the same (lunch money, savings)
        - Variable expenses: Things that change (snacks, entertainment)
        - Savings goals: Money for future purchases
        
        Creating your budget:
        1. Track your income (allowance, gifts, etc.)
        2. List all your expenses
        3. Categorize each expense
        4. Compare income to expenses
        5. Adjust to make sure you're not overspending
        
        Budget tracking tips:
        - Write down every purchase
        - Review your budget weekly
        - Adjust when needed
        - Learn from mistakes
        """,
        
        # Needs vs Wants
        """
        Needs vs Wants - Beginner Level
        
        Understanding the difference between needs and wants is crucial for making smart money decisions.
        
        NEEDS are things you must have to live:
        - Food and water
        - A home to live in
        - Clothes to wear
        - Medicine when sick
        - School supplies
        
        WANTS are things that are nice to have but not essential:
        - Toys and games
        - Candy and treats
        - Latest gadgets
        - Designer clothes
        - Entertainment
        
        Smart money rule: Always take care of needs first, then think about wants.
        """,
        
        """
        Needs vs Wants - Intermediate Level
        
        Making smart spending decisions by prioritizing needs over wants.
        
        The tricky part: Sometimes wants can feel like needs! How to tell the difference:
        - Ask: "Can I live without this?"
        - Ask: "Do I really need this or do I just want it?"
        - Wait 24 hours before buying wants
        
        Categories in between:
        Some things are both needs and wants. You NEED shoes, but designer sneakers are a WANT. You NEED food, but expensive snacks are a WANT.
        
        Decision-making framework:
        1. Identify if it's a need or want
        2. If it's a want, check your budget
        3. Consider if it's worth the cost
        4. Think about what you might give up
        5. Make your decision
        """,
        
        # Earning Money
        """
        Earning Money - Beginner Level
        
        Understanding how people earn money and how you can start earning too.
        
        How do people earn money?
        - Working jobs (what most adults do)
        - Doing chores (what kids can do)
        - Selling things they make
        - Helping others with tasks
        
        Ways kids can earn money:
        - Extra chores at home
        - Helping neighbors (with parent permission)
        - Selling handmade crafts
        - Lemonade stand
        - Tutoring younger kids
        
        Important earning lessons:
        - You must work to earn
        - Harder work often earns more
        - Being reliable gets you more opportunities
        - Save some of what you earn
        """,
        
        # Compound Interest
        """
        Compound Interest - Intermediate Level
        
        Understanding how money can grow over time.
        
        What is compound interest?
        Compound interest is when your money earns money, and then that earned money also earns money!
        
        Simple example:
        - You save $100
        - The bank gives you 5% interest per year
        - Year 1: You earn $5 (you now have $105)
        - Year 2: You earn interest on $105 (not just $100!)
        - You earn $5.25, so you have $110.25
        
        The magic of starting early:
        The longer your money grows, the more powerful compound interest becomes. Starting to save young means your money has more time to grow.
        
        Real-world application:
        If you save just $10 per month from age 10 to 18, and it earns 5% interest per year, you'll have over $1,000 when you're 18!
        """,
        
        # Risk and Reward
        """
        Risk & Reward - Advanced Level
        
        Understanding that different financial choices come with different levels of risk and potential reward.
        
        What is financial risk?
        Risk is the chance that you might lose money or not gain as much as you hoped.
        
        Risk levels:
        - Low risk: Savings account (you won't lose money, but you don't earn much)
        - Medium risk: Some investments (might lose some, might gain some)
        - High risk: Risky investments (could lose a lot or gain a lot)
        
        The risk-reward relationship:
        Generally, higher risk means potential for higher rewards, but also potential for bigger losses.
        
        Kid-friendly examples:
        - Low risk: Saving birthday money in a piggy bank
        - Medium risk: Using allowance to buy items to resell
        - Higher risk: Starting a small business
        
        Important lesson: Never risk money you can't afford to lose!
        """
    ]
    
    metadata = [
        {"concept": "saving", "difficulty": "beginner", "age_group": "6-9"},
        {"concept": "saving", "difficulty": "intermediate", "age_group": "10-12"},
        {"concept": "saving", "difficulty": "advanced", "age_group": "13-17"},
        {"concept": "budgeting", "difficulty": "beginner", "age_group": "6-9"},
        {"concept": "budgeting", "difficulty": "intermediate", "age_group": "10-12"},
        {"concept": "needs_vs_wants", "difficulty": "beginner", "age_group": "6-9"},
        {"concept": "needs_vs_wants", "difficulty": "intermediate", "age_group": "10-12"},
        {"concept": "earning", "difficulty": "beginner", "age_group": "6-9"},
        {"concept": "compound_interest", "difficulty": "intermediate", "age_group": "10-12"},
        {"concept": "risk_reward", "difficulty": "advanced", "age_group": "13-17"}
    ]
    
    print("Adding documents to vector store...")
    rag_service.add_documents(documents, metadata)
    
    print("Saving index to disk...")
    rag_service.save_index()
    
    print(f"✅ Successfully loaded {len(documents)} documents into vector store!")

if __name__ == "__main__":
    load_knowledge_base()
