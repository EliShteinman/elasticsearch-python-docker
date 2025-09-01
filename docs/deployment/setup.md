# Local Development Setup

This guide covers multiple ways to set up the 20 Newsgroups Search API for local development, from quick Docker setup to full native Python development.

---

## 🚀 Quick Start (Recommended)

### Option 1: Docker Compose (Easiest)
Perfect for trying the API or frontend development.

```bash
# 1. Clone repository
git clone <repository-url>
cd 20newsgroups-search-api

# 2. Start all services
docker-compose -f docker-compose-elasticsearch.yml up -d

# 3. Wait for services to be ready (30-60 seconds)
docker-compose -f docker-compose-elasticsearch.yml logs -f

# 4. Test the API
curl http://localhost:8182/health
```

**Access Points:**
- **API**: http://localhost:8182
- **Swagger UI**: http://localhost:8182/docs
- **Kibana**: http://localhost:5601
- **Elasticsearch**: http://localhost:9200

---

## 🛠️ Native Python Development

### Prerequisites
- **Python 3.13+** (recommended) or 3.11+
- **pip** and **venv**
- **Docker** (for Elasticsearch only)
- **Git**

### System Requirements
- **Memory**: 4GB+ (Elasticsearch needs ~1GB)
- **Disk**: 2GB+ free space
- **OS**: Linux, macOS, or Windows with WSL2

---

### Step 1: Environment Setup

#### Create Python Virtual Environment
```bash
# Create project directory
mkdir 20newsgroups-dev
cd 20newsgroups-dev

# Clone repository
git clone <repository-url> .

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate

# On Windows:
# .venv\Scripts\activate

# Verify Python version
python --version  # Should be 3.11+
```

#### Install Python Dependencies
```bash
# Navigate to app directory
cd app

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "(fastapi|elasticsearch|pydantic)"
```

### Step 2: Start Elasticsearch (Docker)

Since Elasticsearch setup is complex, we'll use Docker for it:

```bash
# Start only Elasticsearch and Kibana (not the API)
docker-compose -f docker-compose-elasticsearch.yml up -d elasticsearch kibana

# Wait for Elasticsearch to be ready
curl -f http://localhost:9200/_cluster/health || echo "Waiting..."

# Check Elasticsearch is running
curl http://localhost:9200
# Should return JSON with cluster info
```

### Step 3: Configure Environment

#### Create Local Environment File
```bash
# Create .env file in project root
cat > .env << EOF
# Elasticsearch Configuration
ELASTICSEARCH_PROTOCOL=http
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_INDEX=newsgroups-dev

# Development Configuration  
LOG_LEVEL=DEBUG
DEFAULT_MAX_DOCUMENTS=500

# API Configuration
DEFAULT_SEARCH_LIMIT=10
MAX_SEARCH_LIMIT=100
EOF
```

#### Load Environment Variables
```bash
# On Linux/macOS:
export $(cat .env | xargs)

# On Windows PowerShell:
# Get-Content .env | ForEach-Object { $name, $value = $_.split('='); Set-Item -Path "env:$name" -Value $value }

# Verify environment variables
echo $ELASTICSEARCH_HOST  # Should print: localhost
```

### Step 4: Run the API Locally

#### Start the FastAPI Development Server
```bash
# From the app directory
cd app

# Run with uvicorn directly
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8182

# Alternative: Using Python directly  
python main.py
```

**Expected Output:**
```
INFO:     Will watch for changes in these directories: ['/path/to/app']
INFO:     Uvicorn running on http://0.0.0.0:8182 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     - Elasticsearch connection successful
INFO:     - Index newsgroups-dev created successfully  
INFO:     - Application startup completed successfully
```

#### Test the Local API
```bash
# Health check
curl http://localhost:8182/health

# API documentation
open http://localhost:8182/docs

# Test search (should be empty initially)
curl http://localhost:8182/search | jq
```

### Step 5: Load Test Data

#### Load Sample Data
```bash
# Load 5 sample documents
curl -X POST http://localhost:8182/data/load-sample

# Verify data loaded
curl http://localhost:8182/analytics/stats | jq '.total_documents'
# Should return: 5
```

#### Load Real 20newsgroups Data (Optional)
```bash
# Load 100 real documents for testing
curl -X POST "http://localhost:8182/data/load-20newsgroups?max_documents=100&subset=train"

# Check loading progress in logs
# Wait 30-60 seconds, then verify
curl http://localhost:8182/analytics/stats | jq
```

---

## 🔧 Development Tools Setup

### IDE Configuration

#### VS Code Setup
```bash
# Install recommended extensions
code --install-extension ms-python.python
code --install-extension ms-python.pylint
code --install-extension charliermarsh.ruff

# Create VS Code workspace settings
mkdir .vscode
cat > .vscode/settings.json << EOF
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
EOF
```

#### PyCharm Setup
1. Open project directory in PyCharm
2. Configure Python interpreter → `.venv/bin/python`
3. Enable FastAPI support in settings
4. Configure run configuration:
   - **Script path**: `app/main.py`
   - **Working directory**: `app/`
   - **Environment variables**: Load from `.env`

### Code Quality Tools

#### Install Development Dependencies
```bash
# Install additional dev tools
pip install black isort mypy pytest pytest-asyncio httpx

# Create requirements-dev.txt
cat > requirements-dev.txt << EOF
black==24.1.0
isort==5.13.0  
mypy==1.8.0
pytest==7.4.0
pytest-asyncio==0.23.0
httpx==0.26.0
EOF

pip install -r requirements-dev.txt
```

#### Code Formatting
```bash
# Format code with Black
black app/

# Sort imports with isort  
isort app/

# Type checking with mypy
mypy app/
```

