import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def run_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Define Test Groups by Phase
    phases = {
        "Phase 5: Advanced Features (Windoku, Thai, 12x12)": "tests.test_advanced_features",
        "Phase 5/6: English Alphabet": "tests.test_english_alphabet",
        "Phase 6: Jigsaw Engine": "tests.test_jigsaw",
        "Phase 7: Logic Variants (Consecutive, Even-Odd)": "tests.test_variants"
    }

    print("="*60)
    print("SudokuMaster Gen - System Verification")
    print("="*60)

    all_passed = True
    
    for phase_name, module_name in phases.items():
        print(f"\nRunning {phase_name}...")
        try:
            tests = loader.loadTestsFromName(module_name)
            runner = unittest.TextTestRunner(verbosity=1)
            result = runner.run(tests)
            
            if not result.wasSuccessful():
                all_passed = False
                print(f"❌ {phase_name} FAILED")
            else:
                print(f"✅ {phase_name} PASSED")
        except Exception as e:
            all_passed = False
            print(f"❌ {phase_name} ERROR: {str(e)}")

    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL SYSTEMS GO! The application is ready.")
    else:
        print("⚠️ SOME TESTS FAILED. Please check the logs above.")
    print("="*60)

if __name__ == "__main__":
    run_tests()
