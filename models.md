# Data Models (`models.py`)

## Purpose
Defines all Pydantic data models and enums used throughout the 20 Newsgroups Search API. These models provide type safety, validation, serialization, and automatic API documentation.

## Overview
This module contains the core data structures that define how documents are created, updated, validated, and returned by the API. All models use Pydantic for automatic validation and serialization.

---

## Enums Documentation

### DocumentStatus
```python
class DocumentStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"  
    DRAFT = "draft"
```

**Purpose:** Defines the lifecycle states of documents in the system.

**Values:**
- **`ACTIVE`**: Published and searchable documents
- **`ARCHIVED`**: Older documents kept for reference but not prominently displayed
- **`DRAFT`**: Unpublished documents still being worked on

**Usage Examples:**
```python
from app.models import DocumentStatus

# Creating documents with different statuses
active_doc = DocumentCreate(
    title="Published Article",
    body="This is live content",
    category="sci.space",
    status=DocumentStatus.ACTIVE  # Default value
)

draft_doc = DocumentCreate(
    title="Work in Progress", 
    body="Still writing this...",
    category="comp.graphics",
    status=DocumentStatus.DRAFT
)

# Filtering by status
search_results = await service.search_documents(
    status=DocumentStatus.ACTIVE.value
)
```

**API Integration:**
```bash
# Search only active documents
curl "http://localhost:8182/search?status=active"

# Update document to archived
curl -X PUT "http://localhost:8182/documents/{id}" \
  -H "Content-Type: application/json" \
  -d '{"status": "archived"}'
```

---

### NewsCategory
```python
class NewsCategory(str, Enum):
    ALT_ATHEISM = "alt.atheism"
    COMP_GRAPHICS = "comp.graphics"
    # ... (all 20 categories)
```

**Purpose:** Defines all valid newsgroup categories from the original 20 Newsgroups dataset.

**Complete Category List:**

#### Computer Categories (`comp.*`)
- **`COMP_GRAPHICS`**: `"comp.graphics"` - Computer graphics, visualization, rendering
- **`COMP_OS_MS_WINDOWS_MISC`**: `"comp.os.ms-windows.misc"` - Windows operating system
- **`COMP_SYS_IBM_PC_HARDWARE`**: `"comp.sys.ibm.pc.hardware"` - PC hardware discussions
- **`COMP_SYS_MAC_HARDWARE`**: `"comp.sys.mac.hardware"` - Macintosh hardware
- **`COMP_WINDOWS_X`**: `"comp.windows.x"` - X Window System

#### Recreation Categories (`rec.*`)
- **`REC_AUTOS`**: `"rec.autos"` - Automotive discussions
- **`REC_MOTORCYCLES`**: `"rec.motorcycles"` - Motorcycle enthusiasts  
- **`REC_SPORT_BASEBALL`**: `"rec.sport.baseball"` - Baseball sports
- **`REC_SPORT_HOCKEY`**: `"rec.sport.hockey"` - Hockey sports

#### Science Categories (`sci.*`)  
- **`SCI_CRYPT`**: `"sci.crypt"` - Cryptography and security
- **`SCI_ELECTRONICS`**: `"sci.electronics"` - Electronics and circuits
- **`SCI_MED`**: `"sci.med"` - Medical and health sciences
- **`SCI_SPACE`**: `"sci.space"` - Space, astronomy, aerospace

#### Discussion Categories (`talk.*`)
- **`TALK_POLITICS_GUNS`**: `"talk.politics.guns"` - Gun politics and policy
- **`TALK_POLITICS_MIDEAST`**: `"talk.politics.mideast"` - Middle East politics  
- **`TALK_POLITICS_MISC`**: `"talk.politics.misc"` - General political discussion
- **`TALK_RELIGION_MISC`**: `"talk.religion.misc"` - Religious discussions

#### Society Categories (`soc.*`)
- **`SOC_RELIGION_CHRISTIAN`**: `"soc.religion.christian"` - Christian discussions

#### Alternative Categories (`alt.*`)
- **`ALT_ATHEISM`**: `"alt.atheism"` - Atheism and secular discussions

#### Miscellaneous Categories (`misc.*`)
- **`MISC_FORSALE`**: `"misc.forsale"` - Items for sale, classifieds

**Usage Examples:**
```python
from app.models import NewsCategory

# Creating documents with categories
space_doc = DocumentCreate(
    title="Mars Mission Update",
    body="Latest findings from Mars...",
    category=NewsCategory.SCI_SPACE
)

graphics_doc = DocumentCreate(
    title="3D Rendering Tutorial", 
    body="Learn advanced rendering techniques...",
    category=NewsCategory.COMP_GRAPHICS
)

# Category validation in API
valid_categories = [cat.value for cat in NewsCategory]
print(f"Valid categories: {valid_categories}")
```

