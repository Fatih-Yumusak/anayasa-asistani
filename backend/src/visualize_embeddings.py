import os
import sys
import chromadb
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
import pandas as pd
import seaborn as sns

# Ensure backend directory is in path (though running from root usually works if modules installed)
sys.path.append(os.path.join(os.getcwd(), 'backend/src'))

def visualize():
    print("Connecting to ChromaDB...")
    client = chromadb.PersistentClient(path="backend/chroma_db")
    collection = client.get_collection("anayasa_collection")
    
    # Get all embeddings
    print("Fetching data...")
    result = collection.get(include=['embeddings', 'metadatas', 'documents'])
    
    embeddings = result['embeddings']
    metadatas = result['metadatas']
    documents = result['documents']
    
    if embeddings is None or len(embeddings) == 0:
        print("No embeddings found!")
        return

    print(f"Found {len(embeddings)} vectors.")
    
    # Convert to array
    X = np.array(embeddings)
    
    # Run t-SNE
    print("Running t-SNE (this might take a few seconds)...")
    tsne = TSNE(n_components=2, perplexity=min(30, len(X)-1), random_state=42, init='pca', learning_rate='auto')
    X_embedded = tsne.fit_transform(X)
    
    # Prepare DataFrame for plotting
    df = pd.DataFrame(X_embedded, columns=['x', 'y'])
    
    # Extract Article Numbers for coloring
    maddes = []
    labels = []
    for m in metadatas:
        num = m.get('madde', 0)
        maddes.append(num)
        # Create a simplified label for plot (only label every 5th or 10th to avoid clutter)
        labels.append(f"Md.{num}" if num > 0 else "Başlangıç")

    df['Madde_No'] = maddes
    df['Label'] = labels
    
    # Plotting
    print("Generating Plot...")
    plt.figure(figsize=(16, 12))
    sns.set_style("whitegrid")
    
    # Scatter plot with color gradient based on Article Number
    scatter = sns.scatterplot(
        data=df, 
        x='x', 
        y='y', 
        hue='Madde_No', 
        palette='viridis', 
        s=100,
        alpha=0.8,
        edgecolor='k'
    )
    
    # Annotate specific key articles (System form, Anthem, etc.)
    key_articles = [1, 2, 3, 4, 5, 10, 42, 66] # Example key articles
    
    texts = []
    for i, point in df.iterrows():
        madde_num = point['Madde_No']
        if madde_num in key_articles:
             plt.text(point['x']+0.2, point['y']+0.2, f"Md.{madde_num}", fontsize=12, weight='bold', color='black')
             
    plt.title("T.C. Anayasası - Madde Embedding Uzayı (t-SNE)", fontsize=20)
    plt.xlabel("t-SNE Dimension 1")
    plt.ylabel("t-SNE Dimension 2")
    
    output_path = "backend/data/embeddings_tsne.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Visualization saved to {output_path}")

if __name__ == "__main__":
    visualize()
