# Services Directory

This directory contains the core business logic and data access layer for the 20 Newsgroups Search API.

## Overview

The services layer provides abstraction between the API routes and external systems (Elasticsearch, scikit-learn). It handles data processing, search operations, and document management.

## Files Structure

```
app/services/
├── __init__.py                 # Makes this a Python package
├── elasticsearch_service.py    # Elasticsearch operations and search logic
└── data_loader.py             # Data loading from scikit-learn 20newsgroups
```

---

# ElasticsearchService (`elasticsearch_service.py`)

## Purpose
Handles all Elasticsearch operations including document CRUD, search, and index management.

## Class Structure

### Constructor
```python
def __init__(self, es: Elasticsearch, index_name: str):
```

**Parameters:**
- `es`: Elasticsearch client instance
- `index_name`: Name of the Elasticsearch index to operate on

**Example:**
```python
from elasticsearch import Elasticsearch
from app.services.elasticsearch_service import ElasticsearchService

es_client = Elasticsearch("http://localhost:9200")
service = ElasticsearchService(es_client, "newsgroups")
```

---

## Methods Documentation

### `_create_document_mapping()`
```python
def _create_document_mapping(self) -> Dict[str, Any]:
```

**Purpose:** Creates the Elasticsearch mapping schema for document storage.

**Returns:** Dictionary containing field mappings

**Key Mappings:**
- `title`: Text field with keyword subfield for exact matches
- `body`: Full-text searchable field
- `category`: Keyword field for exact category filtering
- `tags`: Array of keywords for tag filtering
- `author`: Keyword field for author searches
- `created_at/updated_at`: Date fields for temporal queries

**Example mapping output:**
```json
{
  "properties": {
    "title": {
      "type": "text",
      "analyzer": "standard",
      "fields": {
        "keyword": {"type": "keyword", "ignore_above": 256}
      }
    },
    "body": {"type": "text", "analyzer": "standard"},
    "category": {"type": "keyword"}
  }
}
```

---

### `initialize_index()`
```python
async def initialize_index(self) -> None:
```

**Purpose:** Creates the Elasticsearch index with proper mapping if it doesn't exist.

**Process:**
1. Check if index exists
2. If not, create index with mapping from `_create_document_mapping()`
3. Log success/failure

**Example usage:**
```python
await service.initialize_index()
# Logs: "Index newsgroups created successfully" or "Index newsgroups already exists"
```

---

### `create_document()`
```python
async def create_document(self, document: DocumentCreate) -> DocumentResponse:
```

**Purpose:** Creates a single document in Elasticsearch.

**Parameters:**
- `document`: Pydantic model with document data

**Process:**
1. Generate UUID for document ID
2. Add timestamps (`created_at`, `updated_at`)
3. Index document in Elasticsearch
4. Refresh index for immediate searchability
5. Return DocumentResponse with ID and data

**Example:**
```python
from app.models import DocumentCreate

doc_data = DocumentCreate(
    title="Machine Learning Discussion",
    body="Let's discuss neural networks...",
    category="comp.graphics",
    author="ml_researcher",
    tags=["ml", "ai"]
)

result = await service.create_document(doc_data)
print(result.id)  # "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
print(result.created_at)  # "2024-01-15T10:30:00Z"
```

---

### `get_document()`
```python
async def get_document(self, doc_id: str) -> Optional[DocumentResponse]:
```

**Purpose:** Retrieves a single document by ID.

**Parameters:**
- `doc_id`: Document UUID string

**Returns:** 
- `DocumentResponse` if found
- `None` if not found

**Example:**
```python
doc = await service.get_document("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
if doc:
    print(f"Title: {doc.title}")
    print(f"Author: {doc.author}")
else:
    print("Document not found")
```

---

### `update_document()`
```python
async def update_document(self, doc_id: str, update_data: DocumentUpdate) -> Optional[DocumentResponse]:
```

**Purpose:** Updates an existing document with partial data.

