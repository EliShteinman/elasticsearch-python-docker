# Data Router (`data.py`)

## Purpose
Manages data loading operations from external sources into the Elasticsearch index. Handles both real 20newsgroups dataset from scikit-learn and sample data for testing.

## Overview
This router provides endpoints for populating the document collection with data. All loading operations run as background tasks to prevent HTTP timeout issues and allow for responsive API behavior during large data loads.

---

## Dependencies & Imports

```python
import logging
from typing import List, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query

from app.dependencies import get_es_service
from app.models import DocumentCreate
from app.services.data_loader import NewsDataLoader
from app.services.elasticsearch_service import ElasticsearchService
```

### Key Components:
- **BackgroundTasks**: FastAPI's background task system for async operations
- **Query Parameters**: Advanced parameter validation and documentation
- **NewsDataLoader**: Service for loading and processing 20newsgroups data
- **DocumentCreate**: Pydantic model for document validation

---

## Router Setup

```python
logger = logging.getLogger(__name__)
router = APIRouter()
```

- Module-specific logger for tracking data loading operations
- Router instance included in main app with `/data` prefix

---

# Endpoint Documentation

## 1. Load 20 Newsgroups Data

### Endpoint Definition
```python
@router.post("/load-20newsgroups")
async def load_20newsgroups_data(
    background_tasks: BackgroundTasks,
    subset: str = Query("train", description="Dataset subset: train, test, or all"),
    max_documents: int = Query(1000, ge=1, le=5000, description="Maximum documents to load"),
    categories: Optional[List[str]] = Query(None, description="Specific categories to load"),
    service: ElasticsearchService = Depends(get_es_service)
):
```

### Purpose
Loads real newsgroup posts from scikit-learn's 20newsgroups dataset into Elasticsearch.

### URL
`POST /data/load-20newsgroups`

### Parameters

#### Query Parameters
- **`subset`** (string, default: "train")
  - **Options**: "train", "test", "all"
  - **Description**: Which portion of the dataset to load
  - **Train**: ~11,314 documents (training set)
  - **Test**: ~7,532 documents (test set)  
  - **All**: ~18,846 documents (combined)

- **`max_documents`** (integer, range: 1-5000, default: 1000)
  - **Purpose**: Limits the number of documents loaded
  - **Validation**: Must be between 1 and 5000 to prevent system overload
  - **Recommended**: Start with 500-1000 for testing

- **`categories`** (List[string], optional)
  - **Purpose**: Load only specific newsgroup categories
  - **Format**: List of category names
  - **Example**: `["sci.space", "comp.graphics", "rec.sport.baseball"]`
  - **Default**: `None` (loads all 20 categories)

### Background Task Implementation

The actual loading happens in a background task to prevent HTTP timeouts:

```python
async def load_newsgroups_data():
    try:
        # 1. Load data from scikit-learn
        newsgroups_data = NewsDataLoader.load_20newsgroups_data(
            subset=subset,
            categories=categories,
            max_documents=max_documents
        )

        if newsgroups_data:
            # 2. Convert to Pydantic models for validation
            documents = [DocumentCreate(**doc) for doc in newsgroups_data]
            
            # 3. Bulk insert into Elasticsearch
            result = await service.bulk_create_documents(documents)
            
            logger.info(f"20newsgroups data loaded: {result['success_count']} documents")
        else:
            logger.warning("No 20newsgroups data retrieved")
            
    except Exception as e:
        logger.error(f"Failed to load 20newsgroups data: {e}")

background_tasks.add_task(load_newsgroups_data)
```

### Response Structure
```json
{
  "message": "20newsgroups data loading started (subset: train, max: 1000)",
  "note": "scikit-learn is required for this operation"
}
```

### Data Processing Pipeline

#### Step 1: scikit-learn Data Retrieval
```python
from sklearn.datasets import fetch_20newsgroups

newsgroups = fetch_20newsgroups(
    subset='train',
    categories=['sci.space', 'comp.graphics'],
    remove=('headers', 'footers', 'quotes'),
    shuffle=True,
    random_state=42
)
```

#### Step 2: Text Processing
For each raw document:
1. **Header Extraction**: Parse email headers for subject and author
2. **Text Cleaning**: Remove quoted text, headers, excessive whitespace
3. **Tag Generation**: Create tags based on category
4. **Validation**: Ensure minimum content length (50+ characters)

