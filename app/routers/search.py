import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import get_es_service
from app.models import DocumentStatus, NewsCategory, SearchResponse
from app.services.elasticsearch_service import ElasticsearchService

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=SearchResponse)
async def search_documents(
    q: Optional[str] = None,
    category: Optional[NewsCategory] = None,
    tags: Optional[List[str]] = Query(None),
    author: Optional[str] = None,
    status: Optional[DocumentStatus] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: ElasticsearchService = Depends(get_es_service)
):
    """Advanced search with multiple filters"""
    try:
        result = await service.search_documents(
            query=q,
            category=category.value if category else None,
            tags=tags,
            author=author,
            status=status.value if status else None,
            limit=limit,
            offset=offset
        )
        logger.info(f"Search completed: {result.total_hits} results found")
        return result
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/categories")
async def list_categories():
    """List all available newsgroup categories"""
    return {
        "categories": [category.value for category in NewsCategory],
        "total_categories": len(NewsCategory)
    }