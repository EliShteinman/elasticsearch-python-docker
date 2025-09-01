# Documents Router (`documents.py`)

## Purpose
Provides complete CRUD (Create, Read, Update, Delete) operations for individual documents in the Elasticsearch index. This is the core document management interface of the API.

## Overview
This router handles all document lifecycle operations, from creation to deletion. It supports both single document operations and bulk operations for efficiency. All operations include proper validation, error handling, and logging.

---

## Dependencies & Imports

```python
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_es_service
from app.models import (
    BulkOperationResponse,
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate
)
from app.services.elasticsearch_service import ElasticsearchService
```

### Key Components:
- **Pydantic Models**: Type-safe request/response handling
- **HTTPException**: Proper HTTP error responses
- **ElasticsearchService**: Backend document operations
- **Logging**: Operation tracking and debugging

---

## Router Setup

```python
logger = logging.getLogger(__name__)
router = APIRouter()
```

- Module-specific logger for document operation tracking
- Router instance included in main app with `/documents` prefix

---

# CRUD Operations Documentation

## 1. CREATE - Create Document

### Endpoint Definition
```python
@router.post("/", response_model=DocumentResponse, status_code=201)
async def create_document(
    document: DocumentCreate,
    service: ElasticsearchService = Depends(get_es_service)
):
```

### Purpose
Creates a new document in the Elasticsearch index.

### URL
`POST /documents/`

### Request Model: `DocumentCreate`
```python
{
    "title": "string",              # Required, 1-500 characters
    "body": "string",               # Required, minimum 1 character
    "category": "NewsCategory",     # Required, must be valid newsgroup
    "tags": ["string"],             # Optional, list of tags
    "author": "string",             # Optional, author name
    "source_url": "string",         # Optional, source URL
    "status": "DocumentStatus"      # Optional, default: "active"
}
```

### Response Model: `DocumentResponse`
```python
{
    "id": "uuid-string",           # Generated UUID
    "title": "string",
    "body": "string", 
    "category": "string",
    "tags": ["string"],
    "author": "string",
    "source_url": "string",
    "status": "string",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

### Implementation Flow
```python
try:
    # 1. Service generates UUID and timestamps
    result = await service.create_document(document)
    
    # 2. Log successful creation
    logger.info(f"Created document with ID: {result.id}")
    
    # 3. Return with 201 status
    return result
    
except Exception as e:
    logger.error(f"Failed to create document: {e}")
    raise HTTPException(status_code=500, detail=f"Failed to create document: {str(e)}")
```

### Usage Examples

#### cURL Request
```bash
curl -X POST "http://localhost:8182/documents/" \
-H "Content-Type: application/json" \
-d '{
    "title": "Machine Learning Breakthrough", 
    "body": "Researchers have developed a new neural network architecture that significantly improves performance on natural language processing tasks...",
    "category": "comp.graphics",
    "author": "ml_researcher",
    "tags": ["ai", "machine-learning", "neural-networks"],
    "status": "active"
}'
```

#### Python Request
```python
import requests

document_data = {
    "title": "Space Mission Update",
    "body": "The latest Mars rover has discovered interesting geological formations that suggest past water activity...",
    "category": "sci.space", 
    "author": "space_reporter",
    "tags": ["mars", "geology", "water"],
    "source_url": "https://nasa.gov/mars-update"
}

response = requests.post(
    "http://localhost:8182/documents/",
    json=document_data
)

if response.status_code == 201:
    doc = response.json()
    print(f"Created document: {doc['id']}")
    print(f"Created at: {doc['created_at']}")
else:
    print(f"Error: {response.json()}")
```

### Validation Rules
- **Title**: 1-500 characters, required
- **Body**: Minimum 1 character, required
- **Category**: Must be valid NewsCategory enum value
- **Tags**: Optional list of strings
- **Author**: Optional string
- **Status**: Must be valid DocumentStatus enum ("active", "archived", "draft")

---

## 2. READ - Get Document

### Endpoint Definition
```python
@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: str,
    service: ElasticsearchService = Depends(get_es_service)
):
```

### Purpose
Retrieves a single document by its UUID.

### URL
`GET /documents/{doc_id}`

### Parameters
- **`doc_id`** (path): Document UUID string

### Response
- **Success**: `DocumentResponse` with full document data
- **Not Found**: HTTP 404 with error message

### Implementation Flow
```python
try:
    # 1. Attempt to retrieve document
    result = await service.get_document(doc_id)
    
    # 2. Check if document exists
    if not result:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # 3. Return document data
    return result
    
except HTTPException:
    raise  # Re-raise HTTP exceptions
except Exception as e:
    logger.error(f"Failed to get document {doc_id}: {e}")
    raise HTTPException(status_code=500, detail=f"Failed to retrieve document: {str(e)}")
