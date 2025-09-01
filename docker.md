# Docker Configuration Documentation

## Overview
This document provides comprehensive documentation for the Docker setup of the 20 Newsgroups Search API, including container configuration, orchestration, and deployment strategies.

---

## Docker Architecture

### Multi-Container Stack
The application runs as a three-container stack orchestrated by Docker Compose:

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Host                             │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ newsgroups  │  │elasticsearch│  │       kibana        │  │
│  │  (FastAPI)  │  │   (Search)  │  │   (Analytics)       │  │
│  │             │  │             │  │                     │  │
│  │ Port: 8182  │  │ Port: 9200  │  │   Port: 5601        │  │
│  │             │  │             │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│         │                 │                     │           │
│         └─────────────────┼─────────────────────┘           │
│                           │                                 │
│    ┌──────────────────────────────────────────────────┐    │
│    │           elastic_network (bridge)               │    │
│    └──────────────────────────────────────────────────┘    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │        elasticsearch_data_newsgroups                │   │
│  │             (Persistent Volume)                     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Container Specifications

### 1. Elasticsearch Container

#### Image & Version
```yaml
image: docker.elastic.co/elasticsearch/elasticsearch:9.1.2
```

**Why This Version:**
- Latest stable release with performance improvements
- Compatible with Python elasticsearch client 9.1.0
- Includes security features (disabled for development)

#### Environment Configuration
```yaml
environment:
  - discovery.type=single-node        # Single instance mode
  - xpack.security.enabled=false      # Disable security for development
  - "ES_JAVA_OPTS=-Xms512m -Xmx512m"  # JVM heap size limits
```

**Configuration Explained:**
- **`discovery.type=single-node`**: Configures Elasticsearch for single-node operation (development/testing)
- **`xpack.security.enabled=false`**: Disables authentication and SSL (not recommended for production)
- **`ES_JAVA_OPTS`**: Sets JVM heap size to 512MB (adjust based on available memory)

#### Storage Configuration
```yaml
volumes:
  - elasticsearch_data_newsgroups:/usr/share/elasticsearch/data
```

**Data Persistence:**
- Named volume ensures data survives container restarts
- Elasticsearch indices and documents preserved across deployments
- Volume can be backed up for disaster recovery

#### Networking
```yaml
ports:
  - "9200:9200"
networks:
  - elastic_network
```

**Port Mapping:**
- Internal port 9200 mapped to host port 9200
- Accessible directly for debugging/administration
- Network isolation through custom bridge network

#### Health Check
```yaml
healthcheck:
  test: ["CMD-SHELL", "curl -f http://localhost:9200/_cluster/health || exit 1"]
  interval: 30s
  timeout: 10s
  retries: 5
  start_period: 60s
```

**Health Check Strategy:**
- **Test**: Queries Elasticsearch cluster health endpoint
- **Interval**: Checks every 30 seconds
- **Timeout**: 10-second limit per check
- **Retries**: 5 consecutive failures before marking unhealthy
- **Start Period**: 60-second grace period during startup

---

### 2. Kibana Container

#### Image & Version
```yaml
image: docker.elastic.co/kibana/kibana:9.1.2
```

**Version Matching:**
- Matches Elasticsearch version for compatibility
- Ensures feature parity and stable connection
- Reduces version conflict issues

#### Environment Configuration
```yaml
environment:
  ELASTICSEARCH_HOSTS: http://elasticsearch:9200
```

**Connection Configuration:**
- Uses Docker internal networking (container name resolution)
- Connects to Elasticsearch on default port 9200
- No authentication required (matches Elasticsearch config)

#### Service Dependencies
```yaml
depends_on:
  elasticsearch: { condition: service_healthy }
```

**Dependency Management:**
- Waits for Elasticsearch to be healthy before starting
- Prevents connection errors during startup
- Ensures proper initialization order

#### Networking
```yaml
ports:
  - "5601:5601"
networks:
  - elastic_network
```

**Access Configuration:**
- Web interface accessible on port 5601
- Same network as Elasticsearch for internal communication
- External access for data visualization and management

#### Health Check
```yaml
healthcheck:
  test: ["CMD-SHELL", "curl -f http://localhost:5601/api/status || exit 1"]
  interval: 30s
  timeout: 10s
  retries: 5
  start_period: 60s
```

---

### 3. FastAPI Application Container

#### Build Configuration
```yaml
build:
  context: app
  dockerfile: Dockerfile
```

**Build Context:**
- Uses `app/` directory as build context
- Contains application code and dependencies
- Dockerfile optimized for Python applications

#### Application Dependencies
```yaml
depends_on:
  elasticsearch: { condition: service_healthy }
```

**Startup Order:**
- Waits for Elasticsearch to be ready
- Prevents application startup failures
- Allows proper index initialization

#### Environment Configuration
```yaml
environment:
  - ELASTICSEARCH_PROTOCOL=http
  - ELASTICSEARCH_HOST=elasticsearch  # Container name resolution
  - ELASTICSEARCH_PORT=9200
  - LOG_LEVEL=INFO
  - ELASTICSEARCH_INDEX=newsgroups
```

