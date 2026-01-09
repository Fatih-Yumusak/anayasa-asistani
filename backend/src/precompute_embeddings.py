import google.generativeai as genai
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

# TO RUN THIS: You need GEMINI_API_KEY in .env
# If user hasn't provided it, this script will fail gracefully.

def precompute_embeddings():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in .env")
        return

    genai.configure(api_key=api_key)
    model = 'models/text-embedding-004'

    chunks_path = "backend/data/chunks.json"
    output_path = "backend/data/embeddings_gemini.json"

    with open(chunks_path, 'r') as f:
        chunks = json.load(f)

    print(f"Loaded {len(chunks)} chunks. Starting embedding...")

    doc_data = []
    
    # Batch if necessary, but simple loop is safer for rate limits
    for i, chunk in enumerate(chunks):
        text = chunk['text']
        # Add context header
        if "metadata" in chunk and "konu" in chunk["metadata"]:
             full_text = f"Bağlam: {chunk['metadata']['konu']}\n\n{text}"
        else:
             full_text = text
             
        try:
            # Task type retrieval_document is optimized for search
            embedding = genai.embed_content(
                model=model,
                content=full_text,
                task_type="retrieval_document"
            )
            
            doc_data.append({
                "id": chunk["id"],
                "text": text,
                "metadata": chunk.get("metadata", {}),
                "embedding": embedding['embedding']
            })
            
            if i % 10 == 0:
                print(f"Processed {i}/{len(chunks)}")
            
            time.sleep(0.1) # Be gentle with free tier rate limits

        except Exception as e:
            print(f"Error at index {i}: {e}")

    with open(output_path, 'w') as f:
        json.dump(doc_data, f)
        
    print(f"Successfully saved {len(doc_data)} embeddings to {output_path}")

if __name__ == "__main__":
    precompute_embeddings()
