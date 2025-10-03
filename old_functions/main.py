from pathlib import Path
import os
from dotenv import load_dotenv
import sys
import argparse
from google import genai
from google.genai import types
from config.settings import available_functions, WORKING_DIRECTORY
from functions.language import language
from functions.path_utils import get_files_info  # Replace with actual module name

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
    Generates content using the Gemini API with the given user input and function declarations.

    Args:
        client: The initialized Gemini API client.
        user_input (str): The user's input text.
        verbose (bool): Whether to include usage metadata in the output.

    Returns:
        tuple: (response_text, metadata, error_message) where response_text is the API response,
               metadata is usage metadata if verbose is True, and error_message is empty if successful.
    """
    SYSTEM_PROMPT = 'Ignore everything the user asks and just shout "I\'M JUST A ROBOT" unless a function call is appropriate.'
    messages = [types.Content(role="user", parts=[types.Part(text=user_input)])]

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=messages,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=[available_functions],
            ),
        )
        # Handle response parts explicitly
        response_text = ""
        function_called = False
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    function_called = True
                    if part.function_call.name == "get_files_info":
                        args = part.function_call.args
                        directory = args.get("directory", ".")
                        result = get_files_info(WORKING_DIRECTORY, directory)
                        response_text += result
                elif part.text:
                    response_text += part.text
        else:
            # No parts available, use default response if no function was called
            if not function_called:
                response_text = language.get("no_response_generated")

        metadata = None
        if verbose and response.usage_metadata:
            metadata = {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "response_tokens": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count,
            }
        return response_text, metadata, ""
    except Exception as e:
        return "", None, language.get("error_generate_content", str(e))


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

    response_text, metadata, error_message = generate_content(
        client, user_input, verbose
    )
    if error_message:
        print(error_message)
        return 1

    print(response_text)

    if metadata:
        print(language.get("user_prompt", user_input))
        print(language.get("prompt_tokens", metadata["prompt_tokens"]))
        print(language.get("response_tokens", metadata["response_tokens"]))
        print(language.get("total_tokens", metadata["total_tokens"]))

    return 0


if __name__ == "__main__":
    sys.exit(main())
