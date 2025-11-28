import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.factory import PuzzleGenerator
from app.models.settings import GenerationConfig, Difficulty, SudokuType
from tests.strict_validator import SudokuValidator

def verify_static_templates():
    print("="*60)
    print("VERIFYING STATIC TEMPLATES SPEED & VALIDITY")
    print("="*60)
    
    generator = PuzzleGenerator()
    validator = SudokuValidator()
    
    types = [SudokuType.WINDOKU_9X9, SudokuType.ASTERISK_9X9]
    
    for stype in types:
        print(f"\nTesting {stype.name}...")
        config = GenerationConfig(type=stype, difficulty=Difficulty.EASY)
        
        start_time = time.time()
        try:
            grid = generator.generate(config)
            duration = time.time() - start_time
            print(f"✅ Generated in {duration:.4f}s")
            
            if duration > 0.05:
                print("⚠️ Slower than expected for template (should be ~0.00s)")
            else:
                print("🚀 INSTANT! (< 0.05s)")
                
            # Validate
            if validator.validate(grid, config):
                print("✅ VALID")
            else:
                print("❌ INVALID")
                
        except Exception as e:
            print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    verify_static_templates()
