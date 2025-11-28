import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.grid import SudokuGrid
from app.models.settings import GenerationConfig, Difficulty, SudokuType
from tests.strict_validator import SudokuValidator

def verify_template_001():
    print("Verifying template_001.json...")
    
    template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', 'templates', 'jigsaw_9x9', 'template_001.json'))
    
    with open(template_path, 'r') as f:
        data = json.load(f)
        
    grid = SudokuGrid(size=9)
    grid.type_name = "jigsaw_9x9"
    grid.apply_region_map(data['regions'])
    
    # Load solution
    grid.solution = data['solution']
    for r in range(9):
        for c in range(9):
            grid.cells[r][c].value = data['solution'][r][c]
            
    validator = SudokuValidator()
    config = GenerationConfig(type=SudokuType.JIGSAW_9X9, difficulty=Difficulty.EASY)
    
    if validator.validate(grid, config):
        print("✅ template_001 is VALID")
    else:
        print("❌ template_001 is INVALID")

if __name__ == "__main__":
    verify_template_001()
