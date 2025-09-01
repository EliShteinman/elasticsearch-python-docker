# 20 Newsgroups Search API - Project Structure

## Overview
This document provides a comprehensive overview of the project structure, explaining the purpose and contents of each file and directory in the 20 Newsgroups Search API.

---

## Root Directory Structure

```
20newsgroups-search-api/
├── .dockerignore                    # Docker build context exclusions
├── .gitignore                       # Git version control exclusions  
├── README.md                        # Main project documentation
├── docker-compose-elasticsearch.yml # Multi-container orchestration
├── app/                            # Main application directory
│   ├── __init__.py                 # Python package marker
│   ├── Dockerfile                  # Application container definition
│   ├── requirements.txt            # Python dependencies (compiled)
│   ├── config.py                   # Application configuration
│   ├── dependencies.py             # FastAPI dependency injection
│   ├── main.py                     # Application entry point
│   ├── models.py                   # Pydantic data models
│   ├── routers/                    # API route handlers
│   │   ├── __init__.py
│   │   ├── README.md              # Routers documentation
│   │   ├── analytics.py           # Statistics endpoints
│   │   ├── analytics.md           # Analytics router docs
│   │   ├── data.py                # Data loading endpoints  
│   │   ├── data.md                # Data router docs
│   │   ├── documents.py           # CRUD endpoints
│   │   ├── documents.md           # Documents router docs
│   │   ├── search.py              # Search endpoints
│   │   └── search.md              # Search router docs
│   └── services/                   # Business logic layer
│       ├── __init__.py
│       ├── README.md              # Services documentation
│       ├── data_loader.py         # 20newsgroups data processing
│       └── elasticsearch_service.py # Elasticsearch operations
└── [Additional documentation files to be created]
```

---

## File-by-File Documentation

### Root Configuration Files

#### `.dockerignore`
**Purpose:** Specifies files and directories to exclude from Docker build context.

**Key Exclusions:**
- **Virtual environments**: `.venv/`, `env/`, `ENV/`
- **Python cache**: `__pycache__/`, `*.pyc`, `*.pyo`
- **Development files**: `.idea/`, `.vscode/`, `*.swp`
- **Build artifacts**: `dist/`, `build/`, `*.egg-info`
- **Data files**: `*.csv`, `*.sqlite`, `*.db`
- **Testing**: `tests/`, `.coverage`, `.pytest_cache/`

**Benefits:**
- Reduces Docker build context size
- Faster builds by excluding unnecessary files
- Prevents sensitive data from being copied to containers

#### `.gitignore`
**Purpose:** Defines files and patterns for Git to ignore in version control.

**Key Sections:**
- **Python artifacts**: Bytecode, distributions, virtual environments
- **IDE files**: PyCharm, VS Code, Vim temporary files
- **Jupyter Notebooks**: Checkpoints and temporary files
- **Testing**: Coverage reports, cache directories
- **OS files**: `.DS_Store`, `Thumbs.db`
- **Dependency management**: Poetry, PDM, pipenv files

**Template Sources:**
- Based on GitHub's Python `.gitignore` template
- Extended with Jupyter Notebook exclusions
- Includes modern Python tooling patterns

#### `README.md` 
**Purpose:** Main project documentation and quick start guide.

**Contents:**
- Project overview and features
- Quick start instructions
- API endpoint reference
- Environment variable configuration
- Docker service descriptions
- Complete category listing

**Target Audience:**
- Developers getting started with the project  
- API consumers needing endpoint reference
- DevOps engineers setting up deployments

#### `docker-compose-elasticsearch.yml`
**Purpose:** Orchestrates the complete application stack with Docker Compose.

**Services Defined:**
- **elasticsearch**: Search engine and data storage
- **kibana**: Data visualization and Elasticsearch management
- **newsgroups**: FastAPI application container

**Key Features:**
- Health checks for service dependencies
- Volume persistence for Elasticsearch data
- Network isolation with custom bridge network
- Environment variable configuration
- Service restart policies

