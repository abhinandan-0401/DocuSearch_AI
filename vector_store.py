from typing import List, Tuple
from utils import cosine_similarity

class VectorStore:
    """
    Simple in-memory vector store for documents.
    Stores each document's text and embedding vector, and allows similarity search.
    """
    def __init__(self):
        # Dictionary mapping document ID to its text and embedding
        self.index = {} # {id: {"text": ..., "embedding": ...}}
    
    def add_document(self, doc_id: str, text: str, embedding: List[float]):
        """
        Add or update a document in the vector store.
        If the document ID already exists, its content and embedding are updated.
        """
        self.index[doc_id] = {"text": text, "embedding": embedding}
    
    def search(self, query_vector: List[float], top_k: int = 5) -> List[Tuple[str, float, str]]:
        """
        Search for the top_k most similar documents to the given query_vector.
        Returns a list of (document_id, similarity_score, document_text) tuples.
        """
        results = []
        for doc_id, data in self.index.items():
            score = cosine_similarity(query_vector, data["embedding"])
            results.append((doc_id, score, data["text"]))
        # Sort by similarity score (highest first)
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def count(self) -> int:
        """Return the number of documents currently in the store."""
        return len(self.index)