"""
Debug script to visualize Jigsaw regions
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.settings import GenerationConfig, SudokuType, Difficulty
from app.core.factory import PuzzleGenerator

# Generate a Jigsaw puzzle
generator = PuzzleGenerator()
config = GenerationConfig(type=SudokuType.JIGSAW, difficulty=Difficulty.EASY, size=9)
grid = generator.generate(config)

print("Jigsaw Region Map:")
print("=" * 40)

# Print region IDs
for r in range(9):
    row_str = ""
    for c in range(9):
        region_id = grid.cells[r][c].region_id
        if region_id is None:
            row_str += "X "
        else:
            row_str += f"{region_id} "
    print(row_str)

print("\n" + "=" * 40)

# Count cells per region
region_counts = {}
for r in range(9):
    for c in range(9):
        region_id = grid.cells[r][c].region_id
        if region_id is not None:
            region_counts[region_id] = region_counts.get(region_id, 0) + 1

print("Region sizes:")
for region_id in sorted(region_counts.keys()):
    print(f"  Region {region_id}: {region_counts[region_id]} cells")

# Check if all regions have 9 cells
all_valid = all(count == 9 for count in region_counts.values())
print(f"\nAll regions have 9 cells: {all_valid}")

if not all_valid:
    print("❌ PROBLEM: Not all regions have 9 cells!")
else:
    print("✅ All regions are valid")
