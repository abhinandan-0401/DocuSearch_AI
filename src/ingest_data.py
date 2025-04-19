import pandas as pd
import os
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from tqdm import tqdm
from src.config import Config

def ingest_from_dataframe(df, collection_name="mongodb_movies", batch_size=100):
    """
    Ingest data from a pandas DataFrame into ChromaDB.
    The DataFrame should contain at least:
    - 'id': unique identifier for each document
    - 'text': the text content to be indexed (e.g., 'fullplot')
    - 'title': title or name of the document (for metadata)
    - 'embedding' (optional): pre-computed embedding for the document
    
    Returns the ChromaDB collection object.
    """
    print(f"Starting ingestion of {len(df)} documents to collection '{collection_name}'")
    
    # Initialize ChromaDB client
    chroma_client = chromadb.PersistentClient()
    
    # Initialize the OpenAI embedding function
    embedding_function = OpenAIEmbeddingFunction(
        api_key=Config.OPENAI_API_KEY,
        model_name=Config.EMBEDDING_MODEL,
    )
    
    # Create or get the collection
    try:
        collection = chroma_client.get_collection(
            name=collection_name,
            embedding_function=embedding_function
        )
        print(f"Using existing collection '{collection_name}'")
    except:
        collection = chroma_client.create_collection(
            name=collection_name,
            embedding_function=embedding_function
        )
        print(f"Created new collection '{collection_name}'")
    
    # Process the DataFrame in batches
    total_batches = (len(df) + batch_size - 1) // batch_size
    for i in tqdm(range(total_batches), desc="Processing batches"):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, len(df))
        batch_df = df.iloc[start_idx:end_idx]
        
        ids = []
        documents = []
        metadatas = []
        embeddings = []
        has_embeddings = 'plot_embedding' in batch_df.columns or 'embedding' in batch_df.columns
        
        for _, row in batch_df.iterrows():
            # Get or create document ID
            doc_id = str(row.get('id', row.name))
            
            # Get document text (from 'text', 'fullplot', or other specified field)
            text_field = 'fullplot' if 'fullplot' in row else 'text'
            if text_field not in row:
                print(f"Warning: No text found for document {doc_id}, skipping")
                continue
            doc_text = row[text_field]
            
            # Create metadata with title and other fields
            metadata = {}
            if 'title' in row:
                metadata['title'] = row['title']
            
            # Add to batch lists
            ids.append(doc_id)
            documents.append(doc_text)
            metadatas.append(metadata)
            
            # Add embedding if available
            if has_embeddings:
                embedding_field = 'plot_embedding' if 'plot_embedding' in row else 'embedding'
                embedding = row.get(embedding_field, None)
                if isinstance(embedding, list):
                    embeddings.append(embedding)
        
        # Add batch to collection with or without embeddings
        if has_embeddings and len(embeddings) == len(ids):
            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
        else:
            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
        
    print(f"Ingestion complete. Collection '{collection_name}' now has {collection.count()} documents.")
    return collection

if __name__ == "__main__":
    # Example usage
    print("Loading sample data from MongoDB movies dataset...")
    df = pd.read_json("hf://datasets/MongoDB/embedded_movies/sample_mflix.embedded_movies.json")
    
    # Limit to a smaller set for testing
    df = df.head(250)
    
    # Ingest data
    collection = ingest_from_dataframe(df, collection_name="mongodb_movies") 