**Parameters:**
- `doc_id`: Document UUID
- `update_data`: Pydantic model with fields to update (only non-None fields are updated)

**Process:**
1. Check if document exists
2. Filter out None values from update_data
3. Add new `updated_at` timestamp
4. Apply partial update to Elasticsearch
5. Return updated document

**Example:**
```python
from app.models import DocumentUpdate

update = DocumentUpdate(
    title="Updated ML Discussion",
    tags=["ml", "ai", "deep-learning"]
    # body, category, author remain unchanged
)

updated_doc = await service.update_document(doc_id, update)
if updated_doc:
    print(f"Updated title: {updated_doc.title}")
```

---

### `delete_document()`
```python
async def delete_document(self, doc_id: str) -> bool:
```

**Purpose:** Deletes a document from Elasticsearch.

**Parameters:**
- `doc_id`: Document UUID

**Returns:** 
- `True` if deleted successfully
- `False` if document not found

**Example:**
```python
success = await service.delete_document(doc_id)
if success:
    print("Document deleted")
else:
    print("Document not found")
```

---

### `search_documents()` - The Core Search Method
```python
async def search_documents(
    self,
    query: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[List[str]] = None,
    author: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
) -> SearchResponse:
```

**Purpose:** Advanced multi-field search with filters and pagination.

**Parameters:**
- `query`: Free text search across title and body
- `category`: Exact category match (e.g., "sci.space")
- `tags`: List of tags (document must have ALL tags)
- `author`: Exact author match
- `status`: Document status filter
- `limit`: Maximum results to return
- `offset`: Pagination offset

**Search Query Structure:**
```json
{
  "query": {
    "bool": {
      "must": [/* text search */],
      "filter": [/* exact matches */]
    }
  },
  "from": 0,
  "size": 10,
  "sort": [{"created_at": {"order": "desc"}}]
}
```

**Text Search Logic:**
- If `query` provided: Uses `multi_match` across `title^2` (boosted) and `body`
- If no query: Uses `match_all`

**Filter Logic:**
- Category: `{"term": {"category": "sci.space"}}`
- Tags: `{"terms": {"tags": ["ai", "ml"]}}`
- Author: `{"term": {"author": "researcher"}}`

**Example searches:**

```python
# Simple text search
results = await service.search_documents(query="machine learning")

# Category filter
results = await service.search_documents(category="sci.space")

# Complex search
results = await service.search_documents(
    query="neural networks",
    category="comp.graphics", 
    tags=["ai", "ml"],
    author="researcher",
    limit=20,
    offset=10
)

print(f"Found {results.total_hits} documents")
print(f"Max relevance score: {results.max_score}")
print(f"Query took: {results.took_ms}ms")

for doc in results.documents:
    print(f"- {doc.title} by {doc.author}")
```

---

### `bulk_create_documents()`
```python
async def bulk_create_documents(self, documents: List[DocumentCreate]) -> Dict[str, Any]:
```

**Purpose:** Efficiently creates multiple documents in a single request.

**Parameters:**
- `documents`: List of DocumentCreate objects

**Process:**
1. Generate UUIDs for each document
2. Add timestamps to all documents
3. Format as Elasticsearch bulk API actions:
   ```
   {"index": {"_index": "newsgroups", "_id": "uuid1"}}
   {"title": "Doc 1", "body": "Content 1", ...}
   {"index": {"_index": "newsgroups", "_id": "uuid2"}}
   {"title": "Doc 2", "body": "Content 2", ...}
   ```
4. Execute bulk request
5. Parse results and count successes/failures

**Returns:**
```python
{
    "success_count": 15,
    "error_count": 2, 
    "errors": ["Document too large", "Invalid category"]
}
```

**Example:**
```python
docs = [
    DocumentCreate(title="Doc 1", body="Content 1", category="sci.space"),
    DocumentCreate(title="Doc 2", body="Content 2", category="comp.graphics"),
    DocumentCreate(title="Doc 3", body="Content 3", category="rec.autos")
]

result = await service.bulk_create_documents(docs)
print(f"Created {result['success_count']} documents")
if result['error_count'] > 0:
    print(f"Errors: {result['errors']}")
```

