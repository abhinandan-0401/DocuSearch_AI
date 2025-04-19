import math
from openai import OpenAI
from src.config import Config

client = OpenAI(
    api_key=Config.OPENAI_API_KEY,
)

def get_text_snippet(text, max_chars=200):
    """
    Extract a snippet of text, trimming to the nearest word/sentence boundary.
    Returns a string of maximum length max_chars.
    """
    if len(text) <= max_chars:
        return text
    
    # Try to find a sentence boundary near the max_chars
    snippet = text[:max_chars]
    for end_char in ['.', '!', '?', ';']:
        last_period = snippet.rfind(end_char)
        if last_period > max_chars * 0.5:  # At least half the max length
            return text[:last_period + 1]
    
    # If no good sentence break, find a word boundary
    last_space = snippet.rfind(' ')
    if last_space > 0:
        return text[:last_space] + "..."
    else:
        return snippet + "..."

def answer_query_with_gpt(question, context_texts, model_name=None):
    """
    Use GPT (or other specified model) to answer a question based on the given context.
    Returns the model's answer as a string.
    """
    # Default to Config.LLM if specified, otherwise use gpt-4
    model = model_name or Config.LLM or "gpt-4"
    
    # Combine context texts with separators
    combined_context = "\n\n---\n\n".join(context_texts)
    
    # Prepare the prompt
    prompt = f"""Answer the following question based only on the provided context. 
If you cannot answer from the context, say "I don't have enough information to answer this question."

Context:
{combined_context}

Question: {question}

Answer:"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based only on the provided context."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  # Lower temperature for more factual responses
            max_tokens=500    # Limit response length
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Re-raise to let the caller handle it
        raise Exception(f"Error getting response from OpenAI: {str(e)}")