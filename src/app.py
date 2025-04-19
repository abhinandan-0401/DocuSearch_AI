import logging
from flask import Flask, request, jsonify
from src.config import Config
from src.embedding import get_embedding
from src.vector_store import VectorStore
from src.utils import get_text_snippet, answer_query_with_gpt

# Initialize Flask app
app = Flask(__name__)
# Load configuration into Flask (if needed)
app.config.from_object(Config)

# Initialize ChromaDB vector store
vector_store = VectorStore(collection_name="mongodb_documents")

# Set up basic logging
logging.basicConfig(level=logging.INFO)

@app.route('/documents', methods=['POST'])
def add_document():
    """
    Add a new document to the vector store.
    Expects JSON with 'id' and 'text'.
    """
    data = request.get_json()
    if not data or 'id' not in data or 'text' not in data:
        return jsonify({"error": "Invalid request, 'id' and 'text' are required"}), 400
    doc_id = data['id']
    text = data['text']
    try:
        # Add document to ChromaDB (embedding will be generated automatically)
        vector_store.add_document(doc_id, text)
    except Exception as e:
        logging.error(f"Error adding document to vector store: {e}")
        return jsonify({"error": "Failed to add document to vector store"}), 500
    
    logging.info(f"Document added/updated: id={doc_id}, length={len(text)} chars")
    return jsonify({"message": "Document added", "id": doc_id}), 201

@app.route('/documents/batch', methods=['POST'])
def add_documents_batch():
    """
    Add multiple documents to the vector store in a single request.
    Expects JSON array with objects containing 'id' and 'text'.
    """
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({"error": "Invalid request, expected a JSON array of documents"}), 400
    
    # Validate all documents before processing
    for i, doc in enumerate(data):
        if 'id' not in doc or 'text' not in doc:
            return jsonify({"error": f"Document at index {i} is missing 'id' or 'text'"}), 400
    
    # Collect documents for processing
    ids = [doc['id'] for doc in data]
    texts = [doc['text'] for doc in data]
    metadatas = [{"source": doc['id']} for doc in data]
    
    try:
        # Use ChromaDB's batch processing
        vector_store.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )
    except Exception as e:
        logging.error(f"Error batch adding documents: {e}")
        return jsonify({"error": "Failed to add documents in batch"}), 500
    
    logging.info(f"Batch added {len(data)} documents")
    return jsonify({"message": f"Added {len(data)} documents"}), 201

@app.route('/search', methods=['GET'])
def search_documents():
    """
    Search for documents relevant to a query.
    Expects a 'query' parameter in the URL (and optional 'k' for number of results).
    """
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Missing 'query' parameter"}), 400
    
    # Number of results to return (default 5, or provided via 'k')
    try:
        k = int(request.args.get('k', 5))
    except ValueError:
        k = 5
    
    try:
        # Use direct text search in ChromaDB
        results = vector_store.search(query_text=query, top_k=k)
    except Exception as e:
        logging.error(f"Error searching: {e}")
        return jsonify({"error": "Failed to search documents"}), 500
    
    # Format the results for response (with text snippet for readability)
    response_data = []
    for doc_id, score, text in results:
        snippet = get_text_snippet(text, max_chars=200)
        response_data.append({
            "id": doc_id,
            "score": round(score, 4),
            "snippet": snippet
        })
    logging.info(f"Search query='{query}' - returning {len(response_data)} results")
    return jsonify({"query": query, "results": response_data})

@app.route('/ask', methods=['GET'])
def ask_question():
    """
    Answer a question using the indexed documents as context (uses GPT-4 or specified model).
    Expects a 'question' parameter in the URL.
    """
    question = request.args.get('question')
    if not question:
        return jsonify({"error": "Missing 'question' parameter"}), 400
    # If no documents are available, we cannot answer
    if vector_store.count() == 0:
        return jsonify({"error": "No documents available for context"}), 400
    
    try:
        # Use direct text search in ChromaDB
        results = vector_store.search(query_text=question, top_k=3)
    except Exception as e:
        logging.error(f"Error searching for question context: {e}")
        return jsonify({"error": "Failed to search for question context"}), 500
    
    context_texts = [text for (_, _, text) in results]
    try:
        answer = answer_query_with_gpt(question, context_texts)
    except Exception as e:
        logging.error(f"Error generating answer from GPT: {e}")
        return jsonify({"error": "Failed to generate answer"}), 500
    logging.info(f"Question asked: '{question}' - answer length: {len(answer)} chars")
    return jsonify({"question": question, "answer": answer})

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify the service status.
    """
    return jsonify({"status": "ok", "documents_indexed": vector_store.count()}), 200

if __name__ == '__main__':
    # Run the Flask development server for local testing
    app.run(host='0.0.0.0', port=5000, debug=True)
