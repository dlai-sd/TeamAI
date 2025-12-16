"""
Test Recipe Execution
Run this to test the agent runtime with the SEO site-audit recipe
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.recipe_evaluator import RecipeEvaluator


async def test_seo_audit():
    """Test SEO site audit recipe"""
    
    print("=" * 80)
    print("TeamAI Agent Runtime - SEO Site Audit Test")
    print("=" * 80)
    
    # Path to recipe
    recipe_path = Path(__file__).parent.parent / "recipes" / "seo" / "site-audit.yaml"
    
    # Initialize evaluator (mock_mode=True for testing without real API calls)
    evaluator = RecipeEvaluator(str(recipe_path), mock_mode=True)
    
    # Input parameters
    inputs = {
        'website_url': 'https://example.com',
        'max_depth': 2,
        'include_images': True
    }
    
    print(f"\n📥 Input Parameters:")
    for key, value in inputs.items():
        print(f"  - {key}: {value}")
    
    # Execute recipe
    try:
        result = await evaluator.execute(inputs)
        
        print("\n" + "=" * 80)
        print("✅ EXECUTION SUCCESSFUL")
        print("=" * 80)
        
        print(f"\n📊 Metrics:")
        metrics = result['metrics']
        print(f"  - Execution Time: {metrics['execution_time_ms']} ms")
        print(f"  - Nodes Executed: {metrics['nodes_executed']}")
        print(f"  - Tokens Used: {metrics['tokens_used']}")
        print(f"  - Total Cost: ${metrics['total_cost']:.6f}")
        
        print(f"\n📄 Output:")
        output = result['output']
        if isinstance(output, dict):
            if 'content' in output:
                print(output['content'][:500])  # First 500 chars
                print("\n... (truncated)")
            else:
                import json
                print(json.dumps(output, indent=2)[:500])
        else:
            print(str(output)[:500])
        
        print("\n" + "=" * 80)
        
        return result
        
    except Exception as e:
        print(f"\n❌ EXECUTION FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def test_real_api():
    """Test with real Groq API (requires GROQ_API_KEY)"""
    import os
    
    if not os.getenv('GROQ_API_KEY'):
        print("⚠️  GROQ_API_KEY not set - skipping real API test")
        print("   To test with real API: export GROQ_API_KEY='your-key-here'")
        return
    
    print("\n" + "=" * 80)
    print("Testing with Real Groq API")
    print("=" * 80)
    
    recipe_path = Path(__file__).parent.parent / "recipes" / "seo" / "site-audit.yaml"
    evaluator = RecipeEvaluator(str(recipe_path), mock_mode=False)
    
    inputs = {
        'website_url': 'https://example.com',
        'max_depth': 1,  # Smaller depth for testing
        'include_images': True
    }
    
    try:
        result = await evaluator.execute(inputs)
        print(f"\n✅ Real API execution successful")
        print(f"   Cost: ${result['metrics']['total_cost']:.6f}")
        print(f"   Tokens: {result['metrics']['tokens_used']}")
        return result
    except Exception as e:
        print(f"\n❌ Real API execution failed: {str(e)}")
        return None


if __name__ == "__main__":
    # Test with mock data
    print("\n🧪 Running Mock Mode Test...")
    asyncio.run(test_seo_audit())
    
    # Test with real API (if key available)
    print("\n🌐 Testing Real API...")
    asyncio.run(test_real_api())
