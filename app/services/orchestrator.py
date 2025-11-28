import multiprocessing
import queue
import time
import os
from typing import Optional, Callable
from app.services.logger import LoggerService, worker_configurer
from app.models.settings import GenerationConfig
from app.core.factory import PuzzleGenerator

from app.services.worker import worker_task

class OrchestratorService:
    """
    Manages the worker pool and task distribution.
    """
    def __init__(self):
        self.logger_service = LoggerService()
        self.pool: Optional[multiprocessing.Pool] = None
        self.manager = multiprocessing.Manager()
        self.result_queue = self.manager.Queue()
        self.is_running = False

    def start_production(self, config: GenerationConfig, total_tasks: int, num_workers: int = None):
        """
        Starts the generation process.
        """
        if self.is_running:
            self.logger_service.log("Production already running.", level=30) # WARNING
            return

        self.is_running = True
        self.logger_service.log(f"Starting production: {total_tasks} puzzles, Config: {config.difficulty.name}")

        if num_workers is None:
            num_workers = max(1, multiprocessing.cpu_count() - 2)

        self.pool = multiprocessing.Pool(processes=num_workers)
        
        # Launch tasks
        # Note: For very large numbers (e.g. 100k), we shouldn't map all at once.
        # We should use a chunking strategy or apply_async in a loop.
        # For Phase 2 demo (1000 tasks), simple loop is fine.
        
        log_queue = self.logger_service.get_queue()
        
        for i in range(total_tasks):
            self.pool.apply_async(
                worker_task,
                args=(i, config, log_queue, self.result_queue)
            )
        
        self.pool.close() # No more tasks will be added
        # We don't join() here because we want to be non-blocking.
        # The main thread (or a listener thread) should monitor the result_queue.

    def stop_production(self):
        """Terminates all workers."""
        if self.pool:
            self.pool.terminate()
            self.pool.join()
            self.pool = None
        self.is_running = False
        self.logger_service.log("Production stopped.")

    def get_results(self):
        """
        Generator that yields results from the queue as they arrive.
        Non-blocking check.
        """
        while not self.result_queue.empty():
            yield self.result_queue.get()