---

# NewsDataLoader (`data_loader.py`)

## Purpose
Loads and processes data from scikit-learn's 20newsgroups dataset, with text cleaning and metadata extraction.

## Key Components

### Pre-compiled Regex Patterns
```python
RE_SUBJECT_PREFIX = re.compile(r'^(Re:\s*)+', re.IGNORECASE)  # Remove "Re: Re: ..." prefixes
RE_EMAIL_EXTRACT = re.compile(r'<(.+?)>')                    # Extract email from "Name <email>"
RE_EXCESSIVE_WHITESPACE = re.compile(r'\s+')                 # Normalize whitespace
```

### Email Headers Set
```python
EMAIL_HEADERS = {
    'From:', 'Subject:', 'Date:', 'Organization:', 'Lines:', 
    'Message-ID:', 'NNTP-Posting-Host:', 'Reply-To:', 'Newsgroups:'
}
```
Used for O(1) header detection during text cleaning.

---

## Methods Documentation

### `_parse_email_headers()`
```python
@staticmethod
def _parse_email_headers(text: str) -> Dict[str, Optional[str]]:
```

**Purpose:** Efficiently extracts subject and author from email headers in one pass.

**Process:**
1. Split text into lines
2. Look for "Subject:" and "From:" headers
3. Extract and clean values:
   - Subject: Remove "Re:" prefixes, limit to 500 chars
   - Author: Extract name or email address

**Example input:**
```
From: John Doe <john.doe@university.edu>
Subject: Re: Re: Machine Learning Discussion
Date: Mon, 15 Jan 2024 10:30:00 GMT

This is the message body...
```

**Example output:**
```python
{
    'subject': 'Machine Learning Discussion',  # "Re: Re:" removed
    'author': 'John Doe'                       # Name extracted from email format
}
```

---

### `clean_text()`
```python
@staticmethod
def clean_text(text: str) -> str:
```

**Purpose:** Removes email headers, quoted text, and excessive whitespace from newsgroup posts.

**Cleaning Steps:**
1. Split into lines
2. Skip email headers (using EMAIL_HEADERS set)
3. Skip quoted lines (starting with ">")
4. Normalize whitespace with regex
5. Join clean lines

**Example transformation:**

**Input:**
```
From: user@example.com
Subject: Test post
Lines: 15

This is my original content.
> This is quoted from previous post
> More quoted content
This is more original content.


   Extra   whitespace   here   
```

**Output:**
```
This is my original content.
This is more original content.
Extra whitespace here
```

---

### `_generate_tags()`
```python
@staticmethod
def _generate_tags(category: str) -> List[str]:
```

**Purpose:** Generate relevant tags based on newsgroup category.

**Tag Generation Rules:**
- Always include category with dots replaced by dashes
- Add category-family tag based on prefix:

```python
category_mappings = {
    'comp.': 'computer',      # comp.graphics -> ['comp-graphics', 'computer']
    'rec.': 'recreation',     # rec.autos -> ['rec-autos', 'recreation'] 
    'sci.': 'science',        # sci.space -> ['sci-space', 'science']
    'talk.': 'discussion',    # talk.politics.guns -> ['talk-politics-guns', 'discussion']
    'soc.': 'society',        # soc.religion.christian -> ['soc-religion-christian', 'society']
    'misc.': 'misc',          # misc.forsale -> ['misc-forsale', 'misc']
    'alt.': 'alternative'     # alt.atheism -> ['alt-atheism', 'alternative']
}
```

---

### `load_20newsgroups_data()`
```python
@staticmethod
def load_20newsgroups_data(
    subset: str = 'train',
    categories: Optional[List[str]] = None,
    max_documents: int = 1000,
    remove_headers: bool = True,
    remove_footers: bool = True,
    remove_quotes: bool = True
) -> List[Dict[str, Any]]:
```

