#!/usr/bin/env python3
"""
Installation verification script for Financial Education Quiz Engine.
Checks all dependencies and configurations.
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.9 or higher."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need 3.9+")
        return False

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'streamlit',
        'openai',
        'faiss',
        'sentence_transformers',
        'fastapi',
        'uvicorn',
        'httpx',
        'pydantic',
        'pandas',
        'numpy',
        'yaml'
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'yaml':
                __import__('yaml')
            elif package == 'faiss':
                __import__('faiss')
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    return len(missing) == 0

def check_env_file():
    """Check if .env file exists and has required variables."""
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ .env file not found")
        print("   Create .env with: OPENAI_API_KEY=your_key_here")
        return False
    
    with open(env_path, 'r') as f:
        content = f.read()
        if 'OPENAI_API_KEY' in content:
            print("✅ .env file configured")
            return True
        else:
            print("❌ OPENAI_API_KEY not found in .env")
            return False

def check_project_structure():
    """Check if all required directories and files exist."""
    required_paths = [
        'agents/',
        'services/',
        'models/',
        'config/',
        'utils/',
        'data/',
        'docs/',
        'scripts/',
        'app.py',
        'mcp_server.py',
        'config.yaml',
        'requirements.txt'
    ]
    
    missing = []
    for path in required_paths:
        if Path(path).exists():
            print(f"✅ {path}")
        else:
            print(f"❌ {path}")
            missing.append(path)
    
    return len(missing) == 0

def check_knowledge_base():
    """Check if vector store is initialized."""
    index_path = Path('data/vector_store/education.index')
    if index_path.exists():
        print("✅ Knowledge base initialized")
        return True
    else:
        print("⚠️  Knowledge base not found")
        print("   Run: python scripts/load_knowledge_base.py")
        return False

def main():
    """Run all checks."""
    print("╔══════════════════════════════════════════════════════╗")
    print("║  Financial Education Quiz Engine                    ║")
    print("║  Installation Verification                          ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment Config", check_env_file),
        ("Project Structure", check_project_structure),
        ("Knowledge Base", check_knowledge_base)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        print("-" * 40)
        results.append(check_func())
    
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║  Verification Summary                               ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()
    
    passed = sum(results)
    total = len(results)
    
    print(f"Checks passed: {passed}/{total}")
    print()
    
    if all(results):
        print("✅ All checks passed! Ready to run.")
        print()
        print("Start the application:")
        print("  ./demo.sh")
        print()
        print("Or manually:")
        print("  python mcp_server.py &")
        print("  streamlit run app.py")
        return 0
    else:
        print("❌ Some checks failed. Please fix issues above.")
        print()
        print("Quick fixes:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Create .env file with OpenAI API key")
        print("  3. Initialize knowledge base: python scripts/load_knowledge_base.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())
