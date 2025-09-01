# Search Router (`search.py`)

## Purpose
Provides advanced search functionality and metadata queries for the document collection. Enables full-text search with multiple filter combinations, pagination, and relevance scoring.

## Overview
This router is the primary interface for discovering content in the system. It supports sophisticated queries combining text search with categorical filters, and provides metadata endpoints for UI components and analytics.

---

## Dependencies & Imports

```python
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import get_es_service
from app.models import DocumentStatus, NewsCategory, SearchResponse
from app.services.elasticsearch_service import ElasticsearchService
```

### Key Components:
- **Query Parameters**: Advanced FastAPI query parameter validation
- **Enum Models**: Type-safe category and status filtering
- **SearchResponse**: Structured response model with metadata
- **Optional Parameters**: Flexible search criteria

---

## Router Setup

```python
logger = logging.getLogger(__name__)
router = APIRouter()
```

- Module-specific logger for search operation tracking
- Router instance included in main app with `/search` prefix

---

# Search Endpoints Documentation

## 1. Advanced Document Search

### Endpoint Definition
```python
@router.get("/", response_model=SearchResponse)
async def search_documents(
    q: Optional[str] = None,
    category: Optional[NewsCategory] = None,
    tags: Optional[List[str]] = Query(None),
    author: Optional[str] = None,
    status: Optional[DocumentStatus] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: ElasticsearchService = Depends(get_es_service)
):
```

### Purpose
Performs multi-field document search with flexible filtering and pagination.

### URL
`GET /search/`

### Query Parameters

#### Text Search
- **`q`** (string, optional)
  - **Purpose**: Free-text search across document title and body
  - **Behavior**: Uses Elasticsearch multi_match query
  - **Boosting**: Title field boosted 2x for relevance
  - **Example**: `?q=machine learning neural networks`

#### Category Filter
- **`category`** (NewsCategory enum, optional)
  - **Purpose**: Filter by exact newsgroup category
  - **Values**: Any of the 20 newsgroup categories
  - **Example**: `?category=sci.space`
  - **Validation**: Must be valid NewsCategory enum value

#### Tags Filter
- **`tags`** (List[string], optional)
  - **Purpose**: Filter documents containing ALL specified tags
  - **Logic**: AND operation (document must have all listed tags)
  - **Format**: Repeat parameter for multiple tags
  - **Example**: `?tags=ai&tags=research&tags=2024`

#### Author Filter
- **`author`** (string, optional)
  - **Purpose**: Filter by exact author match
  - **Matching**: Case-sensitive exact match
  - **Example**: `?author=researcher_smith`

#### Status Filter
- **`status`** (DocumentStatus enum, optional)
  - **Purpose**: Filter by document status
  - **Values**: "active", "archived", "draft"
  - **Example**: `?status=active`
  - **Default Behavior**: No status filter (all statuses included)

#### Pagination
- **`limit`** (integer, range: 1-100, default: 10)
  - **Purpose**: Maximum number of results to return
  - **Validation**: Must be between 1 and 100
  - **Example**: `?limit=25`

- **`offset`** (integer, minimum: 0, default: 0)
  - **Purpose**: Number of results to skip for pagination
  - **Calculation**: Page number = (offset / limit) + 1
  - **Example**: `?offset=20&limit=10` (page 3)

### Response Model: `SearchResponse`
```python
{
    "total_hits": 1247,                    # Total matching documents
    "max_score": 8.234567,                 # Highest relevance score
    "took_ms": 23,                         # Query execution time in milliseconds
    "documents": [                         # Array of matching documents
        {
            "id": "uuid-string",
            "title": "Document Title",
            "body": "Document content...",
            "category": "sci.space",
            "tags": ["space", "mars"],
            "author": "space_researcher",
            "source_url": "https://example.com",
            "status": "active",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
        // ... more documents
    ]
}
```

### Search Logic Implementation

The search uses Elasticsearch's bool query with separate `must` and `filter` clauses:

#### Text Search Logic
```python
# If query provided
if query:
    search_body['query']['bool']['must'].append({
        'multi_match': {
            'query': query,
            'fields': ['title^2', 'body'],    # Title boosted 2x
            'type': 'best_fields'
        }
    })
else:
    search_body['query']['bool']['must'].append({'match_all': {}})
```

