# Troubleshooting Guide

This guide covers common issues you might encounter while developing, deploying, or using the 20 Newsgroups Search API, along with step-by-step solutions.

---

## 🚨 Critical Issues (Service Down)

### 1. API Returns 500 "Elasticsearch service not initialized"

**Symptoms:**
```bash
curl http://localhost:8182/health
# {"status": "unhealthy", "error": "Elasticsearch service not initialized..."}
```

**Root Cause:** FastAPI started but couldn't connect to Elasticsearch during initialization.

**Debugging Steps:**
```bash
# 1. Check if Elasticsearch is running
curl http://localhost:9200
# Should return JSON with cluster info

# 2. Check Elasticsearch health
curl http://localhost:9200/_cluster/health
# Should show "status": "green" or "yellow"

# 3. Check Docker containers
docker-compose -f docker-compose-elasticsearch.yml ps
# elasticsearch should be "healthy"

# 4. Check API logs
docker-compose -f docker-compose-elasticsearch.yml logs newsgroups
# Look for connection errors
```

**Solutions:**

#### Option A: Elasticsearch Not Running
```bash
# Start Elasticsearch
docker-compose -f docker-compose-elasticsearch.yml up -d elasticsearch

# Wait for it to be healthy (60+ seconds)
docker-compose -f docker-compose-elasticsearch.yml logs -f elasticsearch
# Look for "started"

# Restart API
docker-compose -f docker-compose-elasticsearch.yml restart newsgroups
```

#### Option B: Wrong Configuration
```bash
# Check environment variables
docker-compose -f docker-compose-elasticsearch.yml exec newsgroups env | grep ELASTICSEARCH
# Should show: ELASTICSEARCH_HOST=elasticsearch

# If using local development:
export ELASTICSEARCH_HOST=localhost  # not 'elasticsearch'
```

#### Option C: Network Issues
```bash
# Check Docker network
docker network ls | grep elastic
# Should show the network

# Test connection from API container
docker-compose exec newsgroups curl http://elasticsearch:9200
# Should return Elasticsearch info
```

---

### 2. Elasticsearch Won't Start / Keeps Crashing

**Symptoms:**
```bash
docker-compose logs elasticsearch
# elasticsearch_1 | ERROR: [1] bootstrap checks failed
# elasticsearch_1 | [1]: max virtual memory areas vm.max_map_count [65530] too low, increase to at least [262144]
```

**Root Cause:** System virtual memory limits too low for Elasticsearch.

**Solutions:**

#### Linux/macOS:
```bash
# Check current value
sysctl vm.max_map_count
# If < 262144, increase it:

sudo sysctl -w vm.max_map_count=262144

# Make permanent
echo 'vm.max_map_count=262144' | sudo tee -a /etc/sysctl.conf
```

#### Windows (Docker Desktop):
```powershell
# In PowerShell as Administrator
wsl -d docker-desktop
sysctl -w vm.max_map_count=262144
exit
```

#### Alternative: Reduce Elasticsearch Memory
```yaml
# In docker-compose-elasticsearch.yml
environment:
  - "ES_JAVA_OPTS=-Xms256m -Xmx256m"  # Reduce from 512m
```

**Other Elasticsearch Startup Issues:**
```bash
# Check disk space
df -h
# Elasticsearch needs at least 1GB free

# Check memory
free -h
# Need at least 1GB available RAM

# Check port conflicts
lsof -i :9200
# Kill conflicting processes if found
```

---

## 🔧 Configuration Issues

### 3. Wrong Elasticsearch Index/Data Missing

**Symptoms:**
```bash
curl http://localhost:8182/analytics/stats
# {"total_documents": 0}
# Even after loading data
```

**Debugging:**
```bash
# 1. Check which index is configured
echo $ELASTICSEARCH_INDEX
# Or check in docker-compose.yml

# 2. List all indices in Elasticsearch
curl http://localhost:9200/_cat/indices
# Look for your index name

# 3. Check index contents directly
curl "http://localhost:9200/newsgroups/_search?size=0"
# Should show document count
```

