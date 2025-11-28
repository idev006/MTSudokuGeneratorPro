import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.settings import GenerationConfig, SudokuType, Difficulty
from app.core.factory import PuzzleGenerator
from app.services.pdf_service import PDFService

class TestJigsaw(unittest.TestCase):
    def setUp(self):
        self.generator = PuzzleGenerator()
        self.pdf_service = PDFService()
        self.test_file = "test_jigsaw.pdf"

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_jigsaw_generation(self):
        # Generate Jigsaw Sudoku
        config = GenerationConfig(
            type=SudokuType.JIGSAW,
            difficulty=Difficulty.EASY,
            size=9
        )
        grid = self.generator.generate(config)
        
        # Verify type name
        self.assertIn("jigsaw", grid.type_name.lower())
        
        # Verify regions are assigned
        regions = set()
        for r in range(grid.size):
            for c in range(grid.size):
                regions.add(grid.cells[r][c].region_id)
        
        # Should have 9 regions (0-8)
        self.assertEqual(len(regions), 9)
        self.assertEqual(max(regions), 8)
        self.assertEqual(min(regions), 0)
        
        # Verify solution validity (Constraint check)
        # Check if numbers are unique in each region
        for region_id in range(9):
            values = []
            for r in range(grid.size):
                for c in range(grid.size):
                    if grid.cells[r][c].region_id == region_id:
                        val = grid.solution[r][c]
                        values.append(val)
            
            # Filter 0s (should be none in solution)
            values = [v for v in values if v != 0]
            self.assertEqual(len(values), 9)
            self.assertEqual(len(set(values)), 9, f"Region {region_id} has duplicates: {values}")

        # Generate PDF
        self.pdf_service.create_pdf([grid], self.test_file)
        
        # Check file
        self.assertTrue(os.path.exists(self.test_file))
        print(f"Generated Jigsaw PDF size: {os.path.getsize(self.test_file)} bytes")

if __name__ == '__main__':
    unittest.main()
