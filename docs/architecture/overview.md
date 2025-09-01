# System Architecture Overview

This document provides a comprehensive overview of the 20 Newsgroups Search API architecture, design decisions, and technical implementation details.

---

## 🏗️ High-Level Architecture

### System Components
```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Client Applications                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │   Web App   │  │ Mobile App  │  │   CLI Tool  │  │  3rd Party  │   │
│  │  (React)    │  │  (Native)   │  │   (curl)    │  │    APIs     │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼ HTTP/HTTPS Requests
┌─────────────────────────────────────────────────────────────────────────┐
│                          API Gateway Layer                              │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  Load Balancer (nginx/ALB) + Rate Limiting + SSL Termination      │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼ Balanced Requests
┌─────────────────────────────────────────────────────────────────────────┐
│                        Application Layer                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │  FastAPI    │  │  FastAPI    │  │  FastAPI    │  │  FastAPI    │   │
│  │ Instance 1  │  │ Instance 2  │  │ Instance 3  │  │ Instance N  │   │
│  │             │  │             │  │             │  │             │   │
│  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │   │
│  │ │Routers  │ │  │ │Routers  │ │  │ │Routers  │ │  │ │Routers  │ │   │
│  │ │Services │ │  │ │Services │ │  │ │Services │ │  │ │Services │ │   │
│  │ │Models   │ │  │ │Models   │ │  │ │Models   │ │  │ │Models   │ │   │
│  │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ▼ Elasticsearch Queries
┌─────────────────────────────────────────────────────────────────────────┐
│                          Data Layer                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                  Elasticsearch Cluster                              │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │  │
│  │  │   Master    │  │   Data      │  │   Data      │                 │  │
│  │  │   Node      │  │   Node 1    │  │   Node 2    │                 │  │
│  │  │             │  │             │  │             │                 │  │
│  │  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │                 │  │
│  │  │ │Indexing │ │  │ │ Shard 1 │ │  │ │ Shard 2 │ │                 │  │
│  │  │ │Mapping  │ │  │ │Replica 1│ │  │ │Replica 2│ │                 │  │
│  │  │ │Search   │ │  │ │         │ │  │ │         │ │                 │  │
│  │  │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │                 │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                 │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼ External Data
┌─────────────────────────────────────────────────────────────────────────┐
│                        Data Sources                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │  scikit-    │  │   Sample    │  │   User      │  │   Future    │   │
│  │   learn     │  │    Data     │  │  Uploads    │  │  Sources    │   │
│  │20newsgroups │  │             │  │             │  │             │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Design Principles

### 1. **Separation of Concerns**
Each layer has a specific responsibility:
- **API Layer**: HTTP handling, validation, serialization
- **Service Layer**: Business logic, data processing
- **Data Layer**: Storage, indexing, search operations

### 2. **Scalability by Design**
- **Stateless API**: Each request is independent
- **Horizontal Scaling**: Multiple API instances behind load balancer
- **Elastic Search**: Distributed search with sharding and replication

### 3. **Reliability & Resilience**
- **Health Checks**: Every component monitored
- **Circuit Breaker**: Fail fast and recover gracefully
- **Retry Logic**: Automatic retry with exponential backoff

### 4. **Security First**
- **Authentication**: Service-to-service authentication
- **Rate Limiting**: Prevent abuse and DoS attacks
- **Input Validation**: All data validated at API boundary

---

## 🔧 Technology Stack

### Core Components

#### API Framework: FastAPI
```python
# Why FastAPI?
✅ High performance (Starlette + Pydantic)
✅ Automatic API documentation (OpenAPI)
✅ Type hints and validation
✅ Async/await support
✅ Dependency injection
✅ Easy testing
```

**Key Features Used:**
- **Pydantic Models**: Type-safe request/response validation
- **Dependency Injection**: Service lifecycle management
- **Async Endpoints**: Non-blocking I/O operations
- **Automatic Documentation**: Swagger UI and ReDoc
- **Background Tasks**: Long-running operations

#### Search Engine: Elasticsearch
```yaml
# Why Elasticsearch?
✅ Full-text search capabilities
✅ Distributed and scalable
✅ Rich query DSL
✅ Aggregations and analytics
✅ Real-time indexing
✅ Production-ready
```

**Key Features Used:**
- **Multi-field Search**: Title and body text search
- **Filtering**: Category, author, tags, status filters
- **Aggregations**: Document statistics and analytics
- **Bulk Operations**: Efficient batch operations
- **Index Management**: Custom mappings and settings

#### Data Processing: scikit-learn
```python
# Why scikit-learn?
✅ Standard ML library for Python
✅ Built-in 20newsgroups dataset
✅ Data preprocessing utilities
✅ Well-documented and stable
✅ Easy integration
```

---

## 📊 Data Architecture

### Document Schema
```json
{
  "id": "uuid4-string",
  "title": "string (1-500 chars)",
  "body": "string (full-text searchable)",
  "category": "newsgroup-category",
  "tags": ["array", "of", "keywords"],
  "author": "string (optional)",
  "source_url": "string (optional)",
  "status": "active|archived|draft",
  "created_at": "ISO-8601 datetime",
  "updated_at": "ISO-8601 datetime"
}
```

### Elasticsearch Index Design
```json
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1,
    "index.refresh_interval": "1s",
    "analysis": {
      "analyzer": {
        "newsgroups_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "stop", "stemmer"]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "analyzer": "newsgroups_analyzer",
        "fields": {
          "keyword": {"type": "keyword", "ignore_above": 256}
        }
      },
      "body": {
        "type": "text", 
        "analyzer": "newsgroups_analyzer"
      },
      "category": {"type": "keyword"},
      "tags": {"type": "keyword"},
      "author": {"type": "keyword"},
      "status": {"type": "keyword"},
      "created_at": {"type": "date"},
      "updated_at": {"type": "date"}
    }
  }
}
```

### Data Flow Patterns

#### Write Path (Document Creation)
```
Client Request → API Validation → Service Processing → Elasticsearch Index → Response
     │              │                    │                     │              │
     │              │                    │                     │              │
     ▼              ▼                    ▼                     ▼              ▼
