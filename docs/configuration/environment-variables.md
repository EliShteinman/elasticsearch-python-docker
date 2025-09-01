# Configuration Management (`config.py`)

## Overview
The configuration system provides centralized management of all application settings using environment variables with sensible defaults. This approach enables environment-specific deployments while maintaining security and flexibility.

---

## Configuration Architecture

### Environment-First Approach
```python
import os

# Pattern: Environment variable with fallback default
SETTING_NAME = os.getenv("ENV_VAR_NAME", "default_value")
```

**Benefits:**
- **12-Factor App Compliance**: Configuration through environment
- **Security**: Sensitive values not hard-coded
- **Flexibility**: Different values per deployment environment
- **Docker-Friendly**: Easy container configuration

### Configuration Categories
```python
# Elasticsearch Configuration
ELASTICSEARCH_PROTOCOL = "http"
ELASTICSEARCH_HOST = "localhost"  
ELASTICSEARCH_PORT = 9200
ELASTICSEARCH_INDEX = "newsgroups"

# Logging Configuration  
LOG_LEVEL = "INFO"

# Data Loading Configuration
DEFAULT_MAX_DOCUMENTS = 1000
DEFAULT_SUBSET = "train"

# API Configuration
MAX_BULK_SIZE = 1000
DEFAULT_SEARCH_LIMIT = 10
MAX_SEARCH_LIMIT = 100
```

---

## Detailed Configuration Reference

### Elasticsearch Configuration

#### `ELASTICSEARCH_PROTOCOL`
```python
ELASTICSEARCH_PROTOCOL = os.getenv("ELASTICSEARCH_PROTOCOL", "http")
```

**Purpose:** Sets the default limit for documents loaded from the 20newsgroups dataset.

**Valid Values:**
- `1000` - Default for development/testing
- `5000` - Maximum allowed by API
- `100` - Small datasets for quick testing
- `10000+` - Requires code modification to exceed API limits

**Environment Variable:** `DEFAULT_MAX_DOCUMENTS`

**Usage Examples:**
```bash
# Development
export DEFAULT_MAX_DOCUMENTS=1000

# Testing
export DEFAULT_MAX_DOCUMENTS=100

# Full dataset
export DEFAULT_MAX_DOCUMENTS=5000
```

**API Integration:**
```python
# Used in data loading endpoint
@router.post("/load-20newsgroups")
async def load_20newsgroups_data(
    max_documents: int = Query(config.DEFAULT_MAX_DOCUMENTS, ge=1, le=5000)
):
```

#### `DEFAULT_SUBSET`
```python
DEFAULT_SUBSET = os.getenv("DEFAULT_SUBSET", "train")
```

**Purpose:** Specifies which portion of the 20newsgroups dataset to load by default.

**Valid Values:**
- `"train"` - Training subset (~11,314 documents)
- `"test"` - Testing subset (~7,532 documents)  
- `"all"` - Combined dataset (~18,846 documents)

**Environment Variable:** `DEFAULT_SUBSET`

**Usage Examples:**
```bash
# Training data (default)
export DEFAULT_SUBSET=train

# Testing data
export DEFAULT_SUBSET=test

# Complete dataset
export DEFAULT_SUBSET=all
```

**Dataset Characteristics:**
```python
# Approximate document counts by subset
SUBSET_SIZES = {
    "train": 11314,  # Training documents
    "test": 7532,    # Test documents  
    "all": 18846     # Combined total
}
```

---

### API Configuration

#### `MAX_BULK_SIZE`
```python
MAX_BULK_SIZE = int(os.getenv("MAX_BULK_SIZE", 1000))
```

**Purpose:** Limits the maximum number of documents allowed in bulk creation operations.

**Valid Values:**
- `1000` - Balanced performance/memory usage (default)
- `500` - Conservative for low-memory environments
- `2000` - Higher throughput for powerful systems
- `100` - Testing/development environments

**Environment Variable:** `MAX_BULK_SIZE`