**Solutions:**
```bash
# Option A: Load data into correct index
curl -X POST http://localhost:8182/data/load-sample

# Option B: Fix index name
# Edit docker-compose-elasticsearch.yml:
# - ELASTICSEARCH_INDEX=newsgroups  # correct name

# Option C: Reset everything
docker-compose down -v  # Removes volumes
docker-compose up -d
# Will recreate index and load sample data
```

---

### 4. Port Conflicts

**Symptoms:**
```bash
docker-compose up -d
# ERROR: for elasticsearch  Cannot start service elasticsearch: 
# Ports are not available: listen tcp 0.0.0.0:9200: bind: address already in use
```

**Find Conflicting Process:**
```bash
# Linux/macOS
lsof -i :9200
lsof -i :8182
lsof -i :5601

# Windows
netstat -ano | findstr :9200
```

**Solutions:**
```bash
# Option A: Kill conflicting process
sudo kill -9 <PID>

# Option B: Use different ports
# Edit docker-compose-elasticsearch.yml:
ports:
  - "9201:9200"  # Use 9201 instead of 9200
environment:
  - ELASTICSEARCH_PORT=9201  # Update API config too
```

---

## 📊 Data Loading Issues

### 5. scikit-learn Dataset Won't Load

**Symptoms:**
```bash
curl -X POST "http://localhost:8182/data/load-20newsgroups"
# Returns 200 OK but no data appears

# Check logs:
docker-compose logs newsgroups
# "scikit-learn is required to load 20newsgroups dataset"
```

**Root Cause:** scikit-learn not installed or import failing.

**Solutions:**
```bash
# Option A: Verify installation in container
docker-compose exec newsgroups python -c "import sklearn; print(sklearn.__version__)"
# Should print version number

# Option B: Rebuild container with dependencies
docker-compose build newsgroups
docker-compose up -d newsgroups

# Option C: Use sample data instead
curl -X POST http://localhost:8182/data/load-sample
```

---

### 6. Data Loading Hangs/Times Out

**Symptoms:**
```bash
curl -X POST "http://localhost:8182/data/load-20newsgroups?max_documents=5000"
# Request times out after 30+ seconds
```

**Root Cause:** Large dataset loading is slow, running in background but HTTP request times out.

**Expected Behavior:**
- API returns 200 immediately (background task started)
- Data loads asynchronously
- Check logs for completion

**Solutions:**
```bash
# 1. Check if loading is actually happening
docker-compose logs -f newsgroups
# Look for "20newsgroups data loading started" and progress

# 2. Monitor document count
watch -n 5 'curl -s http://localhost:8182/analytics/stats | jq .total_documents'

# 3. Start with smaller dataset
curl -X POST "http://localhost:8182/data/load-20newsgroups?max_documents=100"
```

---

## 🔍 Search & API Issues

### 7. Search Returns Empty Results

**Symptoms:**
```bash
curl "http://localhost:8182/search?q=machine learning"
# {"total_hits": 0, "documents": []}
```

**Debugging Steps:**
```bash
# 1. Check if data exists
curl http://localhost:8182/analytics/stats
# total_documents should be > 0

# 2. Check index directly
curl "http://localhost:9200/newsgroups/_search?q=machine"
# Should return results if data exists

# 3. Test simple search
curl "http://localhost:8182/search"
# Should return all documents
```

**Common Causes & Solutions:**

#### Wrong Index Name:
```bash
# Check configured index
docker-compose exec newsgroups env | grep ELASTICSEARCH_INDEX

# Should match:
curl http://localhost:9200/_cat/indices | grep newsgroups
```

#### Index Not Refreshed:
```bash
# Force refresh
curl -X POST "http://localhost:9200/newsgroups/_refresh"

# Then test search again
```

