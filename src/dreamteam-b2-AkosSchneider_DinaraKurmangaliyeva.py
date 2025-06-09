import os
import csv
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, XSD
from collections import defaultdict

# Initialize graph and namespaces
g = Graph()
PUB = Namespace("http://example.org/publication-ontology#")
g.bind("pub", PUB)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)

# Load the TBOX first
tbox_file = "data/ontology/dreamteam-b1-AkosSchneider_DinaraKurmangaliyeva.ttl"
if os.path.exists(tbox_file):
    g.parse(tbox_file, format="turtle")
    print(f"Loaded TBOX from '{tbox_file}'")
else:
    print(f"Warning: TBOX file '{tbox_file}' not found. Proceeding with ABOX only.")

# Initialize tracking dictionaries
relationship_counts = defaultdict(int)
inferred_type_entities = defaultdict(set)  # Unique entities with types from domain/range restrictions
inferred_inclusion_entities = defaultdict(set)  # Unique entities with types from subclass relationships
explicit_node_entities = defaultdict(set)  # Unique entities with explicitly created types
processed_entities = set()  # Track entities that got types from relationships

# Helper function to create URIs
def create_uri(id_str, prefix=""):
    """Create URI from ID string, handling special characters"""
    clean_id = id_str.replace("/", "_").replace(" ", "_").replace(":", "_")
    return PUB[f"{prefix}{clean_id}"]

def parse_csv_file(file_path):
    """Parse CSV file and return list of dictionaries"""
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print(f"Warning: CSV file '{file_path}' not found. Skipping.")
        return []
    return data

def track_inferred_type(entity_uri, rdf_type, reason="domain_range"):
    """Track inferred types from relationships - stores unique entities per type"""
    if reason == "domain_range":
        inferred_type_entities[rdf_type].add(entity_uri)
    elif reason == "inclusion":
        inferred_inclusion_entities[rdf_type].add(entity_uri)
    processed_entities.add(entity_uri)

print("Starting ABOX creation with relationship-first approach...")

#######################
#### RELATIONSHIPS ####
#######################

print("Processing authorship relationships...")
write_data = parse_csv_file("data/assignment1/relationships/write_rel.csv")
corresponding_authors = set()

for write_rel in write_data:
    author_uri = create_uri(write_rel[':START_ID'])
    paper_uri = create_uri(write_rel[':END_ID'], "paper_")
    
    # Add hasAuthor relationship - this will infer Paper and Author types
    g.add((paper_uri, PUB.hasAuthor, author_uri))
    relationship_counts['hasAuthor'] += 1
    track_inferred_type(paper_uri, 'Paper')
    track_inferred_type(author_uri, 'Author')
    
    # Check if corresponding author
    if write_rel.get('is_corresponding:boolean') == 'True':
        corresponding_authors.add(write_rel[':START_ID'])
        
        # Add hasCorrAuthor relationship - this will infer CorrAuthor type
        g.add((paper_uri, PUB.hasCorrAuthor, author_uri))
        relationship_counts['hasCorrAuthor'] += 1
        track_inferred_type(author_uri, 'CorrAuthor')
        # CorrAuthor is subclass of Author - track inclusion dependency
        track_inferred_type(author_uri, 'Author', "inclusion")

print("Processing topic relationships...")
is_about_data = parse_csv_file("data/assignment1/relationships/is_about_rel.csv")
for about_rel in is_about_data:
    paper_uri = create_uri(about_rel[':START_ID'], "paper_")
    topic_uri = create_uri(about_rel[':END_ID'])
    
    # Add hasTopic relationship - this will infer Paper and Topic types
    g.add((paper_uri, PUB.hasTopic, topic_uri))
    relationship_counts['hasTopic'] += 1
    track_inferred_type(paper_uri, 'Paper')
    track_inferred_type(topic_uri, 'Topic')

print("Processing citation relationships...")
cite_data = parse_csv_file("data/assignment1/relationships/cite_rel.csv")
for cite_rel in cite_data:
    citing_paper_uri = create_uri(cite_rel[':START_ID'], "paper_")
    cited_paper_uri = create_uri(cite_rel[':END_ID'], "paper_")
    
    # Add cite relationship - this will infer Paper types for both
    g.add((citing_paper_uri, PUB.cite, cited_paper_uri))
    relationship_counts['cite'] += 1
    track_inferred_type(citing_paper_uri, 'Paper')
    track_inferred_type(cited_paper_uri, 'Paper')

