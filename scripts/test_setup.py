"""
Test Setup Checker - Verify system is ready for testing
Created: 2025-01-XX
"""

import sys
import os

def check_dependencies():
    """Check if required packages are installed"""
    print("=" * 60)
    print("CHECKING DEPENDENCIES")
    print("=" * 60)
    
    required_packages = [
        "langgraph",
        "langchain_core",
        "langchain_openai",
        "langchain_anthropic",
        "langchain_google_genai",
        "langchain_tavily",
        "pydantic",
        "dotenv"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n[ACTION REQUIRED] Install missing packages:")
        print(f"pip install {' '.join(missing)}")
        return False
    else:
        print("\n✓ All dependencies installed")
        return True


def check_api_keys():
    """Check if API keys are configured"""
    print("\n" + "=" * 60)
    print("CHECKING API KEYS")
    print("=" * 60)
    
    # Try to load config
    try:
        from src.config import Config
        
        api_keys = {
            "OPENAI_API_KEY": Config.OPENAI_API_KEY,
            "ANTHROPIC_API_KEY": Config.ANTHROPIC_API_KEY,
            "GOOGLE_API_KEY": Config.GOOGLE_API_KEY,
            "TAVILY_API_KEY": Config.TAVILY_API_KEY,
            "DEEPSEEK_API_KEY": Config.DEEPSEEK_API_KEY,
        }
        
        missing = []
        for key_name, key_value in api_keys.items():
            if key_value:
                print(f"✓ {key_name}")
            else:
                print(f"✗ {key_name} - NOT SET")
                missing.append(key_name)
        
        if missing:
            print(f"\n[ACTION REQUIRED] Set missing API keys in .env file:")
            print("Create a .env file in the project root with:")
            for key in missing:
                print(f"  {key}=your-api-key-here")
            return False
        else:
            print("\n✓ All required API keys configured")
            return True
            
    except Exception as e:
        print(f"✗ Error loading config: {e}")
        return False


def check_project_structure():
    """Check if project files exist"""
    print("\n" + "=" * 60)
    print("CHECKING PROJECT STRUCTURE")
    print("=" * 60)
    
    required_files = [
        "src/schemas.py",
        "src/config.py",
        "src/graph.py",
        "src/main.py",
        "src/agents/generator_ensemble.py",
        "src/agents/aggregator.py",
        "src/agents/challenger_a.py",
        "src/agents/challenger_b.py",
        "src/agents/challenger_c.py",
        "src/agents/verifier.py",
    ]
    
    missing = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - MISSING")
            missing.append(file_path)
    
    if missing:
        print(f"\n[ERROR] Missing required files: {missing}")
        return False
    else:
        print("\n✓ All required files present")
        return True


def main():
    """Run all checks"""
    print("\n" + "=" * 60)
    print("MULTI-AGENT SYSTEM TEST SETUP")
    print("=" * 60)
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Project Structure", check_project_structure),
        ("API Keys", check_api_keys),
    ]
    
    results = {}
    for name, check_func in checks:
        results[name] = check_func()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = all(results.values())
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name}: {status}")
    
    if all_passed:
        print("\n✓ System is ready for testing!")
        print("\nTo run a test:")
        print("  python examples/test_full_workflow.py")
        print("\nOr run a quick test:")
        print("  python -c \"from src.main import run_risk_assessment; print('System works!')\"")
    else:
        print("\n✗ Please fix the issues above before testing")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

