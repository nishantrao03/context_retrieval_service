# llm_helper/gemini_helper.py

import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI

# Resolve the path to the .env file in the project root (one level up)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
env_path = os.path.join(project_root, '.env')

# Load the environment variables
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    print(f"Warning: .env file not found at {env_path}")


def call_gemini(
    messages: List[Dict[str, str]], 
    tools: Optional[List[Dict[str, Any]]] = None, 
    stream: bool = False
) -> Any:
    """
    Calls the Gemini 2.5 Flash API using the OpenAI Python SDK architecture.
    
    Args:
        messages (List[Dict[str, str]]): A list of message dictionaries (role, content).
        tools (Optional[List[Dict[str, Any]]]): A list of tools/functions for the LLM.
        stream (bool): Whether to stream the response back.
        
    Returns:
        Any: The OpenAI-compatible response object or a stream generator. Returns None on failure.
    """
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            print("Gemini API key found")
        else:
            print("Gemini API key NOT found")
            return None

        # Initialize the OpenAI client pointing to the Gemini base URL
        client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

        # Dictionary to hold the arguments dynamically
        kwargs = {
            "model": "gemini-2.5-flash",
            "messages": messages,
        }

        # Add tools only if provided to prevent API errors
        if tools is not None:
            kwargs["tools"] = tools

        # Execute the streaming response
        if stream:
            kwargs["stream"] = True
            return client.chat.completions.create(**kwargs)

        # Execute the standard synchronous response
        response = client.chat.completions.create(**kwargs)
        return response

    except Exception as e:
        print("Error while calling Gemini API")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")
        return None


# ---------------- TEMP TEST ----------------
if __name__ == "__main__":
    print("--- Testing Gemini API Call ---")
    
    # Define a sample system and user prompt in the OpenAI messages format
    sample_messages = [
        {
            "role": "system", 
            "content": "You are a highly concise AI assistant. Answer in exactly one sentence."
        },
        {
            "role": "user", 
            "content": "What are the core components of a Retrieval-Augmented Generation (RAG) system?"
        }
    ]
    
    # Execute the API call
    test_response = call_gemini(messages=sample_messages)
    
    # Check if the response is valid and print the content
    if test_response:
        print("\nAPI Call Successful!")
        print("-" * 30)
        # Extracting the generated text from the OpenAI-compatible response object
        print(test_response.choices[0].message.content)
        print("-" * 30)
    else:
        print("\nAPI Call Failed. Please check your API key and connection.")