---

## Application Directory (`app/`)

### Core Application Files

#### `__init__.py`
**Purpose:** Makes the `app` directory a Python package.
**Content:** Empty file (standard Python convention)

#### `Dockerfile`
**Purpose:** Defines how to build the FastAPI application container.

**Build Process:**
1. **Base image**: `python:3.13-slim`
2. **Environment setup**: Python optimization flags
3. **User creation**: Non-root `appuser` for security
4. **Dependency installation**: pip requirements
5. **Code copying**: Application files to `/code/app`
6. **Permission setup**: File ownership to `appuser`
7. **Runtime configuration**: Port exposure and startup command

**Security Features:**
- Runs as non-root user
- Minimal base image (slim)
- Optimized Python bytecode compilation

#### `requirements.txt`
**Purpose:** Pinned Python dependencies for reproducible builds.

**Generated by:** `pip-compile` from `requirements.in`

**Key Dependencies:**
- **FastAPI**: `0.116.1` - Web framework
- **Elasticsearch**: `9.1.0` - Search client
- **Pydantic**: `2.11.7` - Data validation
- **scikit-learn**: `1.7.1` - 20newsgroups dataset
- **uvicorn**: `0.35.0` - ASGI server

**Dependency Categories:**
- Web framework and server
- Data validation and serialization  
- Elasticsearch client and transport
- Machine learning and data processing
- Async and networking utilities

#### `config.py`
**Purpose:** Centralized configuration management using environment variables.

**Configuration Categories:**
- **Elasticsearch**: Connection details and index settings
- **Logging**: Log level configuration
- **API**: Rate limiting and pagination defaults
- **Data Loading**: Dataset loading parameters

**Environment Variables:**
```python
ELASTICSEARCH_PROTOCOL="http"     # Connection protocol
ELASTICSEARCH_HOST="localhost"    # Server hostname  
ELASTICSEARCH_PORT=9200          # Server port
ELASTICSEARCH_INDEX="newsgroups" # Index name
LOG_LEVEL="INFO"                 # Logging verbosity
DEFAULT_MAX_DOCUMENTS=1000       # Data loading limit
```

#### `dependencies.py`
**Purpose:** FastAPI dependency injection setup for service instances.

**Pattern:** Module-level singleton pattern for Elasticsearch service
**Functions:**
- `set_es_service()`: Initialize service during startup
- `get_es_service()`: Dependency injection function  
- `is_service_ready()`: Health check helper
- `cleanup_service()`: Shutdown cleanup

**Benefits:**
- Single Elasticsearch connection pool
- Proper service lifecycle management
- Clean dependency injection throughout API

#### `main.py`
**Purpose:** Application entry point and FastAPI app configuration.

**Key Components:**
- **Lifespan management**: Startup and shutdown logic
- **Elasticsearch initialization**: Connection and index setup
- **Router registration**: API endpoint organization
- **Middleware setup**: CORS and other cross-cutting concerns  
- **Health checks**: Application readiness endpoints

**Application Lifecycle:**
1. **Startup**: Connect to Elasticsearch, initialize index, load sample data
2. **Runtime**: Serve API requests through registered routers
3. **Shutdown**: Clean up connections and resources

#### `models.py`
**Purpose:** Pydantic data models and validation schemas.

**Model Categories:**
- **Enums**: `DocumentStatus`, `NewsCategory` 
- **Base models**: `DocumentBase` with common fields
- **Request models**: `DocumentCreate`, `DocumentUpdate`
- **Response models**: `DocumentResponse`, `SearchResponse`, `BulkOperationResponse`

**Benefits:**
- Type safety throughout application
- Automatic API documentation generation
- Request/response validation
- Serialization/deserialization

---

## Routers Directory (`app/routers/`)

**Purpose:** API endpoint organization using FastAPI router system.

### Router Files

#### `analytics.py` / `analytics.md`
**Endpoints:**
- `GET /analytics/stats` - Collection statistics
- `GET /analytics/categories` - Category breakdown

