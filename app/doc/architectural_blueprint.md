# SudokuMaster Gen: Architectural Blueprint

## 1. Project Overview
**SudokuMaster Gen** is a high-performance, desktop-based Sudoku generator capable of mass-producing various Sudoku variants and exporting them to PDF.

**Supported Features:**
-   **1. 6x6 Classic Sudoku**
-   **2. 6x6 Alphabet Sudoku**
-   **3. 6x6 Diagonal Sudoku**
-   **4. 6x6 Jigsaw Sudoku**
-   **5. 6x6 Thai Alphabet Sudoku**
-   **6. 9x9 Classic Sudoku**
-   **7. 9x9 Alphabet Sudoku**
-   **8. 9x9 Diagonal Sudoku**
-   **9. 9x9 Jigsaw Sudoku**
-   **10. 9x9 Even-Odd Sudoku**
-   **11. 9x9 Jigsaw Diagonal Sudoku**
-   **12. 9x9 Windoku Sudoku**
-   **13. 9x9 Asterisk Sudoku**
-   **14. 9x9 Consecutive Sudoku**
-   **15. 9x9 Thai Alphabet Sudoku**
-   **Output:** PDF with appended solutions.

## 2. System Architecture
The application follows the **MVVM (Model-View-ViewModel)** pattern, integrated with a **Multiprocessing Producer-Consumer Pipeline**.

### 2.1 High-Level Data Flow
```mermaid
graph LR
    User[User Input] --> UI[View (MainWindow)]
    UI <--> VM[ViewModel (GeneratorVM)]
    VM --> Orch[Orchestrator Service]
    
    subgraph "Parallel Processing Core"
        Orch --> JobQ[(Job Queue)]
        JobQ --> W1[Worker Process 1]
        JobQ --> W2[Worker Process 2]
        W1 & W2 -->|Generate & Solve| ResQ[(Result Queue)]
    end
    
    ResQ --> PDF[PDF Service]
    PDF --> Disk[(PDF File)]
```

## 3. Core Components

### 3.1 Presentation Layer (MVVM)
-   **View (`app/mvvm/views/`)**: Built with **PySide6**. Responsible for layout and user interaction.
    -   `MainWindow`: Main dashboard with controls for Type, Size, Difficulty, and Quantity.
-   **ViewModel (`app/mvvm/viewmodels/`)**: Handles business logic state and commands.
    -   `BaseViewModel`: Implements `INotifyPropertyChanged` via Signals.
    -   `GeneratorViewModel`: Manages the generation lifecycle, polls the Orchestrator, and updates UI state (`progress`, `status`).

### 3.2 Service Layer (`app/services/`)
-   **`OrchestratorService`**: The bridge between the UI and the Worker Pool.
    -   Manages `multiprocessing.Pool`.
    -   Distributes `GenerationConfig` tasks.
    -   Collects results via `multiprocessing.Manager().Queue()`.
-   **`LoggerService`**: Centralized logging system.
    -   Aggregates logs from all processes into a single file.
    -   Thread-safe and Process-safe.
-   **`PDFService`**: Handles document generation.
    -   Uses **ReportLab** to draw grids.
    -   Supports multiple layouts (2 puzzles/page).
    -   **Feature:** Appends solutions to the end of the document.
    -   **Feature:** Renders Thai Alphabet and other symbols.

### 3.3 Domain Layer (`app/models/`)
-   **`SudokuGrid`**: The core data structure.
    -   `cells`: 2D list of `SudokuCell`.
    -   `solution`: Stores the solved state.
    -   `constraints`: List of active rules (e.g., Diagonal, Windoku).
-   **`GenerationConfig`**: Configuration object passed to workers.
    -   Encapsulates `Difficulty`, `SudokuType`, `Size`, and `Quantity`.
-   **`ConstraintStrategy`**: Interface for custom rules.
    -   `is_valid(grid, row, col, num)`: Enforces rules like "Unique on Diagonal".

### 3.4 Core Logic (`app/core/`)
-   **`PuzzleGenerator`**: The factory class.
    -   **Pipeline:** `Create Empty` -> `Apply Constraints` -> `Fill Diagonals` -> `Solve` -> `Remove Digits`.
-   **`SudokuSolver`**: Backtracking solver.
    -   Optimized for 9x9 but supports dynamic sizes (6x6).
    -   Respects all injected `ConstraintStrategy` objects.

## 4. Key Technical Decisions

### 4.1 Multiprocessing on Windows
-   **Challenge:** Windows uses `spawn` method, requiring picklable objects and clean imports.
-   **Solution:**
    -   Worker logic isolated in `app/services/worker.py`.
    -   Use `multiprocessing.Manager().Queue()` for robust IPC.
    -   `if __name__ == "__main__": multiprocessing.freeze_support()` in entry point.

### 4.2 Extensibility (Strategy Pattern)
-   New Sudoku variants (e.g., Anti-King, Knight Move) can be added by simply creating a new class inheriting from `ConstraintStrategy` and registering it in the `PuzzleGenerator`. No changes to the Solver are needed.

### 4.3 Jigsaw Implementation Strategy (Planned)
-   **GeometryFactory:** A singleton responsible for generating and caching Jigsaw regions (polyominoes).
-   **Caching:** Pre-generated region maps will be stored to avoid expensive re-calculation during mass production.

## 5. Directory Structure
```
SudokuMaster/
├── main.py                 # Entry Point
├── config/settings.json    # Configuration
├── app/
│   ├── core/               # Algorithms (Solver, Generator)
│   ├── models/             # Data Classes (Grid, Config)
│   ├── mvvm/               # UI Layer (Views, ViewModels)
│   ├── services/           # Infrastructure (Orchestrator, PDF, Logger)
│   └── doc/                # Documentation
└── tests/                  # Unit & Integration Tests
```