#### Query Syntax Issues:
```bash
# Test with simple terms
curl "http://localhost:8182/search?q=test"

# Avoid special characters
curl "http://localhost:8182/search?q=machine%20learning"  # URL encoded
```

---

### 8. API Documentation Not Loading

**Symptoms:**
```bash
curl http://localhost:8182/docs
# 404 Not Found or blank page
```

**Solutions:**
```bash
# 1. Check if API is actually running
curl http://localhost:8182/health
# Should return JSON health status

# 2. Try alternative documentation
curl http://localhost:8182/redoc

# 3. Check for JavaScript errors in browser console
# 4. Try in incognito/private mode

# 5. Access raw OpenAPI schema
curl http://localhost:8182/openapi.json | jq
```

---

## 🐳 Docker-Specific Issues

### 9. Container Keeps Restarting

**Check Restart Status:**
```bash
docker-compose ps
# If restart count is high, there's a crash loop
```

**Debugging:**
```bash
# 1. Check container logs
docker-compose logs newsgroups
# Look for Python tracebacks or startup errors

# 2. Check exit code
docker inspect <container_name> | jq '.[0].State.ExitCode'

# 3. Run container interactively for debugging
docker-compose run --rm newsgroups bash
# Then manually start the app to see errors
```

**Common Solutions:**
```bash
# Fix 1: Environment variable issues
docker-compose config  # Validate compose file

# Fix 2: Dependency missing
docker-compose build --no-cache newsgroups

# Fix 3: Permission issues
docker-compose exec newsgroups ls -la /code
# Should show files owned by appuser
```

---

### 10. Volume Permission Issues

**Symptoms:**
```bash
docker-compose logs elasticsearch
# "AccessDeniedException[/usr/share/elasticsearch/data/nodes]"
```

**Solutions:**
```bash
# Option A: Reset volume permissions
docker-compose down -v
docker volume rm elasticsearch-stack-newsgroups_elasticsearch_data_newsgroups
docker-compose up -d

# Option B: Fix existing volume
docker-compose exec elasticsearch chown -R elasticsearch:elasticsearch /usr/share/elasticsearch/data
```

---

## 🌐 Network & Connectivity Issues

### 11. Can't Access Services from Host

**Symptoms:**
```bash
curl http://localhost:8182/health
# Connection refused
```

**Debugging:**
```bash
# 1. Check if containers are running
docker-compose ps
# All services should be "Up"

# 2. Check port mapping
docker-compose port newsgroups 8182
# Should show 0.0.0.0:8182

# 3. Test from within Docker network
docker-compose exec elasticsearch curl http://newsgroups:8182/health
# Should work if API is running
```

**Solutions:**
```bash
# Fix 1: Firewall blocking ports
sudo ufw allow 8182  # Linux
# Or check Windows firewall settings

# Fix 2: Wrong host binding
# In docker-compose.yml, ensure:
command: ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8182"]
```

---

### 12. Internal Service Communication Issues

**Symptoms:**
```bash
# API logs show:
# "ConnectionError: Elasticsearch connection failed"
```

**Debugging:**
```bash
# 1. Test connectivity between containers
docker-compose exec newsgroups ping elasticsearch
# Should get ping responses

# 2. Test Elasticsearch access from API container
docker-compose exec newsgroups curl http://elasticsearch:9200
# Should return Elasticsearch info

# 3. Check Docker network
docker network inspect elasticsearch-stack-newsgroups_elastic_network
# Should show all containers connected
```

**Solutions:**
```bash
# Fix 1: Wrong hostname in config
# Check environment variables:
docker-compose exec newsgroups env | grep ELASTICSEARCH_HOST
# Should be "elasticsearch", not "localhost"

# Fix 2: Network issues
docker-compose down
docker network prune
docker-compose up -d
```

---

## 🔍 Performance Issues

### 13. Slow Search/API Responses

