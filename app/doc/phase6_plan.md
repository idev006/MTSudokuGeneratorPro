# Phase 6: Jigsaw Engine Implementation Plan

## Goal
Implement the core logic for **Jigsaw Sudoku** (Irregular Sudoku), where regions are not standard 3x3 boxes but arbitrary connected shapes of size N.

## Action Plan

### 1. Geometry Factory (`app/core/geometry.py`)
-   **Responsibility:** Generate valid Jigsaw region maps.
-   **Algorithm:** "Region Growing" or "Random Walk" to partition the NxN grid into N regions of size N.
-   **Caching:** Store generated maps to avoid re-computing (performance optimization).
-   **API:** `get_jigsaw_map(size: int) -> List[List[int]]`

### 2. Update SudokuGrid (`app/models/grid.py`)
-   Add method `apply_region_map(map: List[List[int]])` to assign `region_id` to each cell.

### 3. Update Solver (`app/core/solver.py`)
-   Modify `is_safe` method.
-   **Logic:** If `grid.type` is Jigsaw, skip standard box check and check `grid.get_region_cells(cell.region_id)` instead.
-   *Optimization:* Pre-compute region indices to avoid iterating the whole grid every check.

### 4. Update PDF Service (`app/services/pdf_service.py`)
-   **Challenge:** Drawing irregular borders is harder than straight lines.
-   **Logic:** For each cell, check its neighbors (Right, Bottom). If the neighbor has a *different* `region_id`, draw a thick border between them.

### 5. Integration
-   Update `PuzzleGenerator` (`app/core/factory.py`) to call `GeometryFactory` when `config.type == SudokuType.JIGSAW`.

## Verification
-   **Unit Test:** Verify that generated regions are contiguous and have correct size.
-   **Visual Test:** Generate a PDF and check if the thick borders correctly outline the jigsaw shapes.
