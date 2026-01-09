import json
import shutil
import os
import sys
from vector_store import VectorStore

# Clean existing DB to prevent duplicates/ghosts
db_path = "backend/chroma_db"
if os.path.exists(db_path):
    print(f"Removing existing DB at {db_path}...")
    shutil.rmtree(db_path)

print("Initializing Vector Store (New DB)...")
vs = VectorStore(persist_directory=db_path)

print("Loading chunks...")
with open("backend/data/chunks.json", 'r') as f:
    chunks = json.load(f)

print(f"Upserting {len(chunks)} documents...")
vs.add_documents(chunks)
print("Re-indexing Complete.")
