import requests
import json

def test_query():
    url = "http://localhost:8000/api/chat"
    payload = {"question": "Ayrımcılık yasağı nedir?"}
    
    print(f"Sending query: {payload['question']}")
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        print("\n--- Answer ---")
        print(data['answer'])
        
        print("\n--- Sources ---")
        for src in data.get('sources', []):
            print(f"- {src.get('madde_no')} (Score: {src.get('score', 0):.4f}) SOURCE: {src.get('metadata', {}).get('source')}")
            
    except Exception as e:
        print(f"Error: {e}")
        
    # Also save to file
    with open("backend/data/tihek_test_result.md", "w") as f:
        f.write("# TİHEK Yasası Doğrulama Testi\n\n")
        f.write(f"**Soru:** {payload['question']}\n\n")
        f.write(f"**Cevap:** {data['answer']}\n\n")
        f.write("### Kaynaklar:\n")
        for src in data.get('sources', []):
            f.write(f"- **{src.get('madde')}** (Score: {src.get('score', 0):.4f})\n")
            f.write(f"  - Kaynak: {src.get('metadata', {}).get('source')}\n")
            f.write(f"  - Metin Özeti: {src.get('text', '')[:100]}...\n")

if __name__ == "__main__":
    test_query()
