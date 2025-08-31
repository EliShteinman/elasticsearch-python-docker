import logging
from typing import List, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query

from app.dependencies import get_es_service
from app.models import DocumentCreate
from app.services.data_loader import NewsDataLoader
from app.services.elasticsearch_service import ElasticsearchService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/load-20newsgroups")
async def load_20newsgroups_data(
        background_tasks: BackgroundTasks,
        subset: str = Query("train", description="Dataset subset: train, test, or all"),
        max_documents: int = Query(1000, ge=1, le=5000, description="Maximum documents to load"),
        categories: Optional[List[str]] = Query(None, description="Specific categories to load"),
        service: ElasticsearchService = Depends(get_es_service)
):
    """Load real data from 20newsgroups dataset"""

    async def load_newsgroups_data():
        try:
            newsgroups_data = NewsDataLoader.load_20newsgroups_data(
                subset=subset,
                categories=categories,
                max_documents=max_documents
            )

            if newsgroups_data:
                documents = [DocumentCreate(**doc) for doc in newsgroups_data]
                result = await service.bulk_create_documents(documents)
                logger.info(f"20newsgroups data loaded: {result['success_count']} documents")
            else:
                logger.warning("No 20newsgroups data retrieved")
        except Exception as e:
            logger.error(f"Failed to load 20newsgroups data: {e}")

    background_tasks.add_task(load_newsgroups_data)
    return {
        "message": f"20newsgroups data loading started (subset: {subset}, max: {max_documents})",
        "note": "scikit-learn is required for this operation"
    }


@router.post("/load-sample")
async def load_sample_data(
        background_tasks: BackgroundTasks,
        service: ElasticsearchService = Depends(get_es_service)
):
    """Load sample news data"""

    async def load_data():
        try:
            sample_data = NewsDataLoader.load_sample_data()
            documents = [DocumentCreate(**doc) for doc in sample_data]
            result = await service.bulk_create_documents(documents)
            logger.info(f"Sample data loaded: {result['success_count']} documents")
        except Exception as e:
            logger.error(f"Failed to load sample data: {e}")

    background_tasks.add_task(load_data)
    return {"message": "Sample data loading started in background"}