print("Processing publication relationships...")
published_in_data = parse_csv_file("data/assignment1/relationships/published_in_rel.csv")
for pub_rel in published_in_data:
    paper_uri = create_uri(pub_rel[':START_ID'], "paper_")
    publication_issue_uri = create_uri(pub_rel[':END_ID'])
    
    # Add publishedIn relationship - this will infer Paper and PublicationIssue types
    g.add((paper_uri, PUB.publishedIn, publication_issue_uri))
    relationship_counts['publishedIn'] += 1
    track_inferred_type(paper_uri, 'Paper')
    track_inferred_type(publication_issue_uri, 'PublicationIssue')

print("Processing review relationships...")
reviews_data = parse_csv_file("data/assignment1/relationships/reviews_rel.csv")
reviewers = set()
review_counter = 0

for review_rel in reviews_data:
    reviewer_id = review_rel[':START_ID']
    paper_id = review_rel[':END_ID']
    
    reviewer_uri = create_uri(reviewer_id)
    paper_uri = create_uri(paper_id, "paper_")
    
    # Create Review instance and relationships
    review_counter += 1
    review_uri = create_uri(f"review_{review_counter}")
    
    # Add review relationships - these will infer Paper, Review, and Reviewer types
    g.add((paper_uri, PUB.hasReview, review_uri))
    g.add((review_uri, PUB.writtenBy, reviewer_uri))
    relationship_counts['hasReview'] += 1
    relationship_counts['writtenBy'] += 1
    
    track_inferred_type(paper_uri, 'Paper')
    track_inferred_type(review_uri, 'Review')
    track_inferred_type(reviewer_uri, 'Reviewer')
    # Reviewer is subclass of Author - track inclusion dependency
    track_inferred_type(reviewer_uri, 'Author', "inclusion")
    
    reviewers.add(reviewer_id)

print("Processing journal-volume relationships...")
contain_data = parse_csv_file("data/assignment1/relationships/contain_rel.csv")
for contain_rel in contain_data:
    journal_uri = create_uri(contain_rel[':START_ID'])
    volume_uri = create_uri(contain_rel[':END_ID'])
    
    # Add hasVolume relationship - this will infer Journal and Volume types
    g.add((journal_uri, PUB.hasVolume, volume_uri))
    relationship_counts['hasVolume'] += 1
    track_inferred_type(journal_uri, 'Journal')
    track_inferred_type(volume_uri, 'Volume')
    # Volume is subclass of PublicationIssue - track inclusion dependency
    track_inferred_type(volume_uri, 'PublicationIssue', "inclusion")

print("Processing edition-proceeding relationships...")
print("We do not have proceedings in our TBOX, so we do not need to process this relationship")

print("Processing conference/workshop-edition relationships...")
# Extract conference/workshop to edition relationships from publisher_places data
publisher_places_data = parse_csv_file("data/assignment1/nodes/publisher_places.csv")

for place in publisher_places_data:
    labels = place.get(':LABEL', '')
    
    if 'ConferenceWorkshopEdition' in labels:
        # Extract conference/workshop name from id:ID
        # edition_mobiquitous_2015 -> mobiquitous
        edition_uri = create_uri(place['id:ID'])
        conference_workshop_name = place['id:ID'].split('_')[1]
        conference_workshop_uri = create_uri(conference_workshop_name)
        # Add hasEdition relationship - this will infer Conference/Workshop and Edition types
        g.add((conference_workshop_uri, PUB.hasEdition, edition_uri))
        relationship_counts['hasEdition'] += 1
        # Note: hasEdition has domain JointMeeting
        track_inferred_type(conference_workshop_uri, 'JointMeeting')
        track_inferred_type(edition_uri, 'Edition')
        # Edition is subclass of PublicationIssue - track inclusion dependency
        track_inferred_type(edition_uri, 'PublicationIssue', "inclusion")

#######################
#### DATATYPE PROPS ###
#######################

print("Processing datatype properties for entities...")

# Add datatype properties for papers
papers_data = parse_csv_file("data/assignment1/nodes/research_papers.csv")
for paper in papers_data:
    paper_uri = create_uri(paper['id:ID'], "paper_")
    
    # Add datatype properties - these will infer Paper type through domain restrictions
    if paper.get('title'):
        g.add((paper_uri, PUB.title, Literal(paper['title'], datatype=XSD.string)))
        relationship_counts['title'] += 1
        if paper_uri not in processed_entities:
            track_inferred_type(paper_uri, 'Paper')
    
    if paper.get('abstract'):
        g.add((paper_uri, PUB.abstract, Literal(paper['abstract'], datatype=XSD.string)))
        relationship_counts['abstract'] += 1
        if paper_uri not in processed_entities:
            track_inferred_type(paper_uri, 'Paper')
    
    if paper.get('year:int'):
        try:
            year_val = int(float(paper['year:int']))
            g.add((paper_uri, PUB.year, Literal(year_val, datatype=XSD.int)))
            relationship_counts['year'] += 1
            # year has domain PublicationIssue, but papers should be treated specially
        except (ValueError, TypeError):
            pass

