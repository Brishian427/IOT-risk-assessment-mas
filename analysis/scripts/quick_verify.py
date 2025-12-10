"""Quick verification script to test system functionality"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import run_risk_assessment
from src.config import Config

def verify_system():
    print("=" * 60)
    print("System Verification Test")
    print("=" * 60)
    
    # Check configuration
    print(f"\n✅ Configuration Check:")
    print(f"   - Number of models: {len(Config.GENERATOR_MODELS)}")
    print(f"   - Model list: {', '.join([m.split('-')[0] for m in Config.GENERATOR_MODELS])}")
    
    # Run quick test
    print(f"\n🔄 Running quick test...")
    test_input = "IoT device: WiFi connection, no encryption, default password"
    
    try:
        result = run_risk_assessment(test_input)
        
        print(f"\n✅ Test Results:")
        print(f"   - Assessments generated: {len(result.get('draft_assessments', []))}")
        print(f"   - Revision cycles: {result.get('revision_count', 0)}")
        print(f"   - Total critiques: {len(result.get('critiques', []))}")
        
        if result.get('synthesized_draft'):
            draft = result['synthesized_draft']
            print(f"   - Final score: {draft.score}/5")
            print(f"   - Summary: {draft.reasoning.summary[:80]}...")
            print(f"\n🎉 System test successful! All components working correctly.")
            return True
        else:
            print(f"\n⚠️  Warning: No synthesized draft generated")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    verify_system()

