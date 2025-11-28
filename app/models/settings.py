from dataclasses import dataclass
from enum import Enum

class SudokuType(Enum):
    CLASSIC_6X6 = "6x6 Classic Sudoku"
    ALPHABET_6X6 = "6x6 Alphabet Sudoku"
    DIAGONAL_6X6 = "6x6 Diagonal Sudoku"
    JIGSAW_6X6 = "6x6 Jigsaw Sudoku"
    THAI_6X6 = "6x6 Thai Alphabet Sudoku"
    CLASSIC_9X9 = "9x9 Classic Sudoku"
    ALPHABET_9X9 = "9x9 Alphabet Sudoku"
    DIAGONAL_9X9 = "9x9 Diagonal Sudoku"
    JIGSAW_9X9 = "9x9 Jigsaw Sudoku"
    EVEN_ODD_9X9 = "9x9 Even-Odd Sudoku"
    JIGSAW_DIAGONAL_9X9 = "9x9 Jigsaw Diagonal Sudoku"
    WINDOKU_9X9 = "9x9 Windoku Sudoku"
    ASTERISK_9X9 = "9x9 Asterisk Sudoku"
    CONSECUTIVE_9X9 = "9x9 Consecutive Sudoku"
    THAI_9X9 = "9x9 Thai Alphabet Sudoku"

class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"
    DEVIL = "devil"

@dataclass
class GenerationConfig:
    """Configuration settings for the generator."""
    type: SudokuType = SudokuType.CLASSIC_9X9
    difficulty: Difficulty = Difficulty.MEDIUM
    size: int = 9  # Will be auto-set based on type
    quantity: int = 1
    
    # Advanced settings (using ratios for scalability)
    empty_ratio_min: float = 0.45
    empty_ratio_max: float = 0.55
    use_symmetry: bool = True
    
    def __post_init__(self):
        # Auto-set size based on type name
        if "6x6" in self.type.value:
            self.size = 6
        else:
            self.size = 9

        # Load presets from ConfigManager (SSOT)
        from app.services.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        preset = config_manager.get_difficulty_config(self.difficulty)
        
        self.empty_ratio_min = preset.get("empty_ratio_min", self.empty_ratio_min)
        self.empty_ratio_max = preset.get("empty_ratio_max", self.empty_ratio_max)

    @property
    def empty_cells_range(self):
        """Calculates the absolute range of empty cells based on size and ratio."""
        total_cells = self.size * self.size
        return (
            int(total_cells * self.empty_ratio_min),
            int(total_cells * self.empty_ratio_max)
        )