#### Pre-commit Hooks (Optional)
```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black
        language_version: python3
        
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
EOF

# Install pre-commit hooks
pre-commit install
```

---

## 🧪 Testing Setup

### Run Tests
```bash
# Install test dependencies (if not already installed)
pip install pytest pytest-asyncio httpx

# Run tests (when test files are created)
pytest tests/ -v

# Run with coverage
pip install pytest-cov
pytest tests/ --cov=app --cov-report=html
```

### Manual API Testing

#### Using curl
```bash
# Test document creation
curl -X POST http://localhost:8182/documents/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Document",
    "body": "This is a test document for development",
    "category": "comp.graphics",
    "author": "dev_user",
    "tags": ["test", "development"]
  }'

# Test search
curl "http://localhost:8182/search?q=test&limit=5" | jq

# Test analytics
curl http://localhost:8182/analytics/stats | jq
```

#### Using Python Requests
```python
# Create test_api.py
import requests

base_url = "http://localhost:8182"

# Test health
health = requests.get(f"{base_url}/health")
print(f"Health: {health.json()}")

# Test search
search = requests.get(f"{base_url}/search", params={"q": "test"})
print(f"Search results: {search.json()}")
```

---

## 🐛 Debugging Setup

### Logging Configuration
```bash
# Set debug logging
export LOG_LEVEL=DEBUG

# Restart API to see debug logs
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8182
```

### Debug with Python Debugger
```python
# Add breakpoints in your code
import pdb; pdb.set_trace()

# Or use ipdb for better experience
pip install ipdb
import ipdb; ipdb.set_trace()
```

### VS Code Debugging
Create `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "FastAPI Debug",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/.venv/bin/uvicorn",
            "args": [
                "app.main:app",
                "--reload",
                "--host", "0.0.0.0", 
                "--port", "8182"
            ],
            "cwd": "${workspaceFolder}",
            "envFile": "${workspaceFolder}/.env",
            "console": "integratedTerminal"
        }
    ]
}
```

---

## 🔄 Hot Reload Development

### Automatic Code Reloading
The `--reload` flag automatically restarts the server when Python files change:

```bash
# Start with reload (already included above)
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8182

# Watch for changes in specific directories
python -m uvicorn main:app --reload --reload-dir app/ --host 0.0.0.0 --port 8182
```

### File Watching Tips
- **Excluded**: `__pycache__`, `.pyc`, `.git`, `logs/`
- **Included**: `.py`, `.yml`, `.json`, `.md` files
- **Restart time**: Usually < 2 seconds

---

## 🧹 Cleanup & Reset

### Reset Development Data
```bash
# Clear Elasticsearch data
curl -X DELETE http://localhost:9200/newsgroups-dev

# Restart API (it will recreate the index)
# Load fresh sample data
curl -X POST http://localhost:8182/data/load-sample
```

### Full Environment Reset
```bash
# Stop all services
docker-compose -f docker-compose-elasticsearch.yml down -v

# Remove Python virtual environment  
deactivate
rm -rf .venv

# Start fresh
python -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt
```

---

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using port 8182
lsof -i :8182

# Kill process
kill -9 <PID>

# Or use different port
python -m uvicorn main:app --port 8183
```

#### 2. Elasticsearch Connection Failed
```bash
# Check if Elasticsearch is running
curl http://localhost:9200
docker-compose logs elasticsearch

# Restart Elasticsearch
docker-compose restart elasticsearch
```

#### 3. Module Not Found Errors
```bash
# Ensure you're in the app directory
cd app
pwd  # Should end with /app

# Ensure virtual environment is activated
which python  # Should point to .venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

#### 4. scikit-learn Dataset Issues
```bash
# If you get scikit-learn errors:
pip install scikit-learn==1.7.1

# Test scikit-learn installation
python -c "from sklearn.datasets import fetch_20newsgroups; print('OK')"
```

### Getting Help
- **Logs**: Check `docker-compose logs` for service issues
- **API Logs**: Check FastAPI console output for Python errors
- **Health Check**: Always start with `curl http://localhost:8182/health`
- **Documentation**: See [troubleshooting guide](troubleshooting.md)

---

## 🎯 Development Workflow

### Recommended Development Process
1. **Start Elasticsearch**: `docker-compose up -d elasticsearch kibana`
2. **Activate Python environment**: `source .venv/bin/activate`
3. **Start API with reload**: `python -m uvicorn main:app --reload --port 8182`
4. **Load test data**: `curl -X POST http://localhost:8182/data/load-sample`
5. **Open Swagger UI**: http://localhost:8182/docs
6. **Make changes and test**: Code changes auto-reload
7. **Check Kibana**: http://localhost:5601 for data visualization

### Development Best Practices
- **Use DEBUG logging** for development
- **Test changes** with sample data first
- **Check health endpoint** after changes
- **Use Swagger UI** for interactive testing
- **Monitor logs** for errors and warnings
- **Clean data** regularly to avoid stale state

---

## 📈 Performance Tips

### Local Development Optimization
```bash
# Increase Elasticsearch memory (if you have RAM)
# Edit docker-compose-elasticsearch.yml:
# ES_JAVA_OPTS=-Xms1g -Xmx1g

# Use smaller dataset for faster loading
curl -X POST "http://localhost:8182/data/load-20newsgroups?max_documents=50"

# Enable FastAPI debug toolbar (optional)
pip install fastapi-debug-toolbar
```

### Resource Usage
- **Elasticsearch**: ~512MB-1GB RAM
- **FastAPI**: ~50-100MB RAM
- **Total**: ~1-2GB RAM for comfortable development

---

This completes your local development setup! You now have a fully functional development environment for the 20 Newsgroups Search API. 🚀