```

### Usage Examples

#### cURL Request
```bash
curl -X GET "http://localhost:8182/documents/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

#### Python Request
```python
import requests

doc_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
response = requests.get(f"http://localhost:8182/documents/{doc_id}")

if response.status_code == 200:
    doc = response.json()
    print(f"Title: {doc['title']}")
    print(f"Author: {doc['author']}")
    print(f"Category: {doc['category']}")
    print(f"Tags: {', '.join(doc['tags'])}")
elif response.status_code == 404:
    print("Document not found")
else:
    print(f"Error: {response.json()}")
```

### Error Responses
```json
// 404 Not Found
{
    "detail": "Document not found"
}

// 500 Server Error  
{
    "detail": "Failed to retrieve document: ConnectionError"
}
```

---

## 3. UPDATE - Update Document

### Endpoint Definition
```python
@router.put("/{doc_id}", response_model=DocumentResponse)
async def update_document(
    doc_id: str,
    update_data: DocumentUpdate,
    service: ElasticsearchService = Depends(get_es_service)
):
```

### Purpose
Updates an existing document with partial or complete new data.

### URL
`PUT /documents/{doc_id}`

### Parameters
- **`doc_id`** (path): Document UUID string
- **`update_data`** (body): DocumentUpdate model

### Request Model: `DocumentUpdate`
```python
{
    "title": "string",              # Optional
    "body": "string",               # Optional  
    "category": "NewsCategory",     # Optional
    "tags": ["string"],             # Optional
    "author": "string",             # Optional
    "source_url": "string",         # Optional
    "status": "DocumentStatus"      # Optional
}
```

**Key Features:**
- All fields are optional (partial updates supported)
- Only non-null fields are updated
- `updated_at` timestamp is automatically set
- `created_at` timestamp is preserved

### Implementation Flow
```python
try:
    # 1. Service checks if document exists
    result = await service.update_document(doc_id, update_data)
    
    # 2. Handle not found case
    if not result:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # 3. Log successful update
    logger.info(f"Updated document with ID: {doc_id}")
    
    # 4. Return updated document
    return result
    
except HTTPException:
    raise
except Exception as e:
    logger.error(f"Failed to update document {doc_id}: {e}")
    raise HTTPException(status_code=500, detail=f"Failed to update document: {str(e)}")
```

### Usage Examples

#### Partial Update (Title Only)
```bash
curl -X PUT "http://localhost:8182/documents/a1b2c3d4-e5f6-7890-abcd-ef1234567890" \
-H "Content-Type: application/json" \
-d '{
    "title": "Updated: Machine Learning Breakthrough"
}'
```

#### Multiple Field Update
```bash
curl -X PUT "http://localhost:8182/documents/a1b2c3d4-e5f6-7890-abcd-ef1234567890" \
-H "Content-Type: application/json" \
-d '{
    "title": "Revised Mars Mission Report",
    "tags": ["mars", "geology", "water", "updated"],
    "status": "archived"
}'
```

#### Python Update
```python
import requests

doc_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
update_data = {
    "body": "Updated content with new findings and additional analysis...",
    "tags": ["ai", "machine-learning", "neural-networks", "breakthrough", "2024"]
}

response = requests.put(
    f"http://localhost:8182/documents/{doc_id}",
    json=update_data
)

if response.status_code == 200:
    updated_doc = response.json()
    print(f"Updated at: {updated_doc['updated_at']}")
    print(f"New tags: {updated_doc['tags']}")
elif response.status_code == 404:
    print("Document not found")
else:
    print(f"Update failed: {response.json()}")
```

### Update Strategies

#### Strategy 1: Incremental Updates
```python
# First, get current document
current_doc = requests.get(f"http://localhost:8182/documents/{doc_id}").json()

# Add new tag to existing tags
new_tags = current_doc['tags'] + ['new-tag']

# Update with expanded tags
requests.put(f"http://localhost:8182/documents/{doc_id}", json={
    "tags": new_tags
})
```

#### Strategy 2: Status Workflow
```python
def archive_document(doc_id):
    """Archive a document by changing status"""
    return requests.put(f"http://localhost:8182/documents/{doc_id}", json={
        "status": "archived"
    })

def publish_draft(doc_id):
    """Publish a draft document"""
    return requests.put(f"http://localhost:8182/documents/{doc_id}", json={
        "status": "active"
    })
```

---

## 4. DELETE - Delete Document

### Endpoint Definition
```python
@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    service: ElasticsearchService = Depends(get_es_service)
):
```

### Purpose
Permanently removes a document from the Elasticsearch index.

### URL
`DELETE /documents/{doc_id}`

### Parameters
- **`doc_id`** (path): Document UUID string

