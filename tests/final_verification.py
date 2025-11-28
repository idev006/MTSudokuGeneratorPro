import time
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.settings import GenerationConfig, SudokuType, Difficulty
from app.core.factory import PuzzleGenerator
from app.services.pdf_service import PDFService

def run_comprehensive_test():
    print("="*80)
    print(f"STARTING COMPREHENSIVE TEST - {datetime.now()}")
    print("="*80)
    
    gen = PuzzleGenerator()
    pdf_service = PDFService()
    
    test_cases = [
        ("TC01", "Classic 9x9", SudokuType.STANDARD_9X9, 9),
        ("TC02", "Classic 6x6", SudokuType.STANDARD_6X6, 6),
        # ("TC03", "Classic 12x12", SudokuType.STANDARD_12X12, 12), # Removed support
        ("TC04", "Diagonal", SudokuType.DIAGONAL, 9),
        ("TC05", "Windoku", SudokuType.WINDOKU, 9),
        ("TC06", "Asterisk", SudokuType.ASTERISK, 9),
        ("TC07", "Consecutive", SudokuType.CONSECUTIVE, 9),
        ("TC08", "Even-Odd", SudokuType.EVEN_ODD, 9),
        ("TC09", "Jigsaw 6x6", SudokuType.JIGSAW, 6),
        ("TC10", "Jigsaw 9x9", SudokuType.JIGSAW, 9),
        ("TC11", "Jigsaw+Diagonal", SudokuType.JIGSAW_DIAGONAL, 9),
        ("TC12", "Thai Alphabet", SudokuType.THAI, 9),
        ("TC13", "English Alphabet", SudokuType.ENGLISH, 9),
    ]
    
    results = []
    generated_puzzles = []
    
    for tc_id, name, type_enum, size in test_cases:
        print(f"\nRunning {tc_id}: {name} (Size {size})...")
        start_time = time.time()
        status = "FAIL"
        note = ""
        
        try:
            # Configure
            config = GenerationConfig(type=type_enum, difficulty=Difficulty.EASY, size=size)
            
            # Generate
            puzzle = gen.generate(config)
            
            # Validate basic structure
            if len(puzzle.cells) == size and len(puzzle.cells[0]) == size:
                status = "PASS"
                generated_puzzles.append(puzzle)
            else:
                status = "FAIL"
                note = "Invalid grid size"
                
        except Exception as e:
            status = "ERROR"
            note = str(e)
            
        elapsed = time.time() - start_time
        print(f"  Result: {status} ({elapsed:.4f}s) {note}")
        results.append({
            "id": tc_id,
            "name": name,
            "status": status,
            "time": elapsed,
            "note": note
        })
        
    # Generate PDF Report
    print("\nGenerating PDF Report...")
    try:
        pdf_filename = "final_test_result.pdf"
        pdf_service.create_pdf(generated_puzzles, pdf_filename)
        print(f"✅ PDF Report created: {pdf_filename}")
    except Exception as e:
        print(f"❌ Failed to create PDF: {e}")

    # Save Markdown Report
    save_report(results)

def save_report(results):
    report_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'doc', 'test_report_final.md')
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Final Test Report: Sudoku Generator Pro\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("| ID | Test Case | Status | Time (s) | Note |\n")
        f.write("|----|-----------|--------|----------|------|\n")
        
        total_pass = 0
        total_time = 0
        
        for r in results:
            icon = "✅" if r['status'] == "PASS" else "❌"
            f.write(f"| {r['id']} | {r['name']} | {icon} {r['status']} | {r['time']:.4f} | {r['note']} |\n")
            if r['status'] == "PASS":
                total_pass += 1
            total_time += r['time']
            
        f.write(f"\n**Summary:**\n")
        f.write(f"- Total Tests: {len(results)}\n")
        f.write(f"- Passed: {total_pass}\n")
        f.write(f"- Failed: {len(results) - total_pass}\n")
        f.write(f"- Total Execution Time: {total_time:.4f}s\n")
        
    print(f"\n✅ Markdown Report saved: {report_path}")

if __name__ == "__main__":
    run_comprehensive_test()
