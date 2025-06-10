import random
import torch
from pykeen.pipeline import pipeline
from pykeen.triples import TriplesFactory

# === Load train/test triples ===
train_tf = TriplesFactory.from_path("data/kge/train.tsv", separator="\t")
test_tf = TriplesFactory.from_path("data/kge/test.tsv", separator="\t")

# === Train the model (change model/config if needed) ===
result = pipeline(
    training=train_tf,
    testing=test_tf,
    model="TransH",
    model_kwargs={"embedding_dim": 50},
    training_kwargs={"num_epochs": 100},
    negative_sampler_kwargs={"num_negs_per_pos": 5},
    random_seed=42,
    device="cpu"
)

model = result.model
entity_to_id = train_tf.entity_to_id
id_to_entity = {v: k for k, v in entity_to_id.items()}

# === Pick a random test triple ===
test_triple = random.choice(test_tf.triples)
head, relation, tail = test_triple
print(f"\n🔎 Test Triple:\nHead: {head}\nRelation: {relation}\nTail: {tail}")

# Convert to internal IDs
head_id = entity_to_id.get(head)
relation_id = train_tf.relation_to_id.get(relation)
tail_id = entity_to_id.get(tail)

# === Defensive check ===
if None in (head_id, relation_id, tail_id):
    print("\n⚠️ One or more elements are not in the training dictionary. Skipping this triple.")
    exit()

# === Build all possible tail triples (h, r, ?) ===
num_entities = len(entity_to_id)
head_ids = torch.full((num_entities,), head_id)
relation_ids = torch.full((num_entities,), relation_id)
tail_ids = torch.arange(num_entities)

triples = torch.stack([head_ids, relation_ids, tail_ids], dim=1)

# === Score all candidate triples ===
with torch.no_grad():
    scores = model.score_hrt(triples)

# === Find rank of the correct tail ===
sorted_indices = scores.argsort(descending=True)
matching_indices = (sorted_indices == tail_id).nonzero(as_tuple=True)

if matching_indices[0].numel() == 0:
    print(f"\n⚠️ Correct tail entity not found in ranked list.")
else:
    rank = matching_indices[0].item() + 1
    print(f"\n📊 Rank of the correct tail: {rank}")

    # === Show top-10 predicted tails ===
    print("\n🏅 Top-10 predicted tails:")
    top_10_ids = sorted_indices[:10].tolist()
    for i, eid in enumerate(top_10_ids, 1):
        label = id_to_entity.get(eid, f"[Unknown ID {eid}]")
        print(f"{i}. {label}")
