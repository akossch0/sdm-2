import os
import numpy as np
import pandas as pd
from pykeen.pipeline import pipeline

# === Load the best configuration ===
result = pipeline(
    training='data/kge/train.tsv',
    testing='data/kge/test.tsv',
    model='TransH',
    model_kwargs={'embedding_dim': 50},
    negative_sampler_kwargs={'num_negs_per_pos': 5},
    training_kwargs={'num_epochs': 100},
    random_seed=42,
    device='cpu'
)

# === Extract entity embeddings ===
model = result.model
entity_embeddings = model.entity_representations[0](indices=None).detach().numpy()

# === Get entity-to-ID mapping ===
entity_to_id = result.training.entity_to_id
entity_id_df = pd.DataFrame({
    "entity": list(entity_to_id.keys()),
    "id": list(entity_to_id.values())
}).sort_values("id")

# === Save outputs ===
output_dir = "data/kge/transh_50_5"
os.makedirs(output_dir, exist_ok=True)

np.save(os.path.join(output_dir, "entity_embeddings.npy"), entity_embeddings)
entity_id_df.to_csv(os.path.join(output_dir, "entity_to_id.csv"), index=False)

print(f"Saved entity embeddings to {output_dir}/entity_embeddings.npy")
print(f"Saved entity-to-id mapping to {output_dir}/entity_to_id.csv")
