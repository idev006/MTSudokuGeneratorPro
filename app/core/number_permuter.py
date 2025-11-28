import random
from typing import List, Dict, Tuple
from app.models.grid import SudokuGrid

class NumberPermuter:
    """
    Helper class to generate new puzzles by permuting numbers of an existing solution.
    """
    
    def permute_grid(self, grid: List[List[int]]) -> List[List[int]]:
        """
        Permutes the numbers in a grid (1-9) to create a mathematically equivalent grid.
        
        Args:
            grid: 2D list of integers (0 for empty, 1-9 for values)
            
        Returns:
            New 2D list with permuted numbers
        """
        if not grid:
            return []
            
        size = len(grid)
        # Create a random mapping for numbers 1..size
        numbers = list(range(1, size + 1))
        shuffled = numbers.copy()
        random.shuffle(shuffled)
        
        mapping = {original: new for original, new in zip(numbers, shuffled)}
        # 0 maps to 0 (empty)
        mapping[0] = 0
        
        new_grid = [[mapping[cell] for cell in row] for row in grid]
        return new_grid

    def permute_solution(self, solution: List[List[int]]) -> List[List[int]]:
        """Alias for permute_grid, specifically for full solutions."""
        return self.permute_grid(solution)
