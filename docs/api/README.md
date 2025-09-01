# API Overview - 20 Newsgroups Search API

Welcome to the 20 Newsgroups Search API! This RESTful API provides powerful search and document management capabilities for the classic 20 newsgroups dataset.

---

## 🚀 Quick Start

### Base URL
```
Development: http://localhost:8182
Production:  https://api.newsgroups.example.com
```

### Authentication
Currently, no authentication is required for development. Production deployments should implement proper authentication.

### API Versioning
Current version: **v2.0.0**
- Version is included in response headers
- Breaking changes will increment major version

---

## 📊 API Overview

### Core Capabilities
- **🔍 Full-text Search**: Search across document titles and content
- **📄 Document Management**: Complete CRUD operations
- **📈 Analytics**: Statistics and insights about the collection
- **💾 Data Loading**: Import data from scikit-learn or custom sources
- **🏷️ Rich Filtering**: Filter by category, author, tags, status

### Supported Operations
| Operation | Endpoint | Description |
|-----------|----------|-------------|
| Search | `GET /search` | Multi-field search with filtering |
| List Categories | `GET /search/categories` | Available newsgroup categories |
| Get Document | `GET /documents/{id}` | Retrieve document by ID |
| Create Document | `POST /documents/` | Create new document |
| Update Document | `PUT /documents/{id}` | Update existing document |
| Delete Document | `DELETE /documents/{id}` | Remove document |
| Bulk Create | `POST /documents/bulk` | Create multiple documents |
| Analytics | `GET /analytics/stats` | Collection statistics |
| Category Stats | `GET /analytics/categories` | Document count per category |
| Load Data | `POST /data/load-20newsgroups` | Load real dataset |
| Load Samples | `POST /data/load-sample` | Load sample data |

---

## 🔍 Search Capabilities

### Basic Search
```bash
# Simple text search
curl "http://localhost:8182/search?q=machine learning"

# Search with pagination
curl "http://localhost:8182/search?q=neural networks&limit=20&offset=40"
```

### Advanced Filtering
```bash
# Filter by category
curl "http://localhost:8182/search?category=sci.space&limit=10"

# Multi-filter search
curl "http://localhost:8182/search?q=graphics&category=comp.graphics&author=researcher&status=active"

# Tag-based filtering
curl "http://localhost:8182/search?tags=ai&tags=research&limit=15"
```

### Search Response Format
```json
{
  "total_hits": 1247,
  "max_score": 8.234567,
  "took_ms": 23,
  "documents": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "title": "Machine Learning Discussion",
      "body": "Recent advances in neural networks...",
      "category": "comp.graphics",
      "tags": ["ai", "ml", "neural-networks"],
      "author": "researcher",
      "status": "active",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

## 📄 Document Management

### Document Schema
```json
{
  "id": "uuid4-string",
  "title": "string (1-500 characters, required)",
  "body": "string (required)",
  "category": "newsgroup-category (required)",
  "tags": ["optional", "array", "of", "strings"],
  "author": "optional-string",
  "source_url": "optional-url",
  "status": "active|archived|draft (default: active)",
  "created_at": "iso-8601-datetime (auto-generated)",
  "updated_at": "iso-8601-datetime (auto-generated)"
}
```

### CRUD Operations

#### Create Document
```bash
curl -X POST "http://localhost:8182/documents/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Research Paper",
    "body": "This paper discusses recent advances in...",
    "category": "sci.med",
    "author": "dr_researcher",
    "tags": ["medical", "research", "ai"],
    "status": "active"
  }'
```

#### Get Document
```bash
curl "http://localhost:8182/documents/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

#### Update Document
```bash
curl -X PUT "http://localhost:8182/documents/a1b2c3d4-e5f6-7890-abcd-ef1234567890" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Research Paper",
    "tags": ["medical", "research", "ai", "updated"]
  }'
```

#### Delete Document
```bash
curl -X DELETE "http://localhost:8182/documents/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

### Bulk Operations
```bash
curl -X POST "http://localhost:8182/documents/bulk" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "title": "Document 1",
      "body": "Content for first document...",
      "category": "comp.graphics"
    },
    {
      "title": "Document 2", 
      "body": "Content for second document...",
      "category": "sci.space"
    }
  ]'
