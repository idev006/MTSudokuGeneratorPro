import random
from app.models.grid import SudokuGrid
from app.models.settings import GenerationConfig, SudokuType
from app.core.solver import SudokuSolver
from app.core.logger import AppLogger

class PuzzleGenerator:
    """Generates Sudoku puzzles."""
    
    def __init__(self):
        self.solver = SudokuSolver()
        self.logger = AppLogger.get_logger()

    def generate(self, config: GenerationConfig) -> SudokuGrid:
        """
        Main entry point to generate a puzzle based on config.
        """
        # self.logger.debug(f"Generating puzzle: {config.type.value}, Size {config.size}") # Verbose

        # 1. Create Empty Grid
        grid = SudokuGrid(size=config.size)
        grid.type_name = config.type.value
        
        # 2. Apply Constraints based on Type
        is_jigsaw = config.type in (SudokuType.JIGSAW_9X9, SudokuType.JIGSAW_6X6, SudokuType.JIGSAW_DIAGONAL_9X9)
        is_diagonal = config.type in (SudokuType.DIAGONAL_9X9, SudokuType.DIAGONAL_6X6, SudokuType.JIGSAW_DIAGONAL_9X9)
        
        # Special handling for Jigsaw types (Template Cache + Permutation)
        if is_jigsaw:
            from app.core.geometry import GeometryFactory
            from app.core.number_permuter import NumberPermuter
            
            factory = GeometryFactory()
            # Request template (with solution if available)
            template = factory.get_jigsaw_template(config.size, is_diagonal=(config.type == SudokuType.JIGSAW_DIAGONAL_9X9))
            
            # Apply regions
            grid.apply_region_map(template['regions'])
            
            # Apply Diagonal constraint if needed (for validation/rendering)
            if config.type == SudokuType.JIGSAW_DIAGONAL_9X9:
                from app.models.constraints import DiagonalConstraint
                grid.constraints.append(DiagonalConstraint())
            
            # If template has a solution, use it with permutation! (FAST PATH)
            # If template has a solution, use it with permutation! (FAST PATH)
            # We verified that Jigsaw Diagonal templates DO have valid diagonal solutions.
            if template.get('solution'):
                permuter = NumberPermuter()
                permuted_solution = permuter.permute_solution(template['solution'])
                
                # Fill grid with permuted solution
                for r in range(config.size):
                    for c in range(config.size):
                        grid.cells[r][c].value = permuted_solution[r][c]

        # Standard Diagonal (Non-Jigsaw)
        elif config.type in (SudokuType.DIAGONAL_9X9, SudokuType.DIAGONAL_6X6):
            from app.models.constraints import DiagonalConstraint
            grid.constraints.append(DiagonalConstraint())
        elif config.type == SudokuType.WINDOKU_9X9:
            from app.models.constraints import WindokuConstraint
            grid.constraints.append(WindokuConstraint())
        elif config.type == SudokuType.ASTERISK_9X9:
            from app.models.constraints import AsteriskConstraint
            grid.constraints.append(AsteriskConstraint())
        
        # 3. Solve to get a complete valid board (Randomized)
        # Check for Static Template (Fastest Path)
        from app.core.static_templates import STATIC_TEMPLATES
        if config.type in STATIC_TEMPLATES and not grid.is_full():
            from app.core.number_permuter import NumberPermuter
            base_solution = STATIC_TEMPLATES[config.type]
            permuter = NumberPermuter()
            permuted_solution = permuter.permute_solution(base_solution)
            
            # Fill grid
            for r in range(config.size):
                for c in range(config.size):
                    grid.cells[r][c].value = permuted_solution[r][c]
            
            self.logger.info(f"Used static template for {config.type.name}")

        # If grid is already filled (e.g. from Jigsaw template or Static template), skip solving
        if not grid.is_full():
            # Use randomized solver to ensure uniqueness and speed
            if not self.solver.solve(grid, randomize=True):
                # Retry loop
                max_retries = 5
                self.logger.warning(f"First solve attempt failed. Retrying up to {max_retries} times...")
                for attempt in range(max_retries):
                    # Reset Grid
                    grid = SudokuGrid(size=config.size)
                    grid.type_name = config.type.value
                    
                    # Re-apply constraints
                    if config.type in (SudokuType.DIAGONAL_9X9, SudokuType.DIAGONAL_6X6, SudokuType.JIGSAW_DIAGONAL_9X9):
                        from app.models.constraints import DiagonalConstraint
                        grid.constraints.append(DiagonalConstraint())
                    elif config.type == SudokuType.WINDOKU_9X9:
                        from app.models.constraints import WindokuConstraint
                        grid.constraints.append(WindokuConstraint())
                    elif config.type == SudokuType.ASTERISK_9X9:
                        from app.models.constraints import AsteriskConstraint
                        grid.constraints.append(AsteriskConstraint())
                    
                    # For Jigsaw, we need to re-apply regions too!
                    # If we failed, maybe the region map was bad (unlikely if from template)
                    # But if we are retrying Jigsaw Diagonal, we need a region map.
                    if is_jigsaw:
                        # Re-fetch template (maybe a different one?)
                        template = factory.get_jigsaw_template(config.size, is_diagonal=(config.type == SudokuType.JIGSAW_DIAGONAL_9X9))
                        grid.apply_region_map(template['regions'])

                    # Solve again with randomization
                    if self.solver.solve(grid, randomize=True):
                        self.logger.info(f"Retry {attempt+1} successful.")
                        break
                else:
                    self.logger.error("Failed to generate valid grid after all retries.")
                    raise Exception("Failed to generate valid grid after retries")
        
        # Capture Solution
        grid.solution = [[cell.value for cell in row] for row in grid.cells]

        # 4. Apply Logic Variants (Derived Constraints)
        self._apply_logic_variants(grid, config)

        # 5. Remove Digits to create the puzzle
        self._remove_digits(grid, config)
        
        return grid

    def _apply_logic_variants(self, grid: SudokuGrid, config: GenerationConfig):
        """
        Derives constraints from the solved grid for logic variants.
        """
        if "consecutive" in config.type.value.lower():
            # Identify all consecutive pairs
            for r in range(grid.size):
                for c in range(grid.size):
                    val = grid.cells[r][c].value
                    # Check Right
                    if c < grid.size - 1:
                        right_val = grid.cells[r][c+1].value
                        if abs(val - right_val) == 1:
                            grid.consecutive_pairs.append(((r, c), (r, c+1)))
                    # Check Bottom
                    if r < grid.size - 1:
                        bottom_val = grid.cells[r+1][c].value
                        if abs(val - bottom_val) == 1:
                            grid.consecutive_pairs.append(((r, c), (r+1, c)))
                            
        if "even" in config.type.value.lower() and "odd" in config.type.value.lower():
            # Mark Even cells
            grid.even_odd_mask = [[False for _ in range(grid.size)] for _ in range(grid.size)]
            for r in range(grid.size):
                for c in range(grid.size):
                    if grid.cells[r][c].value % 2 == 0:
                        grid.even_odd_mask[r][c] = True

    def _remove_digits(self, grid: SudokuGrid, config: GenerationConfig):
        """
        Removes digits to reach the target difficulty while ensuring uniqueness.
        """
        # Determine target empty cells from ratio
        min_empty, max_empty = config.empty_cells_range
        target_empty = random.randint(min_empty, max_empty)
        attempts = target_empty + 20 # Buffer attempts
        
        while target_empty > 0 and attempts > 0:
            row = random.randint(0, grid.size - 1)
            col = random.randint(0, grid.size - 1)
            
            if grid.cells[row][col].value != 0:
                # Backup
                backup = grid.cells[row][col].value
                grid.cells[row][col].value = 0
                
                # Check Uniqueness
                grid_copy = grid.clone()
                solutions = self.solver.count_solutions(grid_copy)
                
                if solutions != 1:
                    # Not unique, put it back
                    grid.cells[row][col].value = backup
                else:
                    target_empty -= 1
            
            attempts -= 1
        
        # Mark remaining cells as fixed
        for r in range(grid.size):
            for c in range(grid.size):
                if grid.cells[r][c].value != 0:
                    grid.cells[r][c].is_fixed = True
