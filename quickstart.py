"""
Quick Start Script - Test the application setup
"""
import sys
import os

def check_dependencies():
    """Check if all dependencies are installed"""
    print("Checking dependencies...")
    
    required_modules = [
        'flask',
        'ollama',
        'chromadb',
        'tavily',
        'reportlab',
        'docx',
        'bs4',
        'sentence_transformers'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError:
            print(f"✗ {module} - MISSING")
            missing.append(module)
    
    if missing:
        print(f"\nMissing modules: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("\n✓ All dependencies installed")
    return True


def check_ollama():
    """Check if Ollama is available"""
    print("\nChecking Ollama...")
    
    try:
        from backend.llm import OllamaClient
        client = OllamaClient()
        
        if client.check_availability():
            print("✓ Ollama is running and model is available")
            return True
        else:
            print("✗ Ollama model not found")
            print("Run: ollama pull llama3.2")
            return False
            
    except Exception as e:
        print(f"✗ Ollama error: {e}")
        print("Make sure Ollama is running: ollama serve")
        return False


def check_config():
    """Check configuration"""
    print("\nChecking configuration...")
    
    if not os.path.exists('.env'):
        print("✗ .env file not found")
        print("Copy .env.example to .env and configure")
        return False
    
    from config import Config
    
    if not Config.TAVILY_API_KEY:
        print("⚠ TAVILY_API_KEY not set in .env")
        print("Get API key from: https://tavily.com")
        return False
    
    print("✓ Configuration looks good")
    return True


def check_directories():
    """Check if necessary directories exist"""
    print("\nChecking directories...")
    
    from config import Config
    
    dirs = [
        Config.OUTPUT_DIR,
        Config.TEMP_DIR,
        Config.CHROMA_PERSIST_DIR
    ]
    
    for dir_path in dirs:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            print(f"✓ Created {dir_path}")
        else:
            print(f"✓ {dir_path} exists")
    
    return True


def main():
    """Run all checks"""
    print("=" * 60)
    print("Deep Research Assistant - Quick Start Check")
    print("=" * 60)
    print()
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Directories", check_directories),
        ("Configuration", check_config),
        ("Ollama", check_ollama),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Error in {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:20} {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All checks passed! Ready to run:")
        print("  python main.py")
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == '__main__':
    main()