**Symptoms:**
- Search takes >5 seconds
- High CPU/memory usage
- Timeouts on complex queries

**Diagnosis:**
```bash
# 1. Check resource usage
docker stats

# 2. Monitor Elasticsearch performance
curl "http://localhost:9200/_nodes/stats/jvm,process,fs"

# 3. Check API response times
time curl "http://localhost:8182/search?q=test"

# 4. Check document count (too much data?)
curl http://localhost:8182/analytics/stats | jq .total_documents
```

**Solutions:**

#### Increase Memory:
```yaml
# In docker-compose.yml
environment:
  - "ES_JAVA_OPTS=-Xms1g -Xmx1g"  # Increase memory
```

#### Reduce Dataset Size:
```bash
# Clear large dataset
curl -X DELETE http://localhost:9200/newsgroups
curl -X POST http://localhost:8182/data/load-sample  # Load smaller dataset
```

#### Optimize Queries:
```bash
# Use filters instead of full-text search when possible
curl "http://localhost:8182/search?category=sci.space&limit=10"
# Instead of:
curl "http://localhost:8182/search?q=space&limit=10"
```

---

## 🧪 Development Issues

### 14. Code Changes Not Reflected

**Symptoms:**
- Made code changes but API behavior unchanged
- FastAPI not reloading

**For Docker Development:**
```bash
# 1. Rebuild container
docker-compose build newsgroups
docker-compose up -d newsgroups

# 2. Check if volume mounting works
docker-compose exec newsgroups ls -la /code/app
# Should show your latest files
```

**For Native Python Development:**
```bash
# 1. Ensure uvicorn reload is enabled
python -m uvicorn main:app --reload --port 8182

# 2. Check if Python cache is stale
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

---

### 15. Import/Module Errors

**Symptoms:**
```python
ModuleNotFoundError: No module named 'app.services'
ImportError: cannot import name 'get_es_service' from 'app.dependencies'
```

**Solutions:**
```bash
# 1. Check Python path
python -c "import sys; print(sys.path)"
# Current directory should be in path

# 2. Ensure you're in correct directory
pwd  # Should end with /app for native development

# 3. Check file structure
ls -la app/
# Should show all Python files

# 4. Verify __init__.py files exist
find app/ -name "__init__.py"
# Should show __init__.py in each package directory
```

---

## 🆘 Getting More Help

### Log Collection for Bug Reports
```bash
# Collect comprehensive logs
mkdir debug-logs
docker-compose logs > debug-logs/docker-compose.log
docker-compose config > debug-logs/config.yml
curl http://localhost:8182/health > debug-logs/health.json 2>&1
curl http://localhost:9200 > debug-logs/elasticsearch.json 2>&1

# System information
uname -a > debug-logs/system.txt
docker --version >> debug-logs/system.txt
docker-compose --version >> debug-logs/system.txt
```

### Common Commands Reference
```bash
# Complete system reset
docker-compose down -v
docker system prune -f
docker-compose up -d

# Service-specific restart
docker-compose restart newsgroups
docker-compose restart elasticsearch

# View logs in real-time
docker-compose logs -f
docker-compose logs -f newsgroups

# Execute commands inside containers
docker-compose exec newsgroups bash
docker-compose exec elasticsearch bash

# Check service health
curl http://localhost:8182/health
curl http://localhost:9200/_cluster/health
```

### When to File a Bug Report
- [ ] Followed this troubleshooting guide
- [ ] Issue is reproducible
- [ ] Collected logs and system information
- [ ] Searched existing issues
- [ ] Can provide minimal reproduction steps

### Emergency Recovery
```bash
# Nuclear option - reset everything
docker-compose down -v
docker system prune -a -f
docker volume prune -f
# Then follow setup guide from scratch
```

---

**Remember:** Most issues are configuration or environment-related. Start with the basics (health checks, logs, connectivity) before diving into complex debugging! 🔍