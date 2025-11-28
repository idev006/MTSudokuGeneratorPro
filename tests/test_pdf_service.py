import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.grid import SudokuGrid
from app.services.pdf_service import PDFService

class TestPDFService(unittest.TestCase):
    def setUp(self):
        self.pdf_service = PDFService()
        self.test_file = "test_output.pdf"

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_create_pdf(self):
        # Create dummy puzzles
        puzzles = [SudokuGrid(size=9) for _ in range(3)]
        
        # Generate PDF
        self.pdf_service.create_pdf(puzzles, self.test_file)
        
        # Check if file exists and has content
        self.assertTrue(os.path.exists(self.test_file))
        self.assertGreater(os.path.getsize(self.test_file), 0)
        print(f"Generated PDF size: {os.path.getsize(self.test_file)} bytes")

if __name__ == '__main__':
    unittest.main()
