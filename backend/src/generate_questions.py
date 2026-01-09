import json
import random

def generate_questions():
    # Load chunks
    with open('backend/data/chunks.json', 'r') as f:
        chunks = json.load(f)
    
    # We want 100 questions.
    # We will deterministically map Article titles/contents to questions.
    # Since we don't have an LLM in this script to generate creative questions,
    # we will use templates based on the "Konu" (Heading) and "Madde" content.
    
    questions = []
    
    # Filter for real articles (digits)
    valid_chunks = [c for c in chunks if str(c['madde_no']).isdigit()]
    
    # Shuffle to get random distribution or pick specifically?
    # Let's pick a diverse set: Early (1-20), Rights (20-70), Organs (70-150), etc.
    # Actually, let's just loop and generate.
    
    templates = [
        "{} hakkında anayasa ne der?",
        "{} ile ilgili hükümler nelerdir?",
        "Anayasaya göre {} nedir?",
        "{} konusu nasıl düzenlenmiştir?"
    ]
    
    # Hand-picked/Heuristic list to ensure high quality for "Kapsamlı" aspect
    # We will generate synthetic questions based on the 'konu' field.
    
    count = 0
    for chunk in valid_chunks:
        konu = chunk['metadata']['konu']
        madde = chunk['madde_no']
        text = chunk['text']
        
        if len(konu) < 5: continue 
        
        # Simple heuristic question generation
        q_text = f"{konu} nedir?"
        if "hakkı" in konu.lower() or "hürriyeti" in konu.lower():
            q_text = f"{konu} anayasada nasıl tanımlanmıştır?"
        elif "görevleri" in konu.lower():
             q_text = f"{konu.split('görevleri')[0]} görevleri nelerdir?"
             
        questions.append({
            "id": count + 1,
            "question": q_text,
            "target_madde": madde,
            "target_konu": konu
        })
        count += 1
        if count >= 100:
            break
            
    # Save
    with open('backend/data/test_questions_100.json', 'w') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    
    print(f"Generated {len(questions)} questions.")

if __name__ == "__main__":
    generate_questions()