POST /documents  Pydantic Model   Add timestamps/UUID    Index document   Return with ID
     │              │                    │                     │              │
     │              │                    │                     │              │
     │              │                    │              ┌─────────────┐      │
     │              │                    │              │  Refresh    │      │
     │              │                    │              │  Index      │      │
     │              │                    │              │ (Near       │      │
     │              │                    │              │ Real-time)  │      │
     │              │                    │              └─────────────┘      │
     │              │                    │                     │              │
     └──────────────┴────────────────────┴─────────────────────┴──────────────┘
```

#### Read Path (Search)
```
Search Query → Query Building → Elasticsearch Search → Result Processing → Response
     │              │                    │                     │              │
     │              │                    │                     │              │
     ▼              ▼                    ▼                     ▼              ▼
GET /search    Build ES Query    Execute search query   Format results   JSON Response
     │              │                    │                     │              │
     │        ┌─────────────┐           │              ┌─────────────┐      │
     │        │Text Search  │           │              │Pagination   │      │
     │        │Filters      │           │              │Scoring      │      │  
     │        │Pagination   │           │              │Aggregations │      │
     │        │Sorting      │           │              └─────────────┘      │
     │        └─────────────┘           │                     │              │
     └──────────┴───────────────────────┴─────────────────────┴──────────────┘
