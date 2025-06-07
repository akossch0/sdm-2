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

# Load the TBOX first (assuming it's in the same directory structure)
tbox_file = "data/ontology/publication_ontology.ttl"
if os.path.exists(tbox_file):
    g.parse(tbox_file, format="turtle")
    print(f"Loaded TBOX from '{tbox_file}'")
else:
    print(f"Warning: TBOX file '{tbox_file}' not found. Proceeding with ABOX only.")

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

print("Starting ABOX creation from CSV data...")

#######################
#### CORE ENTITIES ####
#######################

print("Processing papers...")
papers_data = parse_csv_file("data/assignment1/nodes/research_papers.csv")
for paper in papers_data:
    paper_uri = create_uri(paper['id:ID'], "paper_")
    
    # Create Paper instance (explicit rdf:type for core concepts)
    g.add((paper_uri, RDF.type, PUB.Paper))
    
    # Add datatype properties
    if paper.get('title'):
        g.add((paper_uri, PUB.title, Literal(paper['title'], datatype=XSD.string)))
    if paper.get('abstract'):
        g.add((paper_uri, PUB.abstract, Literal(paper['abstract'], datatype=XSD.string)))
    if paper.get('year:int'):
        try:
            year_val = int(float(paper['year:int']))  # Handle both int and float strings
            g.add((paper_uri, PUB.year, Literal(year_val, datatype=XSD.int)))
        except (ValueError, TypeError):
            pass  # Skip invalid year values

print("Processing authors...")
authors_data = parse_csv_file("data/assignment1/nodes/authors.csv")
for author in authors_data:
    author_uri = create_uri(author['id:ID'])
    
    # Create Author instance (explicit rdf:type for core concepts)
    g.add((author_uri, RDF.type, PUB.Author))
    
    # Add name property
    if author.get('name'):
        g.add((author_uri, PUB.name, Literal(author['name'], datatype=XSD.string)))

print("Processing topics...")
topics_data = parse_csv_file("data/assignment1/nodes/topics.csv")
for topic in topics_data:
    topic_uri = create_uri(topic['id:ID'])
    
    # Create Topic instance (explicit rdf:type for core concepts)
    g.add((topic_uri, RDF.type, PUB.Topic))
    
    # Add keyword property
    if topic.get('name'):
        g.add((topic_uri, PUB.hasKeyword, Literal(topic['name'], datatype=XSD.string)))

print("Processing publication places...")
publisher_places_data = parse_csv_file("data/assignment1/nodes/publisher_places.csv")
for place in publisher_places_data:
    place_uri = create_uri(place['id:ID'])
    
    # Determine type based on :LABEL field
    labels = place.get(':LABEL', '')
    
    if 'Journal' in labels:
        # Create Journal instance
        g.add((place_uri, RDF.type, PUB.Journal))
    elif 'ConferenceWorkshopEdition' in labels:
        # Create Edition instance
        g.add((place_uri, RDF.type, PUB.Edition))
        
        # Add edition-specific properties
        if place.get('year:int'):
            try:
                year_val = int(float(place['year:int']))  # Handle both int and float strings
                g.add((place_uri, PUB.year, Literal(year_val, datatype=XSD.int)))
            except (ValueError, TypeError):
                pass  # Skip invalid year values
        if place.get('venue:string'):
            g.add((place_uri, PUB.venue, Literal(place['venue:string'], datatype=XSD.string)))

print("Processing volumes...")
volumes_data = parse_csv_file("data/assignment1/nodes/volumes.csv")
for volume in volumes_data:
    volume_uri = create_uri(volume['id:ID'])
    
    # Create Volume instance
    g.add((volume_uri, RDF.type, PUB.Volume))
    
    # Add year property
    if volume.get('year:int'):
        try:
            year_val = int(float(volume['year:int']))  # Handle both int and float strings
            g.add((volume_uri, PUB.year, Literal(year_val, datatype=XSD.int)))
        except (ValueError, TypeError):
            pass  # Skip invalid year values

print("Processing proceedings...")
proceedings_data = parse_csv_file("data/assignment1/nodes/proceedings.csv")
for proceeding in proceedings_data:
    proceeding_uri = create_uri(proceeding['id:ID'])
    
    # Create PublicationIssue instance
    g.add((proceeding_uri, RDF.type, PUB.PublicationIssue))

#######################
#### RELATIONSHIPS ####
#######################

print("Processing authorship relationships...")
write_data = parse_csv_file("data/assignment1/relationships/write_rel.csv")
corresponding_authors = set()

