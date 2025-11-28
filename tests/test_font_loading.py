import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.pdf_service import PDFService
from app.services.config_manager import ConfigManager

def test_font_loading():
    print("Testing Font Loading...")
    
    # 1. Check Config
    config = ConfigManager()
    font_path = config.get_font_path('thai_font')
    print(f"Configured Font Path: {font_path}")
    
    if font_path and os.path.exists(font_path):
        print("✅ Font file exists")
    else:
        print("❌ Font file missing or not configured")
        
    # 2. Check PDFService
    service = PDFService()
    print(f"PDFService Loaded Font: {service.thai_font}")
    
    if service.thai_font != 'Helvetica':
        print("✅ PDFService successfully registered custom font")
    else:
        print("⚠️ PDFService is using fallback font (Helvetica)")

if __name__ == "__main__":
    test_font_loading()