# Add name properties for authors
authors_data = parse_csv_file("data/assignment1/nodes/authors.csv")
for author in authors_data:
    author_uri = create_uri(author['id:ID'])
    
    if author.get('name'):
        g.add((author_uri, PUB.name, Literal(author['name'], datatype=XSD.string)))
        relationship_counts['name'] += 1
        if author_uri not in processed_entities:
            track_inferred_type(author_uri, 'Author')

# Add keyword properties for topics
topics_data = parse_csv_file("data/assignment1/nodes/topics.csv")
for topic in topics_data:
    topic_uri = create_uri(topic['id:ID'])
    
    if topic.get('name'):
        g.add((topic_uri, PUB.hasKeyword, Literal(topic['name'], datatype=XSD.string)))
        relationship_counts['hasKeyword'] += 1
        if topic_uri not in processed_entities:
            track_inferred_type(topic_uri, 'Topic')

# Add properties for editions (venue, year)
for place in publisher_places_data:
    if 'ConferenceWorkshopEdition' in place.get(':LABEL', ''):
        place_uri = create_uri(place['id:ID'])
        
        if place.get('year:int'):
            try:
                year_val = int(float(place['year:int']))
                g.add((place_uri, PUB.year, Literal(year_val, datatype=XSD.int)))
                relationship_counts['year'] += 1
            except (ValueError, TypeError):
                pass
        
        if place.get('venue:string'):
            g.add((place_uri, PUB.venue, Literal(place['venue:string'], datatype=XSD.string)))
            relationship_counts['venue'] += 1
            if place_uri not in processed_entities:
                track_inferred_type(place_uri, 'Edition')

# Add year properties for volumes
volumes_data = parse_csv_file("data/assignment1/nodes/volumes.csv")
for volume in volumes_data:
    volume_uri = create_uri(volume['id:ID'])
    
    if volume.get('year:int'):
        try:
            year_val = int(float(volume['year:int']))
            g.add((volume_uri, PUB.year, Literal(year_val, datatype=XSD.int)))
            relationship_counts['year'] += 1
            if volume_uri not in processed_entities:
                track_inferred_type(volume_uri, 'PublicationIssue')  # year has domain PublicationIssue
        except (ValueError, TypeError):
            pass

#######################
#### EXPLICIT NODES ###
#######################

print("Creating explicit nodes for entities not covered by relationships...")

# Only creating explicit type assertions for entities that weren't processed through relationships
# This section is minimal since most types of nodes are inferred from relationships

# Check for journals that weren't processed through contain relationships
for place in publisher_places_data:
    if 'Journal' in place.get(':LABEL', ''):
        journal_uri = create_uri(place['id:ID'])
        if journal_uri not in processed_entities:
            g.add((journal_uri, RDF.type, PUB.Journal))
            explicit_node_entities['Journal'].add(journal_uri)

#######################
#### FINAL OUTPUT #####
#######################

# Ensure output directory exists
os.makedirs("data/ontology", exist_ok=True)
output_file = "data/ontology/dreamteam-b2-AkosSchneider_DinaraKurmangaliyeva.ttl"

# Serialize the complete graph (TBOX + ABOX)
g.serialize(destination=output_file, format="turtle")

print(f"\nABOX created and saved to '{output_file}'")
print(f"Total triples in knowledge graph: {len(g)}")

#######################
##### STATISTICS ######
#######################

print(f"\n=== COMPREHENSIVE STATISTICS ===")

print(f"\n--- RELATIONSHIPS ADDED ---")
total_relationships = 0
for rel_type, count in sorted(relationship_counts.items()):
    print(f"- {rel_type}: {count}")
    total_relationships += count
print(f"Total relationships: {total_relationships}")

print(f"\n--- INFERRED TYPES (Domain/Range) - Unique Entities ---")
total_inferred_domain_range = 0
for type_name, entity_set in sorted(inferred_type_entities.items()):
    count = len(entity_set)
    print(f"- {type_name}: {count}")
    total_inferred_domain_range += count
print(f"Total unique entities inferred from domain/range: {total_inferred_domain_range}")

print(f"\n--- INFERRED TYPES (Inclusion/Subclass) - Unique Entities ---")
total_inferred_inclusion = 0
for type_name, entity_set in sorted(inferred_inclusion_entities.items()):
    count = len(entity_set)
    print(f"- {type_name}: {count}")
    total_inferred_inclusion += count
print(f"Total unique entities inferred from inclusion: {total_inferred_inclusion}")