#### Step 3: Document Structure
Each processed document becomes:
```python
{
    'title': 'Extracted or generated title',
    'body': 'Cleaned text content', 
    'category': 'sci.space',
    'author': 'username or "Anonymous"',
    'tags': ['sci-space', 'science'],
    'status': 'active'
}
```

#### Step 4: Bulk Elasticsearch Insertion
- Convert to `DocumentCreate` Pydantic models
- Validate all data
- Use Elasticsearch bulk API for efficiency
- Generate UUIDs and timestamps

### Usage Examples

#### Basic Load (Default Parameters)
```bash
curl -X POST "http://localhost:8182/data/load-20newsgroups"
```
- Loads 1000 training documents
- All categories included

#### Specific Categories Load
```bash
curl -X POST "http://localhost:8182/data/load-20newsgroups?categories=sci.space&categories=comp.graphics&categories=rec.sport.baseball&max_documents=500"
```

#### Large Dataset Load
```bash
curl -X POST "http://localhost:8182/data/load-20newsgroups?subset=all&max_documents=5000"
```

#### Python API Call
```python
import requests

response = requests.post(
    "http://localhost:8182/data/load-20newsgroups",
    params={
        "subset": "train",
        "max_documents": 2000,
        "categories": ["sci.space", "sci.med", "comp.graphics"]
    }
)

print(response.json())
# {"message": "20newsgroups data loading started (subset: train, max: 2000)", ...}
```

### Monitoring Load Progress

Since loading happens in background, monitor via:

#### 1. Application Logs
```bash
docker-compose logs -f newsgroups | grep "20newsgroups"
```

Look for:
- `"20newsgroups data loading started"`
- `"Loaded X documents from 20newsgroups"`
- `"20newsgroups data loaded: X documents"`

#### 2. Document Count Check
```bash
# Before loading
curl "http://localhost:8182/analytics/stats"

# Wait a few minutes, then check again
curl "http://localhost:8182/analytics/stats"
```

#### 3. Search Test
```bash
# Test if new documents are searchable
curl "http://localhost:8182/search?q=space&limit=5"
```

---

## 2. Load Sample Data

### Endpoint Definition
```python
@router.post("/load-sample")
async def load_sample_data(
    background_tasks: BackgroundTasks,
    service: ElasticsearchService = Depends(get_es_service)
):
```

### Purpose
Loads a small set (5 documents) of hand-crafted sample data for testing and development.

### URL
`POST /data/load-sample`

### Parameters
None - uses dependency injection only.

### Background Task Implementation
```python
async def load_data():
    try:
        # Get predefined sample data
        sample_data = NewsDataLoader.load_sample_data()
        
        # Convert and validate
        documents = [DocumentCreate(**doc) for doc in sample_data]
        
        # Bulk create
        result = await service.bulk_create_documents(documents)
        
        logger.info(f"Sample data loaded: {result['success_count']} documents")
    except Exception as e:
        logger.error(f"Failed to load sample data: {e}")

background_tasks.add_task(load_data)
```

### Response Structure
```json
{
  "message": "Sample data loading started in background"
}
```

### Sample Data Content
The sample dataset includes 5 diverse documents:

1. **Computer Graphics** (`comp.graphics`)
   - Advanced rendering techniques
   - Tags: ['comp-graphics', 'computer', 'rendering']

2. **Space Science** (`sci.space`)
   - Mars rover discoveries
   - Tags: ['sci-space', 'science', 'mars']

3. **Baseball Sports** (`rec.sport.baseball`)
   - World Series analysis
   - Tags: ['rec-sport-baseball', 'recreation', 'statistics']

4. **Cryptography** (`sci.crypt`)
   - Quantum cryptography breakthrough
   - Tags: ['sci-crypt', 'science', 'quantum']

5. **Automotive** (`rec.autos`)
   - Electric vehicle trends
   - Tags: ['rec-autos', 'recreation', 'electric']

### Usage Examples

#### cURL Request
```bash
curl -X POST "http://localhost:8182/data/load-sample"
```

#### Python Request
```python
import requests
import time

# Load sample data
response = requests.post("http://localhost:8182/data/load-sample")
print(response.json())

# Wait for background task
time.sleep(2)

# Verify loading
stats = requests.get("http://localhost:8182/analytics/stats").json()
print(f"Total documents now: {stats['total_documents']}")
```

#### When to Use Sample Data
- **Initial testing**: Quick way to populate empty index
- **Development**: Predictable data for feature testing
- **Demos**: Clean, well-formatted content for presentations
- **CI/CD**: Fast data setup for automated tests

