import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.settings import GenerationConfig, SudokuType, Difficulty
from app.core.factory import PuzzleGenerator
from app.services.pdf_service import PDFService

class TestAdvancedFeatures(unittest.TestCase):
    def setUp(self):
        self.generator = PuzzleGenerator()
        self.pdf_service = PDFService()
        self.test_file = "test_advanced.pdf"

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_thai_sudoku_pdf(self):
        # Generate a Thai Sudoku
        config = GenerationConfig(
            type=SudokuType.THAI,
            difficulty=Difficulty.EASY,
            size=9
        )
        grid = self.generator.generate(config)
        
        # Verify type name
        # Verify type
        self.assertIn("thai", grid.type_name.lower())
        
        # Verify solution is captured
        self.assertIsNotNone(grid.solution)
        
        # Generate PDF
        self.pdf_service.create_pdf([grid], self.test_file)
        
        # Check file
        self.assertTrue(os.path.exists(self.test_file))
        print(f"Generated Thai PDF size: {os.path.getsize(self.test_file)} bytes")

    def test_windoku_generation(self):
        # Generate Windoku
        config = GenerationConfig(
            type=SudokuType.WINDOKU,
            difficulty=Difficulty.EASY,
            size=9
        )
        grid = self.generator.generate(config)
        
        # Verify constraints
        has_windoku = any("WindokuConstraint" in str(type(c)) for c in grid.constraints)
        self.assertTrue(has_windoku)

    def test_12x12_generation(self):
        # Generate 12x12
        config = GenerationConfig(
            type=SudokuType.STANDARD_12X12,
            difficulty=Difficulty.EASY,
            size=12
        )
        grid = self.generator.generate(config)
        self.assertEqual(grid.size, 12)
        self.assertIsNotNone(grid.solution)
        
        # PDF
        self.pdf_service.create_pdf([grid], "test_12x12.pdf")
        self.assertTrue(os.path.exists("test_12x12.pdf"))
        print(f"Generated 12x12 PDF size: {os.path.getsize('test_12x12.pdf')} bytes")

if __name__ == '__main__':
    unittest.main()
