import unittest
import sys
import os
import time
import multiprocessing

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.settings import GenerationConfig, Difficulty
from app.services.orchestrator import OrchestratorService
from app.services.logger import LoggerService

class TestOrchestrator(unittest.TestCase):
    
    def setUp(self):
        # Ensure logger is started
        self.logger = LoggerService()
        self.logger.start()
        self.orchestrator = OrchestratorService()

    def tearDown(self):
        self.orchestrator.stop_production()
        self.logger.stop()

    def test_production_flow(self):
        """Test generating a small batch of puzzles."""
        config = GenerationConfig(difficulty=Difficulty.EASY)
        total_tasks = 5
        
        print(f"\nStarting generation of {total_tasks} puzzles...")
        self.orchestrator.start_production(config, total_tasks=total_tasks, num_workers=2)
        
        results = []
        timeout = 10 # seconds
        start_time = time.time()
        
        while len(results) < total_tasks:
            if time.time() - start_time > timeout:
                self.fail("Timed out waiting for results")
            
            for res in self.orchestrator.get_results():
                results.append(res)
                print(f"Received result: {res['task_id']} - {res['status']}")
            
            time.sleep(0.5)
            
        self.assertEqual(len(results), total_tasks)
        for res in results:
            self.assertEqual(res['status'], 'success')
            self.assertIsNotNone(res['data'])
            # Verify it's a valid grid
            self.assertEqual(res['data'].size, 9)

if __name__ == '__main__':
    # Fix for multiprocessing on Windows
    multiprocessing.freeze_support()
    unittest.main()
