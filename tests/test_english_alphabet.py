import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.settings import GenerationConfig, SudokuType, Difficulty
from app.core.factory import PuzzleGenerator
from app.services.pdf_service import PDFService

class TestEnglishAlphabet(unittest.TestCase):
    def setUp(self):
        self.generator = PuzzleGenerator()
        self.pdf_service = PDFService()
        self.test_file = "test_english.pdf"

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_english_sudoku_pdf(self):
        # Generate English Sudoku
        config = GenerationConfig(
            type=SudokuType.ENGLISH,
            difficulty=Difficulty.EASY,
            size=9
        )
        grid = self.generator.generate(config)
        
        # Verify type name
        self.assertIn("english", grid.type_name.lower())
        
        # Generate PDF
        self.pdf_service.create_pdf([grid], self.test_file)
        
        # Check file
        self.assertTrue(os.path.exists(self.test_file))
        print(f"Generated English PDF size: {os.path.getsize(self.test_file)} bytes")

if __name__ == '__main__':
    unittest.main()