**Usage Examples:**
```bash
# Standard configuration
export MAX_BULK_SIZE=1000

# High-performance setup
export MAX_BULK_SIZE=2000

# Low-memory environment
export MAX_BULK_SIZE=500
```

**API Validation:**
```python
@router.post("/bulk")
async def bulk_create_documents(documents: List[DocumentCreate]):
    if len(documents) > config.MAX_BULK_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"Maximum {config.MAX_BULK_SIZE} documents per bulk operation"
        )
```

#### `DEFAULT_SEARCH_LIMIT`
```python
DEFAULT_SEARCH_LIMIT = int(os.getenv("DEFAULT_SEARCH_LIMIT", 10))
```

**Purpose:** Sets the default number of search results returned when no limit is specified.

**Valid Values:**
- `10` - Standard pagination size (default)
- `25` - More results per page
- `5` - Minimal results for mobile interfaces
- `50` - Maximum recommended for UI display

**Environment Variable:** `DEFAULT_SEARCH_LIMIT`

**Usage Examples:**
```bash
# Standard pagination
export DEFAULT_SEARCH_LIMIT=10

# Mobile-optimized
export DEFAULT_SEARCH_LIMIT=5

# Desktop-optimized  
export DEFAULT_SEARCH_LIMIT=25
```

#### `MAX_SEARCH_LIMIT`
```python
MAX_SEARCH_LIMIT = int(os.getenv("MAX_SEARCH_LIMIT", 100))
```

**Purpose:** Enforces maximum limit for search results to prevent performance issues.

**Valid Values:**
- `100` - Reasonable maximum (default)
- `50` - Conservative limit for slower systems
- `200` - Higher limit for internal APIs
- `1000` - Development/testing only

**Environment Variable:** `MAX_SEARCH_LIMIT`

**Usage Examples:**
```bash
# Production limit
export MAX_SEARCH_LIMIT=100

# Conservative setup
export MAX_SEARCH_LIMIT=50

# High-performance API
export MAX_SEARCH_LIMIT=200
```

**API Validation:**
```python
@router.get("/search")
async def search_documents(
    limit: int = Query(config.DEFAULT_SEARCH_LIMIT, ge=1, le=config.MAX_SEARCH_LIMIT)
):
```

---

## Environment-Specific Configuration

### Development Environment
```bash
# .env.development
ELASTICSEARCH_PROTOCOL=http
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_INDEX=newsgroups-dev
LOG_LEVEL=DEBUG
DEFAULT_MAX_DOCUMENTS=100
DEFAULT_SUBSET=train
MAX_BULK_SIZE=500
DEFAULT_SEARCH_LIMIT=10
MAX_SEARCH_LIMIT=50
```

### Staging Environment
```bash
# .env.staging
ELASTICSEARCH_PROTOCOL=https
ELASTICSEARCH_HOST=es-staging.company.com
ELASTICSEARCH_PORT=9243
ELASTICSEARCH_INDEX=newsgroups-staging
LOG_LEVEL=INFO
DEFAULT_MAX_DOCUMENTS=1000
DEFAULT_SUBSET=train
MAX_BULK_SIZE=1000
DEFAULT_SEARCH_LIMIT=10
MAX_SEARCH_LIMIT=100
```

### Production Environment
```bash
# .env.production
ELASTICSEARCH_PROTOCOL=https
ELASTICSEARCH_HOST=es-prod-cluster.company.com
ELASTICSEARCH_PORT=9243
ELASTICSEARCH_INDEX=newsgroups
LOG_LEVEL=WARNING
DEFAULT_MAX_DOCUMENTS=5000
DEFAULT_SUBSET=all
MAX_BULK_SIZE=2000
DEFAULT_SEARCH_LIMIT=10
MAX_SEARCH_LIMIT=100
```

---

## Docker Integration