```

---

## 🏛️ Application Architecture

### Layered Architecture Pattern

#### 1. Presentation Layer (Routers)
**Location**: `app/routers/`

**Responsibilities:**
- HTTP request/response handling
- Input validation (Pydantic models)
- Authentication/authorization
- Error handling and status codes
- API documentation

**Components:**
```python
# Router structure
routers/
├── documents.py     # CRUD operations
├── search.py        # Search and filtering  
├── data.py         # Data loading operations
└── analytics.py    # Statistics and metrics
```

**Example Router Pattern:**
```python
@router.get("/search", response_model=SearchResponse)
async def search_documents(
    q: Optional[str] = None,
    category: Optional[NewsCategory] = None,
    service: ElasticsearchService = Depends(get_es_service)
):
    # Input validation handled by FastAPI + Pydantic
    # Business logic delegated to service layer
    result = await service.search_documents(query=q, category=category.value)
    return result  # Automatic serialization via Pydantic
```

#### 2. Business Logic Layer (Services)
**Location**: `app/services/`

**Responsibilities:**
- Core business logic
- Data processing and transformation
- External system integration
- Transaction coordination
- Error handling and logging

**Components:**
```python
# Service structure
services/
├── elasticsearch_service.py  # Search and CRUD operations
└── data_loader.py            # Data processing and loading
```

**Example Service Pattern:**
```python
class ElasticsearchService:
    def __init__(self, es: Elasticsearch, index_name: str):
        self.es = es
        self.index_name = index_name
    
    async def search_documents(self, query: str, **filters) -> SearchResponse:
        # Build Elasticsearch query
        search_body = self._build_search_query(query, **filters)
        
        # Execute search
        result = self.es.search(index=self.index_name, body=search_body)
        
        # Process and format results
        return self._format_search_response(result)
```

#### 3. Data Access Layer (Elasticsearch Service)
**Location**: Embedded in `services/elasticsearch_service.py`

**Responsibilities:**
- Database connection management
- Query execution
- Result set processing
- Connection pooling
- Transaction management

#### 4. Integration Layer (Dependencies)
**Location**: `app/dependencies.py`

**Responsibilities:**
- Service lifecycle management
- Dependency injection
- Configuration management
- Health monitoring

---

## 🔄 Request Lifecycle

### Complete Request Flow
```
1. HTTP Request Arrives
   ↓
2. FastAPI Routing
   ├─ URL pattern matching
   ├─ HTTP method validation
   └─ Route handler selection
   ↓
3. Dependency Injection
   ├─ get_es_service() called
   ├─ Service instance retrieved
   └─ Dependencies validated
   ↓
4. Input Validation
   ├─ Pydantic model validation
   ├─ Type checking
   └─ Business rule validation
   ↓
5. Business Logic Execution
   ├─ Service method called
   ├─ Data processing
   └─ External service calls
   ↓
6. Data Layer Operations
   ├─ Elasticsearch query building
   ├─ Query execution
   └─ Result processing
   ↓
7. Response Processing
   ├─ Data transformation
   ├─ Pydantic serialization
   └─ HTTP response formatting
   ↓
8. HTTP Response Sent
```

### Error Handling Flow
```
Error Occurs
   ↓
Exception Caught
   ├─ Service Layer: Business logic errors
   ├─ Data Layer: Connection/query errors  
   ├─ Validation Layer: Input validation errors
   └─ HTTP Layer: Request/response errors
   ↓
Error Classification
   ├─ 400: Bad Request (validation errors)
   ├─ 404: Not Found (resource missing)
   ├─ 500: Internal Server Error (system errors)
   └─ 503: Service Unavailable (downstream errors)
   ↓
Error Response
   ├─ Structured JSON error format
   ├─ Appropriate HTTP status code
   ├─ Error logging
   └─ Client-friendly error message
