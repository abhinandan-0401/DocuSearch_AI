import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class Config:
    """
    Configuration settings for the app, loaded from environment variables.
    """
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL")
    LLM = os.environ.get("LLM")