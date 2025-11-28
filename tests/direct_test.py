"""
Direct test of GeometryFactory
"""
import sys
sys.path.insert(0, 'd:/dev/MTSudokuGeneratorPro')

from app.core.geometry import GeometryFactory

factory = GeometryFactory()

print("Testing get_jigsaw_map(9)...")
grid = factory.get_jigsaw_map(9)

print("\nResult:")
for r in range(9):
    print(" ".join(str(grid[r][c]) for c in range(9)))

# Check
is_irregular = False
for r in range(9):
    for c in range(9):
        rid = grid[r][c]
        expected_box = (r // 3) * 3 + (c // 3)
        if rid != expected_box:
            is_irregular = True
            break

if is_irregular:
    print("\n✅ SUCCESS - Irregular regions!")
else:
    print("\n❌ FAIL - Standard boxes (fallback used)")
