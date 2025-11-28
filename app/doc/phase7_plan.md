# Phase 7: Optimization & Remaining Constraints

## Goal
Implement the remaining Sudoku variants (Consecutive, Even-Odd) and optimize the PDF generation pipeline for mass production.

## Action Plan

### 1. Logic Variants Implementation (`app/models/constraints.py`, `app/core/factory.py`)
-   **Strategy:** "Derived Constraints". We generate a standard solution first, then derive the rules (bars/shading) from it.
-   **Consecutive Sudoku:**
    -   **Generation:** Generate full grid. Identify all adjacent pairs with difference of 1. Store these as `consecutive_pairs`.
    -   **Solver:** Enforce "Positive Constraint" (if pair in list, diff must be 1) and "Negative Constraint" (if pair NOT in list, diff must NOT be 1).
    -   **PDF:** Draw small bars between consecutive cells.
-   **Even-Odd Sudoku:**
    -   **Generation:** Generate full grid. Mark all Even numbers (or a random subset) as "Shaded".
    -   **Solver:** Enforce parity check (if cell is shaded, must be even; else odd).
    -   **PDF:** Draw gray background for Even cells (or circles).

### 2. Update SudokuGrid (`app/models/grid.py`)
-   Add fields to store variant-specific metadata:
    -   `consecutive_pairs: List[Tuple[Tuple[int, int], Tuple[int, int]]]`
    -   `even_odd_mask: List[List[bool]]` (True = Even/Shaded)

### 3. Update PDF Service (`app/services/pdf_service.py`)
-   Implement rendering for:
    -   **Consecutive Bars:** Small lines between cells.
    -   **Even-Odd Shading:** Gray background or circles.

### 4. Optimization: Solution Buffering
-   **Current Issue:** `GeneratorViewModel` collects ALL puzzles in RAM before export.
-   **Refactor:**
    -   Modify `Orchestrator` to yield results? (Hard with `multiprocessing.Queue`).
    -   **Better:** Keep the current flow (it's robust enough for 10k puzzles). 10k puzzles * 1KB = 10MB RAM. It's fine.
    -   **Focus:** Ensure `PDFService` handles large lists efficiently.
    -   **Optimization:** We will stick to the "Buffer Solutions in RAM" strategy mentioned in the Blueprint, which is already partially in place (we have the data). We just need to ensure `PDFService` writes the Puzzle pages *first*, then the Solution pages, which it already does.
    -   **Refinement:** Maybe add a "Stream to Disk" feature if requested, but for now, the Logic Variants are higher priority.

## Verification
-   **Test:** `tests/test_variants.py` to verify Consecutive and Even-Odd generation and constraints.
