import logging
from flask import Flask, request, jsonify
from config import Config
from embedding import get_embedding
from vector_store import VectorStore
from utils import get_text_snippet, answer_query_with_gpt

# Initialize Flask app
app = Flask(__name__)
# Load configuration into Flask (if needed)
app.config.from_object(Config)

# Initialize an in-memory vector store (could be replaced with a persistent vector DB)
vector_store = VectorStore()

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
        # Generate embedding for the document text
        embedding_vector = get_embedding(text)
    except Exception as e:
        logging.error(f"Error generating embedding: {e}")
        return jsonify({"error": "Failed to generate embedding"}), 500
    # Add or update the document in the vector store
    vector_store.add_document(doc_id, text, embedding_vector)
    logging.info(f"Document added/updated: id={doc_id}, length={len(text)} chars")
    return jsonify({"message": "Document added", "id": doc_id}), 201

@app.route('/search', methods=['GET'])
def search_documents():
    """
    Search for documents relevant to a query.
    Expects a 'query' parameter in the URL (and optional 'k' for number of results).
    """
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Missing 'query' parameter"}), 400
    try:
        query_vector = get_embedding(query)
    except Exception as e:
        logging.error(f"Error generating query embedding: {e}")
        return jsonify({"error": "Failed to generate query embedding"}), 500
    # Number of results to return (default 5, or provided via 'k')
    try:
        k = int(request.args.get('k', 5))
    except ValueError:
        k = 5
    results = vector_store.search(query_vector, top_k=k)
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
        # Embed the question to find relevant documents
        query_vector = get_embedding(question)
    except Exception as e:
        logging.error(f"Error generating question embedding: {e}")
        return jsonify({"error": "Failed to generate question embedding"}), 500
    # Retrieve top documents for context (e.g., top 3 most relevant)
    results = vector_store.search(query_vector, top_k=3)
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
