from pykeen.pipeline import pipeline
from pykeen.triples import TriplesFactory
import numpy as np
import pandas as pd
import os

# === Load the data ===
data_dir = "data/kge"
train_path = os.path.join(data_dir, "train.tsv")
test_path = os.path.join(data_dir, "test.tsv")

# === Run the PyKEEN pipeline with TransE ===
result = pipeline(
    training=train_path,
    testing=test_path,
    model="TransE",
    model_kwargs={"embedding_dim": 100},  
    training_kwargs={"num_epochs": 100},  
    random_seed=42
)

# === Get embeddings ===
model = result.model
entity_embeddings = model.entity_representations[0](indices=None).detach().numpy()
relation_embeddings = model.relation_representations[0](indices=None).detach().numpy()

entity_to_id = result.training.entity_to_id
id_to_entity = {v: k for k, v in entity_to_id.items()}
relation_to_id = result.training.relation_to_id
id_to_relation = {v: k for k, v in relation_to_id.items()}

# === Step 1: Choose a paper ===
paper_uri = "http://example.org/publication-ontology#paper_conf_rlc_CramerFST24"  
paper_vec = entity_embeddings[entity_to_id[paper_uri]]

# === Step 2: Predict cited paper vector ===
cite_vec = relation_embeddings[relation_to_id["http://example.org/publication-ontology#cite"]]
predicted_cited_paper_vec = paper_vec + cite_vec

# === Step 3: Predict cited paper's author vector ===
has_author_vec = relation_embeddings[relation_to_id["http://example.org/publication-ontology#hasAuthor"]]
predicted_author_vec = predicted_cited_paper_vec + has_author_vec

# === Step 4: Find closest real author ===
def find_closest_entity(target_vec, label_filter="author"):
    distances = np.linalg.norm(entity_embeddings - target_vec, axis=1)
    sorted_indices = np.argsort(distances)
    for idx in sorted_indices:
        candidate = id_to_entity[idx]
        if label_filter in candidate.lower():
            return candidate, distances[idx]
    return None, None

closest_author, dist = find_closest_entity(predicted_author_vec, label_filter="author")

# === Output Results ===
print("Most likely cited paper vector (TransE logic):", predicted_cited_paper_vec[:5], "...")
print("Predicted author's vector (TransE logic):", predicted_author_vec[:5], "...")
print(f"Closest actual author in KG: {closest_author}")
print(f"Distance: {dist:.4f}")
