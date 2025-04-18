import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class Config:
    """
    Configuration settings for the app, loaded from environment variables.
    """
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "text-embedding-ada-002")
    # Model for Q&A (GPT-4 by default, can override to "gpt-3.5-turbo" via env)
    QA_MODEL = os.environ.get("QA_MODEL", "gpt-4")