import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.factory import PuzzleGenerator
from app.models.settings import GenerationConfig, Difficulty, SudokuType
from tests.strict_validator import SudokuValidator

def run_fast_verification():
    print("="*60, flush=True)
    print("FAST SUDOKU VERIFICATION SUITE (Skipping Jigsaw Diagonal)", flush=True)
    print("="*60, flush=True)
    
    generator = PuzzleGenerator()
    validator = SudokuValidator()
    
    # Test remaining types that weren't finished in the main run
    test_cases = [
        (SudokuType.WINDOKU_9X9, 9),
        (SudokuType.ASTERISK_9X9, 9),
        (SudokuType.CONSECUTIVE_9X9, 9),
        (SudokuType.THAI_9X9, 9)
    ]
    
    results = {}
    
    for stype, size in test_cases:
        test_name = f"{stype.name} ({size}x{size})"
        print(f"\nTesting {test_name}...", flush=True)
        
        config = GenerationConfig(
            size=size,
            difficulty=Difficulty.EASY,
            type=stype
        )
        
        start_time = time.time()
        try:
            # Generate
            grid = generator.generate(config)
            gen_time = time.time() - start_time
            
            # Validate
            is_valid = validator.validate(grid, config)
            
            results[test_name] = {
                "status": "PASS" if is_valid else "FAIL",
                "time": f"{gen_time:.2f}s"
            }
            
        except Exception as e:
            print(f"  ❌ CRITICAL ERROR: {e}", flush=True)
            results[test_name] = {
                "status": "ERROR",
                "time": f"{time.time() - start_time:.2f}s",
                "error": str(e)
            }

    print("\n" + "="*60, flush=True)
    print("FAST REPORT", flush=True)
    print("="*60, flush=True)
    
    all_passed = True
    for name, data in results.items():
        status = data['status']
        if status != "PASS": all_passed = False
        print(f"{name:<30} | {status:<10} | {data['time']:<10}", flush=True)
            
    if all_passed:
        print("✅ ALL FAST TESTS PASSED!", flush=True)
    else:
        print("❌ SOME FAST TESTS FAILED.", flush=True)

if __name__ == "__main__":
    run_fast_verification()
