from typing import List, Tuple, Optional
from app.models.grid import SudokuGrid, SudokuCell

class SudokuSolver:
    """Core solver logic using Backtracking."""

    def __init__(self):
        self.solution_count = 0

    def is_safe(self, grid: SudokuGrid, row: int, col: int, num: int) -> bool:
        """
        Checks if it's safe to place 'num' at grid[row][col].
        Validates against Row, Column, and Box.
        """
        
        # 1. Check Row
        if num in grid.get_row(row):
            return False
            
        # 2. Check Column
        if num in grid.get_col(col):
            return False

        # 3. Check Box / Region
        if "jigsaw" in grid.type_name.lower():
            # Check Jigsaw Region
            target_region = grid.cells[row][col].region_id
            # Optimization: We could pre-cache region cells, but for now we iterate or use helper
            # Using get_region_cells is slow (O(N^2)). 
            # Better: Iterate grid and check only matching region_id.
            # Even better: The grid should ideally maintain a map of region_id -> list of cells.
            # For now, let's iterate, but we can optimize later.
            for r in range(grid.size):
                for c in range(grid.size):
                    if grid.cells[r][c].region_id == target_region:
                        if grid.cells[r][c].value == num:
                            return False
        else:
            # Standard Box Check
            # Determine box dimensions based on grid size
            box_rows, box_cols = self._get_box_dimensions(grid.size)

            start_row = row - row % box_rows
            start_col = col - col % box_cols
            
            for i in range(box_rows):
                for j in range(box_cols):
                    if grid.cells[start_row + i][start_col + j].value == num:
                        return False
        
        # 4. Check Custom Constraints (Strategy Pattern)
        if not grid.is_valid_move(row, col, num):
            return False

        return True

    def solve(self, grid: SudokuGrid, randomize: bool = False) -> bool:
        """
        Solves the grid in-place. Returns True if solvable.
        If randomize is True, tries numbers in random order.
        """
        empty_cell = self._find_empty_location(grid)
        if not empty_cell:
            return True # Solved!

        row, col = empty_cell

        numbers = list(range(1, grid.size + 1))
        if randomize:
            import random
            random.shuffle(numbers)

        for num in numbers:
            if self.is_safe(grid, row, col, num):
                grid.cells[row][col].value = num

                if self.solve(grid, randomize):
                    return True

                # Backtrack
                grid.cells[row][col].value = 0

        return False

    def count_solutions(self, grid: SudokuGrid, limit: int = 2) -> int:
        """
        Counts number of solutions. Used to check uniqueness.
        Stops if count reaches 'limit' (optimization).
        """
        self.solution_count = 0
        self._count_helper(grid, limit)
        return self.solution_count

    def _count_helper(self, grid: SudokuGrid, limit: int):
        if self.solution_count >= limit:
            return

        empty_cell = self._find_empty_location(grid)
        if not empty_cell:
            self.solution_count += 1
            return

        row, col = empty_cell
        for num in range(1, grid.size + 1):
            if self.is_safe(grid, row, col, num):
                grid.cells[row][col].value = num
                self._count_helper(grid, limit)
                grid.cells[row][col].value = 0 # Backtrack

    def _find_empty_location(self, grid: SudokuGrid) -> Optional[Tuple[int, int]]:
        """Returns (row, col) of the first empty cell, or None."""
        for r in range(grid.size):
            for c in range(grid.size):
                if grid.cells[r][c].value == 0:
                    return (r, c)
        return None

    def _get_box_dimensions(self, size: int) -> Tuple[int, int]:
        """Returns (rows, cols) for the sub-grid box based on total size."""
        if size == 6: return (2, 3)
        if size == 8: return (2, 4)
        if size == 9: return (3, 3)
        if size == 10: return (2, 5)
        if size == 12: return (3, 4)
        if size == 14: return (2, 7)
        if size == 15: return (3, 5)
        if size == 16: return (4, 4)
        
        # Fallback for perfect squares
        root = int(size ** 0.5)
        if root * root == size:
            return (root, root)
            
        # Default fallback (might not be correct for primes, but safe enough to prevent crash)
        return (1, size)