**Use Cases:**
- Dashboard data visualization
- Collection health monitoring
- Data distribution analysis

#### `data.py` / `data.md` 
**Endpoints:**
- `POST /data/load-20newsgroups` - Load real dataset
- `POST /data/load-sample` - Load sample data

**Features:**
- Background task processing
- Configurable data loading
- scikit-learn integration

#### `documents.py` / `documents.md`
**Endpoints:**
- `POST /documents/` - Create document
- `GET /documents/{id}` - Retrieve document
- `PUT /documents/{id}` - Update document  
- `DELETE /documents/{id}` - Delete document
- `POST /documents/bulk` - Bulk operations

**Features:**
- Complete CRUD operations
- Input validation
- Bulk processing support

#### `search.py` / `search.md`
**Endpoints:**
- `GET /search/` - Advanced multi-field search
- `GET /search/categories` - List available categories

**Features:**
- Full-text search with relevance scoring
- Multiple filter combinations
- Pagination support
- Category and tag filtering

---

## Services Directory (`app/services/`)

**Purpose:** Business logic layer abstracting external system interactions.

### Service Files

#### `data_loader.py`
**Purpose:** Loads and processes data from scikit-learn's 20newsgroups dataset.

**Key Components:**
- Text cleaning and preprocessing
- Email header extraction
- Tag generation from categories
- Sample data creation

**Performance Optimizations:**
- Pre-compiled regex patterns
- Efficient string processing
- Set-based header lookup
- Single-pass parsing

#### `elasticsearch_service.py`
**Purpose:** Handles all Elasticsearch operations including CRUD and search.

**Key Methods:**
- Document lifecycle management (create, read, update, delete)
- Advanced search with filters and pagination
- Bulk operations for efficiency
- Index management and mapping

**Features:**
- Connection management
- Error handling and logging
- Query optimization
- Response formatting

---

## Architecture Patterns

### Layered Architecture
```
┌─────────────────┐
│   Routers       │  ← API endpoints and request handling
│   (FastAPI)     │
├─────────────────┤
│   Services      │  ← Business logic and data processing  
│   (Business)    │
├─────────────────┤
│   Models        │  ← Data validation and serialization
│   (Pydantic)    │
├─────────────────┤
│   External      │  ← Elasticsearch, scikit-learn
│   (Data Layer)  │
└─────────────────┘
```

**Benefits:**
- Clean separation of concerns
- Testable business logic
- Reusable service components
- Type-safe data flow

### Dependency Injection Pattern
```python
# Service initialization (main.py)
es_service = ElasticsearchService(es_client, index_name)
dependencies.set_es_service(es_service)

# Service consumption (routers)
@router.get("/endpoint")
async def handler(service: ElasticsearchService = Depends(get_es_service)):
    return await service.operation()
```

**Benefits:**
- Single service instance (connection pooling)
- Easy testing with mock services
- Clean service lifecycle management
- Consistent error handling

### Configuration Management
```python
# Environment-based configuration
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost")
ELASTICSEARCH_PORT = int(os.getenv("ELASTICSEARCH_PORT", 9200))

# Usage throughout application  
es_url = f"{config.ELASTICSEARCH_PROTOCOL}://{config.ELASTICSEARCH_HOST}:{config.ELASTICSEARCH_PORT}/"
```

**Benefits:**
- Environment-specific deployments
- Secure credential management
- Easy configuration changes
- Default value fallbacks

---

## Data Flow Architecture

### Document Creation Flow
```
API Request → DocumentCreate → ElasticsearchService → Elasticsearch → DocumentResponse
```

1. **API Layer**: Validates request using `DocumentCreate` model
2. **Service Layer**: Processes data, adds timestamps and UUID
3. **Data Layer**: Stores in Elasticsearch with proper mapping
4. **Response**: Returns `DocumentResponse` with generated fields

