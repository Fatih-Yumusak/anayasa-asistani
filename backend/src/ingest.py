import json
from data_processor import DataProcessor
from vector_store import VectorStore
import os

def ingest_data():
    chunks_path = "backend/data/chunks.json"
    
    # Load chunks
    if not os.path.exists(chunks_path):
        print("Chunks file not found. Running processing...")
        processor = DataProcessor("backend/data/anayasa.pdf")
        processor.load_pdf()
        chunks = processor.split_into_articles()
        processor.save_chunks(chunks_path)
    else:
        print("Loading existing chunks...")
        with open(chunks_path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
            
    print(f"Loaded {len(chunks)} chunks.")
    
    # Initialize Vector Store
    print("Initializing Vector Store...")
    vs = VectorStore()
    
    # Add to DB
    print("Adding to Vector DB...")
    vs.add_documents(chunks)
    print("Ingestion complete.")

if __name__ == "__main__":
    ingest_data()