**Configuration Explained:**
- **Protocol**: HTTP connection (no SSL in development)
- **Host**: Uses container name for internal networking
- **Port**: Standard Elasticsearch port
- **Logging**: INFO level for development visibility
- **Index**: Target index name for documents

#### Networking
```yaml
ports:
  - "8182:8182"
networks:
  - elastic_network
```

**API Access:**
- REST API accessible on port 8182
- Internal communication with Elasticsearch
- External access for client applications

---

## Dockerfile Analysis (`app/Dockerfile`)

### Multi-Stage Build Optimization

#### Base Image Selection
```dockerfile
FROM python:3.13-slim
```

**Benefits:**
- **Lightweight**: `-slim` variant reduces image size
- **Security**: Fewer packages = smaller attack surface
- **Performance**: Faster downloads and container startup
- **Compatibility**: Python 3.13 supports latest language features

#### Environment Optimization
```dockerfile
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
```

**Configuration Explained:**
- **`PYTHONUNBUFFERED=1`**: Real-time log output (important for containers)
- **`PYTHONDONTWRITEBYTECODE=1`**: Prevents .pyc file creation (smaller images)
- **`PIP_NO_CACHE_DIR=1`**: Reduces image size by not caching pip downloads
- **`PIP_DISABLE_PIP_VERSION_CHECK=1`**: Faster pip operations

#### Security Configuration
```dockerfile
# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Change ownership and switch user
RUN chown -R appuser:appuser /code
USER appuser
```

**Security Benefits:**
- **Principle of Least Privilege**: Application runs as non-root
- **Container Escape Mitigation**: Limits potential damage from vulnerabilities
- **Production Readiness**: Follows security best practices

#### Dependency Installation
```dockerfile
WORKDIR /code

# Copy requirements first (Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /code/app
```

**Layer Caching Strategy:**
- Dependencies installed before code copying
- Code changes don't invalidate dependency layer
- Faster rebuilds during development
- Optimized CI/CD pipeline performance

#### Runtime Configuration
```dockerfile
EXPOSE 8182
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8182"]
```

**Runtime Setup:**
- **Port Declaration**: Documents expected port for orchestration
- **Module Execution**: Uses Python module syntax for proper path resolution
- **Host Binding**: `0.0.0.0` allows external connections in containers
- **Production Server**: Uvicorn ASGI server for async performance

---

## Docker Compose Configuration

### File: `docker-compose-elasticsearch.yml`

#### Project Configuration
```yaml
name: elasticsearch-stack-newsgroups
```

**Benefits:**
- **Namespace Isolation**: Prevents conflicts with other projects
- **Resource Grouping**: Clear identification of related containers
- **Management Simplification**: Easy stack operations

#### Network Configuration
```yaml
networks:
  elastic_network:
    driver: bridge
```

**Network Strategy:**
- **Custom Bridge**: Isolated network for container communication
- **Service Discovery**: Containers accessible by name
- **Security**: Network-level isolation from other Docker projects
- **Performance**: Direct container-to-container communication

#### Volume Management
```yaml
volumes:
  elasticsearch_data_newsgroups:
```

**Data Persistence:**
- **Named Volume**: Docker-managed storage
- **Automatic Backup**: Can be backed up with Docker tools
- **Cross-Platform**: Works on Linux, macOS, and Windows
- **Performance**: Optimized for container I/O patterns

---

## Development Workflow

### Local Development Setup

#### Quick Start
```bash
# Start the complete stack
docker-compose -f docker-compose-elasticsearch.yml up -d

# Check service health
docker-compose -f docker-compose-elasticsearch.yml ps

# View logs
docker-compose -f docker-compose-elasticsearch.yml logs -f newsgroups
```

#### Individual Service Management
```bash
# Start only Elasticsearch and Kibana
docker-compose -f docker-compose-elasticsearch.yml up -d elasticsearch kibana

# Rebuild and restart FastAPI app
docker-compose -f docker-compose-elasticsearch.yml up -d --build newsgroups

# Scale services (if needed)
docker-compose -f docker-compose-elasticsearch.yml up -d --scale newsgroups=3
```

### Development vs Production Differences

#### Development Configuration
- **Security**: Disabled for ease of use
- **Resources**: Lower memory limits (512MB for Elasticsearch)
- **Logging**: Verbose logging for debugging
- **Networking**: All ports exposed for direct access

#### Production Adjustments Needed
```yaml
# Production elasticsearch configuration
elasticsearch:
  environment:
    - xpack.security.enabled=true          # Enable security
    - "ES_JAVA_OPTS=-Xms2g -Xmx2g"        # Increase memory
    - cluster.name=newsgroups-prod         # Cluster naming
  deploy:
    resources:
      limits:
        memory: 4g                         # Resource limits
      reservations:
        memory: 2g
```

---

## Monitoring and Maintenance

### Health Monitoring

