import os
import pandas as pd
from pykeen.pipeline import pipeline

# === File paths ===
train_path = "data/kge/train.tsv"
test_path = "data/kge/test.tsv"

# === Experiment configurations ===
models_to_run = [
    # TransE hyperparameter exploration
    {"model": "TransE", "embedding_dim": 50, "neg": 5},
    {"model": "TransE", "embedding_dim": 100, "neg": 15},
    {"model": "TransE", "embedding_dim": 200, "neg": 25},

    # TransH hyperparameter exploration
    {"model": "TransH", "embedding_dim": 50, "neg": 5},
    {"model": "TransH", "embedding_dim": 100, "neg": 25},

    # Other models 
    {"model": "ComplEx", "embedding_dim": 150, "neg": 15},
    {"model": "DistMult", "embedding_dim": 100, "neg": 20}
]

results = []

# === Run experiments ===
for config in models_to_run:
    print(f"\nRunning {config['model']} | dim={config['embedding_dim']} | neg={config['neg']}")
    result = pipeline(
        training=train_path,
        testing=test_path,
        model=config["model"],
        model_kwargs={"embedding_dim": config["embedding_dim"]},
        negative_sampler_kwargs={"num_negs_per_pos": config["neg"]},
        training_kwargs={"num_epochs": 100},
        random_seed=42,
        device="cpu"  
    )
    
    metrics = result.metric_results.to_flat_dict()
    
    results.append({
    "Model": config["model"],
    "Embedding Dim": config["embedding_dim"],
    "Neg Samples": config["neg"],
    "MRR": round(metrics.get("both.realistic.mean_reciprocal_rank", 0), 4),
    "Hits@1": round(metrics.get("both.realistic.hits_at_1", 0), 4),
    "Hits@10": round(metrics.get("both.realistic.hits_at_10", 0), 4),
})

# === Output Results Table ===
df = pd.DataFrame(results)
print("\nModel Comparison Results:")
print(df.to_string(index=False))

# Save to CSV for report use
os.makedirs("data/kge", exist_ok=True)
df.to_csv("data/kge/kge_model_comparison.csv", index=False)