**API Integration:**
```bash
# Search by category  
curl "http://localhost:8182/search?category=sci.space"

# Get all available categories
curl "http://localhost:8182/search/categories"

# Create document with category validation
curl -X POST "http://localhost:8182/documents" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI Discussion",
    "body": "Neural networks and machine learning...",
    "category": "comp.graphics"
  }'
```

---

## Base Models Documentation

### DocumentBase
```python
class DocumentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    body: str = Field(..., min_length=1)
    category: NewsCategory
    tags: List[str] = Field(default_factory=list)
    author: Optional[str] = None
    source_url: Optional[str] = None
    status: DocumentStatus = DocumentStatus.ACTIVE
```

**Purpose:** Base model containing all common document fields with validation rules.

**Field Specifications:**

#### `title` (Required)
- **Type:** `str`
- **Validation:** 1-500 characters
- **Purpose:** Document headline or subject line
- **Examples:**
  ```python
  "Mars Rover Discovers Water Evidence"
  "Deep Learning in Computer Graphics: A Tutorial"
  "Baseball Season Statistical Analysis"
  ```

#### `body` (Required) 
- **Type:** `str`
- **Validation:** Minimum 1 character
- **Purpose:** Main document content
- **Examples:**
  ```python
  "The latest Mars rover mission has uncovered compelling evidence of ancient water activity..."
  ```

#### `category` (Required)
- **Type:** `NewsCategory` enum
- **Validation:** Must be one of 20 valid newsgroup categories
- **Purpose:** Classifies document into newsgroup category
- **Examples:**
  ```python
  NewsCategory.SCI_SPACE
  NewsCategory.COMP_GRAPHICS
  NewsCategory.REC_SPORT_BASEBALL
  ```

#### `tags` (Optional)
- **Type:** `List[str]`
- **Default:** Empty list `[]`
- **Purpose:** Keywords for categorization and search
- **Examples:**
  ```python
  ["mars", "water", "geology"]
  ["ai", "machine-learning", "neural-networks"]
  ["baseball", "statistics", "world-series"]
  ```

#### `author` (Optional)
- **Type:** `Optional[str]`
- **Default:** `None`
- **Purpose:** Document author/creator name
- **Examples:**
  ```python
  "nasa_researcher"
  "ml_expert" 
  "sports_analyst"
  None  # Anonymous posts
  ```

#### `source_url` (Optional)
- **Type:** `Optional[str]`  
- **Default:** `None`
- **Purpose:** External reference URL
- **Examples:**
  ```python
  "https://nasa.gov/mars-mission-update"
  "https://arxiv.org/abs/2024.12345"
  None  # Original content
  ```

#### `status` (Optional)
- **Type:** `DocumentStatus` enum
- **Default:** `DocumentStatus.ACTIVE`
- **Purpose:** Document lifecycle state
- **Examples:**
  ```python
  DocumentStatus.ACTIVE    # Published content
  DocumentStatus.DRAFT     # Work in progress  
  DocumentStatus.ARCHIVED  # Historical content
  ```

---

## Request/Response Models Documentation

### DocumentCreate
```python
class DocumentCreate(DocumentBase):
    pass
```

**Purpose:** Model for creating new documents via POST requests.

**Characteristics:**
- Inherits all fields from `DocumentBase`
- Used for document creation endpoints
- All validation rules from base model apply
- No `id`, `created_at`, or `updated_at` fields (auto-generated)

**Usage Examples:**
```python
# API Request Model
create_data = DocumentCreate(
    title="New Research Paper",
    body="Abstract: This paper presents...",
    category=NewsCategory.SCI_MED,
    author="researcher@university.edu",
    tags=["medical", "research", "ai"],
    status=DocumentStatus.DRAFT
)

# API endpoint usage
@router.post("/", response_model=DocumentResponse)
async def create_document(document: DocumentCreate):
    return await service.create_document(document)
```

**JSON Schema (for API requests):**
```json
{
  "title": "New Research Paper",
  "body": "Abstract: This paper presents...",
  "category": "sci.med", 
  "author": "researcher@university.edu",
  "tags": ["medical", "research", "ai"],
  "source_url": "https://example.com/paper",
  "status": "draft"
}
```

---

### DocumentUpdate
```python
class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    body: Optional[str] = Field(None, min_length=1)
    category: Optional[NewsCategory] = None
    tags: Optional[List[str]] = None
    author: Optional[str] = None
    source_url: Optional[str] = None
    status: Optional[DocumentStatus] = None
```

**Purpose:** Model for partial document updates via PUT requests.

**Characteristics:**
- All fields are optional (`Optional[T]`)
- Only non-None fields are updated
- Same validation rules as base model when provided
- Supports partial updates (change only title, or only tags, etc.)