**Purpose:** Load real 20newsgroups data from scikit-learn with cleaning and processing.

**Parameters:**
- `subset`: 'train', 'test', or 'all'
- `categories`: Specific categories to load (None = all 20)
- `max_documents`: Limit number of documents
- `remove_*`: scikit-learn preprocessing options

**Process:**
1. Call scikit-learn's `fetch_20newsgroups()`
2. Process each document:
   - Clean text content
   - Extract subject/author from headers
   - Generate tags
   - Create document dictionary
3. Filter out very short documents (< 50 chars)

**Example usage:**
```python
# Load 500 science-related documents
docs = NewsDataLoader.load_20newsgroups_data(
    subset='train',
    categories=['sci.space', 'sci.med', 'sci.crypt'],
    max_documents=500
)

print(f"Loaded {len(docs)} documents")
for doc in docs[:3]:
    print(f"Title: {doc['title']}")
    print(f"Category: {doc['category']}")
    print(f"Author: {doc['author']}")
    print(f"Tags: {doc['tags']}")
    print(f"Body length: {len(doc['body'])} chars")
    print("---")
```

**Sample output:**
```
Loaded 487 documents
Title: Mars Mission Update
Category: sci.space
Author: nasa_researcher
Tags: ['sci-space', 'science']
Body length: 1247 chars
---
```

---

### `load_sample_data()`
```python
@staticmethod
def load_sample_data() -> List[Dict[str, Any]]:
```

**Purpose:** Provides 5 hand-crafted sample documents for testing and development.

**Sample Categories Covered:**
- `comp.graphics` - Computer graphics discussion
- `sci.space` - Mars rover discoveries  
- `rec.sport.baseball` - World Series analysis
- `sci.crypt` - Quantum cryptography
- `rec.autos` - Electric vehicle trends

**Example usage:**
```python
samples = NewsDataLoader.load_sample_data()
print(f"Sample data contains {len(samples)} documents")

# Each document has this structure:
{
    'title': 'Document title',
    'body': 'Document content...',
    'category': 'newsgroup.category',
    'author': 'username',
    'tags': ['tag1', 'tag2', 'tag3'],
    'status': 'active'
}
```

---

## Performance Optimizations

### 1. **Regex Compilation**
- Patterns compiled once at module level
- Significant speedup for processing many documents

### 2. **Set-based Header Lookup**
- `EMAIL_HEADERS` as set provides O(1) lookup
- Much faster than multiple `if`/`elif` chains

### 3. **Single-pass Header Parsing**
- `_parse_email_headers()` extracts both subject and author in one loop
- Reduces text processing overhead

### 4. **Dictionary-based Tag Mapping**
- Category prefix lookup in O(1) time
- Cleaner than long if/elif chains

### 5. **Efficient String Operations**
- `line.strip()` called only once per line
- Regex substitution done in single calls

## Error Handling

Both services implement comprehensive error handling:

- **ElasticsearchService**: Catches connection errors, index errors, and query failures
- **NewsDataLoader**: Handles missing scikit-learn, data loading failures, and malformed content
- All errors are logged with context for debugging
- Graceful degradation (empty results rather than crashes)

## Usage Patterns

### Service Initialization
```python
# In main.py during app startup
es_client = Elasticsearch("http://localhost:9200")
es_service = ElasticsearchService(es_client, "newsgroups")
await es_service.initialize_index()

# Set service in dependency injection
dependencies.set_es_service(es_service)
```

### Loading Data Pipeline
```python
# Load real data
newsgroups_data = NewsDataLoader.load_20newsgroups_data(
    subset='train', 
    max_documents=1000
)

# Convert to Pydantic models
documents = [DocumentCreate(**doc) for doc in newsgroups_data]

# Bulk create in Elasticsearch
result = await es_service.bulk_create_documents(documents)
```

This services layer provides a clean separation of concerns, efficient data processing, and robust error handling for the entire application.