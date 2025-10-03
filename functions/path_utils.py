from pathlib import Path
from config.settings import MAX_FILE_READ_CHARS, WORKING_DIRECTORY
import os
import subprocess
from functions.language import language  # Import the language module


def check_path_within_directory(given_work_directory, file_path):
    """
    Checks if a file or directory is within a valid working directory.

    Args:
        given_work_directory (str): The base working directory path
        file_path (str): The file or directory path to check

    Returns:
        tuple: (is_valid, error_message) where is_valid is True if within valid directory,
               False otherwise, and error_message explains the failure reason if applicable
    """
    try:
        abs_given_work_directory = Path(given_work_directory).resolve()
        if not abs_given_work_directory.is_dir():
            return (False, language.get("error_invalid_dir", given_work_directory))
        if not abs_given_work_directory.is_relative_to(WORKING_DIRECTORY):
            return (
                False,
                language.get(
                    "error_outside_directory",
                    abs_given_work_directory,
                    WORKING_DIRECTORY,
                ),
            )

        abs_joined_file_path = Path(
            os.path.join(abs_given_work_directory, file_path)
        ).resolve()
        if abs_joined_file_path.is_relative_to(abs_given_work_directory):
            return (True, "")
        return (
            False,
            language.get(
                "error_outside_directory", file_path, abs_given_work_directory
            ),
        )
    except (FileNotFoundError, ValueError):
        return (
            False,
            language.get("error_path_resolution", given_work_directory, file_path),
        )


def get_files_info(given_work_directory: str, directory: str = "."):
    is_valid, error_message = check_path_within_directory(
        given_work_directory, directory
    )

    if not is_valid:
        return error_message

    try:
        abs_directory = Path(os.path.join(given_work_directory, directory)).resolve()
        result = []
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
        return "\n".join(result) if result else language.get("directory_empty")
    except (PermissionError, OSError) as e:
        return language.get("error_list_files", directory, str(e))


def get_file_content(given_work_directory, file):
    is_valid, error_message = check_path_within_directory(given_work_directory, file)

    if not is_valid:
        return error_message

    try:
        abs_joined_file_path = Path(os.path.join(given_work_directory, file)).resolve()

        if not abs_joined_file_path.is_file():
            return language.get("error_file_not_found", abs_joined_file_path)

        with open(abs_joined_file_path, "r") as f:
            file_content_string = f.read(MAX_FILE_READ_CHARS)

        if len(file_content_string) >= MAX_FILE_READ_CHARS:
            truncated_message = (
                f'[...File "{file}" truncated at {MAX_FILE_READ_CHARS} characters].'
            )
            file_content_string = (
                file_content_string[:MAX_FILE_READ_CHARS] + truncated_message
            )
        return file_content_string

    except (FileNotFoundError, PermissionError):
        return language.get("error_file_access")


def write_file(given_work_directory, file_path, content):
    is_valid, error_message = check_path_within_directory(
        given_work_directory, file_path
    )

    if not is_valid:
        return error_message

    try:
        abs_joined_file_path = Path(
            os.path.join(given_work_directory, file_path)
        ).resolve()

        with open(abs_joined_file_path, "w") as file:
            file.write(content)
        return language.get("success_write_file", file_path, len(content))

    except (FileNotFoundError, PermissionError):
        return language.get("error_file_access")


def run_python_file(given_work_directory, file_path, args=[]):
    is_valid, error_message = check_path_within_directory(
        given_work_directory, file_path
    )

    if not is_valid:
        return error_message

    try:
        abs_joined_file_path = Path(
            os.path.join(given_work_directory, file_path)
        ).resolve()

        if not abs_joined_file_path.is_file():
            return language.get("error_file_not_exists", file_path)

        if not has_python_extension(abs_joined_file_path):
            return language.get("error_no_py_extension", file_path)

        try:
            if isinstance(args, str):
                args = args.split()
            runwithargs = ["python", str(abs_joined_file_path)] + args
            result = subprocess.run(
                runwithargs,
                capture_output=True,
                cwd=str(Path(given_work_directory).resolve()),
                timeout=30,
                check=False,
                text=True,
            )
            return f"STDOUT:{result.stdout}"
        except subprocess.TimeoutExpired:
            return language.get("error_execution_timeout", file_path)
        except Exception as e:
            return language.get("error_execution", str(e))

    except (FileNotFoundError, PermissionError):
        return language.get("error_file_access")


def has_python_extension(filename):
    return filename.suffix == ".py"
