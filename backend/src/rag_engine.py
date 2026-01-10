from vector_store_vercel import VectorStoreVercel
import os

class RAGEngine:
    def __init__(self, device: str = None):
        print("Initializing RAG Engine (Lazy Mode)...")
        self.vector_store = None
        self.model = None
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found")
            
    def _initialize_lazy(self):
        if self.vector_store is None:
            print("Lazy Loading: Vector Store...")
            # genai import REMOVED
            self.vector_store = VectorStoreVercel()
            # No need to configure genai or init model object
            print("Lazy Loading Complete.")

    def retrieve(self, question: str, k: int = 5):
        self._initialize_lazy()
        # Fetch more candidates for re-ranking (Hybrid Search)
        results = self.vector_store.query(question, n_results=20)
        
        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        distances = results['distances'][0]
        
        # Combine into objects for sorting
        candidates = []
        for doc, meta, dist in zip(documents, metadatas, distances):
            candidates.append({
                "text": doc,
                "metadata": meta,
                "vector_score": 1 - dist, # Similarity
                "final_score": 1 - dist
            })
            
        # Keyword Boosting (Simple BM25-ish luck)
        # Normalize keys
        q_tokens = set(question.lower().split())
        
        for cand in candidates:
            # Boost if Topic matches
            topic = cand["metadata"].get("konu", "").lower()
            topic_score = sum(1 for t in q_tokens if t in topic) * 0.05
            
            # Boost if Text matches (less weight)
            text_lower = cand["text"].lower()
            text_score = sum(1 for t in q_tokens if t in text_lower) * 0.01
            
            # Specific Hardcoded Boosts for Common Failures
            # "Yönetim şekli" -> Madde 1 (Devletin Şekli)
            if "yönetim" in question.lower() and "şekli" in question.lower() and cand["metadata"].get("madde") == 1:
                cand["final_score"] += 0.3
                
            cand["final_score"] += topic_score + text_score
            
        # Sort by Final Score
        candidates.sort(key=lambda x: x["final_score"], reverse=True)
        
        # STRICT FILTERING LOGIC
        # If the top result is very strong (boosted or high vector score), drop loosely related ones.
        # This prevents "Madde 82" from appearing when "Madde 1" is the clear answer.
        
        final_top_k = []
        if candidates:
            best = candidates[0]
            final_top_k.append(best)
            
            # If Best is Boosted (meaning Keyword Match) -> Be very strict with others
            is_boosted = best["final_score"] > best["vector_score"] + 0.1
            
            # STRICT Relevance Cutoff
            # Logic: If the best result is "Good Enough" (boosted or high score), 
            # we should NOT dilute it with mediocre results.
            
            best_is_very_strong = best["final_score"] > 0.85 or is_boosted
            
            for other in candidates[1:k]:
                if best_is_very_strong:
                     # If best is strong, ONLY accept other STRONG matches.
                     # 1. Must be keyword boosted
                     # 2. OR Must be within 1% score of the best (mathematically identical)
                     is_other_good = (
                         (other["final_score"] > other["vector_score"] + 0.1) or # Is Boosted
                         (other["final_score"] > best["final_score"] - 0.01)     # Identical Score
                     )
                     
                     if is_other_good:
                         final_top_k.append(other)
                     # Else: Drop it.
                else:
                    # If best is weak (e.g. 0.7), maybe we are seeking broadly.
                    # But still, don't include trash. Cutoff at 15% drop.
                    if other["final_score"] > best["final_score"] - 0.15:
                        final_top_k.append(other)
        
        # Re-construct return format
        return {
            "documents": [[c["text"] for c in final_top_k]],
            "metadatas": [[c["metadata"] for c in final_top_k]],
            "distances": [[1 - c["vector_score"] for c in final_top_k]]
        }

    def generate_prompt_content(self, question: str, context_docs: list) -> str:
        """Constructs the prompt string for Gemini."""
        if not context_docs:
            return ""
            
        context_str = "\n\n".join([f"Madde {d['madde_no']} ({d['metadata'].get('konu', '')}):\n{d.get('text', '')}" for d in context_docs])
        
        prompt = (f"""Sen T.C. Anayasası konusunda uzman, yardımsever bir hukuk asistanısın. Kullanıcının sorusunu verilen bağlama göre yanıtla.

Kurallar:
1. Cevabın NET, DOĞRU ve ANLAŞILIR olsun.
2. Hukuki metni robot gibi kopyalama; maddeleri kendi cümlelerinle sadeleştirerek özetle.
3. Yanlış veya uydurma bilgi verme. Bağlamda yoksa 'Bilgi yok' de.
4. İlgili madde numaralarını (örn: Madde 1) mutlaka belirt.

Bağlam:
{context_str}

Soru: {question}""")
        
        return prompt
        
    def answer_question(self, question: str):
        # 0. Check for greetings (No need to load engine for this!)
        greetings = ["merhaba", "selam", "günaydın", "iyi günler", "nasılsın", "hi", "hello"]
        if len(question) < 30 and any(g in question.lower() for g in greetings):
             return {
                "answer": "Merhaba! Ben T.C. Anayasası yapay zeka asistanıyım. Size Anayasa maddeleri ve mevzuat hakkında nasıl yardımcı olabilirim?",
                "retrieved_context": [],
                "prompt_used": "Greeting Check"
            }

        # 1. Retrieve (Triggers lazy load)
        print(f"Retrieving for: {question}")
        results = self.retrieve(question)
        
        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        distances = results['distances'][0]
        
        context_docs = []
        
        if not distances:
             return {
                "answer": "Üzgünüm, aradığınız kriterlere uygun bir bilgi bulamadım.",
                "retrieved_context": [],
                "prompt_used": "No Results"
            }
        
        best_dist = distances[0]
        print(f"DEBUG: Best distance: {best_dist}")
        
        for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
             if dist > 0.6: 
                 continue
                 
             context_docs.append({
                "text": doc,
                "madde_no": meta.get("madde", "?"),
                "metadata": meta,
                "score": 1 - dist
            })
            
        if not context_docs:
             return {
                "answer": "Anayasa'da bu konuya ilişkin doğrudan bilgi bulunamadı.",
                "retrieved_context": [],
                "prompt_used": "Filtered"
            }

        # 2. Generate Prompt
        prompt_text = self.generate_prompt_content(question, context_docs)
        
        # 3. Call LLM (REST API)
        print("Generating answer with Gemini (REST)...")
        import requests
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt_text}]
            }]
        }
        
        try:
            resp = requests.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            # Extract text: candidates[0].content.parts[0].text
            answer = data['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            return {
                "answer": f"API Hatası: {str(e)}",
                "retrieved_context": context_docs,
                "prompt_used": prompt_text
            }
        
        return {
            "answer": answer,
            "retrieved_context": context_docs,
            "prompt_used": prompt_text
        }

if __name__ == "__main__":
    engine = RAGEngine()
    q = "Cumhuriyetin nitelikleri nelerdir?"
    res = engine.answer_question(q)
    print("Cevap:", res['answer'])
    print("Kaynaklar:", [m['madde_no'] for m in res['retrieved_context']])
