import multiprocessing
import os
import logging
import sys
from app.services.logger import worker_configurer
from app.models.settings import GenerationConfig
from app.core.factory import PuzzleGenerator

def worker_task(task_id: int, config: GenerationConfig, log_queue: multiprocessing.Queue, result_queue: multiprocessing.Queue):
    """
    The code running inside each worker process.
    """
    try:
        sys.stderr.write(f"Worker {os.getpid()} started task {task_id} with {config.difficulty}\n")
        sys.stderr.flush()
        
        # 1. Setup Logging
        if log_queue:
            import logging.handlers
            worker_configurer(log_queue)
            logger = logging.getLogger(f"Worker-{os.getpid()}")
            logger.info(f"Worker started task {task_id}")
        
        # 2. Initialize Generator
        generator = PuzzleGenerator()
        
        # 3. Generate
        grid = generator.generate(config)
        
        # 4. Send Result
        result_queue.put({
            "status": "success",
            "task_id": task_id,
            "data": grid
        })
        
        if log_queue:
            logger.info(f"Worker finished task {task_id}")
        
    except Exception as e:
        sys.stderr.write(f"Worker {os.getpid()} failed: {e}\n")
        sys.stderr.flush()
        result_queue.put({
            "status": "error",
            "task_id": task_id,
            "error": str(e)
        })
