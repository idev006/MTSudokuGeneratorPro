import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.factory import PuzzleGenerator
from app.models.settings import GenerationConfig, Difficulty, SudokuType
from tests.strict_validator import SudokuValidator

def verify_jigsaw_diagonal():
    print("="*60, flush=True)
    print("VERIFYING JIGSAW DIAGONAL ONLY", flush=True)
    print("="*60, flush=True)
    
    generator = PuzzleGenerator()
    validator = SudokuValidator()
    
    config = GenerationConfig(
        size=9,
        difficulty=Difficulty.EASY,
        type=SudokuType.JIGSAW_DIAGONAL
    )
    
    print("Generating Jigsaw Diagonal (this may take time)...", flush=True)
    start_time = time.time()
    try:
        grid = generator.generate(config)
        gen_time = time.time() - start_time
        print(f"Generation complete in {gen_time:.2f}s", flush=True)
        
        is_valid = validator.validate(grid, config)
        
        if is_valid:
            print("✅ JIGSAW DIAGONAL PASSED!", flush=True)
        else:
            print("❌ JIGSAW DIAGONAL FAILED!", flush=True)
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}", flush=True)

if __name__ == "__main__":
    verify_jigsaw_diagonal()
