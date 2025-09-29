# Settings file to keep track of a few constants

# config/settings.py
from pathlib import Path

WORKING_DIRECTORY = "/Users/pomegranate/ai-agent"
WORKING_DIRECTORY = Path("/Users/pomegranate/ai-agent").resolve()
if not WORKING_DIRECTORY.is_dir():
    raise ValueError(
        f"Working directory '{WORKING_DIRECTORY}' does not exist or is not a directory"
    )
