import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.factory import PuzzleGenerator
from app.models.settings import GenerationConfig, Difficulty, SudokuType

def verify_jigsaw_diagonal_speed():
    print("="*60)
    print("VERIFYING JIGSAW DIAGONAL SPEED")
    print("="*60)
    
    generator = PuzzleGenerator()
    types_to_test = [
        SudokuType.JIGSAW_DIAGONAL_9X9,
        SudokuType.JIGSAW_9X9,
        SudokuType.DIAGONAL_9X9,
        SudokuType.WINDOKU_9X9
    ]
    
    for stype in types_to_test:
        print(f"\nGenerating {stype.name}...")
        config = GenerationConfig(type=stype, difficulty=Difficulty.EASY)
        
        start_time = time.time()
        try:
            grid = generator.generate(config)
            duration = time.time() - start_time
            print(f"✅ Generated in {duration:.2f}s")
            
            if duration > 1.0:
                print(f"⚠️ {stype.name} is still slow! (> 1s)")
            else:
                print(f"🚀 {stype.name} is FAST! (< 1s)")
                
        except Exception as e:
            print(f"❌ Generation FAILED: {e}")

if __name__ == "__main__":
    verify_jigsaw_diagonal_speed()
