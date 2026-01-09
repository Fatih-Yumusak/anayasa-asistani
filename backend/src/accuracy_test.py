import requests
import json
import time

# Test Data: Question -> Expected Article Number + Critical Keywords
test_data = [
    {"q": "Türkiye Devletinin yönetim şekli nedir?", "expected_madde": 1, "keywords": ["Cumhuriyet"]},
    {"q": "Cumhuriyetin nitelikleri nelerdir?", "expected_madde": 2, "keywords": ["demokratik", "laik", "sosyal", "hukuk"]},
    {"q": "Türkiye Devleti'nin resmi dili nedir?", "expected_madde": 3, "keywords": ["Türkçe"]},
    {"q": "Anayasa'nın değiştirilemeyecek maddeleri hangileridir?", "expected_madde": 4, "keywords": ["1", "2", "3", "değiştirilemez"]},
    {"q": "Devletin temel amaç ve görevleri nelerdir?", "expected_madde": 5, "keywords": ["bağımsızlığını", "bütünlüğünü", "Cumhuriyeti", "refah"]},
    {"q": "Egemenlik kime aittir?", "expected_madde": 6, "keywords": ["Milletindir", "kayıtsız"]},
    {"q": "Yasama yetkisi kime aittir?", "expected_madde": 7, "keywords": ["Meclis", "TBMM", "devredilemez"]},
    {"q": "Yürütme yetkisi ve görevi kime aittir?", "expected_madde": 8, "keywords": ["Cumhurbaşkanı"]},
    {"q": "Yargı yetkisi kim tarafından kullanılır?", "expected_madde": 9, "keywords": ["mahkeme", "bağımsız"]},
    {"q": "Kanun önünde eşitlik ilkesi nedir?", "expected_madde": 10, "keywords": ["eşit", "ayırım"]},
    {"q": "Anayasa hükümleri kimleri bağlar?", "expected_madde": 11, "keywords": ["yasama", "yürütme", "yargı", "bağlayıcı"]},
    {"q": "Herkesin sahip olduğu temel haklar nelerdir?", "expected_madde": 12, "keywords": ["kişiliğine bağlı", "dokunulamaz", "devredilemez"]},
    {"q": "Kişinin dokunulmazlığı ve yaşama hakkı nedir?", "expected_madde": 17, "keywords": ["yaşama", "maddi", "manevi"]},
    {"q": "Angarya ve zorla çalıştırma serbest midir?", "expected_madde": 18, "keywords": ["yasak", "zorla"]},
    {"q": "Özel hayatın gizliliği hakkı nedir?", "expected_madde": 20, "keywords": ["Özel hayat", "aile", "gizli"]},
    {"q": "Konut dokunulmazlığı nedir?", "expected_madde": 21, "keywords": ["dokunulamaz", "girilemez"]},
    {"q": "Haberleşme hürriyeti nedir?", "expected_madde": 22, "keywords": ["haberleşme", "gizlilik"]},
    {"q": "Din ve vicdan hürriyeti neleri kapsar?", "expected_madde": 24, "keywords": ["vicdan", "dini", "inanç"]},
    {"q": "Düşünceyi açıklama ve yayma hürriyeti nedir?", "expected_madde": 26, "keywords": ["düşünce", "açıklama", "yayma"]},
    {"q": "Mülkiyet hakkı ne demektir?", "expected_madde": 35, "keywords": ["mülkiyet", "miras"]},
    {"q": "Türkiye'nin milli marşı nedir?", "expected_madde": 3, "keywords": ["İstiklal"]}
]

def run_accuracy_test():
    print(f"Starting Quality Test with {len(test_data)} questions on Qwen 1.5B...")
    print("-" * 70)
    
    retrieval_score = 0
    generation_score = 0
    failed_questions = []

    for i, item in enumerate(test_data):
        question = item["q"]
        expected_madde = item["expected_madde"]
        keywords = item["keywords"]
        
        try:
            response = requests.post("http://localhost:8000/api/chat", json={"question": question}, timeout=90)
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "")
                sources = data.get("sources", [])
                
                # 1. Retrieval Check
                retrieved_maddes = [src.get('madde') for src in sources]
                is_retrieval_correct = False
                for m in retrieved_maddes:
                    if str(m) == str(expected_madde):
                        is_retrieval_correct = True
                        break
                
                if is_retrieval_correct:
                    retrieval_score += 1
                
                # 2. Generation Quality Check (Keyword Matching)
                # Count how many keywords appear in the answer
                found_keywords = [k for k in keywords if k.lower() in answer.lower()]
                # We consider it "Correct" if at least 50% of keywords are found or if it's a short answer with the main keyword
                # For strictness, let's say ALL critical keywords for short answers, or majority for long.
                # Simplified: If >0 keywords found (at least slightly relevant) implies connection. 
                # Better: Let's require majority match.
                
                is_generation_correct = False
                if len(found_keywords) >= len(keywords) / 2: # At least half needed
                    is_generation_correct = True
                    generation_score += 1
                
                print(f"Q{i+1}: {question}")
                print(f"   -> Retrieval: {'✅' if is_retrieval_correct else '❌'} (Found: {retrieved_maddes})")
                print(f"   -> Generation: {'✅' if is_generation_correct else '❌'} (Matches: {found_keywords}/{keywords})")
                
                if i == 0: # Print first answer for inspection
                     print(f"   [INSPECT Q1 Answer]:\n{answer}\n")

                if not is_generation_correct:
                    print(f"      [Answer Preview]: {answer[:100]}...")
                    failed_questions.append({"q": question, "type": "Generation", "answer": answer})
                    
            else:
                 print(f"❌ Q{i+1}: API Error {response.status_code}")

        except Exception as e:
            print(f"❌ Q{i+1}: Exception {e}")
            
    # Final Report
    print("-" * 70)
    print(f"Retrieval Accuracy: {retrieval_score}/{len(test_data)} ({(retrieval_score/len(test_data))*100:.1f}%)")
    print(f"Generation Accuracy: {generation_score}/{len(test_data)} ({(generation_score/len(test_data))*100:.1f}%)")
    print("-" * 70)

if __name__ == "__main__":
    run_accuracy_test()
