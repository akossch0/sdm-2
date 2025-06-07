# CSV Data to TBOX Ontology Mapping

This document provides a comprehensive mapping between the CSV data from Assignment 1 and the TBOX ontology defined in `b1_tbox_definition.py`.

## Executive Summary

The CSV data provides a rich source for populating the entire TBOX ontology, with strong coverage for all core concepts including papers, authors, topics, publication venues, and **reviews/reviewers**. The discovery of review data in `reviews_rel.csv` means the ontology can be fully populated from the available CSV files.

## Node Mappings

### ✅ **Core Concepts - Well Supported**

#### Papers (`PUB.Paper`)
- **CSV Source**: `nodes/research_papers.csv` 
- **Fields Available**:
  - `id:ID` → Individual paper URIs
  - `title` → Paper titles
  - `abstract` → Paper abstracts  
  - `year:int` → Publication year
  - `:LABEL` → All marked as "ResearchPaper"
- **Coverage**: Excellent (549 papers)
- **TBOX Mapping**: Direct mapping to `PUB.Paper` instances

#### Authors (`PUB.Author`)
- **CSV Source**: `nodes/authors.csv`
- **Fields Available**:
  - `id:ID` → Individual author URIs 
  - `name` → Author names
  - `:LABEL` → All marked as "Author"
- **Coverage**: Excellent (1,838 authors)
- **TBOX Mapping**: Direct mapping to `PUB.Author` instances
- **Additional Info**: Corresponding authors identified in `relationships/write_rel.csv` with `is_corresponding:boolean` field

#### Topics (`PUB.Topic`)
- **CSV Source**: `nodes/topics.csv`
- **Fields Available**:
  - `id:ID` → Topic identifiers (topic_0, topic_1, etc.)
  - `name` → Topic names (Machine Learning, AI, etc.)
  - `LABEL` → All marked as "Topics"
- **Coverage**: Good (30 topics covering major CS domains)
- **TBOX Mapping**: Direct mapping to `PUB.Topic` instances

### ✅ **Publication Places - Good Support**

#### Publication Places Hierarchy
- **CSV Source**: `nodes/publisher_places.csv`
- **Fields Available**:
  - `id:ID` → Publisher place identifiers
  - `name` → Venue names
  - `year:int` → Year (for conference editions, empty for journals)
  - `venue:string` → Venue identifier (for conference editions)
  - `:LABEL` → Multiple labels indicating type

**Mapping to TBOX Classes**:

1. **Journals** (`PUB.Journal`)
   - **CSV Pattern**: `:LABEL` contains "PublisherPlace;Journal"
   - **Examples**: "journal_coap", "journal_tnn", etc.
   - **Coverage**: Excellent (180+ journals)

2. **Conference/Workshop Editions** (`PUB.Edition`)
   - **CSV Pattern**: `:LABEL` contains "PublisherPlace;ConferenceWorkshopEdition"  
   - **Examples**: "edition_rlc_2024", "edition_www_2007"
   - **Coverage**: Good (4+ conference series)
   - **Additional Data**: Year and venue information available

#### Volumes (`PUB.Volume`)
- **CSV Source**: `nodes/volumes.csv`
- **Fields Available**:
  - `id:ID` → Volume identifiers
  - `year:int` → Publication year
  - `:LABEL` → All marked as "Volume"
- **Coverage**: Excellent (376 volumes)
- **TBOX Mapping**: Direct mapping to `PUB.Volume` instances

#### Proceedings (`PUB.PublicationIssue`)
- **CSV Source**: `nodes/proceedings.csv`
- **Fields Available**:
  - `id:ID` → Proceeding identifiers
  - `name` → Proceeding names
  - `:LABEL` → All marked as "Proceeding"
- **Coverage**: Limited (22 proceedings, mainly for conferences)
- **Note**: Could be enhanced with more conference proceedings

### ✅ **Review Support Available**

#### Reviews (`PUB.Review`) & Reviewers (`PUB.Reviewer`)
- **CSV Source**: `relationships/reviews_rel.csv` 
- **Data Available**: 1,546 review relationships
- **Structure**: Author ID → Paper ID with "REVIEWS" relationship type
- **Sample Data**:
  ```csv
  ":START_ID",":END_ID",":TYPE"
  "author_danah_boyd","pub_conf/valuetools/Coppa14","REVIEWS"
  "author_Yanrong_Zhuang","pub_conf/valuetools/Coppa14","REVIEWS"
  ```
- **TBOX Mapping Strategy**:
  - Create `PUB.Review` instances for each relationship (using review IDs)
  - Authors who appear in this CSV become `PUB.Reviewer` instances (subclass of Author)
  - Generate `PUB.hasReview` triples (paper → review)
  - Generate `PUB.writtenBy` triples (review → reviewer)
- **Coverage**: Excellent (1,546 review relationships across diverse papers)
- **Note**: This represents peer review relationships in academic publishing

### ⚠️ **Partial Support**

#### Corresponding Authors (`PUB.CorrAuthor`)
- **CSV Source**: Identified in `relationships/write_rel.csv` via `is_corresponding:boolean` field
- **Coverage**: Available but requires relationship processing
- **TBOX Mapping**: Can be derived from regular authors who have `is_corresponding=True`

## Relationship Mappings

### ✅ **Well Supported Relationships**

#### Paper-Author Relationships
1. **`PUB.hasAuthor`** (Paper → Author)
   - **CSV Source**: `relationships/write_rel.csv`
   - **Field**: `:START_ID` (author) → `:END_ID` (paper), `:TYPE` = "WRITE"
   - **Coverage**: Excellent (1,941 authorship relationships)

