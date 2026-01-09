from data_processor import DataProcessor
import json
import os

def ingest_all():
    all_chunks = []
    
    # 1. Ingest Constitution (Anayasa)
    print("Processing Anayasa...")
    p1 = DataProcessor("backend/data/anayasa.pdf", source_name="Anayasa")
    p1.load_pdf()
    chunks1 = p1.split_into_articles()
    all_chunks.extend(chunks1)
    print(f"Anayasa Articles: {len(chunks1)}")
    
    # 2. Ingest Human Rights Law (6701)
    print("Processing Law 6701...")
    p2 = DataProcessor("backend/data/6701.pdf", source_name="TIHEK Kanunu") # TIHEK = Turkiye Insan Haklari E. K.
    p2.load_pdf()
    chunks2 = p2.split_into_articles()
    all_chunks.extend(chunks2)
    print(f"Law 6701 Articles: {len(chunks2)}")
    
    # Save Combined
    output_path = "backend/data/chunks.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
        
    print(f"Total Articles Saved: {len(all_chunks)} to {output_path}")

if __name__ == "__main__":
    ingest_all()