**Usage Examples:**
```python
# Update only title and tags
update_data = DocumentUpdate(
    title="Updated: Research Paper Final Version",
    tags=["medical", "research", "ai", "published"]
    # body, category, author remain unchanged
)

# Update only status (publish draft)  
publish_update = DocumentUpdate(
    status=DocumentStatus.ACTIVE
)

# Complex partial update
complex_update = DocumentUpdate(
    title="Revised Mars Mission Report",
    body="Updated findings based on new data...",
    tags=["mars", "geology", "water", "revised"],
    status=DocumentStatus.ACTIVE
)
```

**JSON Schema Examples:**
```json
// Minimal update (title only)
{
  "title": "Updated Title"
}

// Multi-field update  
{
  "title": "New Title",
  "tags": ["new", "tags", "list"],
  "status": "active"
}
```

---

### DocumentResponse
```python
class DocumentResponse(DocumentBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

**Purpose:** Model for returning document data from API endpoints.

**Characteristics:**
- Inherits all fields from `DocumentBase`
- Adds system-generated fields: `id`, `created_at`, `updated_at`
- Used for GET, POST, PUT response bodies
- `Config.from_attributes = True` enables ORM-style object creation

**Additional Fields:**

#### `id`
- **Type:** `str` (UUID)
- **Purpose:** Unique document identifier
- **Example:** `"a1b2c3d4-e5f6-7890-abcd-ef1234567890"`

#### `created_at` 
- **Type:** `datetime`
- **Purpose:** Document creation timestamp (UTC)
- **Example:** `"2024-01-15T10:30:00Z"`

#### `updated_at`
- **Type:** `datetime` 
- **Purpose:** Last modification timestamp (UTC)
- **Example:** `"2024-01-15T15:45:30Z"`

**Usage Examples:**
```python
# Service layer returns this model
async def create_document(self, document: DocumentCreate) -> DocumentResponse:
    doc_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    doc_data = document.dict()
    doc_data.update({
        'id': doc_id,
        'created_at': now,
        'updated_at': now
    })
    
    # Store in Elasticsearch...
    return DocumentResponse(**doc_data)
```

**JSON Response Example:**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Mars Rover Discoveries",
  "body": "Recent findings from the Mars rover mission...",
  "category": "sci.space",
  "tags": ["mars", "space", "geology"],
  "author": "space_researcher",
  "source_url": "https://nasa.gov/mars-update",
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

## Specialized Response Models

### SearchResponse
```python
class SearchResponse(BaseModel):
    total_hits: int
    max_score: Optional[float]
    took_ms: int
    documents: List[DocumentResponse]
```

**Purpose:** Response model for search operations with metadata.

**Field Specifications:**

#### `total_hits`
- **Type:** `int`
- **Purpose:** Total number of matching documents (beyond current page)
- **Example:** `1247` (even if only 10 returned)

#### `max_score`
- **Type:** `Optional[float]`
- **Purpose:** Highest Elasticsearch relevance score in results
- **Example:** `8.234567` or `None` for non-scored queries

#### `took_ms`
- **Type:** `int`
- **Purpose:** Elasticsearch query execution time in milliseconds
- **Example:** `23` (query took 23ms)

#### `documents`
- **Type:** `List[DocumentResponse]`
- **Purpose:** Array of matching documents for current page
- **Example:** List of 0-100 DocumentResponse objects

**Usage Example:**
```python
# Search endpoint returns this model
@router.get("/", response_model=SearchResponse)
async def search_documents(q: str = None, limit: int = 10):
    result = await service.search_documents(query=q, limit=limit)
    return result  # Already a SearchResponse object
