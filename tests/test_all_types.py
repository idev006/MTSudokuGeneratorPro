"""
Complete Test Script - Generate All Sudoku Types
ทดสอบการสร้างซูโดกุทุกประเภท ทุกขนาด
"""
import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.settings import GenerationConfig, SudokuType, Difficulty
from app.core.factory import PuzzleGenerator
from app.services.pdf_service import PDFService

def test_all_sudoku_types():
    """ทดสอบการสร้างซูโดกุทุกประเภท"""
    print("="*70)
    print("COMPLETE SUDOKU GENERATION TEST")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    generator = PuzzleGenerator()
    pdf_service = PDFService()
    
    # Define all test cases
    test_cases = [
        # Standard Sizes
        ("Classic 6x6", SudokuType.STANDARD_9X9, 6, 12),
        ("Classic 9x9", SudokuType.STANDARD_9X9, 9, 8),
        ("Classic 12x12", SudokuType.STANDARD_9X9, 12, 4),
        
        # Jigsaw
        ("Jigsaw 9x9", SudokuType.JIGSAW, 9, 6),
        
        # Constraint Types
        ("Diagonal 9x9", SudokuType.DIAGONAL, 9, 6),
        ("Windoku 9x9", SudokuType.WINDOKU, 9, 6),
        ("Asterisk 9x9", SudokuType.ASTERISK, 9, 6),
        
        # Logic Types
        ("Consecutive 9x9", SudokuType.CONSECUTIVE, 9, 6),
        ("Even-Odd 9x9", SudokuType.EVEN_ODD, 9, 6),
        
        # Alphabet Types
        ("Thai Alphabet 9x9", SudokuType.THAI, 9, 6),
        ("English Alphabet 9x9", SudokuType.ENGLISH, 9, 6),
        
        # Combo
        ("Jigsaw+Diagonal 9x9", SudokuType.JIGSAW_DIAGONAL, 9, 4),
    ]
    
    results = []
    total_tests = len(test_cases)
    passed = 0
    failed = 0
    
    for idx, (name, sudoku_type, size, count) in enumerate(test_cases, 1):
        print(f"\n[{idx}/{total_tests}] Testing: {name}")
        print("-" * 70)
        
        try:
            # Generate puzzles
            print(f"  Generating {count} puzzles...")
            config = GenerationConfig(
                type=sudoku_type,
                difficulty=Difficulty.EASY,
                size=size
            )
            
            puzzles = []
            for i in range(count):
                puzzle = generator.generate(config)
                puzzles.append(puzzle)
                print(f"    [{i+1}/{count}] Generated", end="\r")
            
            print(f"    [{count}/{count}] Generated ✓")
            
            # Create PDF
            filename = f"test_all_{name.lower().replace(' ', '_').replace('+', '_')}.pdf"
            print(f"  Creating PDF: {filename}...")
            pdf_service.create_pdf(puzzles, filename)
            
            file_size = os.path.getsize(filename)
            print(f"  ✅ SUCCESS - File size: {file_size:,} bytes")
            
            results.append({
                "name": name,
                "status": "PASS",
                "count": count,
                "file": filename,
                "size": file_size
            })
            passed += 1
            
        except Exception as e:
            print(f"  ❌ FAILED - Error: {str(e)}")
            results.append({
                "name": name,
                "status": "FAIL",
                "error": str(e)
            })
            failed += 1
    
    # Print Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Pass Rate: {(passed/total_tests*100):.1f}%")
    
    # Print Details
    print("\n" + "="*70)
    print("DETAILED RESULTS")
    print("="*70)
    
    for result in results:
        if result["status"] == "PASS":
            print(f"\n✅ {result['name']}")
            print(f"   Puzzles: {result['count']}")
            print(f"   File: {result['file']}")
            print(f"   Size: {result['size']:,} bytes")
        else:
            print(f"\n❌ {result['name']}")
            print(f"   Error: {result['error']}")
    
    # List all generated files
    print("\n" + "="*70)
    print("GENERATED FILES")
    print("="*70)
    pdf_files = [r['file'] for r in results if r['status'] == 'PASS']
    for i, file in enumerate(pdf_files, 1):
        print(f"{i:2d}. {file}")
    
    print(f"\n✅ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    return failed == 0

if __name__ == "__main__":
    success = test_all_sudoku_types()
    sys.exit(0 if success else 1)
