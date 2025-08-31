import logging
import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from elasticsearch import Elasticsearch

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from services.elasticsearch_service import ElasticsearchService
from services.data_loader import NewsDataLoader
from models import DocumentCreate
from routers import documents, search, data, analytics
import dependencies

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Global variables
es_client = None
es_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global es_client, es_service

    logger.info("Starting application lifespan startup")

    try:
        # Initialize Elasticsearch client
        es_url = f"{config.ELESTICSEARCH_WWW}://{config.ELESTICSEARCH_HOST}:{config.ELESTICSEARCH_PORT}/"
        logger.info(f"Initializing Elasticsearch client with URL: {es_url}")
        es_client = Elasticsearch(es_url)

        # Test connection
        if not es_client.ping():
            raise Exception("Elasticsearch connection failed")
        logger.info("Elasticsearch connection successful")

        # Initialize service
        es_service = ElasticsearchService(es_client, config.ELESTICSEARCH_INDEX)
        await es_service.initialize_index()

        # Set the service in dependencies
        dependencies.set_es_service(es_service)

        # Load sample data if index is empty
        search_result = await es_service.search_documents(limit=1)
        if search_result.total_hits == 0:
            logger.info("Index is empty, loading sample data...")
            sample_data = NewsDataLoader.load_sample_data()
            documents = [DocumentCreate(**doc) for doc in sample_data]
            bulk_result = await es_service.bulk_create_documents(documents)
            logger.info(f"Loaded {bulk_result['success_count']} sample documents")

        logger.info("Application startup completed successfully")

    except Exception as e:
        logger.error(f"Error during application startup: {str(e)}")
        raise

    yield

    logger.info("Application shutdown completed")


def get_es_service():
    if es_service is None:
        raise Exception("Elasticsearch service not initialized")
    return es_service


# Create FastAPI app
app = FastAPI(
    title="20 Newsgroups Search API",
    description="A full CRUD API for newsgroup documents with Elasticsearch backend",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency injection
app.dependency_overrides = {}

# Include routers
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(search.router, prefix="/search", tags=["search"])
app.include_router(data.router, prefix="/data", tags=["data"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    try:
        if es_client and es_client.ping():
            return {"status": "healthy", "elasticsearch": "connected"}
        else:
            return {"status": "unhealthy", "elasticsearch": "disconnected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    return {
        "message": "20 Newsgroups Search API",
        "version": "2.0.0",
        "description": "CRUD API for 20newsgroups dataset with Elasticsearch",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "documents": "/documents/*",
            "search": "/search",
            "data": "/data/*",
            "analytics": "/analytics/*"
        }
    }


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting uvicorn server")
    uvicorn.run(app, host="0.0.0.0", port=8182)