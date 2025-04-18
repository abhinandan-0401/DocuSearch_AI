import openai
from config import Config

# Set OpenAI API key for API calls
openai.api_key = Config.OPENAI_API_KEY

def get_embedding(text: str) -> list:
    """
    Generate an embedding vector for the given text using OpenAI's embedding model.
    Returns a list of floats representing the embedding.
    """
    response = openai.Embedding.create(input=text, model=Config.EMBEDDING_MODEL)
    embedding_vector = response['data'][0]['embedding']
    return embedding_vector