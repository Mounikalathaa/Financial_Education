#!/usr/bin/env python3
"""
Verify installation and setup of Financial Education Quiz Engine.
"""
import sys
import os
from pathlib import Path

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_header(text):
    """Print a formatted header."""
    print(f"\n{BOLD}{BLUE}╔{'═' * 54}╗{RESET}")
    print(f"{BOLD}{BLUE}║  {text:<50}║{RESET}")
    print(f"{BOLD}{BLUE}╚{'═' * 54}╝{RESET}\n")

def check_python_version():
    """Check Python version."""
    print(f"{BOLD}Checking Python version...{RESET}")
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"  {GREEN}✓{RESET} Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  {RED}✗{RESET} Python {version.major}.{version.minor}.{version.micro} (3.9+ required)")
        return False

def check_dependencies():
    """Check if required packages are installed."""
    print(f"\n{BOLD}Checking dependencies...{RESET}")
    required_packages = [
        "streamlit",
        "openai",
        "faiss",
        "sentence_transformers",
        "langchain",
        "fastapi",
        "pydantic",
        "pandas"
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"  {GREEN}✓{RESET} {package}")
        except ImportError:
            print(f"  {RED}✗{RESET} {package} (not installed)")
            all_installed = False
    
    return all_installed

def check_env_file():
    """Check if .env file exists with required variables."""
    print(f"\n{BOLD}Checking environment configuration...{RESET}")
    env_path = Path(".env")
    
    if not env_path.exists():
        print(f"  {RED}✗{RESET} .env file not found")
        print(f"    {YELLOW}→{RESET} Copy .env.example to .env and add your OpenAI API key")
        return False
    
    # Check if OpenAI API key is set
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key or api_key.startswith("sk-your-"):
        print(f"  {RED}✗{RESET} OPENAI_API_KEY not configured")
        print(f"    {YELLOW}→{RESET} Add your OpenAI API key to .env file")
        return False
    
    print(f"  {GREEN}✓{RESET} .env file exists with API key")
    return True

def check_directory_structure():
    """Check if required directories exist."""
    print(f"\n{BOLD}Checking directory structure...{RESET}")
    required_dirs = [
        "agents",
        "services",
        "models",
        "config",
        "utils",
        "scripts",
        "data",
        "docs"
    ]
    
    all_exist = True
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"  {GREEN}✓{RESET} {dir_name}/")
        else:
            print(f"  {RED}✗{RESET} {dir_name}/ (missing)")
            all_exist = False
    
    return all_exist

def check_knowledge_base():
    """Check if knowledge base is initialized."""
    print(f"\n{BOLD}Checking knowledge base...{RESET}")
    vector_store_path = Path("data/vector_store")
    
    if not vector_store_path.exists():
        print(f"  {RED}✗{RESET} Vector store not initialized")
        print(f"    {YELLOW}→{RESET} Run: python scripts/load_knowledge_base.py")
        return False
    
    index_file = vector_store_path / "education.index"
    if not index_file.exists():
        print(f"  {RED}✗{RESET} FAISS index not found")
        print(f"    {YELLOW}→{RESET} Run: python scripts/load_knowledge_base.py")
        return False
    
    print(f"  {GREEN}✓{RESET} Knowledge base initialized")
    return True

def main():
    """Run all verification checks."""
    print_header("Financial Education Quiz Engine - Installation Check")
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Directory Structure", check_directory_structure),
        ("Environment Config", check_env_file),
        ("Knowledge Base", check_knowledge_base)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            results.append(check_func())
        except Exception as e:
            print(f"  {RED}✗{RESET} Error: {e}")
            results.append(False)
    
    # Summary
    print_header("Verification Summary")
    passed = sum(results)
    total = len(results)
    
    print(f"Checks passed: {passed}/{total}\n")
    
    if all(results):
        print(f"{GREEN}{BOLD}✓ All checks passed!{RESET}")
        print(f"\nYou're ready to run the application:")
        print(f"  1. Start MCP server: {BOLD}python mcp_server.py{RESET}")
        print(f"  2. Start Streamlit UI: {BOLD}streamlit run app.py{RESET}")
        print(f"\nOr use the quick start script:")
        print(f"  {BOLD}bash scripts/start.sh{RESET}")
        return 0
    else:
        print(f"{RED}{BOLD}✗ Some checks failed.{RESET} Please fix issues above.\n")
        print("Quick fixes:")
        if not results[1]:  # Dependencies
            print("  1. Install dependencies: pip3 install -r requirements.txt")
        if not results[3]:  # Env file
            print("  2. Create .env file with OpenAI API key")
        if not results[4]:  # Knowledge base
            print("  3. Initialize knowledge base: python scripts/load_knowledge_base.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())
