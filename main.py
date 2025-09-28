import os
from dotenv import load_dotenv
import sys

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

from google import genai

client = genai.Client(api_key=api_key)

def main():
    print("Hello from ai-agent!")
    if len(sys.argv) > 1:
        user_input = sys.argv[1]  # First argument after script name
    else:
        print("No variable provided")
        user_input = sys.stdin.readline().strip()

    response = client.models.generate_content(
    model='gemini-2.0-flash-001', contents=user_input)
    
    print(response.text)
    
    if response.usage_metadata:
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
        print(f"Total tokens: {response.usage_metadata.total_token_count}")

if __name__ == "__main__":
    main()