### Docker Compose Configuration
```yaml
# docker-compose-elasticsearch.yml
services:
  newsgroups:
    environment:
      - ELASTICSEARCH_PROTOCOL=http
      - ELASTICSEARCH_HOST=elasticsearch
      - ELASTICSEARCH_PORT=9200
      - LOG_LEVEL=INFO
      - ELASTICSEARCH_INDEX=newsgroups
      
    # Environment file support
    env_file:
      - .env.local
```

### Environment File Usage
```bash
# Create environment file
cat > .env.local << EOF
ELASTICSEARCH_PROTOCOL=http
ELASTICSEARCH_HOST=elasticsearch
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_INDEX=newsgroups-local
LOG_LEVEL=DEBUG
DEFAULT_MAX_DOCUMENTS=500
EOF

# Use with Docker Compose
docker-compose -f docker-compose-elasticsearch.yml --env-file .env.local up -d
```

### Container Environment Injection
```bash
# Direct environment variable passing
docker run -e ELASTICSEARCH_HOST=my-es-server \
           -e LOG_LEVEL=DEBUG \
           -e ELASTICSEARCH_INDEX=test-index \
           newsgroups-api
```

---

## Configuration Validation

### Runtime Validation
```python
# config_validator.py
import os
import sys
from typing import Dict, Any

def validate_config() -> Dict[str, Any]:
    """Validate configuration settings at startup"""
    errors = []
    
    # Required settings
    required_vars = [
        'ELASTICSEARCH_HOST',
        'ELASTICSEARCH_PORT', 
        'ELASTICSEARCH_INDEX'
    ]
    
    for var in required_vars:
        if not os.getenv(var):
            errors.append(f"Missing required environment variable: {var}")
    
    # Validate numeric values
    try:
        port = int(os.getenv('ELASTICSEARCH_PORT', 9200))
        if not (1 <= port <= 65535):
            errors.append(f"Invalid port number: {port}")
    except ValueError:
        errors.append("ELASTICSEARCH_PORT must be a valid integer")
    
    # Validate log level
    valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    if log_level not in valid_log_levels:
        errors.append(f"Invalid LOG_LEVEL: {log_level}. Must be one of {valid_log_levels}")
    
    if errors:
        print("Configuration validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    
    return {
        'status': 'valid',
        'elasticsearch_url': f"{os.getenv('ELASTICSEARCH_PROTOCOL', 'http')}://{os.getenv('ELASTICSEARCH_HOST')}:{os.getenv('ELASTICSEARCH_PORT')}",
        'index': os.getenv('ELASTICSEARCH_INDEX'),
        'log_level': log_level
    }

# Usage in main.py
if __name__ == "__main__":
    config_status = validate_config()
    print(f"Configuration validated: {config_status}")
```

### Health Check Integration
```python
@app.get("/health")
async def health_check():
    """Enhanced health check including configuration status"""
    return {
        "status": "healthy",
        "version": "2.1.0",
        "configuration": {
            "elasticsearch_host": config.ELASTICSEARCH_HOST,
            "elasticsearch_port": config.ELASTICSEARCH_PORT,
            "elasticsearch_index": config.ELASTICSEARCH_INDEX,
            "log_level": config.LOG_LEVEL
        },
        "services": {
            "elasticsearch": "connected"
        }
    }
```

---

## Security Considerations

### Sensitive Configuration
```python
# Sensitive values (use environment variables, never hard-code)
ELASTICSEARCH_USERNAME = os.getenv("ELASTICSEARCH_USERNAME")  # None in development
ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD")  # None in development
ELASTICSEARCH_API_KEY = os.getenv("ELASTICSEARCH_API_KEY")    # None in development

# SSL/TLS Configuration
ELASTICSEARCH_CA_CERT = os.getenv("ELASTICSEARCH_CA_CERT")    # Path to CA certificate
ELASTICSEARCH_VERIFY_CERTS = os.getenv("ELASTICSEARCH_VERIFY_CERTS", "true").lower() == "true"
```

