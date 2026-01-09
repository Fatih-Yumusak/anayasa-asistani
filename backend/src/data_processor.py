import fitz  # PyMuPDF
import re
import json
import os
from typing import List, Dict

class DataProcessor:
    def __init__(self, pdf_path: str, source_name: str = "Anayasa"):
        self.pdf_path = pdf_path
        self.source_name = source_name
        self.pages = [] # List of tuples: (page_num, text)
        self.chunks = []

    def load_pdf(self):
        """Loads the PDF page by page."""
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"PDF file not found at {self.pdf_path}")
        
        doc = fitz.open(self.pdf_path)
        self.pages = []
        for i, page in enumerate(doc):
            # Page numbers in PDF are 0-indexed usually, but browsers use 1-indexed for #page=
            self.pages.append((i + 1, page.get_text()))
        return self.pages

    def clean_text(self, text: str) -> str:
        """Basic text cleaning."""
        # Remove multiple newlines and extra spaces
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def split_into_articles(self) -> List[Dict]:
        """
        Splits text into articles while tracking Page Numbers.
        """
        articles = []
        
        current_header = "GENEL ESASLAR" # Context for current article being built
        next_header = None # Context found for the NEXT article
        
        current_article_lines = []
        current_article_id = None
        current_article_num = -1
        current_article_page = 1 # Default
        
        # Regex for Roman Numeral Headers (e.g., "I. Devletin şekli", "III. ...")
        header_pattern = re.compile(r'^\s*(?:[IVX]+)\.\s+(.*)', re.IGNORECASE)
        
        # Regex for MADDE start
        # Use simpler regex for robustness 
        madde_pattern = re.compile(r'^\s*MADDE\s+(\d+)', re.IGNORECASE)
        
        def save_current_article():
            nonlocal current_article_lines, current_article_id, current_article_num, current_header, current_article_page
            if current_article_id and current_article_lines:
                text_content = "\n".join(current_article_lines).strip()
                
                # FILTER: Skip "Revision/Footer" articles that are just amendment notes
                # These usually start with "Bu Kanun yayımı..." or are very specific metadata flakes.
                if "Bu Kanun yayımı tarihinde yürürlüğe girer" in text_content:
                    # Skip this garbage chunk
                    current_article_lines = []
                    return
                    
                cleaned_text = self.clean_text(text_content)
                
                # ENRICHMENT
                rich_text = f"KONU: {current_header}\n{cleaned_text}"
                
                # Handle unique IDs
                if self.source_name == "Anayasa":
                     base_id = f"MADDE {current_article_num}"
                else:
                     base_id = f"{self.source_name} MADDE {current_article_num}"
                
                unique_id = base_id
                counter = 1
                existing_ids = {a['id'] for a in articles}
                while unique_id in existing_ids:
                    unique_id = f"{base_id}_{counter}"
                    counter += 1

                articles.append({
                    "id": unique_id,
                    "madde_no": current_article_num,
                    "text": rich_text,
                    "metadata": {
                        "source": self.source_name,
                        "madde": current_article_num,
                        "konu": current_header,
                        "page": current_article_page # CAPTURED PAGE
                    }
                })
            current_article_lines = []

        # Iterate Page by Page
        for page_num, page_text in self.pages:
            lines = page_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line: 
                    continue
                    
                # Check for Section Header
                header_match = header_pattern.match(line)
                if header_match:
                    # Found a header (e.g. "I. Devletin Şekli")
                    # This header applies to the NEXT articles, not the one currently being populated.
                    next_header = header_match.group(1).strip()
                    continue

                # Check for New Article
                madde_match = madde_pattern.match(line)
                if madde_match:
                    # Save previous article (it uses the OLD current_header)
                    save_current_article()
                    
                    # Now update context for the NEW article
                    if next_header:
                        current_header = next_header
                        next_header = None # Reset
                    
                    # Start new
                    current_article_num = int(madde_match.group(1))
                    current_article_id = f"MADDE {current_article_num}"
                    current_article_lines = [line] 
                    current_article_page = page_num # Update Page Pointer
                else:
                    # Continuation 
                    if current_article_id:
                         current_article_lines.append(line)
        
        # Save last
        save_current_article()
        
        self.chunks = articles
        return articles

    def save_chunks(self, output_path: str):
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    processor = DataProcessor("backend/data/anayasa.pdf")
    print("Loading PDF...")
    processor.load_pdf()
    print("Splitting into articles...")
    chunks = processor.split_into_articles()
    print(f"Found {len(chunks)} articles.")
    
    # Save for inspection
    processor.save_chunks("backend/data/chunks.json")
    print("Saved to backend/data/chunks.json")
