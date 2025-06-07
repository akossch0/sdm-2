import os
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, XSD

g = Graph()

PUB = Namespace("http://example.org/publication-ontology#")
g.bind("pub", PUB)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)

#######################
######## NODES ########
#######################

# --- Core Concepts ---
paper = PUB.Paper
g.add((paper, RDF.type, RDFS.Class))
g.add((paper, RDFS.label, Literal("Paper")))
g.add((paper, RDFS.comment, Literal("A research paper or article.")))

review = PUB.Review
g.add((review, RDF.type, RDFS.Class))
g.add((review, RDFS.label, Literal("Review")))
g.add((review, RDFS.comment, Literal("A review of a submitted paper.")))

topic = PUB.Topic
g.add((topic, RDF.type, RDFS.Class))
g.add((topic, RDFS.label, Literal("Topic")))
g.add((topic, RDFS.comment, Literal("A keyword or topic describing the subject of a paper.")))

# --- Publication Places ---
publication_place = PUB.PublicationPlace
g.add((publication_place, RDF.type, RDFS.Class))
g.add((publication_place, RDFS.label, Literal("Publication Place")))
g.add((publication_place, RDFS.comment, Literal("A generic place for publishing papers, e.g., a conference or journal.")))

joint_meeting = PUB.JointMeeting
g.add((joint_meeting, RDF.type, RDFS.Class))
g.add((joint_meeting, RDFS.subClassOf, publication_place))
g.add((joint_meeting, RDFS.label, Literal("Joint Meeting")))

conference = PUB.Conference
g.add((conference, RDF.type, RDFS.Class))
g.add((conference, RDFS.subClassOf, joint_meeting))
g.add((conference, RDFS.label, Literal("Conference")))

workshop = PUB.Workshop
g.add((workshop, RDF.type, RDFS.Class))
g.add((workshop, RDFS.subClassOf, joint_meeting))
g.add((workshop, RDFS.label, Literal("Workshop")))

journal = PUB.Journal
g.add((journal, RDF.type, RDFS.Class))
g.add((journal, RDFS.subClassOf, publication_place))
g.add((journal, RDFS.label, Literal("Journal")))

publication_issue = PUB.PublicationIssue
g.add((publication_issue, RDF.type, RDFS.Class))
g.add((publication_issue, RDFS.label, Literal("Publication Issue")))
g.add((publication_issue, RDFS.comment, Literal("A specific instance of a publication, like an edition or volume.")))

volume = PUB.Volume
g.add((volume, RDF.type, RDFS.Class))
g.add((volume, RDFS.subClassOf, publication_issue))
g.add((volume, RDFS.label, Literal("Volume")))

edition = PUB.Edition
g.add((edition, RDF.type, RDFS.Class))
g.add((edition, RDFS.subClassOf, publication_issue))
g.add((edition, RDFS.label, Literal("Edition")))

# --- Authors and Reviewers ---
author = PUB.Author
g.add((author, RDF.type, RDFS.Class))
g.add((author, RDFS.label, Literal("Author")))

corr_author = PUB.CorrAuthor
g.add((corr_author, RDF.type, RDFS.Class))
g.add((corr_author, RDFS.subClassOf, author))
g.add((corr_author, RDFS.label, Literal("Corresponding Author")))

reviewer = PUB.Reviewer
g.add((reviewer, RDF.type, RDFS.Class))
g.add((reviewer, RDFS.subClassOf, author))
g.add((reviewer, RDFS.label, Literal("Reviewer")))
g.add((reviewer, RDFS.comment, Literal("A person who reviews a paper.")))


#######################
######## EDGES ########
#######################

# --- Object Properties ---
has_author = PUB.hasAuthor
g.add((has_author, RDF.type, RDF.Property))
g.add((has_author, RDFS.domain, paper))
g.add((has_author, RDFS.range, author))
g.add((has_author, RDFS.label, Literal("has author")))

has_corr_author = PUB.hasCorrAuthor
g.add((has_corr_author, RDF.type, RDF.Property))
g.add((has_corr_author, RDFS.domain, paper))
g.add((has_corr_author, RDFS.range, corr_author))
g.add((has_corr_author, RDFS.label, Literal("has corresponding author")))

cite = PUB.cite
g.add((cite, RDF.type, RDF.Property))
g.add((cite, RDFS.domain, paper))
g.add((cite, RDFS.range, paper))
g.add((cite, RDFS.label, Literal("cite")))

published_in = PUB.publishedIn
g.add((published_in, RDF.type, RDF.Property))
g.add((published_in, RDFS.domain, paper))
g.add((published_in, RDFS.range, publication_issue))
g.add((published_in, RDFS.label, Literal("published in")))

has_volume = PUB.hasVolume
g.add((has_volume, RDF.type, RDF.Property))
g.add((has_volume, RDFS.domain, journal))
g.add((has_volume, RDFS.range, volume))
g.add((has_volume, RDFS.label, Literal("has volume")))

has_edition = PUB.hasEdition
g.add((has_edition, RDF.type, RDF.Property))
g.add((has_edition, RDFS.domain, conference))
g.add((has_edition, RDFS.range, edition))
g.add((has_edition, RDFS.label, Literal("has edition")))

has_topic = PUB.hasTopic
g.add((has_topic, RDF.type, RDF.Property))
g.add((has_topic, RDFS.domain, paper))
g.add((has_topic, RDFS.range, topic))
g.add((has_topic, RDFS.label, Literal("has topic")))

has_review = PUB.hasReview
g.add((has_review, RDF.type, RDF.Property))
g.add((has_review, RDFS.domain, paper))
g.add((has_review, RDFS.range, review))
g.add((has_review, RDFS.label, Literal("has review")))

written_by = PUB.writtenBy
g.add((written_by, RDF.type, RDF.Property))
g.add((written_by, RDFS.domain, review))
g.add((written_by, RDFS.range, reviewer))
g.add((written_by, RDFS.label, Literal("written by")))


###########################
######## DATATYPES ########
###########################

# --- Datatype Properties (based on xsd types shown in graph) ---
# Adding properties that connect to xsd:string, xsd:int, and xsd:date as shown in the graph
has_keyword = PUB.hasKeyword
g.add((has_keyword, RDF.type, RDF.Property))
g.add((has_keyword, RDFS.domain, topic))
g.add((has_keyword, RDFS.range, XSD.string))
g.add((has_keyword, RDFS.label, Literal("has keyword")))

start_date = PUB.startDate
g.add((start_date, RDF.type, RDF.Property))
g.add((start_date, RDFS.domain, edition))
g.add((start_date, RDFS.range, XSD.date))
g.add((start_date, RDFS.label, Literal("start date")))

end_date = PUB.endDate
g.add((end_date, RDF.type, RDF.Property))
g.add((end_date, RDFS.domain, edition))
g.add((end_date, RDFS.range, XSD.date))
g.add((end_date, RDFS.label, Literal("end date")))

year = PUB.year
g.add((year, RDF.type, RDF.Property))
g.add((year, RDFS.domain, publication_issue))
g.add((year, RDFS.range, XSD.int))
g.add((year, RDFS.label, Literal("year")))

venue = PUB.venue
g.add((venue, RDF.type, RDF.Property))
g.add((venue, RDFS.domain, edition))
g.add((venue, RDFS.range, XSD.string))
g.add((venue, RDFS.label, Literal("venue")))

# ensure data folder exists
os.makedirs("data", exist_ok=True)
output_file = "data/publication_ontology.ttl"
g.serialize(destination=output_file, format="turtle")

print(f"Ontology TBOX created and saved to '{output_file}'")