```

---

## 🔧 Component Interactions

### Service Dependencies
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │  Dependencies   │    │  Configuration  │
│                 │────│    Manager      │────│    Module      │
│ - Routers       │    │                 │    │                 │
│ - Middleware    │    │ - Service       │    │ - Environment   │
│ - Lifespan      │    │   Registry      │    │   Variables     │
└─────────────────┘    │ - Lifecycle     │    │ - Defaults      │
         │              │   Management    │    │ - Validation    │
         │              └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       │
┌─────────────────┐    ┌─────────────────┐              │
│    Routers      │    │    Services     │              │
│                 │    │                 │              │
│ - documents.py  │────│ - elasticsearch │              │
│ - search.py     │    │   _service.py   │              │
│ - data.py       │    │ - data_loader   │              │
│ - analytics.py  │    │   .py           │              │
└─────────────────┘    └─────────────────┘              │
                                │                       │
                                ▼                       │
                    ┌─────────────────┐                 │
                    │ External Systems│◄────────────────┘
                    │                 │
                    │ - Elasticsearch │
                    │ - scikit-learn  │
                    │ - File System   │
                    └─────────────────┘
```

### Data Transformation Pipeline
```
Raw Data → Preprocessing → Validation → Storage → Indexing → Search
    │           │             │          │          │         │
    ▼           ▼             ▼          ▼          ▼         ▼
scikit-    Text Cleaning  Pydantic   Elasticsearch Document  Full-text
learn      Email Header   Models     Index        Refresh   Search
Dataset    Extraction     Validation  Storage      Process   Results
           Tag Generation Type Safety UUID/Times   Near RT   Scoring
```

---

## 📈 Performance Architecture

### Scalability Patterns

#### 1. Horizontal Scaling
```
Load Balancer
    │
    ├─── API Instance 1 ┐
    ├─── API Instance 2 ├─── Shared Nothing Architecture
    ├─── API Instance 3 │    (Stateless)
    └─── API Instance N ┘
                │
                ▼
        Elasticsearch Cluster
        (Shared Data Layer)
```

#### 2. Caching Strategy
```
Request → Cache Check → Cache Hit? → Return Cached Result
           │              │
           │              ▼ No
           │           Business Logic
           │              │
           │              ▼
           │           Database Query
           │              │
           │              ▼
           └────────── Cache Result
                          │
                          ▼
                      Return Result
```

#### 3. Connection Pooling
```python
# Elasticsearch client connection pooling
es_client = Elasticsearch(
    hosts=["http://elasticsearch:9200"],
    maxsize=20,           # Max connections in pool
    timeout=30,           # Request timeout  
    retry_on_timeout=True # Automatic retries
)

# Single service instance across all requests
es_service = ElasticsearchService(es_client, index_name)
```

### Performance Optimizations

#### Query Optimization
```python
# Optimized search query structure
search_body = {
    "query": {
        "bool": {
            "must": [
                # Text search with field boosting
                {
                    "multi_match": {
                        "query": query,
                        "fields": ["title^2", "body"],  # Title boost 2x
                        "type": "best_fields"
                    }
                }
            ],
            "filter": [
                # Exact match filters (cached)
                {"term": {"category": category}},
                {"terms": {"tags": tags}},
                {"range": {"created_at": {"gte": "2024-01-01"}}}
            ]
        }
    },
    "from": offset,
    "size": limit,
    "sort": [{"created_at": {"order": "desc"}}],
    "_source": {
        "excludes": ["body"]  # Exclude large fields when not needed
    }
}
```

#### Index Optimization
```json
{
  "settings": {
    "refresh_interval": "30s",        // Batch refreshes for write performance
    "index.merge.policy.max_merged_segment": "5gb",
    "index.translog.flush_threshold_size": "1gb",
    "index.query.default_field": ["title^2", "body"]
  }
}
```

---

## 🛡️ Security Architecture

### Security Layers
```
1. Network Security
   ├─ HTTPS/TLS encryption
   ├─ VPC/Network isolation
   └─ Firewall rules

2. Application Security  
   ├─ Input validation (Pydantic)
   ├─ Rate limiting
   ├─ CORS configuration
   └─ Error message sanitization

3. Authentication/Authorization
   ├─ Service-to-service auth
   ├─ API key management
   └─ Role-based access (future)

4. Data Security
   ├─ Elasticsearch authentication
   ├─ Data encryption at rest
   └─ Audit logging
```