2. **`PUB.hasCorrAuthor`** (Paper → Corresponding Author)
   - **CSV Source**: `relationships/write_rel.csv` where `is_corresponding:boolean` = "True"
   - **Coverage**: Good (subset of authorship relationships)

#### Paper-Topic Relationships
3. **`PUB.hasTopic`** (Paper → Topic)
   - **CSV Source**: `relationships/is_about_rel.csv`
   - **Field**: `:START_ID` (paper) → `:END_ID` (topic), `:TYPE` = "IS_ABOUT"
   - **Coverage**: Excellent (1,508 topic relationships)

#### Citation Relationships
4. **`PUB.cite`** (Paper → Paper)
   - **CSV Source**: `relationships/cite_rel.csv`
   - **Field**: `:START_ID` (citing paper) → `:END_ID` (cited paper), `:TYPE` = "CITE"
   - **Coverage**: Excellent (21,979+ citations)

#### Publication Relationships
5. **`PUB.publishedIn`** (Paper → Publication Issue)
   - **CSV Source**: `relationships/published_in_rel.csv`
   - **Field**: `:START_ID` (paper) → `:END_ID` (publication issue), `:TYPE` = "PUBLISHED_IN"
   - **Coverage**: Excellent (549 relationships, matches paper count)

#### Volume/Edition Relationships
6. **`PUB.hasVolume`** (Journal → Volume)
   - **CSV Source**: Can be inferred from volume IDs and journal relationships
   - **Coverage**: Good (volume IDs contain journal information)

7. **`PUB.hasEdition`** (Conference → Edition)
   - **CSV Source**: Can be inferred from edition data in `publisher_places.csv`
   - **Coverage**: Good (edition data available for conferences)

### ✅ **Review Relationships - Now Available**

#### Review-Related Relationships  
8. **`PUB.hasReview`** (Paper → Review)
   - **CSV Source**: `relationships/reviews_rel.csv`
   - **Field**: `:START_ID` (reviewer) → `:END_ID` (paper), `:TYPE` = "REVIEWS"
   - **Coverage**: Excellent (1,546 review relationships)
   - **Implementation**: Generate review instances and link papers to them

9. **`PUB.writtenBy`** (Review → Reviewer)
   - **CSV Source**: `relationships/reviews_rel.csv`
   - **Coverage**: Excellent (derived from review relationships)
   - **Implementation**: Link each review instance to its corresponding reviewer

## Datatype Property Mappings

### ✅ **Well Supported**

#### From Papers
- **`PUB.title`** → `research_papers.csv` `title` field
- **`PUB.abstract`** → `research_papers.csv` `abstract` field  
- **`PUB.year`** → `research_papers.csv` `year:int` field

#### From Topics  
- **`PUB.hasKeyword`** → `topics.csv` `name` field (XSD.string)

#### From Volumes/Editions
- **`PUB.year`** → `volumes.csv` `year:int` field (XSD.int)
- **`PUB.venue`** → `publisher_places.csv` `venue:string` field (XSD.string)

#### From Authors
- **`PUB.name`** → `authors.csv` `name` field (XSD.string)

### ⚠️ **Partially Supported**

#### Edition Date Information
- **`PUB.startDate`** and **`PUB.endDate`** → Not directly available
- **Available**: Year information only from `publisher_places.csv` 
- **Recommendation**: Could generate date ranges or use year-based dates

## Data Quality Assessment

### Strengths
1. **Comprehensive Paper Coverage**: 549 papers with rich metadata
2. **Extensive Citation Network**: 21,979+ citation relationships
3. **Rich Author Information**: 1,838 unique authors
4. **Good Topic Coverage**: 30 topics spanning major CS domains
5. **Strong Publication Venue Data**: 180+ journals and multiple conference series
6. **Complete Authorship Information**: Including corresponding author designation
7. **Complete Review System**: 1,546 review relationships enabling full peer review modeling

### Limitations
1. **Limited Conference Proceedings**: Only 22 proceedings vs 376 journal volumes
2. **Missing Temporal Details**: No start/end dates for conference editions
3. **No Publisher Information**: Missing publisher details for venues

## Implementation Recommendations

### High Priority (Immediate Implementation)
1. **Core Entities**: Implement Papers, Authors, Topics, Journals, Volumes
2. **Main Relationships**: hasAuthor, hasTopic, cite, publishedIn
3. **Basic Properties**: titles, abstracts, years, names, keywords
4. **Review System**: Implement Reviews, Reviewers, hasReview, writtenBy relationships

### Medium Priority (Enhanced Features)
1. **Corresponding Authors**: Process `is_corresponding` flags to create CorrAuthor instances
2. **Conference Editions**: Implement conference edition hierarchy
3. **Venue Relationships**: Link journals to volumes, conferences to editions

### Low Priority (Future Enhancement)
1. **Enhanced Temporal Data**: Add specific start/end dates for events
2. **Publisher Information**: Enhance with publisher metadata

### Inference Opportunities
As noted in the assignment, some `rdf:type` triples can be inferred:
- **Author Subclassing**: Regular authors vs corresponding authors
- **Publication Subclassing**: Journals vs conference editions
- **Temporal Relationships**: Publication date relationships

## Conclusion

The CSV data provides excellent coverage for the core publication ontology concepts, enabling a rich semantic representation of the academic publication domain. The main gap is in the review system, which would require external data sources or artificial generation. The data quality is high and suitable for creating a comprehensive ABOX that demonstrates the full capabilities of the TBOX ontology. 