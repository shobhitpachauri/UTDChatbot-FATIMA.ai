import warnings
from langchain.chains import RetrievalQA
from langchain_community.llms import HuggingFacePipeline
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import json

# Suppress FutureWarnings
warnings.filterwarnings("ignore", category=FutureWarning)

def load_scraped_data():
    """Load scraped data from JSON file."""
    with open('utd_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def initialize_chatbot():
    """Initialize the chatbot with FAISS index and GPT-2 model"""
    # Load scraped data
    scraped_data = load_scraped_data()
    
    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
    
    # Load vector store
    vector_store = FAISS.load_local(
        "faiss_index", 
        embeddings,
        allow_dangerous_deserialization=True
    )
    
    return scraped_data, vector_store

def get_response(query, scraped_data, vector_store=None):
    """Get a simple response from the chatbot based on the scraped data."""
    # Truncate the query to a maximum length of 1024 characters
    truncated_query = query[:1024].lower()
    print(f"Debug: Truncated query: '{truncated_query}'")  # Debugging output
    
    # Split query into words for better matching
    query_words = set(truncated_query.split())
    
    # Find the best matches in the scraped data
    matches = []
    for entry in scraped_data:
        # Check if 'content' exists and is a list
        if 'content' in entry and isinstance(entry['content'], list):
            for content_item in entry['content']:
                if isinstance(content_item, str):
                    content_lower = content_item.lower()
                    # Count matching words
                    matching_words = sum(1 for word in query_words if word in content_lower)
                    if matching_words > 0:
                        matches.append({
                            "content": content_item,
                            "url": entry.get('url', 'Unknown source'),
                            "score": matching_words
                        })
    
    # Sort matches by score and return top 3
    matches.sort(key=lambda x: x["score"], reverse=True)
    top_matches = matches[:3]
    
    if top_matches:
        response = {
            "answer": "\n\n".join(match["content"] for match in top_matches),
            "sources": list(set(match["url"] for match in top_matches))
        }
    else:
        response = {
            "answer": "I'm sorry, I couldn't find an answer to your question.",
            "sources": []
        }
    
    return response

if __name__ == "__main__":
    # Test the chatbot
    scraped_data, _ = initialize_chatbot()
    while True:
        query = input("\nAsk about UTD (or 'quit' to exit): ")
        if query.lower() in ['quit', 'exit']:
            break
        
        response = get_response(query, scraped_data)
        print("\nAnswer:", response["answer"])
        if response["sources"]:
            print("\nSource:", response["sources"][0])
