# Dependency Injection System (`dependencies.py`)

## Overview
The 20 Newsgroups API uses FastAPI's dependency injection system to manage service instances throughout the application lifecycle. This document explains how the dependency system works and how to use it effectively.

---

## Core Concepts

### What is Dependency Injection?
Dependency Injection (DI) is a design pattern where objects receive their dependencies from external sources rather than creating them internally. This provides:

- **Single Source of Truth**: One service instance shared across all endpoints
- **Testability**: Easy to mock dependencies for testing
- **Lifecycle Management**: Proper initialization and cleanup
- **Resource Efficiency**: Connection pooling and resource sharing

### Why Use DI in FastAPI?
- **Request-level Dependencies**: Fresh dependencies for each request when needed
- **Application-level Singletons**: Shared services like database connections
- **Automatic Cleanup**: Dependencies cleaned up automatically
- **Type Safety**: Full type hinting and IDE support

---

## Implementation Architecture

### Module Structure
```python
# app/dependencies.py
from typing import Optional
from fastapi import HTTPException
from app.services.elasticsearch_service import ElasticsearchService

# Private module variable (singleton pattern)
_es_service: Optional[ElasticsearchService] = None

def set_es_service(service: ElasticsearchService) -> None:
    """Set service instance during app startup"""
    
def get_es_service() -> ElasticsearchService:
    """FastAPI dependency function"""
    
def is_service_ready() -> bool:
    """Health check helper"""
    
def cleanup_service() -> None:
    """Cleanup during app shutdown"""
```

### Service Lifecycle
```
Application Startup → Service Creation → Dependency Registration → Request Handling → Application Shutdown
       │                    │                     │                     │                    │
   Initialize ES        Create Service        Set Global Ref      Inject into Routes    Cleanup
```

---

## Detailed Implementation

### 1. Service Initialization (Startup)
```python
# In app/main.py - lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application lifespan startup")
    
    try:
        # 1. Create Elasticsearch client
        es_url = f"{config.ELASTICSEARCH_PROTOCOL}://{config.ELASTICSEARCH_HOST}:{config.ELASTICSEARCH_PORT}/"
        es_client = Elasticsearch(es_url)
        
        # 2. Test connection
        if not es_client.ping():
            raise Exception("Elasticsearch connection failed")
            
        # 3. Create service instance
        es_service = ElasticsearchService(es_client, config.ELASTICSEARCH_INDEX)
        await es_service.initialize_index()
        
        # 4. Register with dependency system
        dependencies.set_es_service(es_service)
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Error during application startup: {str(e)}")
        raise
    
    # Application runs here
    yield
    
    # Cleanup on shutdown
    logger.info("Application shutdown completed")
```

### 2. Service Registration
```python
# app/dependencies.py
_es_service: Optional[ElasticsearchService] = None

def set_es_service(service: ElasticsearchService) -> None:
    """Set the Elasticsearch service instance. Called during app startup."""
    global _es_service
    _es_service = service
    logger.info("Elasticsearch service registered successfully")
```

**Key Points:**
- **Global Variable**: Stores service instance at module level
- **Singleton Pattern**: Only one instance throughout app lifecycle
- **Thread Safety**: FastAPI handles concurrency, service is read-only after startup
- **Error Handling**: Clear logging for debugging startup issues

### 3. Dependency Injection Function
```python
def get_es_service() -> ElasticsearchService:
    """Dependency function to get the Elasticsearch service instance."""
    if _es_service is None:
        raise HTTPException(
            status_code=500,
            detail="Elasticsearch service not initialized. Please check application startup logs."
        )
    return _es_service
```

**Features:**
- **Type Hints**: Returns typed service for IDE support
- **Error Handling**: Clear error message if service not ready
- **HTTP Status**: Proper 500 status for service unavailability
- **Debugging**: Points to startup logs for troubleshooting

---

## Usage Patterns

### 1. Basic Endpoint Injection
```python
# app/routers/documents.py
from fastapi import APIRouter, Depends
from app.dependencies import get_es_service
from app.services.elasticsearch_service import ElasticsearchService

router = APIRouter()

@router.get("/{doc_id}")
async def get_document(
    doc_id: str,
    service: ElasticsearchService = Depends(get_es_service)  # DI here
):
    """Get document by ID"""
    result = await service.get_document(doc_id)
    if not result:
        raise HTTPException(status_code=404, detail="Document not found")
    return result
```

### 2. Multiple Dependencies
```python
@router.post("/complex-operation")
async def complex_operation(
    data: SomeModel,
    es_service: ElasticsearchService = Depends(get_es_service),
    # Could add more dependencies here
    # cache_service: CacheService = Depends(get_cache_service),
    # auth_service: AuthService = Depends(get_auth_service)
):
    """Example with multiple dependencies"""
    return await es_service.complex_operation(data)
```

### 3. Health Check Integration
```python
# app/main.py
@app.get("/health")
async def health_check():
    """Health check endpoint with dependency status"""
    try:
        # Check if service is ready
        if not dependencies.is_service_ready():
            return {
                "status": "unhealthy", 
                "error": "Services not initialized"
            }
        
        # Test service functionality
        service = dependencies.get_es_service()
        await service.search_documents(limit=0)  # Quick health check
        
        return {"status": "healthy", "elasticsearch": "connected"}
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e)
        }
```

---

## Advanced Patterns

### 1. Service Factory Pattern
```python
# For future expansion - multiple service types
def create_service_factory():
    """Factory for creating different service types"""
    
    def get_elasticsearch_service() -> ElasticsearchService:
        return get_es_service()
    
    def get_cache_service() -> CacheService:
        # Future implementation
        pass
        
    return {
        'elasticsearch': get_elasticsearch_service,
        'cache': get_cache_service
    }
```

