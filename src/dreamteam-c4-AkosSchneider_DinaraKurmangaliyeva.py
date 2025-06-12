import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

# === Paths to embedding and mapping files ===
embedding_path = "data/kge/transh_50_5/entity_embeddings.npy"
entity_map_path = "data/kge/transh_50_5/entity_to_id.csv"

# === Load embeddings and entities ===
print("Loading embeddings and entity mappings...")
embeddings = np.load(embedding_path)
entity_df = pd.read_csv(entity_map_path, names=["entity", "id"])
entity_df = entity_df.sort_values("id").reset_index(drop=True)

# === Filter only author entities ===
print("Filtering author entities...")
author_mask = entity_df["entity"].str.contains("author_")
author_entities = entity_df[author_mask].reset_index(drop=True)
author_entities["id"] = author_entities["id"].astype(int)  # Ensure it's integer
author_embeddings = embeddings[author_entities["id"].values]

# === Perform KMeans clustering with k=4 ===
n_clusters = 4
print(f"Clustering author embeddings into {n_clusters} groups...")
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
author_entities["cluster"] = kmeans.fit_predict(author_embeddings)

# === Compute silhouette score ===
sil_score = silhouette_score(author_embeddings, author_entities["cluster"])
print(f"Silhouette Score (k={n_clusters}): {sil_score:.4f}")

# === Dimensionality Reduction for Visualization ===
print("Reducing dimensions using PCA for visualization...")
pca = PCA(n_components=2)
pca_result = pca.fit_transform(author_embeddings)

# Add to DataFrame
author_entities["x"] = pca_result[:, 0]
author_entities["y"] = pca_result[:, 1]

# === Plot the clusters ===
print("Generating cluster plot...")
plt.figure(figsize=(10, 6))
for i in range(n_clusters):
    cluster_points = author_entities[author_entities["cluster"] == i]
    plt.scatter(cluster_points["x"], cluster_points["y"], label=f"Cluster {i}", alpha=0.7)

plt.title("Author Clusters (PCA Projection)")
plt.xlabel("PCA Component 1")
plt.ylabel("PCA Component 2")
plt.legend()
plt.grid(True)

# === Save outputs ===
output_dir = "data/kge/clustering/authors"
os.makedirs(output_dir, exist_ok=True)
plot_path = os.path.join(output_dir, "authors_clusters_pca_k4.png")
csv_path = os.path.join(output_dir, "authors_clusters_k4.csv")

plt.savefig(plot_path)
author_entities.to_csv(csv_path, index=False)

print(f"\Clustering complete!")
print(f"• Plot saved to: {plot_path}")
print(f"• Clustered author list saved to: {csv_path}")
print(f"• Silhouette Score: {sil_score:.4f}")
