from typing import Optional
from fastapi import HTTPException
from app.services.elasticsearch_service import ElasticsearchService

# Private module variable to store the service instance
_es_service: Optional[ElasticsearchService] = None

def set_es_service(service: ElasticsearchService) -> None:
    """Set the Elasticsearch service instance. Called during app startup."""
    global _es_service
    _es_service = service

def get_es_service() -> ElasticsearchService:
    """Dependency function to get the Elasticsearch service instance."""
    if _es_service is None:
        raise HTTPException(
            status_code=500,
            detail="Elasticsearch service not initialized. Please check application startup logs."
        )
    return _es_service

def is_service_ready() -> bool:
    """Check if the service is ready to use."""
    return _es_service is not None

def cleanup_service() -> None:
    """Cleanup the service instance. Called during app shutdown if needed."""
    global _es_service
    _es_service = None