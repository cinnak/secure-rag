# secure-rag/list_models.py

import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load API key from .env file in the current directory or parent directories
# Ensure your .env file with GOOGLE_API_KEY is in the secure-rag/ directory
logger.info("Loading environment variables from .env file...")
if load_dotenv():
    logger.info(".env file loaded successfully.")
else:
    logger.info("Warning: .env file not found.")

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    logger.info("Error: GOOGLE_API_KEY not found in environment variables or .env file.")
    logger.info("Please ensure your API key is set correctly.")
else:
    try:
        # Configure the SDK with your API key
        genai.configure(api_key=api_key)
        logger.info("\nFetching available models from Google AI...")

        # List all available models
        models = genai.list_models()

        logger.info("\n--- Available Models ---")
        found_chat_model = False
        for m in models:
            # Check if the model supports the 'generateContent' method (used by chat models)
            supports_chat = 'generateContent' in m.supported_generation_methods
            
            # Log model name and indicate if it's suitable for chat
            logger.info(f"Model Name: {m.name}")
            # logger.info(f"  Display Name: {m.display_name}") # Optional: More readable name
            # logger.info(f"  Description: {m.description}") # Optional: Model description
            # logger.info(f"  Supported Methods: {m.supported_generation_methods}") # Optional: List all methods
            if supports_chat:
                logger.info("  >> Supports 'generateContent' (Suitable for Chat)")
                found_chat_model = True
            else:
                # Check if it supports embedding
                supports_embedding = 'embedContent' in m.supported_generation_methods
                if supports_embedding:
                    logger.info("  >> Supports 'embedContent' (Suitable for Embeddings)")

        if not found_chat_model:
            logger.info("\nWarning: No models found supporting 'generateContent'. Check API key permissions or available models in your region.")

        logger.info("\n------------------------")
        logger.info("Tip: Look for models like 'models/gemini-1.0-pro' or similar under 'Model Name' that support 'generateContent' for use with ChatGoogleGenerativeAI.")

    except Exception as e:
        logger.info(f"\nAn error occurred while trying to list models: {e}")
        logger.info("Please check your API key and network connection.")

