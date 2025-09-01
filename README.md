# 20 Newsgroups Search API

FastAPI application with full CRUD operations for 20 newsgroups dataset, backed by Elasticsearch.

## Quick Start

### 1. Start Services
```bash
docker-compose -f docker-compose-elasticsearch.yml up -d
```

### 2. Check Health
```bash
curl http://localhost:8182/health
```

### 3. View API Docs
Open: http://localhost:8182/docs

## Key Features

- **Full CRUD**: Create, Read, Update, Delete documents
- **Advanced Search**: Multi-field search with category/tag/author filters
- **Real Data**: Load 20newsgroups dataset via scikit-learn
- **Bulk Operations**: Bulk document creation
- **Analytics**: Document statistics

## API Endpoints

### Documents
- `POST /documents` - Create document
- `GET /documents/{id}` - Get document
- `PUT /documents/{id}` - Update document
- `DELETE /documents/{id}` - Delete document
- `POST /documents/bulk` - Bulk create

### Search
- `GET /search?q=term&category=sci.space&limit=10`
- `GET /search/categories` - List all categories

### Data Loading
- `POST /data/load-20newsgroups?subset=train&max_documents=1000`
- `POST /data/load-sample` - Load sample data

### Analytics
- `GET /analytics/stats` - Collection statistics
- `GET /analytics/categories` - Category breakdown

## Example Usage

### Load Real Data
```bash
curl -X POST "http://localhost:8182/data/load-20newsgroups?subset=train&max_documents=500"
```

### Search
```bash
curl "http://localhost:8182/search?q=space&category=sci.space&limit=5"
```

### Create Document
```bash
curl -X POST "http://localhost:8182/documents" \
-H "Content-Type: application/json" \
-d '{
  "title": "New Discussion Topic",
  "body": "This is a test post...",
  "category": "sci.space",
  "author": "test_user",
  "tags": ["test", "space"]
}'
```

## Services

| Service | URL | Purpose |
|---------|-----|---------|
| API | http://localhost:8182 | FastAPI app |
| Elasticsearch | http://localhost:9200 | Search engine |
| Kibana | http://localhost:5601 | Data visualization |

## Environment Variables

Set these in docker-compose or .env file:

```env
ELASTICSEARCH_PROTOCOL=http
ELASTICSEARCH_HOST=elasticsearch
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_INDEX=newsgroups
LOG_LEVEL=INFO
DEFAULT_MAX_DOCUMENTS=1000
```

## 20 Newsgroups Categories

The API supports all 20 original newsgroup categories:
- `alt.atheism`
- `comp.graphics`
- `comp.os.ms-windows.misc`
- `comp.sys.ibm.pc.hardware`
- `comp.sys.mac.hardware`
- `comp.windows.x`
- `misc.forsale`
- `rec.autos`
- `rec.motorcycles`
- `rec.sport.baseball`
- `rec.sport.hockey`
- `sci.crypt`
- `sci.electronics`
- `sci.med`
- `sci.space`
- `soc.religion.christian`
- `talk.politics.guns`
- `talk.politics.mideast`
- `talk.politics.misc`
- `talk.religion.misc`

## Requirements

- Docker & Docker Compose
- Python 3.13+ (for local development)
- scikit-learn (automatically installed)

## Data Persistence

Elasticsearch data is persisted in Docker volume `elasticsearch_data_newsgroups`.