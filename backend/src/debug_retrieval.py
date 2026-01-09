from rag_engine import RAGEngine
import sys

# Initialize Engine
rag = RAGEngine()

# Problematic Query
question = "türkiyenin yönetim şekli nedir"

print(f"--- Debugging: '{question}' ---")
results = rag.retrieve(question)

documents = results['documents'][0]
metadatas = results['metadatas'][0]
distances = results['distances'][0]

print(f"{'Madde':<10} | {'Distance':<10} | {'Score':<10} | {'Content Start'}")
print("-" * 60)

for doc, meta, dist in zip(documents, metadatas, distances):
    madde_no = meta.get("madde", "?")
    content_preview = doc[:50].replace("\n", " ")
    print(f"{madde_no:<10} | {dist:.4f}     | {1-dist:.4f}     | {content_preview}")

print("\n--- Current Threshold Check ---")
best_dist = distances[0]
print(f"Best Distance: {best_dist:.4f}")

if best_dist < 0.25:
    print("Logic: Winner Take All (<0.25)")
elif best_dist < 0.35:
    print("Logic: Good Match (<0.35)")
else:
    print("Logic: Loose Match")
