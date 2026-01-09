import requests
import time

questions = [
    "Türkiye Devletinin yönetim şekli nedir?",
    "Cumhuriyetin nitelikleri nelerdir?",
    "Devletin bütünlüğü ne demektir?",
    "Resmi dil nedir?",
    "Başkent neresidir?",
    "Egemenlik kime aittir?",
    "Yasama yetkisi kime aittir?",
    "Yürütme yetkisi ve görevi kime aittir?",
    "Yargı yetkisi kime aittir?",
    "Kanun önünde eşitlik nedir?",
    "Anayasa'nın bağlayıcılığı ve üstünlüğü nedir?",
    "Temel hak ve hürriyetlerin niteliği nedir?",
    "Temel hak ve hürriyetler nasıl sınırlanır?",
    "Kişi hürriyeti ve güvenliği nedir?",
    "Özel hayatın gizliliği nedir?",
    "Konut dokunulmazlığı nedir?",
    "Haberleşme hürriyeti nedir?",
    "Yerleşme ve seyahat hürriyeti nedir?",
    "Din ve vicdan hürriyeti nedir?",
    "Düşünce ve kanaat hürriyeti nedir?"
]

def run_test():
    print(f"Starting stress test with {len(questions)} questions on Qwen 7B...")
    print("-" * 50)
    
    total_start = time.time()
    successful = 0
    
    for i, q in enumerate(questions):
        print(f"\nQuestion {i+1}/{len(questions)}: {q}")
        start_time = time.time()
        try:
            # Set a long timeout (e.g., 5 minutes per question)
            response = requests.post("http://localhost:8000/api/chat", json={"question": q}, timeout=300)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "")
                print(f"✅ Answered in {elapsed:.2f}s")
                print(f"Preview: {answer[:100]}...")
                successful += 1
            else:
                print(f"❌ Failed (Status {response.status_code}) in {elapsed:.2f}s")
                print(response.text)
                
        except requests.exceptions.Timeout:
            print(f"❌ Timeout after {time.time() - start_time:.2f}s")
        except Exception as e:
            print(f"❌ Error: {e}")

    total_time = time.time() - total_start
    print("-" * 50)
    print(f"Test Complete.")
    print(f"Successful: {successful}/{len(questions)}")
    print(f"Total Time: {total_time:.2f}s")
    print(f"Average Time: {total_time/len(questions):.2f}s/q")

if __name__ == "__main__":
    run_test()
