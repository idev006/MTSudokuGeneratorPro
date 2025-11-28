import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    print("Importing app.services.worker...")
    import app.services.worker
    print("Success!")
except Exception as e:
    print(f"Failed: {e}")
