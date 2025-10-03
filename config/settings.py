# Settings file to keep track of a few constants

from pathlib import Path
from google.genai import types

MAX_FILE_READ_CHARS = 10000
LANGUAGE = "en"
WORKING_DIRECTORY = Path("/Users/pomegranate/ai-agent/calculator").resolve()

if not WORKING_DIRECTORY.is_dir():
    raise ValueError(
        f"Working directory '{WORKING_DIRECTORY}' does not exist or is not a directory"
    )

# SCHEMA FOR AI-AGENT BELOW

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Read first 10000 characters of a file, and output those characters.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file": types.Schema(
                type=types.Type.STRING,
                description="The file to read, relative to the working directory.",
            ),
        },
    ),
)

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
    ]
)