for write_rel in write_data:
    author_uri = create_uri(write_rel[':START_ID'])
    paper_uri = create_uri(write_rel[':END_ID'], "paper_")
    
    # Add hasAuthor relationship
    g.add((paper_uri, PUB.hasAuthor, author_uri))
    
    # Check if corresponding author
    if write_rel.get('is_corresponding:boolean') == 'True':
        corresponding_authors.add(write_rel[':START_ID'])
        
        # Create corresponding author instance (if not already created as subclass)
        # Note: We don't create explicit CorrAuthor type here as it can be inferred
        # Add hasCorrAuthor relationship
        g.add((paper_uri, PUB.hasCorrAuthor, author_uri))

print("Processing topic relationships...")
is_about_data = parse_csv_file("data/assignment1/relationships/is_about_rel.csv")
for about_rel in is_about_data:
    paper_uri = create_uri(about_rel[':START_ID'], "paper_")
    topic_uri = create_uri(about_rel[':END_ID'])
    
    # Add hasTopic relationship
    g.add((paper_uri, PUB.hasTopic, topic_uri))

print("Processing citation relationships...")
# Citation relationships
cite_data = parse_csv_file("data/assignment1/relationships/cite_rel.csv")
for cite_rel in cite_data:
    citing_paper_uri = create_uri(cite_rel[':START_ID'], "paper_")
    cited_paper_uri = create_uri(cite_rel[':END_ID'], "paper_")
    
    # Add cite relationship
    g.add((citing_paper_uri, PUB.cite, cited_paper_uri))

print("Processing publication relationships...")
published_in_data = parse_csv_file("data/assignment1/relationships/published_in_rel.csv")
for pub_rel in published_in_data:
    paper_uri = create_uri(pub_rel[':START_ID'], "paper_")
    publication_issue_uri = create_uri(pub_rel[':END_ID'])
    
    # Add publishedIn relationship
    g.add((paper_uri, PUB.publishedIn, publication_issue_uri))

print("Processing review relationships...")
reviews_data = parse_csv_file("data/assignment1/relationships/reviews_rel.csv")
reviewers = set()
review_counter = 0

for review_rel in reviews_data:
    reviewer_id = review_rel[':START_ID']
    paper_id = review_rel[':END_ID']
    
    reviewer_uri = create_uri(reviewer_id)
    paper_uri = create_uri(paper_id, "paper_")
    
    # Create Review instance
    review_counter += 1
    review_uri = create_uri(f"review_{review_counter}")
    g.add((review_uri, RDF.type, PUB.Review))
    
    # Add review relationships
    g.add((paper_uri, PUB.hasReview, review_uri))
    g.add((review_uri, PUB.writtenBy, reviewer_uri))
    
    # Track reviewers (they are also Authors, but this relationship shows they're Reviewers)
    reviewers.add(reviewer_id)

# Note: We don't explicitly add rdf:type PUB.Reviewer for authors who are reviewers
# as this can be inferred from the writtenBy relationship

#######################
#### VOLUME-JOURNAL ###
#######################

print("Processing volume-journal relationships...")
for volume in volumes_data:
    volume_id = volume['id:ID']
    volume_uri = create_uri(volume_id)
    
    # Try to extract journal information from volume ID pattern
    # This is an approximation based on common patterns in the data
    if 'journal_' in volume_id or 'journals/' in volume_id:
        # Extract potential journal identifier
        parts = volume_id.replace('journal_', '').replace('journals/', '').split('_')[0]
        journal_uri = create_uri(f"journal_{parts}")
        
        # Check if this journal exists in our publication places
        journal_exists = False
        for place in publisher_places_data:
            if f"journal_{parts}" in place['id:ID'] and 'Journal' in place.get(':LABEL', ''):
                journal_exists = True
                journal_uri = create_uri(place['id:ID'])
                break
        
        if journal_exists:
            g.add((journal_uri, PUB.hasVolume, volume_uri))

#######################
#### FINAL OUTPUT #####
#######################

# Ensure output directory exists
os.makedirs("data/ontology", exist_ok=True)
output_file = "data/ontology/publication_abox.ttl"

# Serialize the complete graph (TBOX + ABOX)
g.serialize(destination=output_file, format="turtle")

print(f"\nABOX created and saved to '{output_file}'")
print(f"Total triples in knowledge graph: {len(g)}")

# Print summary statistics
papers_count = len(papers_data)
authors_count = len(authors_data)
topics_count = len(topics_data)
citations_count = len(cite_data)
reviews_count = len(reviews_data)

print(f"\nSummary Statistics:")
print(f"- Papers: {papers_count}")
print(f"- Authors: {authors_count}")
print(f"- Topics: {topics_count}") 
print(f"- Citations: {citations_count}")
print(f"- Reviews: {reviews_count}")
print(f"- Corresponding Authors: {len(corresponding_authors)}")
print(f"- Reviewers: {len(reviewers)}")

print(f"\nNote: Some rdf:type relationships (e.g., CorrAuthor, Reviewer subclasses)")
print(f"are not explicitly created as they can be inferred from the TBOX definitions")
print(f"and the object property relationships.") 