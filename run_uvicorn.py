import os
import sys
import subprocess

# Add the project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set PYTHONPATH environment variable
os.environ["PYTHONPATH"] = project_root + os.pathsep + os.environ.get("PYTHONPATH", "")

# Command to run uvicorn
command = [
    sys.executable,  # Use the current Python interpreter (from venv)
    "-m",
    "uvicorn",
    "backend.api.main:app",
    "--host", "0.0.0.0",
    "--port", "5001"
]

print(f"Starting uvicorn with command: {' '.join(command)}")
subprocess.run(command)
