"""
Comprehensive System Test Script
ทดสอบระบบทั้งหมด พร้อมบันทึกผลและปัญหา
"""
import unittest
import sys
import os
import json
from datetime import datetime
from io import StringIO

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.settings import GenerationConfig, SudokuType, Difficulty
from app.core.factory import PuzzleGenerator
from app.core.solver import SudokuSolver
from app.services.pdf_service import PDFService

class SystemTestRunner:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "issues": [],
            "summary": {}
        }
        self.generator = PuzzleGenerator()
        self.solver = SudokuSolver()
        self.pdf_service = PDFService()
        
    def log_test(self, name, status, details="", error=None):
        """บันทึกผลการทดสอบ"""
        test_result = {
            "name": name,
            "status": status,
            "details": details,
            "error": str(error) if error else None
        }
        self.results["tests"].append(test_result)
        
        if status == "FAILED":
            self.results["issues"].append({
                "test": name,
                "error": str(error),
                "details": details
            })
    
    def test_all_sizes(self):
        """ทดสอบทุกขนาดตาราง"""
        print("\n" + "="*60)
        print("TEST 1: Grid Sizes (6x6 to 15x15)")
        print("="*60)
        
        sizes = [6, 8, 9, 10, 12, 14, 15]
        
        for size in sizes:
            try:
                config = GenerationConfig(
                    type=SudokuType.STANDARD_9X9,
                    difficulty=Difficulty.EASY,
                    size=size
                )
                grid = self.generator.generate(config)
                
                # Verify
                assert grid.size == size, f"Grid size mismatch: {grid.size} != {size}"
                assert grid.solution is not None, "Solution is None"
                assert len(grid.solution) == size, "Solution size mismatch"
                
                print(f"  ✅ {size}x{size} - PASSED")
                self.log_test(f"Grid Size {size}x{size}", "PASSED", 
                            f"Generated and solved {size}x{size} grid successfully")
                
            except Exception as e:
                print(f"  ❌ {size}x{size} - FAILED: {str(e)}")
                self.log_test(f"Grid Size {size}x{size}", "FAILED", 
                            f"Failed to generate {size}x{size} grid", e)
    
    def test_all_types(self):
        """ทดสอบทุกประเภทซูโดกุ"""
        print("\n" + "="*60)
        print("TEST 2: Sudoku Types")
        print("="*60)
        
        types = [
            (SudokuType.STANDARD_9X9, "Classic 9x9"),
            (SudokuType.JIGSAW, "Jigsaw"),
            (SudokuType.DIAGONAL, "Diagonal"),
            (SudokuType.WINDOKU, "Windoku"),
            (SudokuType.ASTERISK, "Asterisk"),
            (SudokuType.CONSECUTIVE, "Consecutive"),
            (SudokuType.EVEN_ODD, "Even-Odd"),
            (SudokuType.THAI, "Thai Alphabet"),
            (SudokuType.ENGLISH, "English Alphabet"),
            (SudokuType.JIGSAW_DIAGONAL, "Jigsaw + Diagonal")
        ]
        
        for sudoku_type, name in types:
            try:
                config = GenerationConfig(
                    type=sudoku_type,
                    difficulty=Difficulty.EASY,
                    size=9
                )
                grid = self.generator.generate(config)
                
                # Verify basic properties
                assert grid.solution is not None, "Solution is None"
                
                # Type-specific checks
                if "jigsaw" in sudoku_type.value.lower():
                    assert any(cell.region_id is not None for row in grid.cells for cell in row), \
                        "Jigsaw regions not assigned"
                
                if "consecutive" in sudoku_type.value.lower():
                    assert len(grid.consecutive_pairs) > 0, "No consecutive pairs found"
                
                if "even" in sudoku_type.value.lower() and "odd" in sudoku_type.value.lower():
                    assert len(grid.even_odd_mask) > 0, "Even-Odd mask not generated"
                
                print(f"  ✅ {name} - PASSED")
                self.log_test(f"Type: {name}", "PASSED", 
                            f"Generated {name} successfully with all features")
                
            except Exception as e:
                print(f"  ❌ {name} - FAILED: {str(e)}")
                self.log_test(f"Type: {name}", "FAILED", 
                            f"Failed to generate {name}", e)
    
    def test_all_difficulties(self):
        """ทดสอบทุกระดับความยาก"""
        print("\n" + "="*60)
        print("TEST 3: Difficulty Levels")
        print("="*60)
        
        difficulties = [
            Difficulty.EASY,
            Difficulty.MEDIUM,
            Difficulty.HARD,
            Difficulty.EXPERT,
            Difficulty.DEVIL
        ]
        
        for diff in difficulties:
            try:
                config = GenerationConfig(
                    type=SudokuType.STANDARD_9X9,
                    difficulty=diff,
                    size=9
                )
                grid = self.generator.generate(config)
                
                # Count empty cells
                empty_count = sum(1 for row in grid.cells for cell in row if cell.value == 0)
                total_cells = grid.size * grid.size
                empty_ratio = empty_count / total_cells
                
                print(f"  ✅ {diff.value.upper()} - PASSED (Empty: {empty_count}/{total_cells} = {empty_ratio:.2%})")
                self.log_test(f"Difficulty: {diff.value}", "PASSED", 
                            f"Empty ratio: {empty_ratio:.2%}")
                
            except Exception as e:
                print(f"  ❌ {diff.value.upper()} - FAILED: {str(e)}")
                self.log_test(f"Difficulty: {diff.value}", "FAILED", 
                            f"Failed to generate {diff.value} difficulty", e)
    
    def test_pdf_generation(self):
        """ทดสอบการสร้าง PDF"""
        print("\n" + "="*60)
        print("TEST 4: PDF Generation")
        print("="*60)
        
        test_cases = [
            (SudokuType.STANDARD_9X9, "standard_test.pdf"),
            (SudokuType.JIGSAW, "jigsaw_test.pdf"),
            (SudokuType.THAI, "thai_test.pdf"),
            (SudokuType.CONSECUTIVE, "consecutive_test.pdf"),
        ]
        
        for sudoku_type, filename in test_cases:
            try:
                config = GenerationConfig(
                    type=sudoku_type,
                    difficulty=Difficulty.EASY,
                    size=9
                )
                grid = self.generator.generate(config)
                
                # Generate PDF
                self.pdf_service.create_pdf([grid], filename)
                
                # Verify file exists
                assert os.path.exists(filename), f"PDF file {filename} not created"
                file_size = os.path.getsize(filename)
                
                print(f"  ✅ {sudoku_type.value} - PASSED (Size: {file_size} bytes)")
                self.log_test(f"PDF: {sudoku_type.value}", "PASSED", 
                            f"PDF created successfully ({file_size} bytes)")
                
                # Cleanup
                os.remove(filename)
                
            except Exception as e:
                print(f"  ❌ {sudoku_type.value} - FAILED: {str(e)}")
                self.log_test(f"PDF: {sudoku_type.value}", "FAILED", 
                            f"Failed to create PDF", e)
    
    def test_solver_correctness(self):
        """ทดสอบความถูกต้องของ Solver"""
        print("\n" + "="*60)
        print("TEST 5: Solver Correctness")
        print("="*60)
        
        test_types = [
            SudokuType.STANDARD_9X9,
            SudokuType.JIGSAW,
            SudokuType.DIAGONAL,
            SudokuType.WINDOKU
        ]
        
        for sudoku_type in test_types:
            try:
                config = GenerationConfig(
                    type=sudoku_type,
                    difficulty=Difficulty.EASY,
                    size=9
                )
                grid = self.generator.generate(config)
                
                # Verify solution is valid
                solution = grid.solution
                
                # Check rows
                for row in solution:
                    assert len(set(row)) == len(row), "Duplicate in row"
                
                # Check columns
                for c in range(len(solution)):
                    col = [solution[r][c] for r in range(len(solution))]
                    assert len(set(col)) == len(col), "Duplicate in column"
                
                print(f"  ✅ {sudoku_type.value} - PASSED")
                self.log_test(f"Solver: {sudoku_type.value}", "PASSED", 
                            "Solution verified (no duplicates in rows/cols)")
                
            except Exception as e:
                print(f"  ❌ {sudoku_type.value} - FAILED: {str(e)}")
                self.log_test(f"Solver: {sudoku_type.value}", "FAILED", 
                            "Solution validation failed", e)
    
    def run_all_tests(self):
        """รันการทดสอบทั้งหมด"""
        print("\n" + "="*60)
        print("COMPREHENSIVE SYSTEM TEST")
        print("="*60)
        print(f"Started at: {self.results['timestamp']}")
        
        # Run all test suites
        self.test_all_sizes()
        self.test_all_types()
        self.test_all_difficulties()
        self.test_pdf_generation()
        self.test_solver_correctness()
        
        # Calculate summary
        total_tests = len(self.results["tests"])
        passed_tests = sum(1 for t in self.results["tests"] if t["status"] == "PASSED")
        failed_tests = total_tests - passed_tests
        
        self.results["summary"] = {
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "pass_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
        }
        
        # Print summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Pass Rate: {self.results['summary']['pass_rate']}")
        
        if failed_tests > 0:
            print("\n" + "="*60)
            print("ISSUES FOUND")
            print("="*60)
            for issue in self.results["issues"]:
                print(f"\n❌ {issue['test']}")
                print(f"   Error: {issue['error']}")
                print(f"   Details: {issue['details']}")
        
        # Save results to file
        self.save_results()
        
        return failed_tests == 0
    
    def save_results(self):
        """บันทึกผลการทดสอบ"""
        results_file = "test_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📝 Results saved to: {results_file}")

if __name__ == "__main__":
    runner = SystemTestRunner()
    success = runner.run_all_tests()
    
    sys.exit(0 if success else 1)