### Response
- **Success**: JSON confirmation message
- **Not Found**: HTTP 404 error

### Response Structure
```json
{
    "message": "Document a1b2c3d4-e5f6-7890-abcd-ef1234567890 deleted successfully"
}
```

### Implementation Flow
```python
try:
    # 1. Attempt to delete document
    result = await service.delete_document(doc_id)
    
    # 2. Check if document existed
    if not result:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # 3. Log successful deletion
    logger.info(f"Deleted document with ID: {doc_id}")
    
    # 4. Return confirmation
    return {"message": f"Document {doc_id} deleted successfully"}
    
except HTTPException:
    raise
except Exception as e:
    logger.error(f"Failed to delete document {doc_id}: {e}")
    raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
```

### Usage Examples

#### cURL Request
```bash
curl -X DELETE "http://localhost:8182/documents/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

#### Python Request
```python
import requests

doc_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
response = requests.delete(f"http://localhost:8182/documents/{doc_id}")

if response.status_code == 200:
    print(f"Success: {response.json()['message']}")
elif response.status_code == 404:
    print("Document not found (already deleted?)")
else:
    print(f"Deletion failed: {response.json()}")
```

#### Safe Deletion Pattern
```python
def safe_delete_document(doc_id):
    """Delete document with confirmation"""
    
    # First, verify document exists
    get_response = requests.get(f"http://localhost:8182/documents/{doc_id}")
    if get_response.status_code == 404:
        print("Document not found")
        return False
    
    # Show document info before deletion
    doc = get_response.json()
    print(f"About to delete: '{doc['title']}' by {doc['author']}")
    
    # Confirm deletion
    confirm = input("Are you sure? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Deletion cancelled")
        return False
    
    # Proceed with deletion
    delete_response = requests.delete(f"http://localhost:8182/documents/{doc_id}")
    return delete_response.status_code == 200
```

---

## 5. BULK CREATE - Bulk Create Documents

### Endpoint Definition
```python
@router.post("/bulk", response_model=BulkOperationResponse)
async def bulk_create_documents(
    documents: List[DocumentCreate],
    service: ElasticsearchService = Depends(get_es_service)
):
```

### Purpose
Efficiently creates multiple documents in a single request using Elasticsearch's bulk API.

### URL
`POST /documents/bulk`

### Request Body
```python
[
    {
        "title": "Document 1",
        "body": "Content 1",
        "category": "sci.space",
        # ... other fields
    },
    {
        "title": "Document 2", 
        "body": "Content 2",
        "category": "comp.graphics",
        # ... other fields
    }
    # ... up to 1000 documents
]
```

### Validation
- **Maximum**: 1000 documents per request (prevents system overload)
- **Individual Validation**: Each document must pass DocumentCreate validation

### Response Model: `BulkOperationResponse`
```python
{
    "success_count": 15,       # Number of successfully created documents
    "error_count": 2,          # Number of failed documents  
    "errors": [                # List of error messages for failed documents
        "Document too large",
        "Invalid category"
    ]
}
```

### Implementation Flow
```python
# 1. Validate request size
if len(documents) > 1000:
    raise HTTPException(status_code=400, detail="Maximum 1000 documents per bulk operation")

try:
    # 2. Execute bulk creation
    result = await service.bulk_create_documents(documents)
    
    # 3. Log operation results
    logger.info(f"Bulk create completed: {result['success_count']} successful, {result['error_count']} failed")
    
    # 4. Return structured response
    return BulkOperationResponse(**result)
    
except Exception as e:
    logger.error(f"Bulk create failed: {e}")
    raise HTTPException(status_code=500, detail=f"Bulk create failed: {str(e)}")
```

### Usage Examples

#### Small Bulk Create
```bash
curl -X POST "http://localhost:8182/documents/bulk" \
-H "Content-Type: application/json" \
-d '[
    {
        "title": "AI Research Update",
        "body": "Recent developments in artificial intelligence...",
        "category": "comp.graphics",
        "author": "ai_researcher",
        "tags": ["ai", "research"]
    },
    {
        "title": "Mars Exploration News", 
        "body": "Latest findings from the Mars rover mission...",
        "category": "sci.space",
        "author": "space_journalist",
        "tags": ["mars", "exploration", "space"]
    }
]'
```

#### Python Bulk Create
```python
import requests

documents = []
for i in range(10):
    documents.append({
        "title": f"Sample Document {i+1}",
        "body": f"This is sample content for document number {i+1}. It contains relevant information for testing purposes.",
        "category": "misc.forsale",
        "author": f"user_{i+1}",
        "tags": ["sample", "test", f"doc-{i+1}"]
    })

response = requests.post(
    "http://localhost:8182/documents/bulk",
    json=documents
)

