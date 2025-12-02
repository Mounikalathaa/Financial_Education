"""Script to populate the vector store with financial education knowledge."""

import sys
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from services.rag_service import RAGService

def load_json_knowledge_base():
    """Load financial education knowledge from JSON files."""
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    knowledge_base_dir = project_root / "data" / "knowledge_base"
    
    # List of JSON files to load
    json_files = [
        "Class_6.json",
        "Class_7.json",
        "Class_8.json",
        "Class_9.json",
        "Class_10.json"
    ]
    
    documents = []
    metadata = []
    
    print("Loading knowledge from JSON files...")
    
    for json_file in json_files:
        file_path = knowledge_base_dir / json_file
        
        if not file_path.exists():
            print(f"⚠️  Warning: {json_file} not found at {file_path}, skipping...")
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            class_level = data.get("class", "unknown")
            topics = data.get("topics", [])
            
            print(f"  Loading {len(topics)} topics from {json_file}...")
            
            for topic in topics:
                topic_name = topic.get("topic_name", "Unknown Topic")
                definition = topic.get("definition", "")
                key_points = topic.get("key_points", [])
                processes = topic.get("processes", [])
                examples = topic.get("examples", [])
                facts = topic.get("facts", [])
                
                # Create a comprehensive document text
                doc_text = f"""
Topic: {topic_name}
Class Level: {class_level}

Definition:
{definition}

Key Points:
{chr(10).join('- ' + point for point in key_points)}

{('Processes:' + chr(10) + chr(10).join('- ' + proc for proc in processes)) if processes else ''}

{('Examples:' + chr(10) + chr(10).join('- ' + ex for ex in examples)) if examples else ''}

{('Facts:' + chr(10) + chr(10).join('- ' + fact for fact in facts)) if facts else ''}
"""
                
                documents.append(doc_text.strip())
                
                # Determine age group and difficulty based on class level
                age_group, difficulty = _map_class_to_age_difficulty(class_level)
                
                # Map topic to financial concept
                concept = _map_topic_to_concept(topic_name)
                
                metadata.append({
                    "class": class_level,
                    "topic": topic_name,
                    "concept": concept,
                    "difficulty": difficulty,
                    "age_group": age_group,
                    "source": json_file
                })
        
        except Exception as e:
            print(f"❌ Error loading {json_file}: {str(e)}")
            continue
    
    return documents, metadata

def _map_class_to_age_difficulty(class_level):
    """Map class level to age group and difficulty."""
    try:
        class_num = int(class_level)
        
        if class_num <= 7:
            return "6-9", "beginner"
        elif class_num <= 9:
            return "10-12", "intermediate"
        else:
            return "13-17", "advanced"
    except:
        return "10-12", "intermediate"  # default

def _map_topic_to_concept(topic_name):
    """Map topic name to financial concept."""
    topic_lower = topic_name.lower()
    
    # Mapping patterns
    if any(word in topic_lower for word in ["saving", "save", "savings"]):
        return "saving"
    elif any(word in topic_lower for word in ["budget", "expense", "planning"]):
        return "budgeting"
    elif any(word in topic_lower for word in ["need", "want", "essential"]):
        return "needs_vs_wants"
    elif any(word in topic_lower for word in ["earn", "income", "salary", "wage"]):
        return "earning"
    elif any(word in topic_lower for word in ["interest", "compound", "growth"]):
        return "compound_interest"
    elif any(word in topic_lower for word in ["risk", "reward", "investment", "stock"]):
        return "risk_reward"
    elif any(word in topic_lower for word in ["barter", "money", "currency", "trade"]):
        return "money_basics"
    elif any(word in topic_lower for word in ["borrow", "loan", "credit", "debt"]):
        return "borrowing"
    elif any(word in topic_lower for word in ["bank", "rbi", "financial"]):
        return "banking"
    elif any(word in topic_lower for word in ["tax", "gst"]):
        return "taxation"
    else:
        return "general_finance"

def load_knowledge_base():
    """Load financial education knowledge into vector store."""
    
    rag_service = RAGService()
    
    # Load documents and metadata from JSON files
    documents, metadata = load_json_knowledge_base()
    
    if not documents:
        print("❌ No documents loaded! Please check your JSON files.")
        return
    
    print(f"\n📚 Total documents prepared: {len(documents)}")
    print("\nAdding documents to vector store...")
    rag_service.add_documents(documents, metadata)
    
    print("Saving index to disk...")
    rag_service.save_index()
    
    print(f"\n✅ Successfully loaded {len(documents)} documents into vector store!")
    
    # Print summary by class
    class_counts = {}
    for meta in metadata:
        class_level = meta.get("class", "unknown")
        class_counts[class_level] = class_counts.get(class_level, 0) + 1
    
    print("\n📊 Summary by Class:")
    for class_level in sorted(class_counts.keys(), key=lambda x: int(x) if x.isdigit() else 0):
        print(f"  Class {class_level}: {class_counts[class_level]} topics")

if __name__ == "__main__":
    load_knowledge_base()
