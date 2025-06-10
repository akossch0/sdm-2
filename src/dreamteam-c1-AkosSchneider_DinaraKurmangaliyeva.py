import os
from rdflib import Graph, URIRef, Literal
import pandas as pd
from pykeen.triples import TriplesFactory

# === Step 1: Load RDF graph ===
abox_path = "data/ontology/dreamteam-b2-AkosSchneider_DinaraKurmangaliyeva.ttl"
print(f"Loading RDF graph from {abox_path}...")
g = Graph()
g.parse(abox_path, format="turtle")

# === Step 2: Filter triples ===
print("Extracting subject-predicate-object triples (excluding literals)...")
triples = [
    (str(s), str(p), str(o))
    for s, p, o in g
    if isinstance(s, URIRef) and isinstance(o, URIRef)
]

# === Step 3: Save all triples as TSV ===
output_dir = "data/kge"
os.makedirs(output_dir, exist_ok=True)

all_triples_path = os.path.join(output_dir, "all_triples.tsv")
pd.DataFrame(triples).to_csv(all_triples_path, sep="\t", index=False, header=False)
print(f"Saved all entity-to-entity triples to {all_triples_path}")

# === Step 4: Create PyKEEN TriplesFactory and split ===
print("Creating stratified train/test splits using PyKEEN...")
tf = TriplesFactory.from_path(all_triples_path, separator="\t")

# Only train/test split
train, test = tf.split(0.8)

# Save the splits
train_path = os.path.join(output_dir, "train.tsv")
test_path = os.path.join(output_dir, "test.tsv")

# Save splits 
pd.DataFrame(train.triples).to_csv(train_path, sep="\t", index=False, header=False)
pd.DataFrame(test.triples).to_csv(test_path, sep="\t", index=False, header=False)

print(f"Saved:")
print(f"- Train triples: {train_path} ({len(train.triples)} triples)")
print(f"- Test triples:  {test_path} ({len(test.triples)} triples)")
