# secure-rag/list_models.py

import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API key from .env file in the current directory or parent directories
# Ensure your .env file with GOOGLE_API_KEY is in the secure-rag/ directory
print("Loading environment variables from .env file...")
if load_dotenv():
    print(".env file loaded successfully.")
else:
    print("Warning: .env file not found.")

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY not found in environment variables or .env file.")
    print("Please ensure your API key is set correctly.")
else:
    try:
        # Configure the SDK with your API key
        genai.configure(api_key=api_key)
        print("\nFetching available models from Google AI...")

        # List all available models
        models = genai.list_models()

        print("\n--- Available Models ---")
        found_chat_model = False
        for m in models:
            # Check if the model supports the 'generateContent' method (used by chat models)
            supports_chat = 'generateContent' in m.supported_generation_methods
            
            # Print model name and indicate if it's suitable for chat
            print(f"Model Name: {m.name}")
            # print(f"  Display Name: {m.display_name}") # Optional: More readable name
            # print(f"  Description: {m.description}") # Optional: Model description
            # print(f"  Supported Methods: {m.supported_generation_methods}") # Optional: List all methods
            if supports_chat:
                print("  >> Supports 'generateContent' (Suitable for Chat)")
                found_chat_model = True
            else:
                 # Check if it supports embedding
                 supports_embedding = 'embedContent' in m.supported_generation_methods
                 if supports_embedding:
                     print("  >> Supports 'embedContent' (Suitable for Embeddings)")


        if not found_chat_model:
             print("\nWarning: No models found supporting 'generateContent'. Check API key permissions or available models in your region.")

        print("\n------------------------")
        print("Tip: Look for models like 'models/gemini-1.0-pro' or similar under 'Model Name' that support 'generateContent' for use with ChatGoogleGenerativeAI.")

    except Exception as e:
        print(f"\nAn error occurred while trying to list models: {e}")
        print("Please check your API key and network connection.")

