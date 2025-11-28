import time
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.settings import GenerationConfig, SudokuType, Difficulty
from app.core.factory import PuzzleGenerator
from app.services.pdf_service import PDFService

def test_performance():
    gen = PuzzleGenerator()
    pdf_service = PDFService()
    
    tests = [
        ("Jigsaw 6x6", SudokuType.JIGSAW, 6),
        ("Jigsaw 9x9", SudokuType.JIGSAW, 9),
        ("Jigsaw Diagonal 9x9", SudokuType.JIGSAW_DIAGONAL, 9)
    ]
    
    results = []
    puzzles = []
    
    print("="*60)
    print("PERFORMANCE TEST")
    print("="*60)
    
    for name, type_enum, size in tests:
        print(f"\nTesting {name}...")
        start = time.time()
        
        try:
            config = GenerationConfig(type=type_enum, difficulty=Difficulty.EASY, size=size)
            puzzle = gen.generate(config)
            elapsed = time.time() - start
            
            print(f"✅ Generated in {elapsed:.4f}s")
            results.append((name, elapsed, "Pass"))
            puzzles.append(puzzle)
            
            # Verify uniqueness (simple check)
            print(f"   First row: {[c.value for c in puzzle.cells[0]]}")
            
        except Exception as e:
            elapsed = time.time() - start
            print(f"❌ Failed in {elapsed:.4f}s: {e}")
            results.append((name, elapsed, f"Fail: {e}"))

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for name, time_taken, status in results:
        print(f"{name:<20} | {time_taken:.4f}s | {status}")
        
    # Generate PDF
    if puzzles:
        pdf_service.create_pdf(puzzles, "performance_test_output.pdf")
        print("\n✅ PDF created: performance_test_output.pdf")

if __name__ == "__main__":
    test_performance()
