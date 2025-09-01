# Analytics Router (`analytics.py`)

## Purpose
Provides statistical and analytical information about the document collection in Elasticsearch.

## Overview
This router handles requests for collection statistics, document counts, and category breakdowns. It's designed for dashboards, monitoring, and data analysis purposes.

---

## Dependencies & Imports

```python
import logging
from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_es_service
from app.models import DocumentStatus, NewsCategory
from app.services.elasticsearch_service import ElasticsearchService
```

### Key Components:
- **FastAPI Router**: Handles HTTP routing
- **Dependency Injection**: Gets Elasticsearch service instance
- **Models**: Uses enum types for consistent filtering
- **Logging**: For operation tracking

---

## Router Setup

```python
logger = logging.getLogger(__name__)
router = APIRouter()
```

- Creates module-specific logger for tracking analytics operations
- Router instance that will be included in main app with `/analytics` prefix

---

# Endpoint Documentation

## 1. Get Analytics Stats

### Endpoint Definition
```python
@router.get("/stats")
async def get_analytics_stats(
    service: ElasticsearchService = Depends(get_es_service)
):
```

### Purpose
Provides a quick overview of the document collection with key metrics.

### URL
`GET /analytics/stats`

### Parameters
None - uses dependency injection to get Elasticsearch service.

### Response Structure
```json
{
  "total_documents": 1523,
  "sample_categories": {
    "sci.space": 87,
    "comp.graphics": 156,
    "rec.sport.baseball": 92,
    "talk.politics.misc": 134,
    "sci.med": 78
  },
  "statuses": {
    "active": 1498,
    "archived": 23,
    "draft": 2
  },
  "note": "sample_categories shows only a subset of all available categories"
}
```

### Implementation Logic

#### 1. Total Documents Count
```python
total_docs = await service.search_documents(limit=0)
```
- Calls search with `limit=0` to get only the count, not actual documents
- Efficient way to get total without transferring data

#### 2. Sample Categories Analysis
```python
sample_categories = [
    NewsCategory.SCI_SPACE,
    NewsCategory.COMP_GRAPHICS, 
    NewsCategory.REC_SPORT_BASEBALL,
    NewsCategory.TALK_POLITICS_MISC,
    NewsCategory.SCI_MED
]

categories = {}
for category in sample_categories:
    cat_result = await service.search_documents(category=category.value, limit=0)
    categories[category.value] = cat_result.total_hits
```

**Why Sample Categories?**
- Querying all 20 categories would be 20 separate Elasticsearch queries
- This endpoint prioritizes speed over completeness
- Shows representative categories from different domains (science, computers, sports, politics)

#### 3. Status Breakdown
```python
statuses = {}
for status in DocumentStatus:
    status_result = await service.search_documents(status=status.value, limit=0)
    statuses[status.value] = status_result.total_hits
```
- Iterates through all possible document statuses (active, archived, draft)
- Provides insight into document lifecycle distribution

### Error Handling
```python
except Exception as e:
    logger.error(f"Failed to get analytics: {e}")
    raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")
```

### Usage Examples

#### cURL Request
```bash
curl -X GET "http://localhost:8182/analytics/stats"
```

#### Python Request
```python
import requests

response = requests.get("http://localhost:8182/analytics/stats")
data = response.json()

print(f"Total documents: {data['total_documents']}")
print(f"Active documents: {data['statuses']['active']}")
print(f"Space articles: {data['sample_categories']['sci.space']}")
```

#### Response Analysis
```python
def analyze_stats(stats):
    total = stats['total_documents']
    active_pct = (stats['statuses']['active'] / total) * 100
    
    print(f"Collection health: {active_pct:.1f}% active documents")
    
    # Find most popular sample category
    popular_cat = max(stats['sample_categories'].items(), key=lambda x: x[1])
    print(f"Most popular sample category: {popular_cat[0]} ({popular_cat[1]} docs)")
```

---

## 2. Get Category Breakdown

### Endpoint Definition
```python
@router.get("/categories")
async def get_category_breakdown(
    service: ElasticsearchService = Depends(get_es_service)
):
```

### Purpose
Provides complete document count for ALL 20 newsgroup categories.

### URL
`GET /analytics/categories`

### Parameters
None

### Response Structure
```json
{
  "categories": {
    "alt.atheism": 45,
    "comp.graphics": 156,
    "comp.os.ms-windows.misc": 89,
    "comp.sys.ibm.pc.hardware": 67,
    "comp.sys.mac.hardware": 73,
    "comp.windows.x": 82,
    "misc.forsale": 91,
    "rec.autos": 88,
    "rec.motorcycles": 85,
    "rec.sport.baseball": 92,
    "rec.sport.hockey": 87,
    "sci.crypt": 76,
    "sci.electronics": 79,
    "sci.med": 78,
    "sci.space": 87,
    "soc.religion.christian": 71,
    "talk.politics.guns": 69,
    "talk.politics.mideast": 84,
    "talk.politics.misc": 134,
    "talk.religion.misc": 63
  },
  "total_categories": 18
}
```

