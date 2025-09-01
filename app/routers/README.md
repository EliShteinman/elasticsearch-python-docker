# Routers Directory

This directory contains the FastAPI route handlers that define the REST API endpoints for the 20 Newsgroups Search API.

## Overview

The routers layer handles HTTP requests, validates input data, calls appropriate services, and returns formatted responses. Each router focuses on a specific domain of functionality.

## Directory Structure

```
app/routers/
├── __init__.py        # Makes this a Python package
├── analytics.py       # Statistics and analytics endpoints
├── data.py           # Data loading and management endpoints  
├── documents.py      # CRUD operations for documents
└── search.py         # Search and category listing endpoints
```

## Architecture Pattern

All routers follow the same architectural pattern:

### 1. **Dependency Injection**
```python
from app.dependencies import get_es_service
from app.services.elasticsearch_service import ElasticsearchService

@router.get("/endpoint")
async def handler(
    service: ElasticsearchService = Depends(get_es_service)
):
```

### 2. **Pydantic Models**
- Input validation with request models
- Response serialization with response models
- Type safety and automatic documentation

### 3. **Error Handling**
```python
try:
    result = await service.some_operation()
    return result
except Exception as e:
    logger.error(f"Operation failed: {e}")
    raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
```

### 4. **Logging**
All operations are logged for monitoring and debugging.

---

## Router Responsibilities

### 📊 **analytics.py**
**Purpose:** Provides statistical information about the document collection

**Endpoints:**
- `GET /analytics/stats` - Overall statistics
- `GET /analytics/categories` - Document count per category

**Use Cases:**
- Dashboard statistics
- Data analysis
- Collection monitoring

---

### 💾 **data.py** 
**Purpose:** Manages data loading operations from external sources

**Endpoints:**
- `POST /data/load-20newsgroups` - Load real scikit-learn data
- `POST /data/load-sample` - Load sample test data

**Features:**
- Background task processing
- Configurable data loading parameters
- Bulk document creation

---

### 📄 **documents.py**
**Purpose:** Full CRUD operations for individual documents

**Endpoints:**
- `POST /documents` - Create single document
- `GET /documents/{id}` - Retrieve document by ID
- `PUT /documents/{id}` - Update existing document  
- `DELETE /documents/{id}` - Delete document
- `POST /documents/bulk` - Bulk create multiple documents

**Features:**
- Complete document lifecycle management
- Input validation with Pydantic models
- Bulk operations support

---

### 🔍 **search.py**
**Purpose:** Advanced search functionality and metadata queries

**Endpoints:**
- `GET /search` - Multi-field document search
- `GET /search/categories` - List available categories

**Features:**
- Full-text search across title and body
- Multiple filter combinations (category, tags, author, status)
- Pagination support
- Relevance scoring

---

## Common Patterns

### Request Validation
All routers use Pydantic models for automatic request validation:

```python
@router.post("/endpoint", response_model=ResponseModel)
async def create_item(
    item: RequestModel,  # Automatic validation
    service: Service = Depends(get_service)
):
```

### Response Models
Consistent response structure with proper typing:

```python
# Success response
return ResponseModel(
    id="doc-123",
    title="Document Title", 
    created_at=datetime.utcnow()
)

# Error response (automatic via HTTPException)
raise HTTPException(
    status_code=404, 
    detail="Document not found"
)
```

### Query Parameters
Standardized query parameter handling:

```python
@router.get("/search")
async def search(
    q: Optional[str] = None,                    # Optional text query
    category: Optional[NewsCategory] = None,    # Enum validation
    limit: int = Query(10, ge=1, le=100),      # Range validation
    offset: int = Query(0, ge=0)               # Non-negative validation
):
```

### Background Tasks
Long-running operations use FastAPI's background tasks:

```python
@router.post("/data/load")
async def load_data(
    background_tasks: BackgroundTasks,
    service: Service = Depends(get_service)
):
    background_tasks.add_task(load_data_function)
    return {"message": "Loading started in background"}
```

## Error Handling Strategy

### HTTP Status Codes
- **200**: Successful operation
- **201**: Resource created successfully  
- **400**: Bad request (validation errors)
- **404**: Resource not found
- **500**: Internal server error

### Error Response Format
```json
{
  "detail": "Human-readable error message"
}
```

### Logging Levels
- **INFO**: Successful operations with key metrics
- **WARNING**: Recoverable issues  
- **ERROR**: Operation failures with context

## Integration with Main App

All routers are registered in `main.py`:

```python
from app.routers import documents, search, data, analytics

app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(search.router, prefix="/search", tags=["search"])
app.include_router(data.router, prefix="/data", tags=["data"])  
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
```

This creates the following URL structure:
- `/documents/*` - Document management
- `/search/*` - Search operations
- `/data/*` - Data loading
- `/analytics/*` - Statistics

## API Documentation

FastAPI automatically generates:
- **Swagger UI**: `http://localhost:8182/docs`
- **ReDoc**: `http://localhost:8182/redoc`
- **OpenAPI JSON**: `http://localhost:8182/openapi.json`

All endpoint documentation, request/response schemas, and examples are automatically generated from:
- Function docstrings
- Pydantic model definitions
- Type hints and parameter validation

## Testing Endpoints

### Using curl
```bash
# Test document creation
curl -X POST "http://localhost:8182/documents" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "body": "Content", "category": "sci.space"}'

# Test search
curl "http://localhost:8182/search?q=machine learning&limit=5"

# Test analytics
curl "http://localhost:8182/analytics/stats"
```

### Using Python requests
```python
import requests

# Create document
response = requests.post("http://localhost:8182/documents", json={
    "title": "Test Document",
    "body": "Test content",
    "category": "comp.graphics"
})
print(response.json())

# Search documents  
response = requests.get("http://localhost:8182/search", params={
    "q": "graphics",
    "category": "comp.graphics",
    "limit": 10
})
print(f"Found {response.json()['total_hits']} documents")
```

---

## Individual Router Documentation

For detailed documentation of each router, see:

- [analytics.py](./analytics.md) - Statistics and analytics endpoints
- [data.py](./data.md) - Data loading and management endpoints
- [documents.py](./documents.md) - CRUD operations for documents  
- [search.py](./search.md) - Search and category listing endpoints

Each router documentation includes:
- Detailed endpoint descriptions
- Request/response examples
- Parameter explanations
- Error scenarios
- Usage patterns