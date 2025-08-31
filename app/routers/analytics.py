import logging

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_es_service
from app.models import DocumentStatus, NewsCategory

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/stats")
async def get_analytics_stats(
        service=Depends(get_es_service)
):
    """Get basic analytics about the document collection"""
    try:
        # Total documents
        total_docs = await service.search_documents(limit=0)

        # Documents by category (sample a few key categories)
        categories = {}
        sample_categories = [
            NewsCategory.SCI_SPACE,
            NewsCategory.COMP_GRAPHICS,
            NewsCategory.REC_SPORT_BASEBALL,
            NewsCategory.TALK_POLITICS_MISC,
            NewsCategory.SCI_MED
        ]

        for category in sample_categories:
            cat_result = await service.search_documents(category=category.value, limit=0)
            categories[category.value] = cat_result.total_hits

        # Documents by status
        statuses = {}
        for status in DocumentStatus:
            status_result = await service.search_documents(status=status.value, limit=0)
            statuses[status.value] = status_result.total_hits

        return {
            "total_documents": total_docs.total_hits,
            "sample_categories": categories,
            "statuses": statuses,
            "note": "sample_categories shows only a subset of all available categories"
        }
    except Exception as e:
        logger.error(f"Failed to get analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")


@router.get("/categories")
async def get_category_breakdown(
        service=Depends(get_es_service)
):
    """Get document count for all categories"""
    try:
        categories = {}
        for category in NewsCategory:
            cat_result = await service.search_documents(category=category.value, limit=0)
            categories[category.value] = cat_result.total_hits

        return {
            "categories": categories,
            "total_categories": len([c for c in categories.values() if c > 0])
        }
    except Exception as e:
        logger.error(f"Failed to get category breakdown: {e}")
        raise HTTPException(status_code=500, detail=f"Category breakdown failed: {str(e)}")