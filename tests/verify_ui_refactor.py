import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.settings import GenerationConfig, SudokuType, Difficulty
from app.core.factory import PuzzleGenerator

def verify_config_auto_size():
    print("="*60)
    print("VERIFYING CONFIG AUTO-SIZE")
    print("="*60)
    
    test_cases = [
        (SudokuType.CLASSIC_6X6, 6),
        (SudokuType.ALPHABET_6X6, 6),
        (SudokuType.CLASSIC_9X9, 9),
        (SudokuType.JIGSAW_9X9, 9),
        (SudokuType.ASTERISK_9X9, 9),
        (SudokuType.THAI_6X6, 6),
    ]
    
    for stype, expected_size in test_cases:
        config = GenerationConfig(type=stype)
        print(f"Type: {stype.value:<30} | Expected Size: {expected_size} | Actual Size: {config.size}")
        if config.size != expected_size:
            print(f"❌ FAILED: Size mismatch for {stype.value}")
            return False
    
    print("✅ All config size tests passed.")
    return True

def verify_generation():
    print("\n" + "="*60)
    print("VERIFYING GENERATION (Smoke Test)")
    print("="*60)
    
    generator = PuzzleGenerator()
    
    # Test a few types
    types_to_test = [
        SudokuType.CLASSIC_6X6,
        SudokuType.CLASSIC_9X9,
        # SudokuType.JIGSAW_9X9 # Skip Jigsaw for speed if needed, or include
    ]
    
    for stype in types_to_test:
        print(f"Generating {stype.value}...")
        config = GenerationConfig(type=stype, difficulty=Difficulty.EASY)
        try:
            start = time.time()
            grid = generator.generate(config)
            duration = time.time() - start
            print(f"✅ Generated in {duration:.2f}s")
            
            if grid.size != config.size:
                print(f"❌ Grid size mismatch! Expected {config.size}, got {grid.size}")
                return False
                
        except Exception as e:
            print(f"❌ Generation FAILED: {e}")
            return False
            
    print("✅ Generation smoke tests passed.")
    return True

if __name__ == "__main__":
    if verify_config_auto_size() and verify_generation():
        print("\n✅✅✅ UI REFACTOR VERIFIED SUCCESSFULLY ✅✅✅")
    else:
        print("\n❌❌❌ VERIFICATION FAILED ❌❌❌")
        sys.exit(1)
