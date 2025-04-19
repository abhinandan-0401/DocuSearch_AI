from openai import OpenAI
from src.config import Config
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

client = OpenAI(
    api_key=Config.OPENAI_API_KEY,
)

# Initialize the OpenAI embedding function for ChromaDB
embedding_function = OpenAIEmbeddingFunction(
    api_key=Config.OPENAI_API_KEY,
    model_name=Config.EMBEDDING_MODEL,
)

def get_embedding(text: str) -> list:
    """
    Generate an embedding vector for the given text using OpenAI's embedding model.
    Returns a list of floats representing the embedding.
    """
    response = client.embeddings.create(
        input=text, 
        model=Config.EMBEDDING_MODEL,
    )
    embedding_vector = response.data[0].embedding
    return embedding_vector

def get_embeddings(texts: list) -> list:
    """
    Generate embedding vectors for a list of texts using ChromaDB's embedding function.
    This is more efficient for batch processing.
    Returns a list of embedding vectors.
    """
    return embedding_function(texts)