import json
import sys
import os
import torch
from tqdm import tqdm

# Ensure backend directory is in path
sys.path.append(os.path.join(os.getcwd(), 'backend/src'))

from rag_engine import RAGEngine

def run_evaluation():
    print("Initializing RAG Engine...")
    # Initialize without reloading if possible, but safely we reload
    engine = RAGEngine(device="cpu")
    
    print("Loading Questions...")
    with open('backend/data/test_questions_100.json', 'r') as f:
        questions = json.load(f)
        
    results = []
    
    # Process
    print(f"Starting Evaluation on sample of 10 questions (Total: {len(questions)})...")
    questions = questions[:10]
    for q in tqdm(questions):
        response = engine.answer_question(q['question'])
        
        # Extract sources
        retrieved_maddes = []
        if response['retrieved_context']:
            for s in response['retrieved_context']:
                retrieved_maddes.append(s['madde_no'])
                
        # Basic Hit Check
        is_hit = False
        target = q['target_madde']
        if target in retrieved_maddes:
            is_hit = True
            
        results.append({
            "id": q['id'],
            "question": q['question'],
            "target_madde": target,
            "retrieved_maddes": retrieved_maddes,
            "is_hit": is_hit,
            "answer_text": response['answer']
        })
        
    # Save Full Results as JSON (for detailed analysis)
    json_path = 'backend/data/eval_results.json'
    with open(json_path, 'w') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # Save Markdown Report
    output_path = 'backend/data/eval_results_raw.md'
    
    # Write as Markdown Report directly for easy reading
    with open(output_path, 'w') as f:
        f.write("# 100 Soru Kapsamlı Değerlendirme Raporu\n\n")
        f.write(f"**Toplam Soru:** {len(questions)}\n")
        
        hits = sum(1 for r in results if r['is_hit'])
        accuracy = (hits / len(questions)) * 100
        f.write(f"**Retrieval Doğruluğu (Target Match):** %{accuracy:.1f}\n\n")
        
        f.write("| ID | Soru | Hedef Madde | Getirilen Maddeler | Durum | Cevap Özeti |\n")
        f.write("|---|---|---|---|---|---|\n")
        
        for r in results:
            status = "✅" if r['is_hit'] else "❌"
            # Truncate answer for table
            ans_short = r['answer_text'][:100].replace('\n', ' ') + "..."
            f.write(f"| {r['id']} | {r['question']} | Md. {r['target_madde']} | {r['retrieved_maddes']} | {status} | {ans_short} |\n")
            
    print(f"Evaluation Complete. Results saved to {output_path}")

if __name__ == "__main__":
    run_evaluation()