```

---

## 📈 Analytics & Insights

### Collection Statistics
```bash
# Get overall statistics
curl "http://localhost:8182/analytics/stats"
```

**Response:**
```json
{
  "total_documents": 1523,
  "sample_categories": {
    "sci.space": 87,
    "comp.graphics": 156,
    "rec.sport.baseball": 92
  },
  "statuses": {
    "active": 1498,
    "archived": 23,
    "draft": 2
  },
  "note": "sample_categories shows only a subset of all available categories"
}
```

### Category Breakdown
```bash
# Get complete category statistics
curl "http://localhost:8182/analytics/categories"
```

**Response:**
```json
{
  "categories": {
    "alt.atheism": 45,
    "comp.graphics": 156,
    "comp.os.ms-windows.misc": 89,
    "sci.space": 87,
    "talk.politics.misc": 134
  },
  "total_categories": 18
}
```

---

## 💾 Data Management

### Load Real Dataset
```bash
# Load 1000 training documents
curl -X POST "http://localhost:8182/data/load-20newsgroups?subset=train&max_documents=1000"

# Load specific categories
curl -X POST "http://localhost:8182/data/load-20newsgroups?categories=sci.space&categories=comp.graphics&max_documents=500"
```

### Load Sample Data
```bash
# Load 5 sample documents for testing
curl -X POST "http://localhost:8182/data/load-sample"
```

---

## 🏷️ Data Categories

### 20 Newsgroups Categories
The API supports all 20 original newsgroup categories:

#### Computer (`comp.*`)
- `comp.graphics` - Computer graphics and visualization
- `comp.os.ms-windows.misc` - Microsoft Windows
- `comp.sys.ibm.pc.hardware` - IBM PC hardware
- `comp.sys.mac.hardware` - Macintosh hardware
- `comp.windows.x` - X Window System

#### Recreation (`rec.*`)
- `rec.autos` - Automobiles
- `rec.motorcycles` - Motorcycles
- `rec.sport.baseball` - Baseball
- `rec.sport.hockey` - Hockey

#### Science (`sci.*`)
- `sci.crypt` - Cryptography
- `sci.electronics` - Electronics
- `sci.med` - Medicine
- `sci.space` - Space and astronomy

#### Talk (`talk.*`)
- `talk.politics.guns` - Gun politics
- `talk.politics.mideast` - Middle East politics
- `talk.politics.misc` - General politics
- `talk.religion.misc` - Religion

#### Society (`soc.*`)
- `soc.religion.christian` - Christianity

#### Alternative (`alt.*`)
- `alt.atheism` - Atheism

#### Miscellaneous (`misc.*`)
- `misc.forsale` - Items for sale

---

## 🔍 Query Parameters Reference

### Search Parameters
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `q` | string | Text query across title and body | `q=machine learning` |
| `category` | enum | Exact category match | `category=sci.space` |
| `tags` | array | Must have ALL specified tags | `tags=ai&tags=research` |
| `author` | string | Exact author match | `author=researcher` |
| `status` | enum | Document status filter | `status=active` |
| `limit` | integer | Max results (1-100) | `limit=25` |
| `offset` | integer | Pagination offset | `offset=50` |

### Data Loading Parameters
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `subset` | string | Dataset portion (train/test/all) | `subset=train` |
| `max_documents` | integer | Max documents to load (1-5000) | `max_documents=1000` |
| `categories` | array | Specific categories to load | `categories=sci.space` |

---

## 📊 Response Formats

### Standard Response Structure
All API responses follow consistent patterns:

#### Success Response (200/201)
```json
{
  "field1": "value1",
  "field2": "value2",
  "metadata": {
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

#### Error Response (400/404/500)
```json
{
  "detail": "Human-readable error message"
}
```

#### Validation Error (422)
```json
{
  "detail": [
    {
      "loc": ["field_name"],
      "msg": "validation error description",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 🚀 Performance & Limits

### Rate Limits
- **Development**: No limits
- **Production**: 100 requests/minute per IP

### Request Limits
- **Search results**: Max 100 per request
- **Bulk operations**: Max 1000 documents per request
- **Query length**: Max 1000 characters
- **Document size**: Max 10MB per document

### Performance Tips
1. **Use pagination** for large result sets
2. **Use filters** instead of text search when possible
3. **Limit fields** in responses when full document not needed
4. **Cache results** on client side when appropriate
5. **Use bulk operations** for multiple document operations

---

## 🔄 Interactive Documentation

### Swagger UI
- **URL**: `http://localhost:8182/docs`
- **Features**: Interactive API explorer, request/response examples
- **Authentication**: Try requests directly from browser

### ReDoc
- **URL**: `http://localhost:8182/redoc`
- **Features**: Clean, readable API documentation
- **Export**: Download OpenAPI specification

### OpenAPI Schema
- **URL**: `http://localhost:8182/openapi.json`
- **Use case**: Generate client libraries, import into tools

---

## 🛠️ Client Libraries

### Python Client Example
```python
import requests

class NewsGroupsAPI:
    def __init__(self, base_url="http://localhost:8182"):
        self.base_url = base_url
    
    def search(self, query=None, **filters):
        params = {"q": query} if query else {}
        params.update(filters)
        
        response = requests.get(f"{self.base_url}/search", params=params)
        return response.json()
    
    def create_document(self, doc_data):
        response = requests.post(
            f"{self.base_url}/documents/", 
            json=doc_data
        )
        return response.json()
    
    def get_stats(self):
        response = requests.get(f"{self.base_url}/analytics/stats")
        return response.json()

# Usage
api = NewsGroupsAPI()
results = api.search("machine learning", category="comp.graphics", limit=10)
```

### JavaScript Client Example
```javascript
class NewsGroupsAPI {
    constructor(baseUrl = 'http://localhost:8182') {
        this.baseUrl = baseUrl;
    }
    
    async search(query, options = {}) {
        const params = new URLSearchParams();
        if (query) params.append('q', query);
        
        Object.entries(options).forEach(([key, value]) => {
            if (Array.isArray(value)) {
                value.forEach(v => params.append(key, v));
            } else {
                params.append(key, value);
            }
        });
        
        const response = await fetch(`${this.baseUrl}/search?${params}`);
        return response.json();
    }
    
    async createDocument(docData) {
        const response = await fetch(`${this.baseUrl}/documents/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(docData)
        });
        return response.json();
    }
    
    async getStats() {
        const response = await fetch(`${this.baseUrl}/analytics/stats`);
        return response.json();
    }
}