### Implementation Logic

#### Complete Category Enumeration
```python
categories = {}
for category in NewsCategory:
    cat_result = await service.search_documents(category=category.value, limit=0)
    categories[category.value] = cat_result.total_hits
```

**Process:**
1. Iterate through ALL `NewsCategory` enum values (all 20 categories)
2. For each category, perform a filtered search with `limit=0`
3. Extract just the `total_hits` count
4. Build comprehensive dictionary

#### Active Categories Count
```python
total_categories = len([c for c in categories.values() if c > 0])
```
- Counts only categories that actually have documents
- Useful for understanding data distribution

### Performance Considerations

**Query Cost:**
- Makes 20 separate Elasticsearch queries
- Each query is optimized (limit=0, only count)
- Total time typically < 100ms for reasonable collection sizes

**When to Use:**
- Dashboard initialization
- Data distribution analysis
- Category selection UI population

**Alternative for High Frequency:**
- Consider caching results for 5-10 minutes
- Use Elasticsearch aggregations for single-query solution

### Usage Examples

#### cURL Request
```bash
curl -X GET "http://localhost:8182/analytics/categories"
```

#### Python Analysis
```python
import requests

response = requests.get("http://localhost:8182/analytics/categories")
data = response.json()

categories = data['categories']

# Find top 5 categories by document count
top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]

print("Top 5 Categories:")
for category, count in top_categories:
    print(f"  {category}: {count} documents")

# Category family analysis
families = {}
for category, count in categories.items():
    family = category.split('.')[0]  # comp, sci, rec, etc.
    families[family] = families.get(family, 0) + count

print("\nBy Category Family:")
for family, count in sorted(families.items(), key=lambda x: x[1], reverse=True):
    print(f"  {family}.*: {count} documents")
```

#### Sample Output
```
Top 5 Categories:
  talk.politics.misc: 134 documents
  comp.graphics: 156 documents  
  rec.sport.baseball: 92 documents
  misc.forsale: 91 documents
  rec.autos: 88 documents

By Category Family:
  comp.*: 467 documents
  rec.*: 352 documents
  talk.*: 350 documents
  sci.*: 320 documents
  soc.*: 71 documents
  misc.*: 91 documents
  alt.*: 45 documents
```

---

## Error Scenarios

### 1. Elasticsearch Connection Issues
```json
{
  "detail": "Analytics failed: ConnectionTimeout: Connection timeout"
}
```

**Causes:**
- Elasticsearch service down
- Network connectivity issues
- High query load

**Status Code:** 500

### 2. Service Not Initialized
```json
{
  "detail": "Elasticsearch service not initialized. Please check application startup logs."
}
```

**Causes:**
- Application startup failure
- Dependency injection misconfiguration

**Status Code:** 500

---

## Performance Characteristics

### `/stats` Endpoint
- **Queries:** 8 (1 total + 5 categories + 3 statuses)
- **Typical Response Time:** 20-50ms
- **Data Transfer:** Minimal (counts only)
- **Use Case:** Frequent dashboard updates

### `/categories` Endpoint  
- **Queries:** 20 (one per category)
- **Typical Response Time:** 50-100ms
- **Data Transfer:** Minimal (counts only)  
- **Use Case:** Less frequent, complete analysis

---

## Integration Examples

### Dashboard Component
```javascript
// Fetch analytics data for dashboard
async function loadDashboard() {
    try {
        const [stats, categories] = await Promise.all([
            fetch('/analytics/stats').then(r => r.json()),
            fetch('/analytics/categories').then(r => r.json())
        ]);
        
        updateStatsWidget(stats);
        updateCategoryChart(categories);
    } catch (error) {
        console.error('Failed to load analytics:', error);
    }
}
```

### Monitoring Alert
```python
import requests
import time

def check_collection_health():
    try:
        response = requests.get("http://localhost:8182/analytics/stats")
        stats = response.json()
        
        total_docs = stats['total_documents']
        active_pct = (stats['statuses']['active'] / total_docs) * 100
        
        if active_pct < 90:
            alert(f"Warning: Only {active_pct:.1f}% documents are active")
            
        if total_docs < 100:
            alert(f"Warning: Collection size is low ({total_docs} documents)")
            
    except Exception as e:
        alert(f"Analytics health check failed: {e}")

# Run every 5 minutes
while True:
    check_collection_health()
    time.sleep(300)
```

This analytics router provides essential insights into the document collection, enabling effective monitoring and data-driven decisions about the search system.