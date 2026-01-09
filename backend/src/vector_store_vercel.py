import json
import os
import math
from typing import List, Dict, Any

class VectorStoreVercel:
    def __init__(self, embeddings_path: str = "backend/data/embeddings_gemini.json"):
        self.embeddings_path = embeddings_path
        self.documents = []
        self.vectors = [] # List of lists (not numpy array)
        self.model_name = 'models/text-embedding-004'
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in env")
            
        # Lazy load data only when needed (or we can load here if we want to fail fast)
        self._load_data()

    def _load_data(self):
        if not os.path.exists(self.embeddings_path):
             print(f"Warning: {self.embeddings_path} not found. DB empty.")
             return

        with open(self.embeddings_path, 'r') as f:
            data = json.load(f)
            
        self.documents = data
        self.vectors = [d['embedding'] for d in data]
        print(f"Vector Store Loaded: {len(self.documents)} docs.")
        
    def query(self, query_text: str, n_results: int = 5):
        # Local import used to be here, now removed.
        import requests
        
        # 1. Embed Query
        url = f"https://generativelanguage.googleapis.com/v1beta/{self.model_name}:embedContent?key={self.api_key}"
        
        payload = {
            "content": {
                "parts": [{ "text": query_text }]
            },
            "taskType": "RETRIEVAL_QUERY"
        }
        
        try:
            resp = requests.post(url, json=payload, timeout=10)
            resp.raise_for_status() # Raise for 4xx/5xx
            frame = resp.json()
            # Extract embedding: frame['embedding']['values']
            query_vector = frame['embedding']['values']
        except Exception as e:
            print(f"Embedding API Error: {e}")
            # Fallback or empty result to avoid crash
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
        
        # 2. Cosine Similarity (Pure Python)
        
        # Calculate norm of query vector
        query_norm = math.sqrt(sum(x * x for x in query_vector))
        
        scores = []
        for doc_vec in self.vectors:
            # Dot Product
            dot_product = sum(a * b for a, b in zip(doc_vec, query_vector))
            # Doc vectors are usually normalized by embedding model, but let's be safe?
            # Assuming pre-computed vectors are normalized or we trust dot product for ranking if query is normalized.
            # Actually for cosine similarity: (A . B) / (|A| * |B|)
            # If we assume doc vectors |B| approx 1 (usually true for embeddings), and we normalize A...
            
            # Let's do full cosine for correctness
            doc_norm = math.sqrt(sum(x * x for x in doc_vec))
            
            if query_norm * doc_norm == 0:
                score = 0.0
            else:
                score = dot_product / (query_norm * doc_norm)
            scores.append(score)
        
        # 3. Get Top K
        # Create list of (index, score)
        indexed_scores = list(enumerate(scores))
        # Sort by score descending
        indexed_scores.sort(key=lambda x: x[1], reverse=True)
        
        top_indices = [x[0] for x in indexed_scores[:n_results]]
        
        results = {
            "documents": [],
            "metadatas": [],
            "distances": [] 
        }
        
        for idx in top_indices:
            doc = self.documents[idx]
            score = scores[idx]
            results["documents"].append(doc["text"])
            results["metadatas"].append(doc["metadata"])
            # Convert similarity to distance
            results["distances"].append(1.0 - score) 
            
        return {
            "documents": [results["documents"]],
            "metadatas": [results["metadatas"]],
            "distances": [results["distances"]]
        }
