import numpy as np
import openai
from config import Config

# Ensure the OpenAI API key is set for any OpenAI calls from this module
openai.api_key = Config.OPENAI_API_KEY

def cosine_similarity(vec1: list, vec2: list) -> float:
    """
    Compute the cosine similarity between two vectors.
    """
    v1 = np.array(vec1, dtype=float)
    v2 = np.array(vec2, dtype=float)
    if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
        # If either vector has zero magnitude, return 0 similarity
        return 0.0
    cos_sim = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    return float(cos_sim)

def get_text_snippet(text: str, max_chars: int = 200) -> str:
    """
    Return a snippet of the text (at most max_chars characters) for preview purposes.
    """
    if text is None:
        return ""
    if len(text) <= max_chars:
        return text
    else:
        return text[:max_chars] + "..."

def answer_query_with_gpt(question: str, docs: list, model: str = None) -> str:
    """
    Use OpenAI's GPT model to answer a question given a list of document texts as context.
    Returns the answer as a string.
    """
    if model is None:
        model = Config.QA_MODEL
    # Construct the prompt with provided documents
    context = ""
    for i, doc_text in enumerate(docs, start=1):
        context += f"Document {i}:\n{doc_text}\n\n"
    prompt = (
        "Use the following documents to answer the question.\n"
        "If the answer is not contained in the documents, say you do not have that information.\n\n"
        f"{context}"
        f"Question: {question}\nAnswer:"
    )
    # Call the OpenAI ChatCompletion API (GPT model) to get an answer
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0
    )
    answer = response['choices'][0]['message']['content'].strip()
    return answer