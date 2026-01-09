from rag_engine import RAGEngine
import time

def run_evaluation():
    print("Self-Evaluation Modu Başlatılıyor...")
    engine = RAGEngine()
    
    test_cases = [
        {
            "question": "Cumhuriyetin nitelikleri nelerdir?", 
            "keywords": ["demokratik", "laik", "sosyal", "hukuk"],
            "expected_madde": 2
        },
        {
            "question": "Egemenlik kime aittir?", 
            "keywords": ["Millet"],
            "expected_madde": 6
        },
        {
            "question": "Yasama yetkisi kime aittir?", 
            "keywords": ["Türkiye Büyük Millet Meclisi", "TBMM"],
            "expected_madde": 7
        },
        {
            "question": "Herkesin yaşama hakkı var mıdır?", 
            "keywords": ["yaşama", "hakkı"],
            "expected_madde": 17
        }
    ]
    
    score = 0
    total = len(test_cases)
    
    print(f"\nToplam {total} adet test sorusu çalıştırılacak.\n")
    
    for i, test in enumerate(test_cases):
        print(f"Test {i+1}: {test['question']}")
        
        start_time = time.time()
        result = engine.answer_question(test["question"])
        duration = time.time() - start_time
        
        answer = result["answer"].lower()
        retrieved_maddes = [d["madde_no"] for d in result["retrieved_context"]]
        
        # Check Keywords
        keyword_match = any(k.lower() in answer for k in test["keywords"])
        
        # Check Retrieval
        madde_match = test["expected_madde"] in retrieved_maddes
        
        status = "BAŞARILI" if (keyword_match and madde_match) else "BAŞARISIZ"
        if status == "BAŞARILI":
            score += 1
            
        print(f"  - Süre: {duration:.2f}s")
        print(f"  - Anahtar Kelimeler Bulundu mu?: {keyword_match}")
        print(f"  - Doğru Madde ({test['expected_madde']}) Getirildi mi?: {madde_match} (Gelenler: {retrieved_maddes})")
        print(f"  - Sonuç: {status}")
        print("-" * 30)

    accuracy = (score / total) * 100
    print(f"\nGenel Başarım: %{accuracy:.1f}")
    if accuracy < 80:
        print("Öneri: RAG pipeline'ını veya promptları iyileştirmeniz gerekebilir.")
    else:
        print("Sistem kararlı görünüyor.")

if __name__ == "__main__":
    run_evaluation()
