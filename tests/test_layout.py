"""
Test script for Multi-File and Layout features
"""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.settings import GenerationConfig, SudokuType, Difficulty
from app.core.factory import PuzzleGenerator
from app.services.pdf_service import PDFService

def test_multi_puzzle_layout():
    """Test different grid sizes with multiple puzzles per page"""
    print("Testing Multi-Puzzle Layout...")
    
    generator = PuzzleGenerator()
    pdf_service = PDFService()
    
    # Test 6x6 (should be 9 per page)
    print("\n1. Testing 6x6 (9 puzzles/page)...")
    config_6 = GenerationConfig(type=SudokuType.STANDARD_9X9, difficulty=Difficulty.EASY, size=6)
    puzzles_6 = [generator.generate(config_6) for _ in range(18)]  # 2 pages
    pdf_service.create_pdf(puzzles_6, "test_layout_6x6.pdf")
    print(f"   ✅ Created test_layout_6x6.pdf with {len(puzzles_6)} puzzles")
    
    # Test 9x9 (should be 4 per page)
    print("\n2. Testing 9x9 (4 puzzles/page)...")
    config_9 = GenerationConfig(type=SudokuType.STANDARD_9X9, difficulty=Difficulty.EASY, size=9)
    puzzles_9 = [generator.generate(config_9) for _ in range(8)]  # 2 pages
    pdf_service.create_pdf(puzzles_9, "test_layout_9x9.pdf")
    print(f"   ✅ Created test_layout_9x9.pdf with {len(puzzles_9)} puzzles")
    
    # Test 12x12 (should be 2 per page)
    print("\n3. Testing 12x12 (2 puzzles/page)...")
    config_12 = GenerationConfig(type=SudokuType.STANDARD_9X9, difficulty=Difficulty.EASY, size=12)
    puzzles_12 = [generator.generate(config_12) for _ in range(4)]  # 2 pages
    pdf_service.create_pdf(puzzles_12, "test_layout_12x12.pdf")
    print(f"   ✅ Created test_layout_12x12.pdf with {len(puzzles_12)} puzzles")
    
    print("\n✅ All layout tests completed!")
    print("\nGenerated files:")
    print("  - test_layout_6x6.pdf (18 puzzles, 9 per page)")
    print("  - test_layout_9x9.pdf (8 puzzles, 4 per page)")
    print("  - test_layout_12x12.pdf (4 puzzles, 2 per page)")

if __name__ == "__main__":
    test_multi_puzzle_layout()
