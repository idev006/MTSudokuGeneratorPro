import sys
import os
import time
import multiprocessing

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.models.settings import GenerationConfig, Difficulty
from app.services.orchestrator import OrchestratorService
from app.services.logger import LoggerService

def main():
    multiprocessing.freeze_support()
    
    print("Initializing Logger...")
    logger = LoggerService()
    logger.start()
    
    print("Initializing Orchestrator...")
    orchestrator = OrchestratorService()
    
    config = GenerationConfig(difficulty=Difficulty.EASY)
    total_tasks = 2
    
    print(f"Starting production of {total_tasks} puzzles...")
    orchestrator.start_production(config, total_tasks=total_tasks, num_workers=2)
    
    results = []
    start_time = time.time()
    
    while len(results) < total_tasks:
        if time.time() - start_time > 10:
            print("Timeout!")
            break
        
        for res in orchestrator.get_results():
            results.append(res)
            print(f"Got result: {res}")
        
        time.sleep(0.5)
        
    print("Stopping production...")
    orchestrator.stop_production()
    logger.stop()
    print("Done.")

if __name__ == "__main__":
    main()
