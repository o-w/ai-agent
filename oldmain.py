from pathlib import Path
import os
from dotenv import load_dotenv
import sys
import argparse
from google import genai
from google.genai import types
from functions.language import *  # Import the language module
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
        verbose (bool): Whether to include usage metadata in the output.

    Returns:
        tuple: (response_text, metadata, function_calls, error_message)
               where response_text is the API response text,
               metadata is usage metadata if verbose is True,
               function_calls is a list of function call details,
               and error_message is empty if successful.
    """
    SYSTEM_PROMPT = "You are a helpful AI coding agent. When a user asks a question or makes a request, make a function call plan. You can perform the following functions: - List files, and directories. And you can output the content of those files. All paths you provide should be relative to the working path. You do not need to specify the working directory in your function calls, as it will be injected. If you can determine it, feel free to include it."
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
            if hasattr(candidate, "content") and candidate.content.parts:
                for part in candidate.content.parts:
                    # Check if part has text and it's a string
                    if hasattr(part, "text") and isinstance(part.text, str):
                        response_text += part.text
                    # Check for function calls
                    if hasattr(part, "function_call"):
                        function_calls.append(
                            {
                                "name": part.function_call.name,
                                "args": dict(part.function_call.args),
                            }
                        )

        # Extract metadata if verbose
        if verbose and response.usage_metadata:
            metadata = {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "response_tokens": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count,
            }

        return response_text, metadata, function_calls, ""
    except Exception as e:
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

    # Print response text
    print(response_text)

    # Print function calls if any
    if function_calls:
        print("\nFunction Calls:")
        for call in function_calls:
            print(f"Function: {call['name']}, Arguments: {call['args']}")

    # Print metadata if verbose
    if metadata:
        print(language.get("user_prompt", user_input))
        print(language.get("prompt_tokens", metadata["prompt_tokens"]))
        print(language.get("response_tokens", metadata["response_tokens"]))
        print(language.get("total_tokens", metadata["total_tokens"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