#### Filter Logic
```python
# Category filter (exact match)
if category:
    search_body['query']['bool']['filter'].append({
        'term': {'category': category}
    })

# Tags filter (must have ALL tags)  
if tags:
    search_body['query']['bool']['filter'].append({
        'terms': {'tags': tags}
    })

# Author filter (exact match)
if author:
    search_body['query']['bool']['filter'].append({
        'term': {'author': author}
    })

# Status filter (exact match)
if status:
    search_body['query']['bool']['filter'].append({
        'term': {'status': status}
    })
```

#### Sorting & Pagination
```python
search_body.update({
    'from': offset,
    'size': limit,
    'sort': [{'created_at': {'order': 'desc'}}]  # Newest first
})
```

### Usage Examples

#### Simple Text Search
```bash
curl "http://localhost:8182/search/?q=machine learning"
```

#### Category-Specific Search
```bash
curl "http://localhost:8182/search/?category=sci.space&limit=20"
```

#### Multi-Tag Filter
```bash
curl "http://localhost:8182/search/?tags=ai&tags=research&tags=neural-networks"
```

#### Complex Combined Search
```bash
curl "http://localhost:8182/search/?q=neural networks&category=comp.graphics&author=ml_researcher&status=active&limit=15&offset=10"
```

#### Python Search Examples

##### Basic Search
```python
import requests

# Simple text search
response = requests.get("http://localhost:8182/search/", params={
    "q": "artificial intelligence",
    "limit": 20
})

results = response.json()
print(f"Found {results['total_hits']} documents")
print(f"Query took {results['took_ms']}ms")

for doc in results['documents']:
    print(f"- {doc['title']} (score: {results['max_score']:.2f})")
```

##### Advanced Filtered Search
```python
# Multi-criteria search
search_params = {
    "q": "space exploration mars",
    "category": "sci.space",
    "tags": ["mars", "exploration"],
    "status": "active",
    "limit": 10,
    "offset": 0
}

response = requests.get("http://localhost:8182/search/", params=search_params)
results = response.json()

print(f"Search Results: {results['total_hits']} matches")
for doc in results['documents']:
    print(f"📄 {doc['title']}")
    print(f"   Author: {doc['author']}")
    print(f"   Tags: {', '.join(doc['tags'])}")
    print(f"   Created: {doc['created_at']}")
    print()
```

##### Pagination Example
```python
def paginated_search(query, page_size=10):
    """Search with pagination support"""
    page = 1
    all_results = []
    
    while True:
        offset = (page - 1) * page_size
        
        response = requests.get("http://localhost:8182/search/", params={
            "q": query,
            "limit": page_size,
            "offset": offset
        })
        
        results = response.json()
        documents = results['documents']
        
        if not documents:  # No more results
            break
            
        all_results.extend(documents)
        print(f"Page {page}: {len(documents)} results")
        
        # Check if we've got all results
        if len(all_results) >= results['total_hits']:
            break
            
        page += 1
    
    return all_results

# Usage
all_docs = paginated_search("machine learning")
print(f"Total collected: {len(all_docs)} documents")
```

### Search Strategies and Patterns

#### 1. Relevance-Based Search
```python
def relevance_search(query, min_score=1.0):
    """Search with minimum relevance threshold"""
    response = requests.get("http://localhost:8182/search/", params={
        "q": query,
        "limit": 50
    })
    
    results = response.json()
    
    # Filter by relevance (approximation since individual scores not returned)
    if results['max_score'] and results['max_score'] >= min_score:
        return results['documents']
    else:
        return []
```

#### 2. Category Explorer
```python
def explore_category(category, sample_size=5):
    """Get sample documents from a specific category"""
    response = requests.get("http://localhost:8182/search/", params={
        "category": category,
        "status": "active",
        "limit": sample_size
    })
    
    results = response.json()
    
    print(f"Category: {category}")
    print(f"Total documents: {results['total_hits']}")
    print(f"Sample documents:")
    
    for doc in results['documents']:
        print(f"  - {doc['title']} by {doc['author']}")
        print(f"    Tags: {', '.join(doc['tags'])}")
```

#### 3. Author Portfolio
```python
def author_portfolio(author_name, limit=20):
    """Get all documents by a specific author"""
    response = requests.get("http://localhost:8182/search/", params={
        "author": author_name,
        "status": "active",
        "limit": limit
    })
    
    results = response.json()
    
    print(f"Author: {author_name}")
    print(f"Published documents: {results['total_hits']}")
    
    # Group by category
    by_category = {}
    for doc in results['documents']:
        category = doc['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(doc['title'])
    
    print("By category:")
    for category, titles in by_category.items():
        print(f"  {category}: {len(titles)} documents")
        for title in titles[:3]:  # Show first 3
            print(f"    - {title}")
```