### Search Flow
```
Search Query → Query Parameters → ElasticsearchService → Elasticsearch Query → SearchResponse
```

1. **API Layer**: Validates and parses query parameters
2. **Service Layer**: Builds Elasticsearch query with filters
3. **Data Layer**: Executes search and returns results
4. **Response**: Formats as `SearchResponse` with metadata

### Data Loading Flow
```
Background Task → NewsDataLoader → scikit-learn → DocumentCreate[] → ElasticsearchService → Bulk Insert
```

1. **API Layer**: Triggers background task to prevent timeouts
2. **Data Loading**: Fetches and processes 20newsgroups data
3. **Validation**: Converts to `DocumentCreate` models
4. **Service Layer**: Bulk inserts into Elasticsearch
5. **Logging**: Reports success/failure statistics

---

## Docker Architecture

### Multi-Container Setup
```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  newsgroups  │    │elasticsearch │    │    kibana    │
│   (FastAPI)  │───▶│  (Search DB) │◀───│ (Analytics)  │
│   Port 8182  │    │  Port 9200   │    │ Port 5601    │
└──────────────┘    └──────────────┘    └──────────────┘
       │                     │                     │
       └─────────────────────┼─────────────────────┘
                             │
                    ┌──────────────┐
                    │elastic_network│
                    │  (Bridge)     │
                    └──────────────┘
```

**Container Responsibilities:**
- **newsgroups**: FastAPI application serving REST API
- **elasticsearch**: Document storage and search engine
- **kibana**: Data visualization and Elasticsearch management

**Networking:**
- Custom bridge network for container communication
- Port mapping for external access
- Service discovery by container name

### Health Check Strategy
```yaml
healthcheck:
  test: ["CMD-SHELL", "curl -f http://localhost:8182/health || exit 1"]
  interval: 30s
  timeout: 10s
  retries: 5
  start_period: 60s
```

**Benefits:**
- Automatic service restart on failure
- Dependency ordering (newsgroups waits for elasticsearch)
- Load balancer integration readiness
- Monitoring system compatibility

---

## Development Workflow

### Local Development Setup
```bash
# 1. Clone repository
git clone <repository-url>
cd 20newsgroups-search-api

# 2. Start services
docker-compose -f docker-compose-elasticsearch.yml up -d

# 3. Verify health
curl http://localhost:8182/health

# 4. Access interfaces
# API: http://localhost:8182
# Swagger: http://localhost:8182/docs  
# Kibana: http://localhost:5601
```

### File Organization Principles

#### Separation of Concerns
- **Routers**: HTTP request/response handling
- **Services**: Business logic and external system integration
- **Models**: Data validation and type safety
- **Config**: Environment-specific settings

#### Documentation Strategy
- **README files**: Comprehensive documentation for each component
- **Inline docstrings**: Function and class documentation  
- **API docs**: Automatic generation via FastAPI/Pydantic
- **Type hints**: Self-documenting code with mypy support

---

## Deployment Considerations

### Environment Configuration
- **Development**: Local Docker Compose
- **Staging**: Container orchestration (K8s/Docker Swarm)
- **Production**: Cloud-managed Elasticsearch + containerized API

### Scaling Strategy
- **Horizontal**: Multiple FastAPI container instances
- **Vertical**: Elasticsearch cluster scaling  
- **Caching**: Redis for frequent search queries
- **CDN**: Static asset delivery optimization

### Monitoring & Observability
- **Logging**: Structured JSON logs with correlation IDs
- **Metrics**: Prometheus metrics for API and Elasticsearch
- **Health Checks**: Kubernetes readiness/liveness probes
- **Tracing**: Distributed tracing for request flow

### Security Considerations
- **Container Security**: Non-root user, minimal base images
- **Network Security**: Firewall rules, VPC isolation
- **Data Security**: Elasticsearch authentication in production
- **API Security**: Rate limiting, input validation, CORS policies


This project structure provides a solid foundation for a scalable, maintainable search API with clear separation of concerns and comprehensive documentation.