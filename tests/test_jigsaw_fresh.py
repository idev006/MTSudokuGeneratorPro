"""
Fresh test - import everything fresh
"""
import subprocess
import sys

# Run in subprocess to ensure fresh imports
code = """
from app.models.settings import GenerationConfig, SudokuType, Difficulty
from app.core.factory import PuzzleGenerator
from app.services.pdf_service import PDFService

gen = PuzzleGenerator()
pdf = PDFService()

# Generate Jigsaw 9x9
config = GenerationConfig(type=SudokuType.JIGSAW, difficulty=Difficulty.EASY, size=9)
puzzle = gen.generate(config)

# Check regions
print("Jigsaw Region Map:")
print("=" * 40)
for r in range(9):
    row_str = ""
    for c in range(9):
        region_id = puzzle.cells[r][c].region_id
        if region_id is None:
            row_str += "X "
        else:
            row_str += f"{region_id} "
    print(row_str)

# Count
region_counts = {}
for r in range(9):
    for c in range(9):
        rid = puzzle.cells[r][c].region_id
        if rid is not None:
            region_counts[rid] = region_counts.get(rid, 0) + 1

print("\\nRegion sizes:")
for rid in sorted(region_counts.keys()):
    print(f"  Region {rid}: {region_counts[rid]} cells")

# Check if irregular
is_irregular = False
for r in range(9):
    for c in range(9):
        rid = puzzle.cells[r][c].region_id
        expected_box = (r // 3) * 3 + (c // 3)
        if rid != expected_box:
            is_irregular = True
            break

if is_irregular:
    print("\\n✅ IRREGULAR REGIONS - Jigsaw working!")
else:
    print("\\n❌ STANDARD BOXES - Still using fallback")

# Create PDF
puzzles = [gen.generate(config) for _ in range(2)]
pdf.create_pdf(puzzles, 'jigsaw_fresh_test.pdf')
print("\\n✅ Created jigsaw_fresh_test.pdf")
"""

result = subprocess.run(
    [sys.executable, "-c", code],
    cwd="d:/dev/MTSudokuGeneratorPro",
    capture_output=True,
    text=True
)

print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