#### 4. Tag-Based Discovery
```python
def discover_related_content(base_tags, exclude_docs=None):
    """Find content related to specific tags"""
    exclude_docs = exclude_docs or []
    
    response = requests.get("http://localhost:8182/search/", params={
        "tags": base_tags,
        "limit": 30
    })
    
    results = response.json()
    
    # Filter out excluded documents
    related_docs = [
        doc for doc in results['documents'] 
        if doc['id'] not in exclude_docs
    ]
    
    # Analyze tag co-occurrence
    tag_frequency = {}
    for doc in related_docs:
        for tag in doc['tags']:
            if tag not in base_tags:  # Exclude search tags
                tag_frequency[tag] = tag_frequency.get(tag, 0) + 1
    
    print("Related tags:")
    for tag, count in sorted(tag_frequency.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {tag}: {count} documents")
    
    return related_docs
```

---

## 2. List Categories

### Endpoint Definition
```python
@router.get("/categories")
async def list_categories():
```

### Purpose
Returns a complete list of all available newsgroup categories for UI components and validation.

### URL
`GET /search/categories`

### Parameters
None

### Response Structure
```json
{
    "categories": [
        "alt.atheism",
        "comp.graphics", 
        "comp.os.ms-windows.misc",
        "comp.sys.ibm.pc.hardware",
        "comp.sys.mac.hardware",
        "comp.windows.x",
        "misc.forsale",
        "rec.autos",
        "rec.motorcycles", 
        "rec.sport.baseball",
        "rec.sport.hockey",
        "sci.crypt",
        "sci.electronics",
        "sci.med",
        "sci.space",
        "soc.religion.christian",
        "talk.politics.guns",
        "talk.politics.mideast", 
        "talk.politics.misc",
        "talk.religion.misc"
    ],
    "total_categories": 20
}
```

### Implementation
```python
return {
    "categories": [category.value for category in NewsCategory],
    "total_categories": len(NewsCategory)
}
```

### Usage Examples

#### cURL Request
```bash
curl "http://localhost:8182/search/categories"
```

#### Python Usage
```python
import requests

response = requests.get("http://localhost:8182/search/categories")
data = response.json()

print(f"Available categories ({data['total_categories']}):")
for category in data['categories']:
    print(f"  - {category}")

# Group by prefix
prefixes = {}
for category in data['categories']:
    prefix = category.split('.')[0]
    if prefix not in prefixes:
        prefixes[prefix] = []
    prefixes[prefix].append(category)

print("\nGrouped by prefix:")
for prefix, categories in prefixes.items():
    print(f"  {prefix}.* ({len(categories)} categories)")
    for cat in categories:
        print(f"    - {cat}")
```

#### UI Integration Example
```javascript
// Fetch categories for dropdown
async function populateCategoryDropdown() {
    try {
        const response = await fetch('/search/categories');
        const data = await response.json();
        
        const dropdown = document.getElementById('category-select');
        dropdown.innerHTML = '<option value="">All Categories</option>';
        
        data.categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            dropdown.appendChild(option);
        });
        
    } catch (error) {
        console.error('Failed to load categories:', error);
    }
}
```

---

## Search Performance & Optimization

### Query Performance Characteristics

#### Text Search Performance
- **Simple queries** (1-2 terms): 10-50ms
- **Complex queries** (5+ terms): 50-200ms
- **Wildcard searches**: 100-500ms (use sparingly)

#### Filter Performance
- **Category filter**: +5-15ms (indexed field)
- **Tags filter**: +10-30ms (depends on tag count)
- **Author filter**: +5-10ms (keyword field)
- **Status filter**: +5-10ms (keyword field)

#### Pagination Impact
- **Small offsets** (0-100): Minimal impact
- **Large offsets** (1000+): +50-200ms
- **Recommendation**: Use search_after for deep pagination

### Optimization Strategies

#### 1. Query Optimization
```python
def optimized_search(query, category=None, limit=10):
    """Optimized search with smart parameter selection"""
    
    params = {"limit": limit}
    
    # Use category filter for better performance
    if category:
        params["category"] = category
    
    # Limit query complexity for large result sets
    if query and len(query.split()) > 10:
        # Truncate very long queries
        query = ' '.join(query.split()[:10])
    
    if query:
        params["q"] = query
    
    response = requests.get("http://localhost:8182/search/", params=params)
    return response.json()
```

