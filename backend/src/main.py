from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles # Import
from pydantic import BaseModel
from rag_engine import RAGEngine
import uvicorn
import asyncio
import os

app = FastAPI()

# Mount Static Files (PDFs)
# Ensures that http://localhost:8000/static/anayasa.pdf works
static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/api/legislation")
def get_legislation(source: str = None):
    """Returns the full text of the legislation for the Reader View."""
    chunks_path = os.path.join(static_path, "chunks.json")
    if not os.path.exists(chunks_path):
        return {"error": "Legislation data not found."}
        
    import json
    with open(chunks_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # Filter by Source if provided
    filtered_data = []
    source_query = source.lower() if source else None
    
    for d in data:
        # Check source match
        doc_source = d.get("metadata", {}).get("source", "Anayasa") # Default to Anayasa
        if source and doc_source != source:
            continue
            
        if isinstance(d.get("madde_no"), int):
            filtered_data.append(d)

    filtered_data.sort(key=lambda x: x["madde_no"])
    
    return {"articles": filtered_data}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production specify domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Engine (Global state)
engine = None

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: list
    prompt: str

@app.on_event("startup")
def startup_event():
    global engine
    # Ensure CWD is correct or paths are absolute in RAGEngine
    # backend/src is where this runs? Or root?
    # We'll assume running from root: python backend/src/main.py
    # or uvicorn backend.src.main:app
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    try:
        engine = RAGEngine()
    except Exception as e:
        print(f"Failed to initialize engine: {e}")

@app.post("/api/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):
    if not engine:
        raise HTTPException(status_code=503, detail="RAG Engine not initialized")
    
    try:
        result = engine.answer_question(request.question)
        
        # Format sources
        sources = [
            {
                "madde": ctx["madde_no"], 
                "text": ctx["text"],
                "metadata": ctx["metadata"],
                "score": ctx["score"]
            } 
            for ctx in result["retrieved_context"]
        ]
        
        return QueryResponse(
            answer=result["answer"],
            sources=sources,
            prompt=result["prompt_used"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    # Dev run
    uvicorn.run(app, host="0.0.0.0", port=8000)