### Security Implementation
```python
# Rate limiting example
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/search")
@limiter.limit("100/minute")  # 100 requests per minute
async def search_endpoint(request: Request, ...):
    pass

# Input validation
class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)  # Length validation
    body: str = Field(..., min_length=1)                   # Required field
    category: NewsCategory                                  # Enum validation
    tags: List[str] = Field(default_factory=list)         # Type validation
```

---

## 🔍 Monitoring Architecture

### Observability Stack
```
Application Metrics → Prometheus → Grafana Dashboards
       │                 │              │
       ├─ Request Rate    │              ├─ API Performance
       ├─ Response Time   │              ├─ Error Rates  
       ├─ Error Count     │              ├─ Resource Usage
       └─ Business KPIs   │              └─ Alert Status
                          │
Application Logs → Elasticsearch → Kibana Dashboards
       │              (ELK Stack)         │
       ├─ Error Logs                     ├─ Log Analysis
       ├─ Access Logs                    ├─ Error Tracking
       ├─ Audit Logs                     └─ Search Analytics
       └─ Debug Logs
                          
Health Checks → Alerting System → Notifications
       │              │                 │
       ├─ API Health   │                ├─ PagerDuty
       ├─ DB Health    │                ├─ Slack
       └─ Deps Health  │                └─ Email
```

### Key Metrics
```python
# Application metrics
- newsgroups_requests_total{method, endpoint, status}
- newsgroups_request_duration_seconds{method, endpoint}
- newsgroups_active_connections
- newsgroups_documents_total
- newsgroups_search_queries_total
- newsgroups_elasticsearch_health

# System metrics  
- container_cpu_usage_seconds_total
- container_memory_usage_bytes
- container_network_receive_bytes_total
- container_fs_usage_bytes
```

---

## 🔄 Deployment Architecture

### Container Strategy
```
Base Image: python:3.13-slim
    │
    ├─ Security: Non-root user (appuser)
    ├─ Dependencies: Pinned versions (requirements.txt)
    ├─ Application: /code/app/
    └─ Runtime: uvicorn ASGI server

Multi-stage builds for optimization:
    │
    ├─ Build stage: Install dependencies, compile code
    └─ Runtime stage: Copy artifacts, minimal runtime
```

### Orchestration Options
```
Development:
    └─ Docker Compose (single machine)

Staging/Production:
    ├─ Docker Swarm (simple orchestration)
    ├─ Kubernetes (full orchestration)
    └─ Cloud Services (ECS, GKE, AKS)
```

---

## 🚀 Future Architecture Considerations

### Planned Enhancements
1. **Microservices Split**: Separate search, analytics, and data loading services
2. **Caching Layer**: Redis for frequent queries and session management  
3. **Message Queue**: Asynchronous processing with RabbitMQ/Apache Kafka
4. **API Gateway**: Centralized routing, authentication, and rate limiting
5. **GraphQL**: More flexible data fetching for complex client needs

### Scalability Roadmap
```
Phase 1 (Current): Monolithic FastAPI + Elasticsearch
    └─ Single service, multiple instances

Phase 2: Service Separation
    ├─ Search Service
    ├─ Analytics Service  
    └─ Data Management Service

Phase 3: Event-Driven Architecture  
    ├─ Message Queues
    ├─ Event Sourcing
    └─ CQRS Pattern

Phase 4: Cloud-Native
    ├─ Service Mesh (Istio)
    ├─ Serverless Functions
    └─ Managed Services
```

This architecture provides a solid foundation that can evolve from a simple deployment to a complex, distributed system as requirements grow. The key is maintaining clean interfaces between layers and designing for change from the beginning. 🏗️