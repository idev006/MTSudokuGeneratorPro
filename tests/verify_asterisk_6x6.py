import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.factory import PuzzleGenerator
from app.models.settings import GenerationConfig, Difficulty, SudokuType
from tests.strict_validator import SudokuValidator

def verify_asterisk_6x6():
    print("="*60, flush=True)
    print("VERIFYING ASTERISK 6x6 SAFETY", flush=True)
    print("="*60, flush=True)
    
    generator = PuzzleGenerator()
    validator = SudokuValidator()
    
    # Config: Asterisk Type but 6x6 Size
    # The generator should treat this as Standard 6x6 (ignoring Asterisk constraint)
    config = GenerationConfig(
        size=6,
        difficulty=Difficulty.EASY,
        type=SudokuType.ASTERISK
    )
    
    print("Generating Asterisk 6x6 (Should be treated as Standard 6x6)...", flush=True)
    start_time = time.time()
    try:
        grid = generator.generate(config)
        gen_time = time.time() - start_time
        print(f"Generation complete in {gen_time:.2f}s", flush=True)
        
        # Validate as Standard 6x6
        # We need to temporarily change type to STANDARD_6X6 for validator to skip Asterisk check?
        # No, validator calls _check_asterisk if type is ASTERISK.
        # But _check_asterisk in validator checks specific cells.
        # Wait, the validator ALSO needs to know that Asterisk is invalid for 6x6?
        # Or we just check if it's a valid Sudoku.
        
        print("Validating grid structure...", flush=True)
        if grid.size != 6:
            print("❌ Error: Grid size is not 6!", flush=True)
            return

        # Check basic validity (Row, Col, Box)
        # We can use the validator but we might need to suppress the Asterisk check failure 
        # if the validator enforces it strictly.
        # Let's see what the validator does.
        
        is_valid = validator.validate(grid, config)
        
        if is_valid:
             print("✅ ASTERISK 6x6 PASSED (Validator accepted it)", flush=True)
        else:
             print("⚠️ Validator failed (Expected if validator enforces Asterisk on 6x6)", flush=True)
             # If validator fails, it might be because it tries to check Asterisk on 6x6.
             # Let's check if the grid is valid as a STANDARD 6x6
             config.type = SudokuType.STANDARD_6X6
             is_valid_std = validator.validate(grid, config)
             if is_valid_std:
                 print("✅ Grid is a valid STANDARD 6x6 (Fallback successful)", flush=True)
             else:
                 print("❌ Grid is NOT a valid STANDARD 6x6", flush=True)

    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}", flush=True)

if __name__ == "__main__":
    verify_asterisk_6x6()
