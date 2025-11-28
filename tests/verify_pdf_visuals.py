import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.factory import PuzzleGenerator
from app.models.settings import GenerationConfig, Difficulty, SudokuType
from app.services.pdf_service import PDFService

def verify_pdf_visuals():
    print("Generating sample PDF for visual verification...")
    
    generator = PuzzleGenerator()
    pdf_service = PDFService()
    
    # Generate Windoku (uses gray cells)
    config = GenerationConfig(type=SudokuType.WINDOKU_9X9, difficulty=Difficulty.EASY)
    grid = generator.generate(config)
    
    output_file = "verify_visuals_windoku.pdf"
    
    try:
        pdf_service.create_pdf([grid], output_file)
        print(f"✅ PDF created successfully: {output_file}")
        print("Please open this file and check:")
        print("1. Cover Page exists with Thai text.")
        print("2. Gray windows have correct color (#c5c5c5) and margin (3px).")
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")

if __name__ == "__main__":
    verify_pdf_visuals()
