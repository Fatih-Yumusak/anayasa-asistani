from vector_store_vercel import VectorStoreVercel
import google.generativeai as genai
import os

class RAGEngine:
    def __init__(self, device: str = None): # device param kept for backward compatibility but unused
        print("Initializing RAG Engine (Vercel/Gemini Mode)...")
        self.vector_store = VectorStoreVercel()
        
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        print("Gemini LLM Loaded.")
    
    def retrieve(self, question: str, k: int = 5):
        return self.vector_store.query(question, n_results=k)

    def generate_prompt_content(self, question: str, context_docs: list) -> str:
        """Constructs the prompt string for Gemini."""
        if not context_docs:
            return ""
            
        context_str = "\n\n".join([f"Madde {d['madde_no']} ({d['metadata'].get('konu', '')}):\n{d.get('text', '')}" for d in context_docs])
        
        # Combined System + User Prompt (Gemini accepts single prompt or history)
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
        # 0. Check for greetings
        greetings = ["merhaba", "selam", "günaydın", "iyi günler", "nasılsın", "hi", "hello"]
        if len(question) < 30 and any(g in question.lower() for g in greetings):
             return {
                "answer": "Merhaba! Ben T.C. Anayasası yapay zeka asistanıyım. Size Anayasa maddeleri ve mevzuat hakkında nasıl yardımcı olabilirim?",
                "retrieved_context": [],
                "prompt_used": "Greeting Check"
            }

        # 1. Retrieve
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

        # Simplified Logic for Demo: Thresholding
        # Note: 'distances' here are 1 - CosineSimilarity. Lower is better?
        # In vector_store_vercel we returned (1 - similarity). So 0 means identical.
        # Cosine Similarity: 1.0 (identical) -> Distance 0.0
        # Cosine Similarity: 0.0 (orthogonal) -> Distance 1.0
        
        best_dist = distances[0]
        print(f"DEBUG: Best distance: {best_dist}")
        
        # Adjust Thresholds for Gemini Embeddings (0.3 is usually a good similarity, so 0.7 distance)
        # Wait, usually for E5: < 0.2 was strict.
        # For Gemini text-embedding-004: distribution might be different.
        # Let's keep it loose for safety first.
        
        for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
             # Filter very bad matches (Distance > 0.6 means Similarity < 0.4)
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
        
        # 3. Call LLM
        print("Generating answer with Gemini...")
        try:
            response = self.model.generate_content(prompt_text)
            answer = response.text
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
