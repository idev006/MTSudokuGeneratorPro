import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QComboBox, QSpinBox, 
                               QPushButton, QProgressBar, QMessageBox, QFileDialog, QGroupBox, QTextEdit)
from PySide6.QtCore import Qt
from app.mvvm.viewmodels.generator_vm import GeneratorViewModel
from app.models.settings import Difficulty, SudokuType
from app.core.logger import AppLogger

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SudokuMaster Gen")
        self.resize(800, 650) # Increased height for log console
        
        self.vm = GeneratorViewModel()
        self.setup_ui()
        self.setup_bindings()

        # Initialize Logger Connection
        AppLogger.setup()
        AppLogger.get_qt_handler().log_signal.connect(self.update_log)

    def setup_ui(self):
        # Load saved theme
        from app.services.config_manager import ConfigManager
        self.config_manager = ConfigManager()
        saved_theme = self.config_manager.get_app_setting("theme", "Dark")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Root Layout (Vertical)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setSpacing(15)
        root_layout.setContentsMargins(30, 30, 30, 30)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Sudoku Generator Pro")
        title.setObjectName("title") # For styling
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Theme Selector
        lbl_theme = QLabel("Theme:")
        header_layout.addWidget(lbl_theme)
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["System", "Light", "Dark", "Midnight"])
        self.combo_theme.setCurrentText(saved_theme)
        self.combo_theme.currentTextChanged.connect(self.change_theme)
        header_layout.addWidget(self.combo_theme)
        
        # Config Button
        btn_config = QPushButton("⚙️ Config")
        btn_config.setToolTip("Open Configuration Folder (Fonts, Settings)")
        btn_config.setObjectName("btn_config")
        btn_config.clicked.connect(self.open_config_folder)
        header_layout.addWidget(btn_config)

        # About Button
        btn_about = QPushButton("ℹ️ About")
        btn_about.setToolTip("About Application")
        btn_about.setObjectName("btn_about")
        btn_about.clicked.connect(self.show_about_dialog)
        header_layout.addWidget(btn_about)
        
        root_layout.addLayout(header_layout)
        
        # Separator
        line = QLabel()
        line.setFixedHeight(2)
        line.setObjectName("separator")
        root_layout.addWidget(line)

        # Controls Container
        controls_group = QWidget()
        controls_group.setObjectName("controls_container")
        controls_layout = QVBoxLayout(controls_group)
        controls_layout.setContentsMargins(20, 20, 20, 20)

        # Row 1: Type (Size is now implied)
        row1_layout = QHBoxLayout()
        
        # Type
        lbl_type = QLabel("Pattern:")
        lbl_type.setFixedWidth(80)
        row1_layout.addWidget(lbl_type)
        self.combo_type = QComboBox()
        self.combo_type.addItems([t.value for t in SudokuType])
        self.combo_type.setCurrentText(SudokuType.CLASSIC_9X9.value)
        row1_layout.addWidget(self.combo_type)
        
        controls_layout.addLayout(row1_layout)

        # Row 2: Difficulty
        row2_layout = QHBoxLayout()
        lbl_diff = QLabel("Difficulty:")
        lbl_diff.setFixedWidth(80)
        row2_layout.addWidget(lbl_diff)
        self.combo_difficulty = QComboBox()
        self.combo_difficulty.addItems([d.name for d in Difficulty])
        self.combo_difficulty.setCurrentText("EASY")
        row2_layout.addWidget(self.combo_difficulty)
        controls_layout.addLayout(row2_layout)
        
        # Row 3: Files & Puzzles
        row3_layout = QHBoxLayout()
        
        lbl_files = QLabel("Files:")
        lbl_files.setFixedWidth(80)
        row3_layout.addWidget(lbl_files)
        self.spin_file_count = QSpinBox()
        self.spin_file_count.setRange(1, 100)
        self.spin_file_count.setValue(1)
        self.spin_file_count.valueChanged.connect(self.update_total_label)
        row3_layout.addWidget(self.spin_file_count)
        
        row3_layout.addSpacing(20)
        
        lbl_puz = QLabel("Puzzles/File:")
        # lbl_puz.setFixedWidth(100)
        row3_layout.addWidget(lbl_puz)
        self.spin_puzzles_per_file = QSpinBox()
        self.spin_puzzles_per_file.setRange(1, 1000)
        self.spin_puzzles_per_file.setValue(10)
        self.spin_puzzles_per_file.valueChanged.connect(self.update_total_label)
        row3_layout.addWidget(self.spin_puzzles_per_file)
        
        controls_layout.addLayout(row3_layout)

        # Row 4: Output Folder
        row4_layout = QHBoxLayout()
        lbl_out = QLabel("Output:")
        lbl_out.setFixedWidth(80)
        row4_layout.addWidget(lbl_out)
        
        self.txt_output = QLabel(os.getcwd()) # Use Label for display, or QLineEdit
        self.txt_output.setObjectName("txt_output")
        row4_layout.addWidget(self.txt_output)
        
        btn_browse = QPushButton("...")
        btn_browse.setFixedWidth(40)
        btn_browse.setObjectName("btn_browse")
        btn_browse.clicked.connect(self.browse_output_folder)
        row4_layout.addWidget(btn_browse)
        
        controls_layout.addLayout(row4_layout)
        
        root_layout.addWidget(controls_group)
        
        # Total Display
        self.lbl_total = QLabel("Total to Generate: 10 puzzles")
        self.lbl_total.setAlignment(Qt.AlignCenter)
        self.lbl_total.setObjectName("lbl_total")
        root_layout.addWidget(self.lbl_total)

        # Progress Section
        self.lbl_status = QLabel("Ready")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setObjectName("lbl_status")
        root_layout.addWidget(self.lbl_status)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(10)
        root_layout.addWidget(self.progress_bar)

        # Action Buttons
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("START GENERATION")
        self.btn_start.setCursor(Qt.PointingHandCursor)
        self.btn_start.setObjectName("btn_start")
        self.btn_start.clicked.connect(self.on_start_clicked)
        btn_layout.addWidget(self.btn_start)

        self.btn_stop = QPushButton("STOP")
        self.btn_stop.setCursor(Qt.PointingHandCursor)
        self.btn_stop.setObjectName("btn_stop")
        self.btn_stop.clicked.connect(self.on_stop_clicked)
        self.btn_stop.setEnabled(False)
        btn_layout.addWidget(self.btn_stop)
        
        root_layout.addLayout(btn_layout)

        # Log Console
        self.setup_log_console(root_layout)
        
        # Apply initial theme
        self.change_theme(saved_theme)

    def show_about_dialog(self):
        """Reads about.txt and shows it in a dialog."""
        try:
            about_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config', 'about.txt')
            if os.path.exists(about_path):
                with open(about_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = "About file not found."
        except Exception as e:
            content = f"Error reading about file: {e}"

        QMessageBox.information(self, "About Sudoku Generator Pro", content)

    def open_config_folder(self):
        import subprocess
        import platform
        
        # Path to config folder (app/config)
        current_dir = os.path.dirname(os.path.abspath(__file__)) # app/mvvm/views
        mvvm_dir = os.path.dirname(current_dir) # app/mvvm
        app_dir = os.path.dirname(mvvm_dir) # app
        config_path = os.path.join(app_dir, 'config')
        
        if not os.path.exists(config_path):
            os.makedirs(config_path)
            
        if platform.system() == "Windows":
            os.startfile(config_path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", config_path])
        else:
            subprocess.Popen(["xdg-open", config_path])



    def change_theme(self, theme_name):
        """Applies the selected theme QSS."""
        self.config_manager.set_app_setting("theme", theme_name)
        
        # Common Base Styles
        # Use forward slashes for paths in QSS
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'assets', 'icons').replace('\\', '/')
        
        base_qss = f"""
            * {{ font-family: 'Segoe UI', 'Roboto', sans-serif; }}
            
            QLabel#title {{ font-size: 32px; font-weight: bold; margin-bottom: 10px; }}
            QLabel#lbl_total {{ font-size: 16px; font-weight: 600; margin-top: 15px; }}
            QProgressBar {{ border: none; border-radius: 6px; text-align: center; min-height: 12px; }}
            QProgressBar::chunk {{ border-radius: 6px; }}
            
            /* Uniform Height Controls */
            QComboBox, QSpinBox, QPushButton, QLabel#txt_output {{
                min-height: 36px;
                max-height: 36px;
                padding: 0 10px;
                font-size: 14px;
                border-radius: 6px;
            }}
            
            /* ComboBox Arrow Container */
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 36px;
                border-left-width: 0px;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }}
            
            /* SpinBox Buttons Container */
            QSpinBox::up-button, QSpinBox::down-button {{
                subcontrol-origin: border;
                width: 24px;
                border-width: 0px;
            }}
            QSpinBox::up-button {{ subcontrol-position: top right; border-top-right-radius: 6px; }}
            QSpinBox::down-button {{ subcontrol-position: bottom right; border-bottom-right-radius: 6px; }}
            
            /* Buttons */
            QPushButton {{ font-weight: 600; }}
            QPushButton:pressed {{ padding-top: 2px; padding-left: 12px; }}
        """

        themes = {
            "Dark": f"""
                QMainWindow, QWidget {{ background-color: #1e1e1e; color: #f0f0f0; }}
                QLabel {{ color: #e0e0e0; }}
                QLabel#title {{ color: #4CAF50; }}
                QLabel#separator {{ background-color: #333; }}
                QWidget#controls_container {{ background-color: #252526; border: 1px solid #333; border-radius: 12px; }}
                
                QPushButton#btn_config, QPushButton#btn_about {{ background-color: #333; color: #ccc; border: 1px solid #444; }}
                QPushButton#btn_config:hover, QPushButton#btn_about:hover {{ background-color: #3e3e42; border-color: #555; color: white; }}
                
                QPushButton#btn_browse {{ background-color: #333; color: #ccc; border: 1px solid #444; }}
                QPushButton#btn_browse:hover {{ background-color: #3e3e42; border-color: #555; color: white; }}
                
                QLabel#txt_output {{ background-color: #1e1e1e; border: 1px solid #333; color: #aaa; }}
                
                QComboBox, QSpinBox {{ background-color: #1e1e1e; color: #f0f0f0; border: 1px solid #333; }}
                QComboBox:hover, QSpinBox:hover {{ border-color: #555; }}
                QComboBox::drop-down {{ background-color: transparent; }}
                QComboBox::down-arrow {{ image: url({icon_path}/arrow_down_white.png); width: 16px; height: 16px; }}
                
                QComboBox QAbstractItemView {{
                    background-color: #252526;
                    color: #f0f0f0;
                    selection-background-color: #37373d;
                    border: 1px solid #333;
                    outline: none;
                    padding: 4px;
                }}
                
                QSpinBox::up-button, QSpinBox::down-button {{ background-color: transparent; }}
                QSpinBox::up-button:hover, QSpinBox::down-button:hover {{ background-color: #333; }}
                QSpinBox::up-arrow {{ image: url({icon_path}/arrow_up_white.png); width: 10px; height: 10px; }}
                QSpinBox::down-arrow {{ image: url({icon_path}/arrow_down_white.png); width: 10px; height: 10px; }}
                
                QLabel#lbl_total {{ color: #64B5F6; }}
                QLabel#lbl_status {{ color: #888; }}
                QProgressBar {{ background-color: #2d2d2d; }}
                QProgressBar::chunk {{ background-color: #4CAF50; }}
                
                QPushButton#btn_start {{ background-color: #2E7D32; color: white; border: none; }}
                QPushButton#btn_start:hover {{ background-color: #388E3C; }}
                QPushButton#btn_stop {{ background-color: #C62828; color: white; border: none; }}
                QPushButton#btn_stop:hover {{ background-color: #D32F2F; }}
                QPushButton:disabled {{ background-color: #333; color: #555; }}
                
                QTextEdit {{ background-color: #1e1e1e; color: #0f0; border: 1px solid #333; border-radius: 6px; }}
                QGroupBox {{ border: 1px solid #333; color: #ccc; margin-top: 24px; }}
            """,
            "Light": f"""
                QMainWindow, QWidget {{ background-color: #f3f3f3; color: #333; }}
                QLabel {{ color: #333; }}
                QLabel#title {{ color: #2E7D32; }}
                QLabel#separator {{ background-color: #ddd; }}
                QWidget#controls_container {{ background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 12px; }}
                
                QPushButton#btn_config, QPushButton#btn_about {{ background-color: #fff; color: #555; border: 1px solid #ccc; }}
                QPushButton#btn_config:hover, QPushButton#btn_about:hover {{ background-color: #f5f5f5; border-color: #bbb; color: #333; }}
                
                QPushButton#btn_browse {{ background-color: #fff; color: #555; border: 1px solid #ccc; }}
                QPushButton#btn_browse:hover {{ background-color: #f5f5f5; border-color: #bbb; color: #333; }}
                
                QLabel#txt_output {{ background-color: #f9f9f9; border: 1px solid #ddd; color: #555; }}
                
                QComboBox, QSpinBox {{ background-color: #fff; color: #333; border: 1px solid #ddd; }}
                QComboBox:hover, QSpinBox:hover {{ border-color: #bbb; }}
                QComboBox::drop-down {{ background-color: transparent; }}
                QComboBox::down-arrow {{ image: url({icon_path}/arrow_down_black.png); width: 16px; height: 16px; }}
                
                QComboBox QAbstractItemView {{
                    background-color: #fff;
                    color: #333;
                    selection-background-color: #e0e0e0;
                    selection-color: #000;
                    border: 1px solid #ddd;
                    outline: none;
                    padding: 4px;
                }}
                
                QSpinBox::up-button, QSpinBox::down-button {{ background-color: transparent; }}
                QSpinBox::up-button:hover, QSpinBox::down-button:hover {{ background-color: #f0f0f0; }}
                QSpinBox::up-arrow {{ image: url({icon_path}/arrow_up_black.png); width: 10px; height: 10px; }}
                QSpinBox::down-arrow {{ image: url({icon_path}/arrow_down_black.png); width: 10px; height: 10px; }}
                
                QLabel#lbl_total {{ color: #1976D2; }}
                QLabel#lbl_status {{ color: #666; }}
                QProgressBar {{ background-color: #e0e0e0; }}
                QProgressBar::chunk {{ background-color: #4CAF50; }}
                
                QPushButton#btn_start {{ background-color: #4CAF50; color: white; border: none; }}
                QPushButton#btn_start:hover {{ background-color: #43A047; }}
                QPushButton#btn_stop {{ background-color: #ef5350; color: white; border: none; }}
                QPushButton#btn_stop:hover {{ background-color: #e53935; }}
                QPushButton:disabled {{ background-color: #e0e0e0; color: #999; }}
                
                QTextEdit {{ background-color: #fff; color: #333; border: 1px solid #ddd; border-radius: 6px; }}
                QGroupBox {{ border: 1px solid #ddd; color: #555; margin-top: 24px; }}
            """,
            "Midnight": f"""
                QMainWindow, QWidget {{ background-color: #0a0a1a; color: #e0e0ff; }}
                QLabel {{ color: #ccccff; }}
                QLabel#title {{ color: #00bcd4; }}
                QLabel#separator {{ background-color: #1a1a3d; }}
                QWidget#controls_container {{ background-color: #101020; border: 1px solid #1a1a3d; border-radius: 12px; }}
                
                QPushButton#btn_config, QPushButton#btn_about {{ background-color: #101020; color: #00bcd4; border: 1px solid #1a1a3d; }}
                QPushButton#btn_config:hover, QPushButton#btn_about:hover {{ background-color: #1a1a3d; border-color: #00bcd4; }}
                
                QPushButton#btn_browse {{ background-color: #101020; color: #00bcd4; border: 1px solid #1a1a3d; }}
                QPushButton#btn_browse:hover {{ background-color: #1a1a3d; border-color: #00bcd4; }}
                
                QLabel#txt_output {{ background-color: #050510; border: 1px solid #1a1a3d; color: #aaaaff; }}
                
                QComboBox, QSpinBox {{ background-color: #050510; color: #00bcd4; border: 1px solid #1a1a3d; }}
                QComboBox:hover, QSpinBox:hover {{ border-color: #00bcd4; }}
                QComboBox::drop-down {{ background-color: transparent; }}
                QComboBox::down-arrow {{ image: url({icon_path}/arrow_down_cyan.png); width: 16px; height: 16px; }}
                
                QComboBox QAbstractItemView {{
                    background-color: #050510;
                    color: #00bcd4;
                    selection-background-color: #00bcd4;
                    selection-color: #000;
                    border: 1px solid #1a1a3d;
                    outline: none;
                    padding: 4px;
                }}
                
                QSpinBox::up-button, QSpinBox::down-button {{ background-color: transparent; }}
                QSpinBox::up-button:hover, QSpinBox::down-button:hover {{ background-color: #1a1a3d; }}
                QSpinBox::up-arrow {{ image: url({icon_path}/arrow_up_cyan.png); width: 10px; height: 10px; }}
                QSpinBox::down-arrow {{ image: url({icon_path}/arrow_down_cyan.png); width: 10px; height: 10px; }}
                
                QLabel#lbl_total {{ color: #00bcd4; }}
                QLabel#lbl_status {{ color: #8888aa; }}
                QProgressBar {{ background-color: #101020; }}
                QProgressBar::chunk {{ background-color: #00bcd4; }}
                
                QPushButton#btn_start {{ background-color: #00bcd4; color: #000; border: none; }}
                QPushButton#btn_start:hover {{ background-color: #00acc1; }}
                QPushButton#btn_stop {{ background-color: #ff4081; color: white; border: none; }}
                QPushButton#btn_stop:hover {{ background-color: #f50057; }}
                QPushButton:disabled {{ background-color: #101020; color: #333366; }}
                
                QTextEdit {{ background-color: #050510; color: #00bcd4; border: 1px solid #1a1a3d; border-radius: 6px; }}
                QGroupBox {{ border: 1px solid #1a1a3d; color: #ccccff; margin-top: 24px; }}
            """
        }
        
        # Apply base styles to System theme as well for layout consistency
        if theme_name == "System":
            # For System, we use a clean light theme style to ensure visibility and borders
            # while respecting the base layout
            system_qss = base_qss + f"""
                QMainWindow, QWidget {{ background-color: #f0f0f0; color: #000; }}
                QLabel {{ color: #000; }}
                QLabel#title {{ color: #000; }}
                QLabel#separator {{ background-color: #ccc; }}
                QWidget#controls_container {{ background-color: #fff; border: 1px solid #ccc; border-radius: 12px; }}
                
                QPushButton#btn_config, QPushButton#btn_about {{ background-color: #e0e0e0; color: #000; border: 1px solid #ccc; }}
                QPushButton#btn_config:hover, QPushButton#btn_about:hover {{ background-color: #d0d0d0; }}
                
                QPushButton#btn_browse {{ background-color: #e0e0e0; color: #000; border: 1px solid #ccc; }}
                QPushButton#btn_browse:hover {{ background-color: #d0d0d0; }}
                
                QLabel#txt_output {{ background-color: #fff; border: 1px solid #ccc; color: #000; }}
                
                QComboBox, QSpinBox {{ background-color: #fff; color: #000; border: 1px solid #ccc; }}
                QComboBox:hover, QSpinBox:hover {{ border-color: #999; }}
                QComboBox::drop-down {{ background-color: transparent; }}
                QComboBox::down-arrow {{ image: url({icon_path}/arrow_down_black.png); width: 16px; height: 16px; }}
                
                QComboBox QAbstractItemView {{
                    background-color: #fff;
                    color: #000;
                    selection-background-color: #e0e0e0;
                    selection-color: #000;
                    border: 1px solid #ccc;
                    outline: none;
                    padding: 4px;
                }}
                
                QSpinBox::up-button, QSpinBox::down-button {{ background-color: transparent; }}
                QSpinBox::up-button:hover, QSpinBox::down-button:hover {{ background-color: #e0e0e0; }}
                QSpinBox::up-arrow {{ image: url({icon_path}/arrow_up_black.png); width: 10px; height: 10px; }}
                QSpinBox::down-arrow {{ image: url({icon_path}/arrow_down_black.png); width: 10px; height: 10px; }}
                
                QLabel#lbl_total {{ color: #000; font-weight: bold; }}
                QLabel#lbl_status {{ color: #444; }}
                QProgressBar {{ background-color: #ccc; }}
                QProgressBar::chunk {{ background-color: #4CAF50; }}
                
                QPushButton#btn_start {{ background-color: #4CAF50; color: white; border: none; }}
                QPushButton#btn_start:hover {{ background-color: #45a049; }}
                QPushButton#btn_stop {{ background-color: #f44336; color: white; border: none; }}
                QPushButton#btn_stop:hover {{ background-color: #d32f2f; }}
                QPushButton:disabled {{ background-color: #ccc; color: #888; }}
                
                QTextEdit {{ background-color: #fff; color: #000; border: 1px solid #ccc; border-radius: 6px; }}
                QGroupBox {{ border: 1px solid #ccc; color: #000; margin-top: 24px; }}
            """
            self.setStyleSheet(system_qss)
        else:
            self.setStyleSheet(base_qss + themes.get(theme_name, themes["Dark"]))

    def setup_log_console(self, parent_layout):
        log_group = QGroupBox("System Logs")
        log_group.setStyleSheet("QGroupBox { border: 1px solid #555; border-radius: 5px; margin-top: 10px; font-weight: bold; } QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }")
        log_layout = QVBoxLayout()
        
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setMaximumHeight(150) # Limit height
        self.log_console.setStyleSheet("font-family: Consolas, Monospace; font-size: 11px; background-color: #111; color: #0f0; border: none;")
        
        log_layout.addWidget(self.log_console)
        log_group.setLayout(log_layout)
        
        parent_layout.addWidget(log_group)

    def update_log(self, message):
        self.log_console.append(message)
        # Auto scroll to bottom
        sb = self.log_console.verticalScrollBar()
        sb.setValue(sb.maximum())

    def open_config_folder(self):
        import subprocess
        import platform
        
        # Path to config folder (app/config)
        current_dir = os.path.dirname(os.path.abspath(__file__)) # app/mvvm/views
        mvvm_dir = os.path.dirname(current_dir) # app/mvvm
        app_dir = os.path.dirname(mvvm_dir) # app
        config_path = os.path.join(app_dir, 'config')
        
        if not os.path.exists(config_path):
            os.makedirs(config_path)
            
        if platform.system() == "Windows":
            os.startfile(config_path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", config_path])
        else:
            subprocess.Popen(["xdg-open", config_path])

    def setup_bindings(self):
        # Connect ViewModel signals to UI updates
        self.vm.property_changed.connect(self.on_property_changed)

    def on_property_changed(self, name, value):
        if name == "is_running":
            self.btn_start.setEnabled(not value)
            self.btn_stop.setEnabled(value)
            self.combo_difficulty.setEnabled(not value)
            self.spin_file_count.setEnabled(not value)
            self.spin_puzzles_per_file.setEnabled(not value)
            self.combo_type.setEnabled(not value)
            # Size is removed
            # Export button removed
            
            if value:
                self.progress_bar.setValue(0)
        elif name == "progress":
            self.progress_bar.setValue(value)
        elif name == "status_message":
            self.lbl_status.setText(value)

    def update_total_label(self):
        """Update total puzzles label"""
        total = self.spin_file_count.value() * self.spin_puzzles_per_file.value()
        self.lbl_total.setText(f"Total: {total} puzzles")

    def browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.txt_output.setText(folder)

    def on_start_clicked(self):
        file_count = self.spin_file_count.value()
        puzzles_per_file = self.spin_puzzles_per_file.value()
        difficulty = self.combo_difficulty.currentText()
        # size is now derived from type
        sudoku_type = self.combo_type.currentText()
        output_folder = self.txt_output.text()
        
        self.vm.start_generation(file_count, puzzles_per_file, difficulty, sudoku_type, output_folder)

    def on_stop_clicked(self):
        self.vm.stop_generation()

    def closeEvent(self, event):
        self.vm.stop_generation()
        event.accept()
