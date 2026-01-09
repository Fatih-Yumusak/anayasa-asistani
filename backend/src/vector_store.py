import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
import os
from typing import List, Dict, Any

class VectorStore:
    def __init__(self, persist_directory: str = "backend/chroma_db", model_name: str = "intfloat/multilingual-e5-base"):
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.model_name = model_name
        
        # Initialize model once
        self.embedding_model = SentenceTransformer(self.model_name)
        
        # We will use a custom embedding function wrapper for SentenceTransformer
        self.embedding_function = self._create_embedding_function()
        
        self.collection = self.client.get_or_create_collection(
            name="anayasa_collection",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"}
        )

    def _create_embedding_function(self):
        # Custom wrapper using the pre-loaded model
        model = self.embedding_model
        
        class STEmbeddingFunction(chromadb.EmbeddingFunction):
            def __call__(self, input: List[str]) -> List[List[float]]:
                # Add "passage: " prefix for document storage
                prefixed_input = ["passage: " + t for t in input]
                embeddings = model.encode(prefixed_input, normalize_embeddings=True)
                return embeddings.tolist()
                
        return STEmbeddingFunction()
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        ids = [doc["id"] for doc in documents]
        documents_text = [doc["text"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]
        
        self.collection.upsert(
            ids=ids,
            documents=documents_text,
            metadatas=metadatas
        )
        print(f"Upserted {len(documents)} documents.")

    def query(self, query_text: str, n_results: int = 5):
        # Use the same pre-loaded model
        # Add "query: " prefix for retrieval
        query_embedding = self.embedding_model.encode(["query: " + query_text], normalize_embeddings=True).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        return results

if __name__ == "__main__":
    # Test initialization
    vs = VectorStore()
    print("VectorStore initialized.")
