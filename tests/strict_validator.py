import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.grid import SudokuGrid
from app.models.settings import SudokuType, GenerationConfig, Difficulty

class SudokuValidator:
    """
    Strictly validates Sudoku grids against their rules.
    """

    def validate(self, grid: SudokuGrid, config: GenerationConfig) -> bool:
        print(f"  > Validating {config.type.name} (Size {config.size}x{config.size})...")
        
        # Use the SOLUTION for validation, as the puzzle itself has empty cells.
        # We want to verify that the generated solution is valid.
        # If grid.solution is not available, we can't fully validate.
        if not grid.solution:
            print("    ❌ No solution found in grid object!")
            return False

        # Create a temporary grid filled with solution for easier checking
        solved_grid = self._create_solved_grid_wrapper(grid)

        try:
            # 1. Check Basic Rules (Row, Col, Box/Region)
            self._check_rows(solved_grid)
            self._check_cols(solved_grid)
            
            # Check Boxes or Regions
            if "jigsaw" in config.type.value.lower():
                self._check_regions(solved_grid)
            else:
                self._check_boxes(solved_grid)
            
            # 2. Check Variant Constraints
            # 2. Check Variant Constraints
            type_val = config.type.value.lower()
            
            if "diagonal" in type_val:
                self._check_diagonal(solved_grid)
                
            if "windoku" in type_val:
                self._check_windoku(solved_grid)
                
            if "asterisk" in type_val:
                self._check_asterisk(solved_grid)
                
            if "consecutive" in type_val:
                self._check_consecutive(solved_grid, grid) # Pass original grid for constraints
                
            if "even" in type_val and "odd" in type_val:
                self._check_even_odd(solved_grid, grid) # Pass original grid for mask
                
            print(f"    ✅ Passed All Checks")
            return True
            
        except AssertionError as e:
            print(f"    ❌ Validation Failed: {e}")
            return False
        except Exception as e:
            print(f"    ❌ Error during validation: {e}")
            return False

    def _create_solved_grid_wrapper(self, grid):
        """Creates a mock grid object where cells return solution values."""
        class MockCell:
            def __init__(self, val, region):
                self.value = val
                self.region_id = region
        
        class MockGrid:
            def __init__(self, size, solution, cells):
                self.size = size
                self.cells = [[MockCell(solution[r][c], cells[r][c].region_id) 
                               for c in range(size)] for r in range(size)]
        
        return MockGrid(grid.size, grid.solution, grid.cells)

    def _check_unique(self, values: list, context: str):
        # Filter out 0s if we were checking puzzle, but here we check solution so no 0s allowed
        if 0 in values:
            raise AssertionError(f"{context}: Contains zeros (incomplete solution)")
        
        if len(values) != len(set(values)):
            raise AssertionError(f"{context}: Duplicate values found {values}")

    def _check_rows(self, grid):
        for r in range(grid.size):
            values = [grid.cells[r][c].value for c in range(grid.size)]
            self._check_unique(values, f"Row {r}")

    def _check_cols(self, grid):
        for c in range(grid.size):
            values = [grid.cells[r][c].value for r in range(grid.size)]
            self._check_unique(values, f"Col {c}")

    def _check_regions(self, grid):
        # Group values by region_id
        regions = {}
        for r in range(grid.size):
            for c in range(grid.size):
                rid = grid.cells[r][c].region_id
                if rid not in regions: regions[rid] = []
                regions[rid].append(grid.cells[r][c].value)
        
        for rid, values in regions.items():
            self._check_unique(values, f"Region {rid}")

    def _check_boxes(self, grid):
        # Determine box dimensions
        if grid.size == 6: box_rows, box_cols = 2, 3
        elif grid.size == 8: box_rows, box_cols = 2, 4
        elif grid.size == 9: box_rows, box_cols = 3, 3
        elif grid.size == 10: box_rows, box_cols = 2, 5
        elif grid.size == 12: box_rows, box_cols = 3, 4
        elif grid.size == 14: box_rows, box_cols = 2, 7
        elif grid.size == 15: box_rows, box_cols = 3, 5
        elif grid.size == 16: box_rows, box_cols = 4, 4
        else:
            # Try to find integer sqrt
            root = int(grid.size ** 0.5)
            if root * root == grid.size:
                box_rows, box_cols = root, root
            else:
                # Fallback? Or assume no box constraint?
                # For now, assume square if not listed
                box_rows, box_cols = root, grid.size // root

        for r in range(0, grid.size, box_rows):
            for c in range(0, grid.size, box_cols):
                values = []
                for br in range(box_rows):
                    for bc in range(box_cols):
                        if r + br < grid.size and c + bc < grid.size:
                            values.append(grid.cells[r + br][c + bc].value)
                self._check_unique(values, f"Box ({r},{c})")

    def _check_diagonal(self, grid):
        # Main Diagonal
        main = [grid.cells[i][i].value for i in range(grid.size)]
        self._check_unique(main, "Main Diagonal")
        
        # Anti Diagonal
        anti = [grid.cells[i][grid.size - 1 - i].value for i in range(grid.size)]
        self._check_unique(anti, "Anti Diagonal")

    def _check_windoku(self, grid):
        windows = [(1, 1), (1, 5), (5, 1), (5, 5)]
        for i, (sr, sc) in enumerate(windows):
            values = []
            for r in range(sr, sr + 3):
                for c in range(sc, sc + 3):
                    values.append(grid.cells[r][c].value)
            self._check_unique(values, f"Window {i+1}")

    def _check_asterisk(self, grid):
        asterisk_cells = {
            (1, 4), (2, 2), (2, 6),
            (4, 1), (4, 4), (4, 7),
            (6, 2), (6, 6), (7, 4)
        }
        values = [grid.cells[r][c].value for r, c in asterisk_cells]
        self._check_unique(values, "Asterisk")

    def _check_consecutive(self, solved_grid, original_grid):
        # 1. Verify marked pairs are actually consecutive
        marked_pairs = set(original_grid.consecutive_pairs)
        for (r1, c1), (r2, c2) in marked_pairs:
            v1 = solved_grid.cells[r1][c1].value
            v2 = solved_grid.cells[r2][c2].value
            if abs(v1 - v2) != 1:
                raise AssertionError(f"Marked pair ({r1},{c1})-({r2},{c2}) is NOT consecutive: {v1}, {v2}")

        # 2. Verify ALL consecutive neighbors are marked (Strictness)
        for r in range(solved_grid.size):
            for c in range(solved_grid.size):
                val = solved_grid.cells[r][c].value
                
                # Check Right
                if c < solved_grid.size - 1:
                    right_val = solved_grid.cells[r][c+1].value
                    if abs(val - right_val) == 1:
                        # Must be in marked_pairs
                        pair1 = ((r, c), (r, c+1))
                        pair2 = ((r, c+1), (r, c)) # Order might differ
                        if pair1 not in marked_pairs and pair2 not in marked_pairs:
                            raise AssertionError(f"Consecutive pair ({r},{c})-({r},{c+1}) with values {val},{right_val} is MISSING a bar!")

                # Check Bottom
                if r < solved_grid.size - 1:
                    bottom_val = solved_grid.cells[r+1][c].value
                    if abs(val - bottom_val) == 1:
                        pair1 = ((r, c), (r+1, c))
                        pair2 = ((r+1, c), (r, c))
                        if pair1 not in marked_pairs and pair2 not in marked_pairs:
                            raise AssertionError(f"Consecutive pair ({r},{c})-({r+1},{c}) with values {val},{bottom_val} is MISSING a bar!")

    def _check_even_odd(self, solved_grid, original_grid):
        if not original_grid.even_odd_mask:
            raise AssertionError("Even-Odd mask is missing")
            
        for r in range(solved_grid.size):
            for c in range(solved_grid.size):
                val = solved_grid.cells[r][c].value
                is_even_mask = original_grid.even_odd_mask[r][c]
                
                if is_even_mask and val % 2 != 0:
                    raise AssertionError(f"Cell ({r},{c}) is marked EVEN but has value {val} (ODD)")
                if not is_even_mask and val % 2 == 0:
                    raise AssertionError(f"Cell ({r},{c}) is marked ODD but has value {val} (EVEN)")
