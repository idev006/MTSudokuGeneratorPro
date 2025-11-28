from abc import ABC, abstractmethod
from typing import List, Tuple, Set

class ConstraintStrategy(ABC):
    """
    Abstract base class for Sudoku constraints.
    """
    @abstractmethod
    def is_valid(self, grid, row: int, col: int, num: int) -> bool:
        """
        Returns True if placing 'num' at (row, col) satisfies the constraint.
        """
        pass

class DiagonalConstraint(ConstraintStrategy):
    """
    Constraint for Diagonal Sudoku (X-Sudoku).
    Numbers must be unique on both main diagonals.
    """
    def is_valid(self, grid, row: int, col: int, num: int) -> bool:
        size = grid.size
        
        # Check Main Diagonal (Top-Left to Bottom-Right)
        if row == col:
            for i in range(size):
                if grid.cells[i][i].value == num:
                    return False
                    
        # Check Anti-Diagonal (Top-Right to Bottom-Left)
        if row + col == size - 1:
            for i in range(size):
                if grid.cells[i][size - 1 - i].value == num:
                    return False
                    
        return True

class WindokuConstraint(ConstraintStrategy):
    """
    Constraint for Windoku (Hyper Sudoku).
    Numbers must be unique in 4 extra 3x3 windows.
    Windows are usually at (1,1), (1,5), (5,1), (5,5) (top-left corners).
    """
    def __init__(self):
        # Define the top-left corners of the 4 windows
        self.windows = [
            (1, 1), (1, 5),
            (5, 1), (5, 5)
        ]

    def is_valid(self, grid, row: int, col: int, num: int) -> bool:
        # Only check if the cell is inside one of the windows
        for start_row, start_col in self.windows:
            if start_row <= row < start_row + 3 and start_col <= col < start_col + 3:
                # Check uniqueness in this window
                for r in range(start_row, start_row + 3):
                    for c in range(start_col, start_col + 3):
                        if grid.cells[r][c].value == num:
                            return False
        return True

class AsteriskConstraint(ConstraintStrategy):
    """
    Constraint for Asterisk Sudoku.
    Numbers must be unique in the 9 asterisk cells.
    """
    def __init__(self):
        # Define the 9 cells of the asterisk
        self.asterisk_cells = {
            (1, 4), (2, 2), (2, 6),
            (4, 1), (4, 4), (4, 7),
            (6, 2), (6, 6), (7, 4)
        }

    def is_valid(self, grid, row: int, col: int, num: int) -> bool:
        # Asterisk constraint is only defined for 9x9 grids
        if grid.size != 9:
            return True

        if (row, col) in self.asterisk_cells:
            # Check other asterisk cells
            for r, c in self.asterisk_cells:
                if grid.cells[r][c].value == num:
                    return False
        return True
