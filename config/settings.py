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

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Execute a python file after checking if the extension is correct.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Run this python file, if extension is correct.",
            ),
        },
    ),
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Write a file to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Write a new file in working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="Content of file",
            ),
        },
        #        "required": ["file_path", "content"]
    ),
)


available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)