print(f"\n--- EXPLICIT NODES CREATED - Unique Entities ---")
total_explicit = 0
for type_name, entity_set in sorted(explicit_node_entities.items()):
    count = len(entity_set)
    print(f"- {type_name}: {count}")
    total_explicit += count
print(f"Total unique explicit nodes: {total_explicit}")

#######################
### GRAPH ANALYSIS ####
#######################

print(f"\n=== GRAPH ANALYSIS ===")

# Analyze TBOX vs ABOX triples
tbox_predicates = {
    RDFS.Class, RDFS.subClassOf, RDFS.domain, RDFS.range, 
    RDFS.label, RDFS.comment, RDF.Property
}

# Get all classes defined in the ontology
classes = set()
for subj, pred, obj in g:
    if pred == RDF.type and obj == RDFS.Class:
        classes.add(subj)

# Separate TBOX and ABOX triples
tbox_triples = []
abox_triples = []
abox_type_triples = []
abox_object_property_triples = []
abox_datatype_property_triples = []

for subj, pred, obj in g:
    # Check if this is a TBOX triple
    is_tbox = (
        pred in tbox_predicates or 
        subj in classes or 
        (pred == RDF.type and obj == RDFS.Class) or
        str(pred).startswith('http://www.w3.org/2000/01/rdf-schema#') or
        str(pred).startswith('http://www.w3.org/1999/02/22-rdf-syntax-ns#Property')
    )
    
    if is_tbox:
        tbox_triples.append((subj, pred, obj))
    else:
        abox_triples.append((subj, pred, obj))
        
        # Further categorize ABOX triples
        if pred == RDF.type:
            abox_type_triples.append((subj, pred, obj))
        elif str(pred).startswith(str(PUB)) and isinstance(obj, URIRef):
            # Object property (pointing to another resource)
            abox_object_property_triples.append((subj, pred, obj))
        elif str(pred).startswith(str(PUB)) and isinstance(obj, Literal):
            # Datatype property (pointing to a literal)
            abox_datatype_property_triples.append((subj, pred, obj))

print(f"\n--- TRIPLE DISTRIBUTION ---")
print(f"Total triples in graph: {len(g)}")
print(f"- TBOX triples (schema/ontology): {len(tbox_triples)}")
print(f"- ABOX triples (instance data): {len(abox_triples)}")

print(f"\n--- ABOX BREAKDOWN ---")
print(f"- rdf:type assertions: {len(abox_type_triples)}")
print(f"- Object property assertions: {len(abox_object_property_triples)}")
print(f"- Datatype property assertions: {len(abox_datatype_property_triples)}")

# Analyze by predicate frequency in ABOX
print(f"\n--- ABOX PREDICATES ---")
predicate_counts = defaultdict(int)
for subj, pred, obj in abox_triples:
    predicate_counts[pred] += 1

sorted_predicates = sorted(predicate_counts.items(), key=lambda x: x[1], reverse=True)
for pred, count in sorted_predicates:
    # Extract local name from URI
    local_name = str(pred).split('#')[-1] if '#' in str(pred) else str(pred).split('/')[-1]
    print(f"- {local_name}: {count}")

# Analyze type distribution in ABOX
print(f"\n--- ABOX TYPE DISTRIBUTION ---")
type_counts = defaultdict(int)
for subj, pred, obj in abox_type_triples:
    type_counts[obj] += 1

sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
for rdf_type, count in sorted_types:
    # Extract local name from URI
    local_name = str(rdf_type).split('#')[-1] if '#' in str(rdf_type) else str(rdf_type).split('/')[-1]
    print(f"- {local_name}: {count}")

# Analyze unique entities by namespace
print(f"\n--- ENTITY NAMESPACES ---")
namespace_counts = defaultdict(set)
for subj, pred, obj in abox_triples:
    if isinstance(subj, URIRef):
        if str(subj).startswith(str(PUB)):
            namespace_counts['PUB entities'].add(subj)
    if isinstance(obj, URIRef) and str(obj).startswith(str(PUB)):
        namespace_counts['PUB entities'].add(obj)

for namespace, entities in namespace_counts.items():
    print(f"- {namespace}: {len(entities)} unique entities")

print(f"\n--- GRAPH DENSITY METRICS ---")
total_entities = len(namespace_counts.get('PUB entities', set()))
if total_entities > 0:
    avg_relationships_per_entity = len(abox_object_property_triples) / total_entities
    avg_properties_per_entity = len(abox_datatype_property_triples) / total_entities
    print(f"- Average object relationships per entity: {avg_relationships_per_entity:.2f}")
    print(f"- Average datatype properties per entity: {avg_properties_per_entity:.2f}")
    print(f"- Total unique entities: {total_entities}")
