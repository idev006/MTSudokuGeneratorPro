import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.settings import GenerationConfig, SudokuType, Difficulty
from app.core.factory import PuzzleGenerator
from app.services.pdf_service import PDFService

class TestVariants(unittest.TestCase):
    def setUp(self):
        self.generator = PuzzleGenerator()
        self.pdf_service = PDFService()
        self.test_file = "test_variants.pdf"

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_consecutive_generation(self):
        # Generate Consecutive Sudoku
        config = GenerationConfig(
            type=SudokuType.CONSECUTIVE,
            difficulty=Difficulty.EASY,
            size=9
        )
        grid = self.generator.generate(config)
        
        # Verify pairs exist
        self.assertTrue(len(grid.consecutive_pairs) > 0)
        
        # Verify correctness
        for (r1, c1), (r2, c2) in grid.consecutive_pairs:
            val1 = grid.solution[r1][c1]
            val2 = grid.solution[r2][c2]
            self.assertEqual(abs(val1 - val2), 1, f"Pair {val1}-{val2} at ({r1},{c1})-({r2},{c2}) is not consecutive")

        # Generate PDF
        self.pdf_service.create_pdf([grid], "test_consecutive.pdf")
        self.assertTrue(os.path.exists("test_consecutive.pdf"))

    def test_even_odd_generation(self):
        # Generate Even-Odd Sudoku
        config = GenerationConfig(
            type=SudokuType.EVEN_ODD,
            difficulty=Difficulty.EASY,
            size=9
        )
        grid = self.generator.generate(config)
        
        # Verify mask exists
        self.assertTrue(len(grid.even_odd_mask) > 0)
        
        # Verify correctness
        for r in range(grid.size):
            for c in range(grid.size):
                val = grid.solution[r][c]
                is_even_masked = grid.even_odd_mask[r][c]
                self.assertEqual(val % 2 == 0, is_even_masked, f"Value {val} at ({r},{c}) does not match mask {is_even_masked}")

        # Generate PDF
        self.pdf_service.create_pdf([grid], "test_even_odd.pdf")
        self.assertTrue(os.path.exists("test_even_odd.pdf"))

if __name__ == '__main__':
    unittest.main()
