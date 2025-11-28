# Phase 4 Action Plan: Advanced Features & Optimization

## 1. Objective
Implement the ability to export generated Sudoku puzzles to PDF files for printing, and polish the User Interface with themes and better UX.

## 2. Technical Approach
-   **PDF Generation:** Use `reportlab` library to draw Sudoku grids, numbers, and layout.
-   **Service Layer:** Create `PDFService` to handle PDF creation logic.
-   **MVVM:** Update `GeneratorViewModel` to handle the "Export" command.
-   **UI:** Add "Export to PDF" button and potentially a "Preview" feature (optional).
-   **Theming:** Use `qdarktheme` or custom CSS/QSS for a modern look.

## 3. Step-by-Step Implementation

### Step 1: Implement PDFService
-   **File:** `app/services/pdf_service.py`
-   **Class:** `PDFService`
-   **Methods:**
    -   `draw_grid(canvas, x, y, size, cell_size)`
    -   `draw_numbers(canvas, grid, x, y, cell_size)`
    -   `create_pdf(puzzles: List[SudokuGrid], filename: str)`
-   **Details:** Support multiple puzzles per page (e.g., 2x2 or 1 per page).

### Step 2: Update ViewModel
-   **File:** `app/mvvm/viewmodels/generator_vm.py`
-   **Changes:**
    -   Add `export_puzzles(path: str)` method.
    -   Store generated puzzles in memory (list) to allow exporting after generation.

### Step 3: Update UI
-   **File:** `app/mvvm/views/main_window.py`
-   **Changes:**
    -   Add "Export PDF" button (enabled only after generation).
    -   Add File Dialog to select save location.

### Step 4: UI Polish (Theming)
-   **File:** `main.py`
-   **Changes:** Apply a dark theme or custom style.

## 4. Verification Plan
-   **Unit Test:** Test `PDFService` by generating a dummy PDF and checking file existence/size.
-   **Manual Test:** Run the app, generate puzzles, click Export, and open the resulting PDF to verify layout and correctness.

## 5. Potential Risks
-   **Performance:** Generating large PDFs might be slow. (Mitigation: Show progress bar for export).
-   **Layout:** Grids might look ugly or misaligned. (Mitigation: Iterative tweaking of coordinates).