### Production Security Setup
```bash
# Production environment variables (set in deployment pipeline)
export ELASTICSEARCH_USERNAME=api_user
export ELASTICSEARCH_PASSWORD=$(vault kv get -field=password secret/elasticsearch/api_user)
export ELASTICSEARCH_API_KEY=$(vault kv get -field=api_key secret/elasticsearch/api_keys)
export ELASTICSEARCH_CA_CERT=/etc/ssl/certs/elasticsearch-ca.pem
export ELASTICSEARCH_VERIFY_CERTS=true
```

### Secrets Management Integration
```python
# secrets.py (production deployment)
import boto3
import os

def get_secret(secret_name: str) -> str:
    """Retrieve secret from AWS Secrets Manager"""
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']

# Enhanced configuration for production
if os.getenv('ENVIRONMENT') == 'production':
    ELASTICSEARCH_PASSWORD = get_secret('elasticsearch-password')
    ELASTICSEARCH_API_KEY = get_secret('elasticsearch-api-key')
```

---

## Monitoring and Observability

### Configuration Logging
```python
import logging
from app import config

logger = logging.getLogger(__name__)

def log_configuration():
    """Log non-sensitive configuration at startup"""
    logger.info("Application configuration:")
    logger.info(f"  Elasticsearch Host: {config.ELASTICSEARCH_HOST}")
    logger.info(f"  Elasticsearch Port: {config.ELASTICSEARCH_PORT}")
    logger.info(f"  Elasticsearch Index: {config.ELASTICSEARCH_INDEX}")
    logger.info(f"  Log Level: {config.LOG_LEVEL}")
    logger.info(f"  Max Documents: {config.DEFAULT_MAX_DOCUMENTS}")
    logger.info(f"  Max Bulk Size: {config.MAX_BULK_SIZE}")
    
    # Never log sensitive values
    if hasattr(config, 'ELASTICSEARCH_PASSWORD'):
        logger.info("  Authentication: Enabled")
    else:
        logger.info("  Authentication: Disabled")
```

### Metrics Integration
```python
# metrics.py
from prometheus_client import Info

# Configuration metrics for monitoring
config_info = Info('app_configuration', 'Application configuration information')
config_info.info({
    'elasticsearch_host': config.ELASTICSEARCH_HOST,
    'elasticsearch_index': config.ELASTICSEARCH_INDEX,
    'log_level': config.LOG_LEVEL,
    'max_bulk_size': str(config.MAX_BULK_SIZE)
})
```

---

## Best Practices

### Configuration Management
1. **Environment Variables**: Use environment variables for all configuration
2. **Defaults**: Provide sensible defaults for development
3. **Validation**: Validate configuration at startup
4. **Documentation**: Document all configuration options
5. **Secrets**: Never commit secrets to version control

### Deployment Practices
1. **Environment Files**: Use `.env` files for local development
2. **CI/CD Integration**: Inject environment variables in deployment pipelines
3. **Configuration as Code**: Store environment-specific configs in version control
4. **Immutable Infrastructure**: Bake configuration into container images when possible
5. **Secret Management**: Use dedicated secret management systems in production

### Development Workflow
1. **Local Override**: Allow local environment files to override defaults
2. **Testing**: Provide test-specific configurations
3. **Documentation**: Keep configuration documentation up to date
4. **Validation**: Include configuration validation in tests

This configuration system provides a robust, secure, and flexible foundation for managing application settings across all deployment environments. Defines the connection protocol for Elasticsearch communication.

**Valid Values:**
- `"http"` - Standard HTTP connection (development)
- `"https"` - Encrypted HTTPS connection (production)

**Environment Variable:** `ELASTICSEARCH_PROTOCOL`

**Usage Examples:**
```bash
# Development
export ELASTICSEARCH_PROTOCOL=http

# Production  
export ELASTICSEARCH_PROTOCOL=https
```

**Docker Configuration:**
```yaml
environment:
  - ELASTICSEARCH_PROTOCOL=http
```

#### `ELASTICSEARCH_HOST` 
```python
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost")
```

