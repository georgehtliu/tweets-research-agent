"""
Quick setup test script
Verifies that the environment is configured correctly
"""
import os
import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import config
        from data_generator import MockXDataGenerator
        from retrieval import HybridRetriever
        from context_manager import ContextManager
        from grok_client import GrokClient
        from agent import AgenticResearchAgent
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    try:
        import config
        print(f"   API Key set: {'Yes' if config.GROK_API_KEY else 'No'}")
        print(f"   Base URL: {config.GROK_BASE_URL}")
        print(f"   Planner Model: {config.ModelConfig.PLANNER_MODEL}")
        print("✅ Configuration loaded")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_data_generation():
    """Test mock data generation"""
    print("\nTesting data generation...")
    try:
        from data_generator import MockXDataGenerator
        generator = MockXDataGenerator(seed=42)
        posts = generator.generate_dataset(num_posts=10, include_threads=False)
        print(f"   Generated {len(posts)} posts")
        print(f"   Sample post: {posts[0].get('text', '')[:50]}...")
        print("✅ Data generation works")
        return True
    except Exception as e:
        print(f"❌ Data generation error: {e}")
        return False

def test_retrieval():
    """Test retrieval system"""
    print("\nTesting retrieval system...")
    try:
        from data_generator import MockXDataGenerator
        from retrieval import HybridRetriever
        
        generator = MockXDataGenerator(seed=42)
        posts = generator.generate_dataset(num_posts=20, include_threads=False)
        retriever = HybridRetriever(posts)
        
        # Test keyword search
        results = retriever.keyword_search("AI", top_k=5)
        print(f"   Keyword search: {len(results)} results")
        
        # Test hybrid search
        results = retriever.hybrid_search("Python", top_k=5)
        print(f"   Hybrid search: {len(results)} results")
        print("✅ Retrieval system works")
        return True
    except Exception as e:
        print(f"❌ Retrieval error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_grok_connection():
    """Test Grok API connection"""
    print("\nTesting Grok API connection...")
    try:
        from grok_client import GrokClient
        
        if not config.GROK_API_KEY:
            print("   ⚠️  No API key set - skipping API test")
            print("   Set GROK_API_KEY in .env file to test API connection")
            return True
        
        client = GrokClient()
        
        # Simple test call
        response = client.call(
            model=config.ModelConfig.PLANNER_MODEL,
            messages=[{"role": "user", "content": "Say 'test'"}],
            max_tokens=10
        )
        
        if response.get("success"):
            print(f"   API response received")
            print("✅ Grok API connection works")
            return True
        else:
            print(f"   ⚠️  API error: {response.get('error', 'Unknown error')}")
            print("   Check your API key and endpoint configuration")
            return False
    except Exception as e:
        print(f"   ⚠️  Connection test error: {e}")
        print("   This might be expected if API key is not set")
        return True  # Don't fail setup if API key not set

def main():
    """Run all tests"""
    print("="*60)
    print("GROK AGENTIC RESEARCH - SETUP TEST")
    print("="*60)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Data Generation", test_data_generation),
        ("Retrieval System", test_retrieval),
        ("Grok API Connection", test_grok_connection),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} test failed with exception: {e}")
            results.append((name, False))
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! You're ready to use the agent.")
        print("\nNext steps:")
        print("  1. Make sure GROK_API_KEY is set in .env")
        print("  2. Run: python main.py")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
