import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.factory import PuzzleGenerator
from app.models.settings import GenerationConfig, Difficulty, SudokuType
from app.services.pdf_service import PDFService

def verify_jigsaw_6x6_pdf():
    print("Verifying Jigsaw 6x6 PDF generation...")
    
    generator = PuzzleGenerator()
    pdf_service = PDFService()
    
    # Generate Jigsaw 6x6
    config = GenerationConfig(type=SudokuType.JIGSAW_6X6, difficulty=Difficulty.EASY)
    grid = generator.generate(config)
    
    output_file = "verify_jigsaw_6x6.pdf"
    
    try:
        pdf_service.create_pdf([grid], output_file)
        print(f"✅ PDF created successfully: {output_file}")
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")

if __name__ == "__main__":
    verify_jigsaw_6x6_pdf()
