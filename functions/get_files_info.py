from pathlib import Path
from config.settings import WORKING_DIRECTORY
import os


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
