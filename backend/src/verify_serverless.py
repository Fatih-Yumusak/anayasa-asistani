from rag_engine import RAGEngine
import os
from dotenv import load_dotenv

load_dotenv()

def test_serverless():
    print("Testing Serverless setup...")
    print(f"API Key present: {'Yes' if os.getenv('GEMINI_API_KEY') else 'No'}")
    
    try:
        engine = RAGEngine()
        q = "Cumhuriyetin nitelikleri nelerdir?"
        print(f"Asking: {q}")
        
        result = engine.answer_question(q)
        
        print("\n--- Result ---")
        print(f"Answer: {result['answer'][:100]}...")
        print("Sources:")
        for doc in result['retrieved_context']:
             print(f"- Madde {doc['madde_no']} (Score: {doc['score']:.4f})")
             
        if any(d['madde_no'] == 2 for d in result['retrieved_context']):
            print("\n✅ Success: Madde 2 retrieved.")
        else:
            print("\n❌ Failure: Madde 2 not found.")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    test_serverless()
