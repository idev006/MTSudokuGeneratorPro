"""
Test with fresh Python process
"""
import subprocess
import sys

code = """
# Clear any cached instances
import sys
sys.path.insert(0, 'd:/dev/MTSudokuGeneratorPro')

from app.core.geometry import GeometryFactory

# Clear instance
GeometryFactory.clear_instance()

# Get fresh map
factory = GeometryFactory()
grid = factory.get_jigsaw_map(9)

# Check
print("Jigsaw Region Map:")
for r in range(9):
    print(" ".join(str(grid[r][c]) for c in range(9)))

# Check if irregular
is_irregular = False
for r in range(9):
    for c in range(9):
        rid = grid[r][c]
        expected_box = (r // 3) * 3 + (c // 3)
        if rid != expected_box:
            is_irregular = True
            break
    if is_irregular:
        break

if is_irregular:
    print("\\n✅ IRREGULAR REGIONS!")
else:
    print("\\n❌ STANDARD BOXES")
"""

result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