// Usage
const api = new NewsGroupsAPI();
const results = await api.search('neural networks', { 
    category: 'comp.graphics', 
    limit: 10 
});
```

---

## 🔧 Development Tools

### Health Monitoring
```bash
# Check API health
curl "http://localhost:8182/health"

# Expected response
{
  "status": "healthy",
  "elasticsearch": "connected"
}
```

### API Testing
```bash
# Test all main endpoints
curl "http://localhost:8182/search?limit=1"
curl "http://localhost:8182/analytics/stats"  
curl "http://localhost:8182/search/categories"
curl -X POST "http://localhost:8182/data/load-sample"
```

---

## 📝 Best Practices

### API Usage Guidelines

#### 1. Efficient Querying
```bash
# Good: Use specific filters
curl "http://localhost:8182/search?category=sci.space&limit=10"

# Avoid: Overly broad searches without limits
curl "http://localhost:8182/search?q=the&limit=1000"
```

#### 2. Pagination
```bash
# Implement proper pagination for large datasets
page_size=25
offset=0

while true; do
    response=$(curl "http://localhost:8182/search?limit=${page_size}&offset=${offset}")
    # Process results
    offset=$((offset + page_size))
done
```

#### 3. Error Handling
```python
import requests
from requests.exceptions import RequestException

def safe_api_call(url, **kwargs):
    try:
        response = requests.get(url, **kwargs)
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response.json()
    except RequestException as e:
        print(f"API call failed: {e}")
        return None
