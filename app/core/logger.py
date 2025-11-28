import logging
import os
from logging.handlers import RotatingFileHandler
from PySide6.QtCore import QObject, Signal

class QtLogHandler(logging.Handler, QObject):
    """
    Custom logging handler that emits a Qt signal for each log record.
    Allows the UI to subscribe to log updates.
    """
    log_signal = Signal(str)

    def __init__(self):
        logging.Handler.__init__(self)
        QObject.__init__(self)

    def emit(self, record):
        msg = self.format(record)
        self.log_signal.emit(msg)

class AppLogger:
    """
    Centralized logger configuration.
    """
    _instance = None
    _qt_handler = None

    @staticmethod
    def setup():
        if AppLogger._instance:
            return

        # Create logger
        logger = logging.getLogger("MTSudoku")
        logger.setLevel(logging.DEBUG)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')

        # 1. File Handler (Rotating)
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, "app.log"), 
            maxBytes=1024*1024, # 1MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # 2. Console Handler (Standard Output)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 3. Qt Signal Handler (For UI)
        AppLogger._qt_handler = QtLogHandler()
        AppLogger._qt_handler.setLevel(logging.INFO)
        AppLogger._qt_handler.setFormatter(formatter)
        logger.addHandler(AppLogger._qt_handler)

        AppLogger._instance = logger
        logger.info("Logger initialized.")

    @staticmethod
    def get_qt_handler():
        if not AppLogger._qt_handler:
            AppLogger.setup()
        return AppLogger._qt_handler

    @staticmethod
    def get_logger():
        if not AppLogger._instance:
            AppLogger.setup()
        return AppLogger._instance