#### Container Health Status
```bash
# Check all container health
docker-compose -f docker-compose-elasticsearch.yml ps

# View health check logs
docker inspect <container_name> --format='{{.State.Health}}'
```

#### Service-Specific Health Checks
```bash
# Elasticsearch cluster health
curl http://localhost:9200/_cluster/health

# API health endpoint
curl http://localhost:8182/health

# Kibana status
curl http://localhost:5601/api/status
```

### Log Management

#### Real-time Monitoring
```bash
# Follow all logs
docker-compose -f docker-compose-elasticsearch.yml logs -f

# Service-specific logs
docker-compose -f docker-compose-elasticsearch.yml logs -f elasticsearch
docker-compose -f docker-compose-elasticsearch.yml logs -f newsgroups
```

#### Log Analysis
```bash
# Search logs for errors
docker-compose -f docker-compose-elasticsearch.yml logs | grep ERROR

# Filter by timestamp
docker-compose -f docker-compose-elasticsearch.yml logs --since="1h" elasticsearch
```

### Data Management

#### Backup Operations
```bash
# Create volume backup
docker run --rm -v elasticsearch_data_newsgroups:/data -v $(pwd):/backup alpine tar czf /backup/elasticsearch-backup-$(date +%Y%m%d).tar.gz -C /data .

# Restore volume backup
docker run --rm -v elasticsearch_data_newsgroups:/data -v $(pwd):/backup alpine tar xzf /backup/elasticsearch-backup-20240115.tar.gz -C /data
```

#### Data Reset
```bash
# Stop services and remove volumes
docker-compose -f docker-compose-elasticsearch.yml down -v

# Start fresh (will recreate sample data)
docker-compose -f docker-compose-elasticsearch.yml up -d
```

---

## Troubleshooting Guide

### Common Issues

#### 1. Elasticsearch Won't Start
**Symptoms:**
- Container exits immediately
- "max virtual memory areas vm.max_map_count [65530] too low"

**Solution:**
```bash
# Linux/macOS
sudo sysctl -w vm.max_map_count=262144

# Make permanent (Linux)
echo 'vm.max_map_count=262144' | sudo tee -a /etc/sysctl.conf

# Windows/macOS Docker Desktop
# Increase memory allocation in Docker Desktop settings
```

#### 2. API Can't Connect to Elasticsearch
**Symptoms:**
- API returns 500 errors
- "Connection refused" in logs

**Debug Steps:**
```bash
# Check Elasticsearch health
curl http://localhost:9200/_cluster/health

# Verify network connectivity
docker network inspect elasticsearch-stack-newsgroups_elastic_network

# Check API logs
docker-compose -f docker-compose-elasticsearch.yml logs newsgroups
```

#### 3. Port Conflicts
**Symptoms:**
- "Port already in use" errors
- Services fail to start

**Solution:**
```bash
# Find process using port
sudo lsof -i :9200
sudo lsof -i :8182

# Kill conflicting processes or change ports in docker-compose.yml
```

#### 4. Slow Performance
**Symptoms:**
- Slow API responses
- High memory usage

**Optimization:**
```bash
# Increase Elasticsearch memory
# Edit docker-compose.yml:
# ES_JAVA_OPTS=-Xms1g -Xmx1g

# Monitor resource usage
docker stats

# Clean up unused resources
docker system prune
```

---

## Performance Optimization

### Resource Allocation

#### Memory Configuration
```yaml
# Elasticsearch memory tuning
environment:
  - "ES_JAVA_OPTS=-Xms1g -Xmx1g"  # Production: 50% of available RAM
  
# Container resource limits (Docker Compose v3.8+)
deploy:
  resources:
    limits:
      memory: 2g
    reservations:
      memory: 1g
```

#### CPU Optimization
```yaml
# Multi-core utilization
deploy:
  resources:
    limits:
      cpus: '2.0'
    reservations:
      cpus: '1.0'
```

### Networking Performance

#### Container Communication
- Use internal Docker networks (no localhost calls)
- Container name resolution (e.g., `elasticsearch:9200`)
- Avoid unnecessary port mappings for internal services

#### Load Balancing (Future)
```yaml
# Multiple FastAPI instances
services:
  newsgroups:
    deploy:
      replicas: 3
  
  nginx:
    image: nginx:alpine
    # Load balancer configuration
```

---

## Security Considerations

### Development Security
- **Network Isolation**: Custom Docker network
- **Non-root Users**: All containers run as non-root
- **Minimal Attack Surface**: Slim base images
- **No Secrets in Images**: Environment variables for configuration

### Production Security Checklist
- [ ] Enable Elasticsearch authentication
- [ ] Use HTTPS/TLS encryption
- [ ] Implement proper firewall rules
- [ ] Regular security updates
- [ ] Secrets management (Docker secrets/Kubernetes secrets)
- [ ] Container image scanning
- [ ] Runtime security monitoring

This Docker configuration provides a solid foundation for both development and production deployments of the 20 Newsgroups Search API.