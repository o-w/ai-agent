import os
from dotenv import load_dotenv
import sys
from google import genai
from google.genai import types

import argparse

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

from google import genai

client = genai.Client(api_key=api_key)

def main():
    print("Hello from ai-agent!")
    parser = argparse.ArgumentParser(description='Process verbose flag and a string.')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose mode')
    parser.add_argument('text', type=str, help='A string in quotes')

# Parse arguments
    args = parser.parse_args()

# Access the values
    verbose = args.verbose

    if verbose:
        print("Verbose mode is enabled")

    if len(sys.argv) > 1:
        text = args.text
        user_input = text
    else:
        print("No variable provided")
        #user_input = sys.stdin.readline().strip()
        exit(1)

    messages = [types.Content(role="user", parts=[types.Part(text=user_input)]),]
    response = client.models.generate_content(model='gemini-2.0-flash-001', contents=messages)
    
    print(response.text)
    
    if response.usage_metadata and verbose:
        print(f"User prompt: {user_input}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
        print(f"Total tokens: {response.usage_metadata.total_token_count}")

    if response.usage_metadata:
        exit(0)

if __name__ == "__main__":
    main()