```

**JSON Response Example:**
```json
{
  "total_hits": 1247,
  "max_score": 8.234567,
  "took_ms": 23,
  "documents": [
    {
      "id": "doc1-uuid",
      "title": "Machine Learning in Space",
      "body": "AI applications for space exploration...",
      "category": "sci.space",
      "tags": ["ai", "space", "ml"],
      "author": "space_ai_researcher",
      "source_url": null,
      "status": "active", 
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
    // ... more documents
  ]
}
```

---

### BulkOperationResponse  
```python
class BulkOperationResponse(BaseModel):
    success_count: int
    error_count: int
    errors: List[str]
```

**Purpose:** Response model for bulk document creation operations.

**Field Specifications:**

#### `success_count`
- **Type:** `int` 
- **Purpose:** Number of successfully created documents
- **Example:** `15` (15 out of 17 documents created successfully)

#### `error_count`
- **Type:** `int`
- **Purpose:** Number of documents that failed to create
- **Example:** `2` (2 documents had errors)

#### `errors`
- **Type:** `List[str]`
- **Purpose:** Array of error messages for failed documents
- **Example:** `["Document too large", "Invalid category"]`

**Usage Example:**
```python
# Bulk creation endpoint returns this model
@router.post("/bulk", response_model=BulkOperationResponse)
async def bulk_create_documents(documents: List[DocumentCreate]):
    result = await service.bulk_create_documents(documents)
    return BulkOperationResponse(**result)
```

**JSON Response Example:**
```json
{
  "success_count": 15,
  "error_count": 2,
  "errors": [
    "Document validation failed: title too long",
    "Elasticsearch indexing error: connection timeout"
  ]
}
```

---

## Validation Examples

### Field Validation
```python
from pydantic import ValidationError
from app.models import DocumentCreate, NewsCategory

# Valid document
try:
    valid_doc = DocumentCreate(
        title="Valid Title",
        body="Valid body content with sufficient length",
        category=NewsCategory.SCI_SPACE
    )
    print("✅ Document created successfully")
except ValidationError as e:
    print(f"❌ Validation error: {e}")

# Invalid document (title too long)
try:
    invalid_doc = DocumentCreate(
        title="x" * 501,  # Exceeds 500 character limit
        body="Valid body",
        category=NewsCategory.SCI_SPACE
    )
except ValidationError as e:
    print(f"❌ Title too long: {e}")

# Invalid document (empty body)
try:
    invalid_doc = DocumentCreate(
        title="Valid Title",
        body="",  # Empty body not allowed
        category=NewsCategory.SCI_SPACE  
    )
except ValidationError as e:
    print(f"❌ Empty body: {e}")

# Invalid category
try:
    invalid_doc = DocumentCreate(
        title="Valid Title", 
        body="Valid body",
        category="invalid.category"  # Not a valid NewsCategory
    )
except ValidationError as e:
    print(f"❌ Invalid category: {e}")
```

### API Validation Integration
```python
# FastAPI automatically validates using these models
@router.post("/", response_model=DocumentResponse)
async def create_document(document: DocumentCreate):
    # DocumentCreate validation happens automatically
    # Invalid data returns 422 Unprocessable Entity
    return await service.create_document(document)

# Example validation error response (422):
{
  "detail": [
    {
      "loc": ["title"], 
      "msg": "ensure this value has at most 500 characters",
      "type": "value_error.any_str.max_length",
      "ctx": {"limit_value": 500}
    }
  ]
}
```

---

## Model Usage Patterns

### Service Layer Integration
```python
class ElasticsearchService:
    async def create_document(self, document: DocumentCreate) -> DocumentResponse:
        # Convert Pydantic model to dict
        doc_data = document.dict()
        
        # Add system fields  
        doc_data.update({
            'id': str(uuid.uuid4()),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        
        # Store in Elasticsearch...
        
        # Return as DocumentResponse
        return DocumentResponse(**doc_data)
```

### Data Transformation
```python
# Converting between models
def update_to_response(existing: DocumentResponse, update: DocumentUpdate) -> DocumentResponse:
    # Get existing data
    doc_data = existing.dict()
    
    # Apply updates (only non-None fields)
    for field, value in update.dict().items():
        if value is not None:
            doc_data[field] = value
    
    # Update timestamp
    doc_data['updated_at'] = datetime.utcnow()
    
    return DocumentResponse(**doc_data)
```

### Bulk Operations
```python
def process_bulk_data(raw_data: List[dict]) -> List[DocumentCreate]:
    """Convert raw data to validated DocumentCreate models"""
    documents = []
    
    for item in raw_data:
        try:
            doc = DocumentCreate(**item)
            documents.append(doc)
        except ValidationError as e:
            logger.warning(f"Skipping invalid document: {e}")
    
    return documents
```

---

## Integration with FastAPI

### Automatic API Documentation
These Pydantic models automatically generate:
- **OpenAPI schema** at `/openapi.json`
- **Swagger UI** at `/docs`
- **ReDoc** at `/redoc`

### Request/Response Examples
FastAPI uses these models to provide:
- Request body examples in Swagger UI
- Response schema documentation  
- Automatic validation error messages
- Type hints for client code generation

### Model Configuration
```python
class DocumentResponse(DocumentBase):
    # ... fields ...
    
    class Config:
        from_attributes = True  # Enable ORM mode
        json_encoders = {       # Custom JSON encoding
            datetime: lambda v: v.isoformat() + 'Z'
        }
        schema_extra = {        # Additional schema info
            "example": {
                "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "title": "Example Document",
                "body": "This is example content...",
                "category": "sci.space",
                "tags": ["example", "demo"],
                "author": "demo_user", 
                "status": "active",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }
```

This comprehensive model system provides type safety, validation, documentation, and seamless integration with both the API layer and the data storage layer.