if response.status_code == 200:
    result = response.json()
    print(f"Success: {result['success_count']} documents created")
    if result['error_count'] > 0:
        print(f"Errors: {result['error_count']} failed")
        for error in result['errors']:
            print(f"  - {error}")
else:
    print(f"Bulk create failed: {response.json()}")
```

#### Large Dataset Bulk Create
```python
def bulk_create_with_batching(all_documents, batch_size=1000):
    """Create documents in batches to respect API limits"""
    
    total_success = 0
    total_errors = 0
    
    # Process in batches
    for i in range(0, len(all_documents), batch_size):
        batch = all_documents[i:i + batch_size]
        
        print(f"Processing batch {i//batch_size + 1}: {len(batch)} documents")
        
        response = requests.post(
            "http://localhost:8182/documents/bulk",
            json=batch
        )
        
        if response.status_code == 200:
            result = response.json()
            total_success += result['success_count']
            total_errors += result['error_count']
            
            print(f"  Success: {result['success_count']}, Errors: {result['error_count']}")
        else:
            print(f"  Batch failed: {response.json()}")
            total_errors += len(batch)
    
    print(f"\nFinal Results:")
    print(f"  Total Success: {total_success}")
    print(f"  Total Errors: {total_errors}")
    
    return total_success, total_errors

# Usage
large_dataset = [...]  # Your large list of documents
bulk_create_with_batching(large_dataset)
```

---

## Error Handling Patterns

### HTTP Status Codes
- **200 OK**: Successful GET, PUT, DELETE operations
- **201 Created**: Successful POST operations
- **400 Bad Request**: Validation errors, request too large
- **404 Not Found**: Document doesn't exist
- **500 Internal Server Error**: Service failures

### Common Error Scenarios

#### 1. Validation Errors
```json
{
    "detail": [
        {
            "loc": ["title"],
            "msg": "ensure this value has at most 500 characters", 
            "type": "value_error.any_str.max_length"
        }
    ]
}
```

#### 2. Elasticsearch Connection Issues
```json
{
    "detail": "Failed to create document: ConnectionTimeout"
}
```

#### 3. Document Not Found
```json
{
    "detail": "Document not found"
}
```

---

## Performance Characteristics

### Single Operations
- **CREATE**: ~10-50ms per document
- **READ**: ~5-20ms per document  
- **UPDATE**: ~15-60ms per document
- **DELETE**: ~10-40ms per document

### Bulk Operations
- **Bulk Create**: ~100-500ms for 100 documents
- **Efficiency**: ~10x faster than individual creates
- **Optimal Batch Size**: 100-1000 documents

### Memory Usage
- **Single Doc**: <1MB memory per operation
- **Bulk Create**: ~1-10MB per 1000 documents
- **Processing**: Streaming-friendly for large batches

---

## Integration Patterns

### Document Workflow Management
```python
class DocumentWorkflow:
    def __init__(self, base_url="http://localhost:8182"):
        self.base_url = base_url
    
    def create_draft(self, title, body, category, author):
        """Create document as draft"""
        doc_data = {
            "title": title,
            "body": body, 
            "category": category,
            "author": author,
            "status": "draft"
        }
        
        response = requests.post(f"{self.base_url}/documents/", json=doc_data)
        return response.json()['id'] if response.status_code == 201 else None
    
    def publish_draft(self, doc_id):
        """Move document from draft to active"""
        return requests.put(f"{self.base_url}/documents/{doc_id}", json={
            "status": "active"
        })
    
    def archive_document(self, doc_id):
        """Archive active document"""
        return requests.put(f"{self.base_url}/documents/{doc_id}", json={
            "status": "archived"
        })
```

### Document Migration Tool
```python
def migrate_documents(source_docs, target_url):
    """Migrate documents from one system to another"""
    
    batch_size = 500
    migrated = 0
    
    for i in range(0, len(source_docs), batch_size):
        batch = source_docs[i:i + batch_size]
        
        # Convert to DocumentCreate format
        formatted_batch = [
            {
                "title": doc['title'],
                "body": doc['content'],
                "category": doc['newsgroup'],
                "author": doc.get('author', 'migrated_user'),
                "tags": doc.get('tags', [])
            }
            for doc in batch
        ]
        
        # Bulk create
        response = requests.post(
            f"{target_url}/documents/bulk",
            json=formatted_batch
        )
        
        if response.status_code == 200:
            result = response.json()
            migrated += result['success_count']
            print(f"Migrated {migrated} documents so far...")
    
    print(f"Migration completed: {migrated} total documents")
```

This documents router provides comprehensive document management capabilities, supporting the full document lifecycle from creation to deletion, with efficient bulk operations for large-scale data management.