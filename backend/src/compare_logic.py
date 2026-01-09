import sys
import os
import chromadb
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F

# Setup paths
sys.path.append(os.path.join(os.getcwd(), 'backend/src'))

# 1. Setup Same Embedding Model
device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Loading Model on {device}...")
tokenizer = AutoTokenizer.from_pretrained('intfloat/multilingual-e5-base')
model = AutoModel.from_pretrained('intfloat/multilingual-e5-base').to(device)

def get_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1)
    embeddings = F.normalize(embeddings, p=2, dim=1)
    return embeddings[0].cpu().numpy().tolist()

# 2. Connect to DB
client = chromadb.PersistentClient(path="backend/chroma_db")
collection = client.get_collection("anayasa_collection")

# 3. Define Logics

def old_logic(distances, documents, metadatas):
    """
    Simulates the OLD, permissive logic.
    """
    results = []
    # distances[0] is the list of distances for the first query
    # documents[0] is the list of docs for the first query
    
    if not distances or not distances[0]: return []
    
    current_dists = distances[0]
    best_dist = current_dists[0] # This should be a float
    
    absolute_limit = 0.60
    relative_margin = 0.15 
    
    for doc, meta, dist in zip(documents[0], metadatas[0], current_dists):
        if dist > absolute_limit: continue
        if dist > (best_dist + relative_margin): continue
        results.append(f"Madde {meta.get('madde')} (Dist: {dist:.4f})")
    return results

def new_logic(distances, documents, metadatas):
    """
    The NEW 'Super Strict' logic.
    """
    results = []
    
    if not distances or not distances[0]: return []
    
    current_dists = distances[0]
    best_dist = current_dists[0]
    
    absolute_limit = 0.48
    return_top_1_only = False

    if best_dist < 0.20:
         return_top_1_only = True
         relative_margin = 0.0
    elif best_dist < 0.25:
         relative_margin = 0.015
    elif best_dist < 0.35:
         relative_margin = 0.08
    else:
         relative_margin = 0.12
        
    for i, (doc, meta, dist) in enumerate(zip(documents[0], metadatas[0], current_dists)):
        if dist > absolute_limit: continue
        if return_top_1_only and i > 0: continue
        if dist > (best_dist + relative_margin): continue
        
        results.append(f"Madde {meta.get('madde')} (Dist: {dist:.4f})")
    return results

# 4. Compare Queries
queries = [
    "Türkiye'nin yönetim şekli nedir?",
    "Milletvekili seçilme yeterliliği nelerdir?",
    "Cumhurbaşkanı'nın görevleri nelerdir?"
]

print("\n" + "="*80)
print(f"{'SORU':<40} | {'ESKİ SİSTEM (Permissive)':<35} | {'YENİ SİSTEM (Strict)':<35}")
print("="*80)

for q in queries:
    emb = get_embedding(f"query: {q}")
    res = collection.query(query_embeddings=[emb], n_results=5)
    
    old_res = old_logic(res['distances'], res['documents'], res['metadatas'])
    new_res = new_logic(res['distances'], res['documents'], res['metadatas'])
    
    print(f"'{q[:38]}...'")
    print(f"{'':<40} | {str(old_res):<35} | {str(new_res):<35}")
    print("-" * 80)