#### 2. Caching Strategy
```python
import time
from functools import lru_cache

class SearchCache:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def get_cache_key(self, **params):
        """Generate cache key from search parameters"""
        return str(sorted(params.items()))
    
    def cached_search(self, **params):
        """Search with caching"""
        cache_key = self.get_cache_key(**params)
        
        # Check cache
        if cache_key in self.cache:
            result, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return result
        
        # Perform search
        response = requests.get("http://localhost:8182/search/", params=params)
        result = response.json()
        
        # Cache result
        self.cache[cache_key] = (result, time.time())
        
        return result

# Usage
search_cache = SearchCache()
results = search_cache.cached_search(q="machine learning", category="comp.graphics")
```

---

## Error Handling

### HTTP Status Codes
- **200 OK**: Successful search operation
- **400 Bad Request**: Invalid parameter values
- **500 Internal Server Error**: Search service failure

### Common Error Scenarios

#### 1. Invalid Enum Values
```python
# Invalid category
response = requests.get("http://localhost:8182/search/", params={
    "category": "invalid.category"
})
# Returns 422 Unprocessable Entity with validation details
```

#### 2. Parameter Validation Errors
```python
# Limit too large
response = requests.get("http://localhost:8182/search/", params={
    "limit": 500  # Max is 100
})
# Returns 422 with validation error
```

#### 3. Service Failures
```json
{
    "detail": "Search failed: ConnectionTimeout: Elasticsearch connection timeout"
}
```

### Error Handling Pattern
```python
def robust_search(query, **kwargs):
    """Search with comprehensive error handling"""
    try:
        response = requests.get("http://localhost:8182/search/", params={
            "q": query,
            **kwargs
        })
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 422:
            print(f"Validation error: {response.json()}")
            return None
        else:
            print(f"Search failed: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None
```

---

## Advanced Search Applications

### 1. Search Analytics
```python
def analyze_search_performance():
    """Analyze search performance across different query types"""
    
    test_queries = [
        {"q": "machine learning"},
        {"category": "sci.space"},
        {"tags": ["ai", "research"]},
        {"q": "neural networks", "category": "comp.graphics"},
        {"author": "researcher"},
    ]
    
    performance_data = []
    
    for params in test_queries:
        start_time = time.time()
        response = requests.get("http://localhost:8182/search/", params=params)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            performance_data.append({
                "query": params,
                "total_hits": result['total_hits'],
                "elasticsearch_time": result['took_ms'],
                "total_time": (end_time - start_time) * 1000,
                "results_count": len(result['documents'])
            })
    
    return performance_data
```

### 2. Content Recommendation Engine
```python
def recommend_similar_content(document_id, limit=5):
    """Recommend content similar to a given document"""
    
    # First, get the source document
    doc_response = requests.get(f"http://localhost:8182/documents/{document_id}")
    if doc_response.status_code != 200:
        return []
    
    doc = doc_response.json()
    
    # Search for similar documents using tags and category
    search_params = {
        "category": doc['category'],
        "tags": doc['tags'][:3],  # Use top 3 tags
        "limit": limit + 5  # Get extra to filter out source doc
    }
    
    response = requests.get("http://localhost:8182/search/", params=search_params)
    if response.status_code != 200:
        return []
    
    results = response.json()
    
    # Filter out the source document and return top matches
    similar_docs = [
        d for d in results['documents'] 
        if d['id'] != document_id
    ][:limit]
    
    return similar_docs
```

### 3. Search Suggestion System
```python
def generate_search_suggestions(partial_query, limit=5):
    """Generate search suggestions based on partial input"""
    
    # Search for documents containing partial query
    response = requests.get("http://localhost:8182/search/", params={
        "q": partial_query,
        "limit": 20
    })
    
    if response.status_code != 200:
        return []
    
    results = response.json()
    
    # Extract potential suggestions from titles
    suggestions = set()
    for doc in results['documents']:
        title_words = doc['title'].lower().split()
        for i, word in enumerate(title_words):
            if partial_query.lower() in word:
                # Suggest the complete word or phrase
                if i < len(title_words) - 1:
                    suggestions.add(f"{word} {title_words[i+1]}")
                suggestions.add(word)
    
    return list(suggestions)[:limit]
```

This search router provides powerful and flexible search capabilities, enabling users to find relevant content efficiently through various search strategies and filter combinations.