### 2. Conditional Dependencies
```python
def get_service_or_mock() -> ElasticsearchService:
    """Returns mock service in test environment"""
    if os.getenv("ENVIRONMENT") == "test":
        return MockElasticsearchService()
    return get_es_service()

# Usage in endpoints that need testing flexibility
@router.get("/test-friendly-endpoint")
async def endpoint(service: ElasticsearchService = Depends(get_service_or_mock)):
    return await service.operation()
```

### 3. Request-Scoped Dependencies
```python
def get_request_id() -> str:
    """Generate unique request ID for tracing"""
    return str(uuid.uuid4())

def get_logger(request_id: str = Depends(get_request_id)) -> logging.Logger:
    """Get logger with request ID for correlation"""
    logger = logging.getLogger(__name__)
    return logger.bind(request_id=request_id)

@router.post("/with-tracing")
async def traced_endpoint(
    data: SomeModel,
    service: ElasticsearchService = Depends(get_es_service),
    logger: logging.Logger = Depends(get_logger)
):
    logger.info("Processing request")
    result = await service.operation(data)
    logger.info("Request completed")
    return result
```

---

## Testing with Dependencies

### 1. Mock Service for Testing
```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock
from app import dependencies
from app.services.elasticsearch_service import ElasticsearchService

@pytest.fixture
def mock_es_service():
    """Create mock Elasticsearch service"""
    mock_service = AsyncMock(spec=ElasticsearchService)
    
    # Set up mock responses
    mock_service.get_document.return_value = {
        "id": "test-doc",
        "title": "Test Document",
        "body": "Test content"
    }
    
    return mock_service

@pytest.fixture
def app_with_mock_service(mock_es_service):
    """FastAPI app with mocked dependencies"""
    from app.main import app
    
    # Override dependency
    app.dependency_overrides[dependencies.get_es_service] = lambda: mock_es_service
    
    yield app
    
    # Cleanup
    app.dependency_overrides.clear()
```

### 2. Integration Tests
```python
# tests/test_integration.py
def test_real_service_integration():
    """Test with real Elasticsearch service"""
    # Start real Elasticsearch in test
    # Use actual dependencies
    # Test full integration flow
    pass

def test_mocked_service_unit():
    """Test with mocked service"""
    # Use mocked dependencies  
    # Test business logic only
    # Fast, isolated tests
    pass
```

---

## Error Handling & Debugging

### Common Issues

#### 1. Service Not Initialized
**Symptom:**
```
HTTPException: 500 - Elasticsearch service not initialized
```

**Debugging:**
```python
# Check if service was set during startup
if dependencies.is_service_ready():
    print("✅ Service is ready")
else:
    print("❌ Service not initialized")
    # Check startup logs for Elasticsearch connection errors
```

**Solutions:**
- Check Elasticsearch connectivity during startup
- Verify environment variables are correct
- Check Docker container health and networking

#### 2. Connection Pool Issues
**Symptom:**
```
ConnectionTimeout: Elasticsearch connection timeout
```

**Debugging:**
```python
# Test direct connection
from elasticsearch import Elasticsearch
es = Elasticsearch("http://localhost:9200")
print(es.ping())  # Should return True
```

**Solutions:**
- Increase Elasticsearch connection timeout
- Check network configuration
- Verify Elasticsearch container is healthy

#### 3. Memory Leaks (Future Consideration)
**Prevention:**
```python
def cleanup_service() -> None:
    """Cleanup service instance during shutdown"""
    global _es_service
    if _es_service:
        # Close connections, cleanup resources
        if hasattr(_es_service, 'close'):
            _es_service.close()
    _es_service = None
```

---

## Performance Considerations

### Connection Pooling
```python
# Elasticsearch client automatically handles connection pooling
# Single service instance = single connection pool
# Shared across all requests = efficient resource usage
```

### Resource Management
- **Single Instance**: One ElasticsearchService per application
- **Connection Reuse**: HTTP connections pooled and reused
- **Memory Efficient**: No per-request service creation
- **Thread Safe**: Elasticsearch client is thread-safe

### Scaling Considerations
```python
# For high-traffic applications, consider:
# 1. Connection pool tuning
es_client = Elasticsearch(
    hosts=["http://localhost:9200"],
    maxsize=20,        # Max connections in pool
    timeout=30,        # Request timeout
    retry_on_timeout=True
)

# 2. Service instance per worker (if needed)
# 3. Circuit breaker pattern for resilience
```

---

## Future Enhancements

### Multi-Service Support
```python
# Pattern for adding more services
_services: Dict[str, Any] = {}

def register_service(name: str, service: Any) -> None:
    _services[name] = service

def get_service(name: str) -> Any:
    if name not in _services:
        raise HTTPException(500, f"Service {name} not initialized")
    return _services[name]
```

### Configuration-Based DI
```python
# Load service configuration from config
def create_services_from_config(config: Config):
    services = {}
    
    if config.ELASTICSEARCH_ENABLED:
        es_client = Elasticsearch(config.ELASTICSEARCH_URL)
        services['elasticsearch'] = ElasticsearchService(es_client)
    
    if config.REDIS_ENABLED:
        redis_client = Redis(config.REDIS_URL)
        services['cache'] = CacheService(redis_client)
    
    return services
```

This dependency injection system provides a robust foundation for managing service lifecycles while maintaining clean, testable, and scalable code architecture.