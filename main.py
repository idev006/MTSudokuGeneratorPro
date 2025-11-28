import sys
import multiprocessing
import os

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from app.mvvm.views.main_window import MainWindow

def main():
    # Fix for multiprocessing on Windows
    multiprocessing.freeze_support()
    
    app = QApplication(sys.argv)
    
    # Optional: Set Theme
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
