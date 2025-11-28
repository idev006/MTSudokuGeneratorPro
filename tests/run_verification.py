import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.factory import PuzzleGenerator
from app.models.settings import GenerationConfig, Difficulty, SudokuType
from tests.strict_validator import SudokuValidator

def run_verification():
    print("="*60, flush=True)
    print("STRICT SUDOKU VERIFICATION SUITE", flush=True)
    print("="*60, flush=True)
    
    generator = PuzzleGenerator()
    validator = SudokuValidator()
    
    # Define test cases: (SudokuType, Size)
    # Move Jigsaw types to the end as they might be slower
    test_cases = [
        (SudokuType.CLASSIC_6X6, 6),
        (SudokuType.ALPHABET_6X6, 6),
        (SudokuType.DIAGONAL_6X6, 6),
        (SudokuType.JIGSAW_6X6, 6),
        (SudokuType.THAI_6X6, 6),
        (SudokuType.CLASSIC_9X9, 9),
        (SudokuType.ALPHABET_9X9, 9),
        (SudokuType.DIAGONAL_9X9, 9),
        (SudokuType.JIGSAW_9X9, 9),
        (SudokuType.EVEN_ODD_9X9, 9),
        (SudokuType.JIGSAW_DIAGONAL_9X9, 9),
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
    print("FINAL REPORT", flush=True)
    print("="*60, flush=True)
    print(f"{'TYPE':<30} | {'STATUS':<10} | {'TIME':<10}", flush=True)
    print("-" * 55, flush=True)
    
    all_passed = True
    for name, data in results.items():
        status = data['status']
        if status != "PASS": all_passed = False
        print(f"{name:<30} | {status:<10} | {data['time']:<10}", flush=True)
        if "error" in data:
            print(f"  -> Error: {data['error']}", flush=True)
            
    print("-" * 55, flush=True)
    if all_passed:
        print("✅ ALL TESTS PASSED! The generator is strictly valid.", flush=True)
    else:
        print("❌ SOME TESTS FAILED. Please review the errors.", flush=True)

if __name__ == "__main__":
    run_verification()
