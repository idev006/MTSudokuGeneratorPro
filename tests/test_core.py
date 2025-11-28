import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.settings import GenerationConfig, Difficulty
from app.core.factory import PuzzleGenerator
from app.core.solver import SudokuSolver

class TestCoreLogic(unittest.TestCase):
    
    def setUp(self):
        self.generator = PuzzleGenerator()
        self.solver = SudokuSolver()

    def test_generation_validity(self):
        """Test if generated puzzle is valid and has unique solution."""
        config = GenerationConfig(difficulty=Difficulty.EASY)
        grid = self.generator.generate(config)
        
        # 1. Check if grid is not full (has holes)
        self.assertFalse(grid.is_full(), "Generated grid should have empty cells")
        
        # 2. Check if it has unique solution
        solutions = self.solver.count_solutions(grid.clone())
        self.assertEqual(solutions, 1, "Puzzle must have exactly one unique solution")
        
        print(f"\nGenerated Puzzle (9x9 Easy):\n{grid}")

    def test_6x6_generation(self):
        """Test if 6x6 puzzle generation works."""
        from app.models.settings import SudokuType
        config = GenerationConfig(type=SudokuType.STANDARD_6X6, difficulty=Difficulty.EASY)
        grid = self.generator.generate(config)
        
        self.assertEqual(grid.size, 6, "Grid size should be 6")
        self.assertFalse(grid.is_full(), "Generated grid should have empty cells")
        
        solutions = self.solver.count_solutions(grid.clone())
        self.assertEqual(solutions, 1, "6x6 Puzzle must have exactly one unique solution")
        
        print(f"\nGenerated Puzzle (6x6 Easy):\n{grid}")

    def test_solver_correctness(self):
        """Test if solver can solve a known simple puzzle."""
        # Create a nearly full grid
        config = GenerationConfig(difficulty=Difficulty.EASY)
        grid = self.generator.generate(config)
        
        # Solve it
        solved = self.solver.solve(grid)
        self.assertTrue(solved, "Solver failed to solve a valid puzzle")
        self.assertTrue(grid.is_full(), "Grid should be full after solving")

if __name__ == '__main__':
    unittest.main()
