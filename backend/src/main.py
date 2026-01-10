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
def get_engine():
    global engine
    if engine is None:
        try:
            engine = RAGEngine()
        except Exception as e:
            print(f"Engine Init Error: {e}")
            raise HTTPException(status_code=500, detail=f"Engine Init Failed: {str(e)}")
    return engine

class RetrieveRequest(BaseModel):
    question: str

class RetrieveResponse(BaseModel):
    context_docs: list
    message: str

class GenerateRequest(BaseModel):
    question: str
    context_docs: list

class GenerateResponse(BaseModel):
    answer: str
    prompt: str

@app.post("/api/retrieve", response_model=RetrieveResponse)
async def retrieve_context(request: RetrieveRequest):
    engine = get_engine()
    
    try:
        # Step 1: Just retrieve documents
        # This should take < 5 seconds
        results = engine.retrieve(request.question)
        
        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        distances = results['distances'][0]
        
        context_docs = []
        
        if not distances:
             return RetrieveResponse(context_docs=[], message="No results")
        
        for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
             if dist > 0.6: 
                 continue
                 
             context_docs.append({
                "text": doc,
                "madde_no": meta.get("madde", "?"),
                "metadata": meta,
                "score": 1 - dist
            })
            
        return RetrieveResponse(
            context_docs=context_docs,
            message="Found matches" if context_docs else "No strong matches"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Retrieval Error: {e}")
        # Return empty list rather than fail, so flow continues
        return RetrieveResponse(context_docs=[], message=f"Error: {str(e)}")

@app.post("/api/answer", response_model=GenerateResponse)
async def generate_answer(request: GenerateRequest):
    engine = get_engine()
        
    # Step 2: Generate Answer using provided context
    # This also takes < 5-10 seconds
    
    # 0. Check for greetings (in case context is empty but it's a greeting)
    greetings = ["merhaba", "selam", "günaydın", "iyi günler", "nasılsın", "hi", "hello"]
    if len(request.question) < 30 and any(g in request.question.lower() for g in greetings):
         return GenerateResponse(
            answer="Merhaba! Ben T.C. Anayasası yapay zeka asistanıyım. Size Anayasa maddeleri ve mevzuat hakkında nasıl yardımcı olabilirim?",
            prompt="Greeting"
        )
        
    if not request.context_docs:
         return GenerateResponse(
            answer="Anayasa'da bu konuya ilişkin doğrudan bilgi bulunamadı.",
            prompt="No Context"
        )

    # Generate Prompt
    prompt_text = engine.generate_prompt_content(request.question, request.context_docs)
    
    # Call LLM (REST API call happens here)
    # Re-use engine's method but we need to bypass answer_question method's retrieve logic
    # Or refactor engine. Let's just do REST call here or add a method to engine?
    # Better to add a 'generate_answer_from_context' method to engine, or just duplicate the simple requests logic here.
    # To keep it clean, let's call engine logic. 
    # But wait, engine.answer_question does BOTH.
    # We should add `engine.generate_only(question, context)` to rag_engine.py.
    # For now, I will implement the REST call here to avoid editing rag_engine.py again right now if possible, 
    # BUT I should edit rag_engine.py to expose generation logic cleanly.
    # Actually I CANNOT edit rag_engine.py cleanly without tool call.
    # I will inline the generation request here for speed.
    
    import requests
    import time
    
    # Need API Key. defined in engine?
    api_key = engine.api_key
    
    # Models to try in order
    models_to_try = ["gemini-1.5-flash", "gemini-1.0-pro", "gemini-pro"]
    
    last_error = None
    
    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt_text}]
            }]
        }
        
        try:
            print(f"Trying model: {model_name}")
            resp = requests.post(url, json=payload, timeout=30)
            
            if resp.status_code == 429:
                # Rate limit? Wait and try next model or same?
                # Let's simple wait and continue matching loop or retry same?
                # For simplicity, move to next model if this one is busy/rate limited
                time.sleep(2)
                continue
                
            resp.raise_for_status()
            data = resp.json()
            answer = data['candidates'][0]['content']['parts'][0]['text']
            
            # Success!
            # Append Debug info about retrieval confidence
            scores = [f"%{int(d['score']*100)}" for d in request.context_docs[:3]]
            debug_footer = f"\n\n(AI Güveni: {', '.join(scores)} - Model: {model_name})"
            
            return GenerateResponse(answer=answer + debug_footer, prompt=prompt_text)
            
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            last_error = e
            time.sleep(1)

    # If all failed
    err_msg = str(last_error).replace(api_key, "HIDDEN_KEY")
    return GenerateResponse(answer=f"Üzgünüm, tüm yapay zeka modelleri şu an meşgul veya erişilemez durumda. Hata: {err_msg}", prompt=prompt_text)

# Keep legacy endpoint for backward compat if needed, but Frontend will switch
# Removed @app.post("/api/chat") ... to force switch and save space.

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    # Dev run
    uvicorn.run(app, host="0.0.0.0", port=8000)
