from PySide6.QtCore import QObject, Signal, QThread
from app.models.settings import GenerationConfig, Difficulty, SudokuType
from app.core.factory import PuzzleGenerator
from app.services.pdf_service import PDFService
import os
import datetime
from app.core.logger import AppLogger

class GeneratorWorker(QThread):
    progress_changed = Signal(int)
    status_changed = Signal(str)
    finished = Signal()
    error_occurred = Signal(str)

    def __init__(self, configs, output_folder, puzzles_per_file):
        super().__init__()
        self.configs = configs
        self.output_folder = output_folder
        self.puzzles_per_file = puzzles_per_file
        self.is_running = True
        self.logger = AppLogger.get_logger()

    def run(self):
        try:
            total_files = len(self.configs)
            generator = PuzzleGenerator()
            pdf_service = PDFService()
            
            self.logger.info(f"Starting generation of {total_files} files...")

            for i, config in enumerate(self.configs):
                if not self.is_running:
                    self.logger.info("Generation stopped by user.")
                    break
                
                self.status_changed.emit(f"Generating file {i+1}/{total_files} ({config.difficulty.name})...")
                self.logger.info(f"Processing File {i+1}/{total_files}: {config.type.value} - {config.difficulty.name}")
                
                # Generate Batch
                puzzles = []
                for j in range(self.puzzles_per_file):
                    if not self.is_running: break
                    try:
                        grid = generator.generate(config)
                        puzzles.append(grid)
                    except Exception as e:
                        self.logger.error(f"Error generating puzzle {j+1} in file {i+1}: {e}")
                        # Continue or retry? For now continue
                
                if not self.is_running: break

                # Save PDF
                self.status_changed.emit(f"Saving file {i+1}...")
                self._save_batch(pdf_service, puzzles, config, i)
                
                progress = int((i + 1) / total_files * 100)
                self.progress_changed.emit(progress)
            
            if self.is_running:
                self.logger.info("Generation completed successfully.")
                self.status_changed.emit("Generation Completed!")
            
            self.finished.emit()
            
        except Exception as e:
            self.logger.error(f"Critical Error in Worker: {e}", exc_info=True)
            self.error_occurred.emit(str(e))

    def stop(self):
        self.is_running = False

    def _save_batch(self, pdf_service, puzzles, config, index):
        # Format: sudoku_{TYPE}_{SIZE}_{LEVEL}_{TIMESTAMP}_{INDEX}.pdf
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sudoku_{config.type.value}_{config.size}x{config.size}_{config.difficulty.name.lower()}_{timestamp}_{index+1}.pdf"
        filepath = os.path.join(self.output_folder, filename)
        
        try:
            pdf_service.create_pdf(puzzles, filepath)
            self.logger.info(f"Saved: {filename}")
        except Exception as e:
            self.logger.error(f"Failed to save PDF {filename}: {e}")
            raise e

class GeneratorViewModel(QObject):
    property_changed = Signal(str, object) # name, value

    def __init__(self):
        super().__init__()
        self._is_running = False
        self._progress = 0
        self._status_message = "Ready"
        self.worker = None
        self.logger = AppLogger.get_logger()

    @property
    def is_running(self): return self._is_running
    @is_running.setter
    def is_running(self, value):
        if self._is_running != value:
            self._is_running = value
            self.property_changed.emit("is_running", value)

    @property
    def progress(self): return self._progress
    @progress.setter
    def progress(self, value):
        if self._progress != value:
            self._progress = value
            self.property_changed.emit("progress", value)

    @property
    def status_message(self): return self._status_message
    @status_message.setter
    def status_message(self, value):
        if self._status_message != value:
            self._status_message = value
            self.property_changed.emit("status_message", value)

    def start_generation(self, file_count, puzzles_per_file, difficulty_name, type_name, output_folder):
        if self._is_running: return
        
        if not output_folder or not os.path.exists(output_folder):
            self.status_message = "Invalid Output Folder!"
            self.logger.warning("Attempted to start without valid output folder.")
            return

        self.logger.info(f"Start Request: {file_count} files, {puzzles_per_file} puzzles/file, {difficulty_name}, {type_name}")

        # Create Configs
        configs = []
        diff = Difficulty[difficulty_name]
        stype = SudokuType(type_name)
        
        for _ in range(file_count):
            cfg = GenerationConfig(
                difficulty=diff,
                type=stype
            )
            configs.append(cfg)
            
        self.is_running = True
        self.progress = 0
        self.status_message = "Starting..."
        
        self.worker = GeneratorWorker(configs, output_folder, puzzles_per_file)
        self.worker.progress_changed.connect(lambda v: setattr(self, 'progress', v))
        self.worker.status_changed.connect(lambda v: setattr(self, 'status_message', v))
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.error_occurred.connect(self.on_worker_error)
        
        self.worker.start()

    def stop_generation(self):
        if self.worker and self.worker.isRunning():
            self.logger.info("Stopping generation...")
            self.worker.stop()
            self.status_message = "Stopping..."

    def on_worker_finished(self):
        self.is_running = False
        self.progress = 100
        # self.status_message = "Completed" # Worker sets this

    def on_worker_error(self, error_msg):
        self.is_running = False
        self.status_message = f"Error: {error_msg}"
        self.logger.error(f"Worker reported error: {error_msg}")
