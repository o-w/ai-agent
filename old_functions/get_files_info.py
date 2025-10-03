from pathlib import Path
from config.settings import *
import os
import subprocess
from functions.language import *


def get_files_info(given_work_directory: str, directory: str = "."):
    try:
        abs_directory = Path(os.path.join(given_work_directory, directory)).resolve()

        if not abs_directory.is_dir():
            return f"Error: {directory} is not a directory"

        abs_given_work_directory = Path(given_work_directory).resolve()
        result = []

        if not abs_given_work_directory.is_relative_to(WORKING_DIRECTORY):
            return f"Directory '{abs_given_work_directory}' is outside the permitted working directory '{WORKING_DIRECTORY}'"

        if not abs_directory.is_relative_to(abs_given_work_directory):
            return f"Error: Cannot list '{directory}' as it is outside the permitted working directory '{abs_given_work_directory}'"

    except FileNotFoundError:
        return f"Directory '{directory}' does not exist"

    try:
        for item in sorted(abs_directory.iterdir(), key=lambda x: x.name):
            try:
                file_size = item.stat().st_size
                is_dir = item.is_dir()
                formatted_line = (
                    f"- {item.name}: file_size={file_size} bytes, is_dir={is_dir}"
                )
                result.append(formatted_line)

            except (PermissionError, FileNotFoundError):
                result.append(
                    f"- {item.name}: file_size=unknown, is_dir=unknown (access error)"
                )

        return "\n".join(result) if result else "Directory is empty"

    except (PermissionError, OSError) as e:
        return f"Cannot list files in '{directory}': {e}"


def get_file_content(given_work_directory, file_path):
    try:
        abs_given_work_directory = Path(given_work_directory).resolve()
        abs_file_path = Path(file_path).resolve()
        abs_joined_file_path = Path(
            os.path.join(abs_given_work_directory, file_path)
        ).resolve()

    except:
        return "File or path error."

    file_content_string = "No file processed yet"

    if not abs_joined_file_path.is_relative_to(abs_given_work_directory):
        print(f"File path: {abs_file_path}")
        print(f"Working directory: {abs_given_work_directory}")
        print(f"Merged file path: {abs_joined_file_path}")
        return f'Error: Cannot read "{abs_file_path}" as it is outside the permitted working directory'

    if not abs_joined_file_path.is_file():
        return (
            f'Error: File not found or is not a regular file: "{abs_joined_file_path}"'
        )
    else:
        with open(abs_joined_file_path, "r") as f:
            file_content_string = f.read(MAX_FILE_READ_CHARS)

    if len(file_content_string) > 9999:
        truncated_message = f'[...File "{file_path}" truncated at 10000 characters].'
        file_content_string = file_content_string + truncated_message
    return file_content_string


def write_file(given_work_directory, file_path, content):
    try:
        abs_given_work_directory = Path(given_work_directory).resolve()
        abs_file_path = Path(file_path).resolve()
        abs_joined_file_path = Path(
            os.path.join(abs_given_work_directory, file_path)
        ).resolve()
    except:
        return "File or path error."

    if not abs_joined_file_path.is_relative_to(abs_given_work_directory):
        print(f"File path: {abs_file_path}")
        print(f"Working directory: {abs_given_work_directory}")
        print(f"Merged file path: {abs_joined_file_path}")
        return f'Error: Cannot write to "{abs_file_path}" as it is outside the permitted working directory'

    try:
        with open(abs_joined_file_path, "w") as file:
            file.write(content)
            # print(f"File "{abs_joined_file_path}" created successfully.")
            # return f'File "{abs_joined_file_path}" created successfully.'
        return (
            f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
        )

    except FileExistsError:
        return "File write error."


def run_python_file(given_work_directory, file_path, args=[]):
    try:
        abs_given_work_directory = Path(given_work_directory).resolve()
        abs_file_path = Path(file_path).resolve()
        abs_joined_file_path = Path(
            os.path.join(abs_given_work_directory, file_path)
        ).resolve()
    except:
        print(abs_given_work_directory)
        print(abs_file_path)
        print(abs_joined_file_path)
        return "File or path error."

    if not abs_joined_file_path.is_relative_to(abs_given_work_directory):
        print(f"File path: {abs_file_path}")
        print(f"Working directory: {abs_given_work_directory}")
        print(f"Merged file path: {abs_joined_file_path}")
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

    if not abs_joined_file_path.is_file():
        return f'Error: File "{file_path}" not found. "'

    if not has_python_extension(abs_joined_file_path):
        return f'Error: "{file_path}" does not have a .py extension'
    else:
        ## execute
        try:
            if isinstance(args, str):
                args = args.split()
            runwithargs = ["python", str(abs_joined_file_path)] + args
            result = subprocess.run(
                runwithargs,
                capture_output=True,
                cwd=str(abs_given_work_directory),
                timeout=30,
                check=False,
                text=True,
            )
            return f"STDOUT:{result.stdout}"
        except subprocess.TimeoutExpired:
            return f"Error: Execution of '{file_path}' timed out after 30 seconds"
        except Exception as e:
            return f"Error: executing Python file: {e}"


def has_python_extension(filename):
    return filename.suffix == ".py"