**Purpose:** Specifies the hostname or IP address of the Elasticsearch server.

**Valid Values:**
- `"localhost"` - Local development
- `"elasticsearch"` - Docker container name
- `"es-cluster.example.com"` - Production hostname
- `"10.0.1.100"` - IP address

**Environment Variable:** `ELASTICSEARCH_HOST`

**Usage Examples:**
```bash
# Local development
export ELASTICSEARCH_HOST=localhost

# Docker Compose
export ELASTICSEARCH_HOST=elasticsearch

# Cloud deployment
export ELASTICSEARCH_HOST=my-es-cluster.us-east-1.aws.found.io
```

#### `ELASTICSEARCH_PORT`
```python
ELASTICSEARCH_PORT = int(os.getenv("ELASTICSEARCH_PORT", 9200))
```

**Purpose:** Defines the port number for Elasticsearch connections.

**Valid Values:**
- `9200` - Standard Elasticsearch HTTP port
- `9243` - Elasticsearch Cloud HTTPS port
- Custom ports for specific deployments

**Environment Variable:** `ELASTICSEARCH_PORT`

**Type Conversion:** Automatically converted to integer

**Usage Examples:**
```bash
# Standard port
export ELASTICSEARCH_PORT=9200

# Custom port
export ELASTICSEARCH_PORT=9243

# Non-standard deployment
export ELASTICSEARCH_PORT=8080
```

#### `ELASTICSEARCH_INDEX`
```python
ELASTICSEARCH_INDEX = os.getenv("ELASTICSEARCH_INDEX", "newsgroups")
```

**Purpose:** Names the Elasticsearch index for document storage and search.

**Valid Values:**
- `"newsgroups"` - Default production index
- `"newsgroups-dev"` - Development environment
- `"newsgroups-test"` - Testing environment
- `"newsgroups-staging"` - Staging environment

**Environment Variable:** `ELASTICSEARCH_INDEX`

**Usage Examples:**
```bash
# Production
export ELASTICSEARCH_INDEX=newsgroups

# Environment-specific
export ELASTICSEARCH_INDEX=newsgroups-${ENVIRONMENT}

# Feature branch
export ELASTICSEARCH_INDEX=newsgroups-feature-auth
```

**Index Management:**
```python
# Application usage
es_service = ElasticsearchService(es_client, config.ELASTICSEARCH_INDEX)
await es_service.initialize_index()  # Creates if not exists
```

---

### Logging Configuration

#### `LOG_LEVEL`
```python
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
```

**Purpose:** Controls the verbosity of application logging output.

**Valid Values:**
- `"DEBUG"` - Detailed debugging information
- `"INFO"` - General information (default)
- `"WARNING"` - Warning messages only
- `"ERROR"` - Error messages only
- `"CRITICAL"` - Critical errors only

**Environment Variable:** `LOG_LEVEL`

**Usage Examples:**
```bash
# Development (verbose)
export LOG_LEVEL=DEBUG

# Production (standard)
export LOG_LEVEL=INFO

# Production (quiet)
export LOG_LEVEL=WARNING
```

**Log Output Examples:**
```python
# DEBUG level output
2024-01-15 10:30:00 - elasticsearch_service - DEBUG - Building search query: {"query": {"match_all": {}}}
2024-01-15 10:30:00 - elasticsearch_service - INFO - Search completed: 1247 results found

# INFO level output
2024-01-15 10:30:00 - elasticsearch_service - INFO - Search completed: 1247 results found

# WARNING level output
2024-01-15 10:30:00 - data_loader - WARNING - No 20newsgroups data retrieved
```

**Integration with Python Logging:**
```python
import logging
from app import config

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

### Data Loading Configuration

#### `DEFAULT_MAX_DOCUMENTS`
```python
DEFAULT_MAX_DOCUMENTS = int(os.getenv("DEFAULT_MAX_DOCUMENTS", 1000))
```

**Purpose:**