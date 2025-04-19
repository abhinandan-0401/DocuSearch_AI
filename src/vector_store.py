import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from typing import List, Tuple
from src.config import Config

class VectorStore:
    """
    ChromaDB implementation of vector store for documents.
    Stores each document's text and embedding vector, and allows similarity search.
    """
    def __init__(self, collection_name="mongodb_documents"):
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient()
        
        # Initialize the OpenAI embedding function
        self.embedding_function = OpenAIEmbeddingFunction(
            api_key=Config.OPENAI_API_KEY,
            model_name=Config.EMBEDDING_MODEL,
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
    
    def add_document(self, doc_id: str, text: str, embedding: List[float] = None):
        """
        Add or update a document in the vector store.
        If embedding is provided, it will be used; otherwise, the embedding function will generate one.
        """
        # Store document with metadata
        metadata = {"source": doc_id}
        
        # If embedding is provided, use it, otherwise let ChromaDB generate one
        if embedding:
            self.collection.add(
                ids=[doc_id],
                documents=[text],
                embeddings=[embedding],
                metadatas=[metadata]
            )
        else:
            self.collection.add(
                ids=[doc_id],
                documents=[text],
                metadatas=[metadata]
            )
    
    def search(self, query_vector: List[float] = None, query_text: str = None, top_k: int = 5) -> List[Tuple[str, float, str]]:
        """
        Search for the top_k most similar documents.
        Either query_vector or query_text must be provided.
        Returns a list of (document_id, similarity_score, document_text) tuples.
        """
        if query_vector:
            results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=top_k
            )
        elif query_text:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=top_k
            )
        else:
            raise ValueError("Either query_vector or query_text must be provided")
        
        # Format results to match the expected return format
        formatted_results = []
        if results["ids"] and len(results["ids"][0]) > 0:
            for i in range(len(results["ids"][0])):
                doc_id = results["ids"][0][i]
                # Distance in ChromaDB is actually a measure of dissimilarity, 
                # lower is better, so we adjust to make it similar to cosine similarity
                similarity = 2.0 - results["distances"][0][i] if "distances" in results else 1.0
                text = results["documents"][0][i]
                formatted_results.append((doc_id, similarity, text))
        
        return formatted_results
    
    def count(self) -> int:
        """Return the number of documents currently in the store."""
        return self.collection.count()