---

## Error Scenarios

### 1. scikit-learn Not Installed
**Endpoint**: `/load-20newsgroups`

```json
{
  "message": "20newsgroups data loading started (subset: train, max: 1000)",
  "note": "scikit-learn is required for this operation"
}
```

**Background task logs:**
```
ERROR - Failed to load 20newsgroups data: scikit-learn is required to load 20newsgroups dataset. Install with: pip install scikit-learn
```

**Resolution**: scikit-learn should be in requirements.txt

### 2. Invalid Category Names
**Request:**
```bash
curl -X POST "http://localhost:8182/data/load-20newsgroups?categories=invalid.category"
```

**Background task behavior**: scikit-learn will ignore invalid categories, potentially loading no data.

### 3. Elasticsearch Connection Issues
**Response**: Normal HTTP 200 (background task queued)
**Background logs**:
```
ERROR - Failed to load 20newsgroups data: ConnectionTimeout: Connection timeout
```

### 4. Bulk Insert Failures
**Background logs**:
```
ERROR - Failed to load 20newsgroups data: BulkIndexError: ('N errors occurred during bulk operation', ['Document too large', ...])
```

---

## Performance Characteristics

### `/load-20newsgroups` Performance

**Data Processing Time:**
- 100 docs: ~2-5 seconds
- 1000 docs: ~10-30 seconds  
- 5000 docs: ~60-180 seconds

**Factors Affecting Speed:**
- Document size (average: 1-3KB per document)
- Text processing complexity
- Elasticsearch bulk insert performance
- System resources

**Memory Usage:**
- Peak: ~2-5MB per 1000 documents
- Processing is streaming-friendly

### `/load-sample` Performance
- **Processing Time**: <1 second
- **Memory Usage**: <1MB
- **Documents**: 5 fixed documents

---

## Best Practices

### 1. Gradual Loading Strategy
```bash
# Start small for testing
curl -X POST "http://localhost:8182/data/load-20newsgroups?max_documents=100"

# Increase gradually 
curl -X POST "http://localhost:8182/data/load-20newsgroups?max_documents=500"

# Full load only when confident
curl -X POST "http://localhost:8182/data/load-20newsgroups?max_documents=5000"
```

### 2. Category-Specific Loading
```bash
# Load science categories first
curl -X POST "http://localhost:8182/data/load-20newsgroups?categories=sci.space&categories=sci.med&categories=sci.crypt"

# Then computer categories
curl -X POST "http://localhost:8182/data/load-20newsgroups?categories=comp.graphics&categories=comp.sys.mac.hardware"
```

### 3. Monitor During Large Loads
```python
import requests
import time

def monitor_loading():
    initial_count = requests.get("http://localhost:8182/analytics/stats").json()['total_documents']
    
    # Start loading
    requests.post("http://localhost:8182/data/load-20newsgroups?max_documents=2000")
    
    # Monitor progress
    while True:
        time.sleep(10)
        current_count = requests.get("http://localhost:8182/analytics/stats").json()['total_documents']
        new_docs = current_count - initial_count
        
        print(f"Progress: +{new_docs} documents loaded")
        
        if new_docs >= 2000:  # Expected load amount
            break
```

---

## Integration Examples

### Automated Data Refresh
```python
import requests
import schedule
import time

def refresh_data():
    """Weekly data refresh with latest scikit-learn data"""
    
    # Clear old sample data (if needed)
    # Load fresh training data
    response = requests.post(
        "http://localhost:8182/data/load-20newsgroups",
        params={"subset": "train", "max_documents": 1000}
    )
    
    print(f"Data refresh initiated: {response.json()['message']}")

# Schedule weekly refresh
schedule.every().monday.at("02:00").do(refresh_data)

while True:
    schedule.run_pending()
    time.sleep(3600)  # Check every hour
```

### Development Environment Setup
```python
import requests
import time

def setup_dev_environment():
    """Initialize development environment with sample data"""
    
    # Load sample data first
    requests.post("http://localhost:8182/data/load-sample")
    time.sleep(2)
    
    # Add some real data for variety
    requests.post(
        "http://localhost:8182/data/load-20newsgroups", 
        params={
            "max_documents": 100,
            "categories": ["comp.graphics", "sci.space"]
        }
    )
    
    print("Development environment ready!")

if __name__ == "__main__":
    setup_dev_environment()
```

This data router enables flexible and efficient population of the document collection, supporting both quick testing scenarios and production-scale data loading.