```

#### 4. Bulk Operations
```bash
# Efficient: Use bulk operations for multiple documents
curl -X POST "http://localhost:8182/documents/bulk" \
  -H "Content-Type: application/json" \
  -d '[doc1, doc2, doc3, ...]'

# Inefficient: Multiple individual requests
for doc in documents; do
    curl -X POST "http://localhost:8182/documents/" -d "$doc"
done
```

---

## 🚨 Common Issues & Solutions

### 1. Empty Search Results
**Problem**: Search returns no results despite having data

**Troubleshooting:**
```bash
# Check if data exists
curl "http://localhost:8182/analytics/stats"

# Try broader search
curl "http://localhost:8182/search"  # No filters

# Check specific category
curl "http://localhost:8182/search?category=sci.space"
```

### 2. Validation Errors (422)
**Problem**: Request data doesn't match expected schema

**Example Error:**
```json
{
  "detail": [
    {
      "loc": ["category"],
      "msg": "value is not a valid enumeration member",
      "type": "type_error.enum"
    }
  ]
}
```

**Solution:**
```bash
# Check valid categories
curl "http://localhost:8182/search/categories"

# Use exact category names
curl -X POST "http://localhost:8182/documents/" \
  -d '{"category": "sci.space"}'  # Not "science" or "space"
```

### 3. Performance Issues
**Problem**: Slow API responses

**Optimization:**
```bash
# Use pagination
curl "http://localhost:8182/search?q=test&limit=10"

# Use filters to narrow results
curl "http://localhost:8182/search?category=comp.graphics&limit=10"

# Avoid complex text queries
curl "http://localhost:8182/search?tags=specific-tag"
```

---

## 🔮 Upcoming Features

### Planned API Enhancements
- **Authentication**: JWT-based authentication system
- **Advanced Analytics**: Time-based statistics, trending topics
- **Full-text Highlighting**: Search term highlighting in results
- **Faceted Search**: Dynamic filter suggestions
- **GraphQL**: Alternative query interface
- **Webhooks**: Real-time notifications for data changes
- **API Versioning**: Formal versioning strategy
- **Advanced Filtering**: Date ranges, fuzzy matching

### Beta Features (Available Soon)
- **Similarity Search**: Find documents similar to a given document
- **Auto-tagging**: ML-based automatic tag generation
- **Export Capabilities**: CSV/JSON data export
- **Advanced Sorting**: Multiple sort criteria

---

## 📚 Related Documentation

### For Developers
- **[Data Models](models.md)** - Request/response schemas and validation
- **[Endpoint Details](endpoints/)** - Detailed documentation for each endpoint
- **[Development Setup](../development/setup.md)** - Local development environment

### For Operations
- **[Production Deployment](../deployment/production.md)** - Production setup guide
- **[Monitoring](../deployment/monitoring.md)** - Observability and alerting
- **[Configuration](../configuration/environment-variables.md)** - Environment setup

### For Architecture
- **[System Overview](../architecture/overview.md)** - High-level architecture
- **[Data Flow](../architecture/data-flow.md)** - How data moves through the system

---

## 💡 Tips for Success

### Getting Started
1. **Start with health check**: Verify API is running
2. **Load sample data**: Quick way to have test data
3. **Explore with Swagger**: Interactive API documentation
4. **Try simple searches**: Build up to complex queries
5. **Monitor performance**: Use analytics to understand usage

### Production Readiness
1. **Implement error handling**: Robust client-side error handling
2. **Use connection pooling**: Reuse HTTP connections
3. **Cache results**: Cache frequent queries client-side
4. **Monitor usage**: Track API performance and errors
5. **Plan for scale**: Implement pagination and rate limiting

---

## 🆘 Getting Help

### Resources
- **Interactive Docs**: http://localhost:8182/docs
- **Health Check**: http://localhost:8182/health
- **API Status**: Check system status and uptime
- **Community**: GitHub issues and discussions

### Support Levels
- **Community**: GitHub issues and documentation
- **Developer**: Check troubleshooting guides and logs
- **Enterprise**: Dedicated support channels (when available)

---

**Ready to build something amazing? Start exploring the API! 🚀**