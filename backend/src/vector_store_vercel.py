import json
import os
from typing import List, Dict, Any

class VectorStoreVercel:
    def __init__(self, embeddings_path: str = "backend/data/embeddings_gemini.json"):
        self.embeddings_path = embeddings_path
        self.documents = []
        self.vectors = None
        self.model_name = 'models/text-embedding-004'
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in env")
            
        # Lazy load data only when needed (or we can load here if we want to fail fast)
        # For Vercel, it's better to load fast.
        self._load_data()

    def _load_data(self):
        # Local import to reduce cold start time
        import numpy as np
        
        if not os.path.exists(self.embeddings_path):
             print(f"Warning: {self.embeddings_path} not found. DB empty.")
             return

        with open(self.embeddings_path, 'r') as f:
            data = json.load(f)
            
        self.documents = data
        # Convert list of lists to numpy array for fast calculation
        self.vectors = np.array([d['embedding'] for d in data])
        print(f"Vector Store Loaded: {len(self.documents)} docs.")
        
    def query(self, query_text: str, n_results: int = 5):
        # Local imports
        import numpy as np
        import google.generativeai as genai
        
        genai.configure(api_key=self.api_key)

        # 1. Embed Query
        # Task type retrieval_query specific for query side
        q_embed = genai.embed_content(
            model=self.model_name,
            content=query_text,
            task_type="retrieval_query"
        )
        query_vector = np.array(q_embed['embedding'])
        
        # 2. Cosine Similarity
        # Dot product of normalized vectors = Cosine Similarity
        # Note: Gemini embeddings are usually already normalized? Let's assume so or normalize.
        # Check norm
        norm = np.linalg.norm(query_vector)
        if norm > 0:
            query_vector = query_vector / norm
            
        # Vectorized dot product
        # vectors shape: (N, D), query shape: (D,) -> scores: (N,)
        scores = np.dot(self.vectors, query_vector)
        
        # 3. Get Top K
        # argsort returns indices of sorted elements (ascending)
        top_indices = np.argsort(scores)[-n_results:][::-1]
        
        results = {
            "documents": [],
            "metadatas": [],
            "distances": [] # We return distances to match Chroma interface (1 - score or similar)
            # Actually Chroma returns distance (lower better for L2, higher better for Cosine?)
            # We used Cosine Space in Chroma. Chroma Cosine distance = 1 - Cosine Similarity.
        }
        
        for idx in top_indices:
            doc = self.documents[idx]
            score = scores[idx]
            results["documents"].append(doc["text"])
            results["metadatas"].append(doc["metadata"])
            # Convert similarity to distance (0.0 to 1.0)
            # 1.0 similarity -> 0.0 distance
            results["distances"].append(1.0 - score) 
            
        # Format to match ChromaDB list-of-lists structure if needed, or simplify RAGEngine
        # RAGEngine expects: results['documents'][0], results['metadatas'][0], etc.
        return {
            "documents": [results["documents"]], # Chroma returns list of lists (batch)
            "metadatas": [results["metadatas"]],
            "distances": [results["distances"]]
        }
