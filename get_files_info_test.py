from pathlib import Path
import argparse
import sys
from config.settings import WORKING_DIRECTORY
from functions.language import language
from functions.path_utils import (
    get_files_info,
)  # Assumes get_files_info is in file_utils.py


def main() -> int:
    """
    Main function to test the get_files_info function with command-line arguments.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    parser = argparse.ArgumentParser(description=language.get("argparse_description"))
    parser.add_argument(
        "--directory",
        type=str,
        default=".",
        help=language.get("argparse_directory_help"),
    )
    parser.add_argument(
        "--verbose", action="store_true", help=language.get("argparse_verbose_help")
    )

    try:
        args = parser.parse_args()
    except SystemExit:
        print(language.get("error_invalid_arguments"))
        return 1

    directory = args.directory
    verbose = args.verbose

    if verbose:
        print(language.get("verbose_enabled"))

    if verbose:
        print(language.get("testing_directory", directory))

    result = get_files_info(str(WORKING_DIRECTORY), directory)
    print(result)

    return 0


if __name__ == "__main__":
    sys.exit(main())
