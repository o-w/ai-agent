from pathlib import Path
import os
from dotenv import load_dotenv
import sys
import argparse
from google import genai
from google.genai import types
from functions.language import *  # Import the language module
from functions.path_utils import *  # Import path utility functions
from config.settings import *

# Load environment variables
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")


def initialize_client(api_key: str) -> tuple:
    """
    Initializes the Gemini API client with the provided API key.

    Args:
        api_key (str): The API key for Gemini API.

    Returns:
        tuple: (client, error_message) where client is the initialized client or None,
               and error_message is empty if successful or contains the error reason.
    """
    if not api_key:
        return None, language.get("error_missing_api_key")
    try:
        client = genai.Client(api_key=api_key)
        return client, ""
    except Exception as e:
        return None, language.get("error_client_init", str(e))


def generate_content(client, user_input: str, verbose: bool = False) -> tuple:
    """
    Generates content using the Gemini API with the given user input.

    Args:
        client: The initialized Gemini API client.
        user_input (str): The user's input text.
        verbose (bool): Whether to include usage metadata and debug info in the output.

    Returns:
        tuple: (response_text, metadata, function_calls, error_message)
               where response_text is the API response text,
               metadata is usage metadata if verbose is True,
               function_calls is a list of function call details,
               and error_message is empty if successful.
    """
    SYSTEM_PROMPT = """
    You are a helpful AI coding agent. When a user asks a question or makes a request, make a function call plan. Available functions:
    - get_files_info(directory): List files and directories in the specified directory (relative to the working directory).
    - get_file_content(file): Read the first 10000 characters of the specified file (relative to the working directory).
    - write_file(file): Write to a file.
    - run_python_file(file): Execute a python file.
    All paths must be relative to the working directory. Do not include the working directory in your function call arguments.
    """
    messages = [types.Content(role="user", parts=[types.Part(text=user_input)])]

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions], system_instruction=SYSTEM_PROMPT
            ),
        )
        response_text = ""
        function_calls = []
        metadata = None

        # Extract response text and function calls from candidates
        if response.candidates:
            candidate = response.candidates[0]  # Take the first candidate
            if verbose:
                print(f"Debug: Candidate content: {candidate.content}")
            if hasattr(candidate, "content") and candidate.content.parts:
                for part in candidate.content.parts:
                    # Check if part has text and it's a string
                    if hasattr(part, "text") and isinstance(part.text, str):
                        response_text += part.text
                    # Check for function calls
                    if hasattr(part, "function_call") and part.function_call:
                        try:
                            function_calls.append(
                                {
                                    "name": part.function_call.name,
                                    "args": dict(part.function_call.args),
                                }
                            )
                        except (AttributeError, TypeError) as e:
                            if verbose:
                                print(
                                    f"Debug: Invalid function call in part: {part}, error: {str(e)}"
                                )
                            continue
            else:
                if verbose:
                    print("Debug: No content parts in candidate")

        # Extract metadata if verbose
        if verbose and response.usage_metadata:
            metadata = {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "response_tokens": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count,
            }

        return response_text, metadata, function_calls, ""
    except Exception as e:
        if verbose:
            print(f"Debug: Exception in generate_content: {str(e)}")
        return "", None, [], language.get("error_generate_content", str(e))


def main() -> int:
    """
    Main function to handle command-line arguments and interact with the Gemini API.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    parser = argparse.ArgumentParser(description=language.get("argparse_description"))
    parser.add_argument(
        "--verbose", action="store_true", help=language.get("argparse_verbose_help")
    )
    parser.add_argument("text", type=str, help=language.get("argparse_text_help"))

    try:
        args = parser.parse_args()
    except SystemExit:
        print(language.get("error_invalid_arguments"))
        return 1

    verbose = args.verbose
    user_input = args.text

    if not user_input:
        print(language.get("error_no_input"))
        return 1

    if verbose:
        print(language.get("verbose_enabled"))

    client, error_message = initialize_client(api_key)
    if not client:
        print(error_message)
        return 1

    response_text, metadata, function_calls, error_message = generate_content(
        client, user_input, verbose
    )
    if error_message:
        print(error_message)
        return 1

    # Print response text if available
    if response_text:
        print(response_text)
    elif not function_calls:
        print(language.get("error_no_response", user_input))

    # Handle function calls
    if function_calls:
        print("\nFunction Calls:")
        # Map function names to their implementations
        function_map = {
            "get_files_info": get_files_info,
            "get_file_content": get_file_content,
            "run_python_file": run_python_file,
            "write_file": write_file,
        }
        for call in function_calls:
            func_name = call["name"]
            func_args = call["args"]
            print(f"Function: {func_name}, Arguments: {func_args}")

            # Execute the function if it exists
            if func_name in function_map:
                try:
                    # Inject WORKING_DIRECTORY as the first argument
                    result = function_map[func_name](WORKING_DIRECTORY, **func_args)
                    print(f"Result: {result}")
                    # print(
                    #    f"Would call function: {func_name} with arguments {func_args}"
                    # )
                except Exception as e:
                    print(language.get("error_function_execution", func_name, str(e)))
            else:
                print(language.get("error_unknown_function", func_name))

    # Print metadata if verbose
    if metadata:
        print(language.get("user_prompt", user_input))
        print(language.get("prompt_tokens", metadata["prompt_tokens"]))
        print(language.get("response_tokens", metadata["response_tokens"]))
        print(language.get("total_tokens", metadata["total_tokens"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
