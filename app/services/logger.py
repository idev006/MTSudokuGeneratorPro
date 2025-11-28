import logging
import multiprocessing
import threading
import queue
import os
import sys
from datetime import datetime
from typing import Optional

class LoggerService:
    """
    Centralized logging service using a multiprocessing Queue.
    Ensures thread-safe and process-safe logging.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.manager = multiprocessing.Manager()
        self.log_queue = self.manager.Queue()
        self.stop_event = threading.Event()
        self.listener_thread: Optional[threading.Thread] = None
        
        # Ensure log directory exists
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.log_file = os.path.join(self.log_dir, f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        # Setup internal logger for the listener
        self.file_logger = logging.getLogger("AppMasterLogger")
        self.file_logger.setLevel(logging.DEBUG)
        
        # File Handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s [%(processName)s] %(levelname)s: %(message)s')
        file_handler.setFormatter(formatter)
        self.file_logger.addHandler(file_handler)
        
        # Console Handler (Optional, for debugging)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.file_logger.addHandler(console_handler)

    def start(self):
        """Starts the background listener thread."""
        if self.listener_thread and self.listener_thread.is_alive():
            return
            
        self.stop_event.clear()
        self.listener_thread = threading.Thread(target=self._listener_loop, daemon=True, name="LogListenerThread")
        self.listener_thread.start()
        self.log("LoggerService started.")

    def stop(self):
        """Stops the listener thread."""
        self.log("Stopping LoggerService...")
        self.stop_event.set()
        if self.listener_thread:
            self.listener_thread.join()

    def _listener_loop(self):
        """
        Continuously reads from the queue and writes to the log file.
        Runs in the Main Process.
        """
        while not self.stop_event.is_set() or not self.log_queue.empty():
            try:
                # Timeout allows checking stop_event periodically
                record = self.log_queue.get(timeout=0.1)
                self._handle_record(record)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"CRITICAL ERROR in LogListener: {e}", file=sys.stderr)

    def _handle_record(self, record):
        """Process a log record."""
        if isinstance(record, dict):
            level = record.get('level', logging.INFO)
            msg = record.get('msg', '')
            self.file_logger.log(level, msg)
        elif isinstance(record, str):
            self.file_logger.info(record)
        elif isinstance(record, logging.LogRecord):
            self.file_logger.handle(record)

    def get_queue(self):
        """Returns the queue to be passed to worker processes."""
        return self.log_queue

    def log(self, message: str, level: int = logging.INFO):
        """Log a message from the main process."""
        self.log_queue.put({'level': level, 'msg': message})

# Helper function for workers to configure their logging to send to the queue
def worker_configurer(queue):
    import logging.handlers
    h = logging.handlers.QueueHandler(queue)
    root = logging.getLogger()
    root.addHandler(h)
    root.setLevel(logging.DEBUG)
