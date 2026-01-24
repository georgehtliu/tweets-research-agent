"""
Main Entry Point for Agentic Research Agent
Interactive CLI for asking questions and running the agent workflow
"""
import json
import os
import sys
from pathlib import Path

# Add server directory to path
sys.path.insert(0, str(Path(__file__).parent))

from data_generator import MockXDataGenerator
from agent import AgenticResearchAgent
import config

# Get project root (parent of server/)
PROJECT_ROOT = Path(__file__).parent.parent

def load_data(data_file: str = None) -> list:
    """Load mock data from file or generate if not exists"""
    if data_file is None:
        data_file = config.DATA_FILE
    
    # Make path absolute if relative
    if not Path(data_file).is_absolute():
        data_file = PROJECT_ROOT / data_file
    
    data_path = Path(data_file)
    
    if data_path.exists():
        print(f"📂 Loading data from {data_file}...")
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"   ✅ Loaded {len(data)} posts\n")
        return data
    else:
        print(f"📝 Generating mock dataset...")
        generator = MockXDataGenerator(seed=42)
        data = generator.generate_dataset(
            num_posts=config.MOCK_DATA_SIZE,
            include_threads=True
        )
        generator.save_to_file(data_file)
        print(f"   ✅ Generated {len(data)} posts\n")
        return data

def save_results(result: dict, output_file: str = "output/research_result.json"):
    """Save research results to file"""
    # Make path absolute if relative
    if not Path(output_file).is_absolute():
        output_file = PROJECT_ROOT / output_file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"💾 Results saved to {output_file}")

def print_summary(result: dict):
    """Print formatted summary"""
    print("\n" + "="*70)
    print("📊 RESEARCH SUMMARY")
    print("="*70)
    print(f"\nQuery: {result['query']}")
    print(f"\nQuery Type: {result['plan'].get('query_type', 'unknown')}")
    print(f"Results Found: {result['results_count']} items")
    print(f"Refinement Iterations: {result['refinement_iterations']}")
    print(f"Total Steps: {result['execution_steps']}")
    print(f"Tokens Used: {result['total_tokens_used']}")
    
    confidence = result['analysis'].get('confidence', 0)
    print(f"Confidence: {confidence:.2%}")
    
    print("\n" + "-"*70)
    print("FINAL SUMMARY")
    print("-"*70)
    print(result['final_summary'])
    print("="*70 + "\n")

def interactive_mode():
    """Run interactive CLI mode"""
    print("\n" + "="*70)
    print("🔍 GROK AGENTIC RESEARCH SYSTEM")
    print("="*70)
    print("\nThis agent can answer various types of questions about X/Twitter data:")
    print("  • Trend analysis: 'What are people saying about AI?'")
    print("  • Information extraction: 'Find posts about Python from verified accounts'")
    print("  • Comparisons: 'Compare discussions about crypto vs traditional finance'")
    print("  • Temporal analysis: 'How has sentiment changed over time?'")
    print("  • And more...")
    print("\n" + "-"*70 + "\n")
    
    # Load or generate data
    data = load_data()
    
    # Initialize agent
    try:
        agent = AgenticResearchAgent(data)
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\nPlease set GROK_API_KEY in your .env file or environment variable.")
        print("Get your API key from https://console.x.ai")
        print("Use promo code: grok_eng_b4d86a51 for $20 free credits")
        return
    
    # Example queries
    example_queries = [
        "What are people saying about AI safety?",
        "Find the most discussed topics this week",
        "Compare sentiment about crypto vs traditional finance",
        "What are the main concerns about machine learning?",
        "Find posts from verified accounts about Python"
    ]
    
    while True:
        print("\n" + "-"*70)
        query = input("\n💬 Enter your research query (or 'exit' to quit, 'examples' for suggestions): ").strip()
        
        if not query:
            continue
        
        if query.lower() == 'exit':
            print("\n👋 Goodbye!")
            break
        
        if query.lower() == 'examples':
            print("\n📝 Example queries:")
            for i, eq in enumerate(example_queries, 1):
                print(f"  {i}. {eq}")
            continue
        
        # Run workflow
        try:
            result = agent.run_workflow(query)
            
            # Print summary
            print_summary(result)
            
            # Save results
            save_results(result)
            
            # Ask if user wants to continue
            continue_query = input("Ask another question? (y/n): ").strip().lower()
            if continue_query != 'y':
                break
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            continue

def single_query_mode(query: str):
    """Run agent for a single query"""
    print(f"\n🔍 Processing query: {query}\n")
    
    # Load data
    data = load_data()
    
    # Initialize agent
    try:
        agent = AgenticResearchAgent(data)
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    # Run workflow
    result = agent.run_workflow(query)
    
    # Print summary
    print_summary(result)
    
    # Save results
    save_results(result)
    
    return result

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Grok Agentic Research Agent - Ask questions about X/Twitter data"
    )
    parser.add_argument(
        "--query",
        type=str,
        help="Single query to process (if not provided, runs in interactive mode)"
    )
    parser.add_argument(
        "--data",
        type=str,
        help="Path to data file (default: generates mock data)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output/research_result.json",
        help="Output file path"
    )
    
    args = parser.parse_args()
    
    if args.query:
        # Single query mode
        single_query_mode(args.query)
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()
