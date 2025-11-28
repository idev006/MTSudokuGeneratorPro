from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import copy

@dataclass
class SudokuCell:
    """Represents a single cell in the Sudoku grid."""
    row: int
    col: int
    value: int = 0  # 0 represents an empty cell
    is_fixed: bool = False  # True if this is an initial clue
    region_id: int = 0  # ID of the region/cage this cell belongs to (for Jigsaw)
    candidates: List[int] = field(default_factory=list) # Possible values for solver

    def __repr__(self):
        return f"Cell({self.row}, {self.col}, val={self.value})"

from app.models.constraints import ConstraintStrategy

@dataclass
class SudokuGrid:
    """Represents the entire Sudoku board."""
    size: int = 9
    cells: List[List[SudokuCell]] = field(default_factory=list)
    constraints: List[ConstraintStrategy] = field(default_factory=list)
    solution: Optional[List[List[int]]] = None # Stores the solved grid values
    type_name: str = "standard_9x9" # Store type name to avoid circular import with SudokuType enum
    
    # Variant Specific Data
    consecutive_pairs: List[Tuple[Tuple[int, int], Tuple[int, int]]] = field(default_factory=list)
    even_odd_mask: List[List[bool]] = field(default_factory=list) # True if Even/Shaded
    
    def __post_init__(self):
        if not self.cells:
            self.cells = [[SudokuCell(r, c) for c in range(self.size)] for r in range(self.size)]

    def is_valid_move(self, row: int, col: int, num: int) -> bool:
        """Checks if placing num at (row, col) is valid against all constraints."""
        # 1. Check Standard Rules (Row, Col) - Box is handled by solver or specific constraint
        # Ideally, Row/Col/Box should also be constraints, but for performance we keep them core for now
        # or we can move them to StandardConstraint later.
        
        # Check custom constraints
        for constraint in self.constraints:
            if not constraint.is_valid(self, row, col, num):
                return False
        return True


    def get_row(self, r: int) -> List[int]:
        return [cell.value for cell in self.cells[r]]

    def get_col(self, c: int) -> List[int]:
        return [self.cells[r][c].value for r in range(self.size)]

    def get_region_cells(self, region_id: int) -> List[SudokuCell]:
        """Returns all cells belonging to a specific region ID."""
        region_cells = []
        for r in range(self.size):
            for c in range(self.size):
                if self.cells[r][c].region_id == region_id:
                    region_cells.append(self.cells[r][c])
        return region_cells

    def clone(self):
        """Creates a deep copy of the grid."""
        return copy.deepcopy(self)

    def is_full(self) -> bool:
        """Checks if the grid is completely filled."""
        for r in range(self.size):
            for c in range(self.size):
                if self.cells[r][c].value == 0:
                    return False
        return True

    def apply_region_map(self, region_map: List[List[int]]):
        """Applies a Jigsaw region map to the grid."""
        if len(region_map) != self.size or len(region_map[0]) != self.size:
            raise ValueError("Region map size does not match grid size")
            
        for r in range(self.size):
            for c in range(self.size):
                self.cells[r][c].region_id = region_map[r][c]

    def __str__(self):
        """Simple string representation for debugging."""
        res = ""
        for r in range(self.size):
            row_str = " ".join(str(c.value) if c.value != 0 else "." for c in self.cells[r])
            res += row_str + "\n"
        return res
