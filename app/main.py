import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from elasticsearch import Elasticsearch

from app import config, dependencies
from app.services.elasticsearch_service import ElasticsearchService
from app.services.data_loader import NewsDataLoader
from app.models import DocumentCreate
from app.routers import documents, search, data, analytics

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application lifespan startup")

    try:
        # Initialize Elasticsearch client
        es_url = f"{config.ELASTICSEARCH_PROTOCOL}://{config.ELASTICSEARCH_HOST}:{config.ELASTICSEARCH_PORT}/"
        logger.info(f"Initializing Elasticsearch client with URL: {es_url}")
        es_client = Elasticsearch(es_url)

        # Test connection
        if not es_client.ping():
            raise Exception("Elasticsearch connection failed")
        logger.info("Elasticsearch connection successful")

        # Initialize service
        es_service = ElasticsearchService(es_client, config.ELASTICSEARCH_INDEX)
        await es_service.initialize_index()

        # Set the service in dependencies (this is the proper way)
        dependencies.set_es_service(es_service)

        # Load sample data if index is empty
        search_result = await es_service.search_documents(limit=1)
        if search_result.total_hits == 0:
            logger.info("Index is empty, loading sample data...")
            sample_data = NewsDataLoader.load_sample_data()
            documents_data = [DocumentCreate(**doc) for doc in sample_data]
            bulk_result = await es_service.bulk_create_documents(documents_data)
            logger.info(f"Loaded {bulk_result['success_count']} sample documents")

        logger.info("Application startup completed successfully")

    except Exception as e:
        logger.error(f"Error during application startup: {str(e)}")
        raise

    yield

    logger.info("Application shutdown completed")


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

# Include routers
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(search.router, prefix="/search", tags=["search"])
app.include_router(data.router, prefix="/data", tags=["data"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    try:
        # Get service through proper dependency injection
        service = dependencies.get_es_service()
        # Simple check - if we can get the service, ES should be connected
        await service.search_documents(limit=0)
        return {"status": "healthy", "elasticsearch": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "elasticsearch": "disconnected", "error": str(e)}


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