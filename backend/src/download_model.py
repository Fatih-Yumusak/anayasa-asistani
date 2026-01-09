```python
from huggingface_hub import snapshot_download
import os

def download_sequentially():
    # model_id = "Qwen/Qwen2.5-7B-Instruct" 
    model_id = "Qwen/Qwen2.5-1.5B-Instruct"
    print(f"Model ({model_id}) dosyaları teker teker indiriliyor...")
    print("Bu işlem daha stabil olabilir ancak toplam süre uzayabilir.")
    
    # max_workers=1 ensures sequential download
    path = snapshot_download(
        repo_id=model_id,
        max_workers=1,
        resume_download=True
    )
    
    print(f"\nİndirme tamamlandı! Dosyalar şuraya kaydedildi: {path}")
    print("Artık 'python3.12 backend/src/main.py' komutunu çalıştırabilirsiniz, model cache'den hızlıca yüklenecektir.")

if __name__ == "__main__":
    download_sequentially()
