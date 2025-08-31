import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_es_service
from app.models import (BulkOperationResponse, DocumentCreate, DocumentResponse,
                      DocumentUpdate)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=DocumentResponse, status_code=201)
async def create_document(
        document: DocumentCreate,
        service=Depends(get_es_service)
):
    """Create a new document"""
    try:
        result = await service.create_document(document)
        logger.info(f"Created document with ID: {result.id}")
        return result
    except Exception as e:
        logger.error(f"Failed to create document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create document: {str(e)}")


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
        doc_id: str,
        service=Depends(get_es_service)
):
    """Get a document by ID"""
    try:
        result = await service.get_document(doc_id)
        if not result:
            raise HTTPException(status_code=404, detail="Document not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document {doc_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve document: {str(e)}")


@router.put("/{doc_id}", response_model=DocumentResponse)
async def update_document(
        doc_id: str,
        update_data: DocumentUpdate,
        service=Depends(get_es_service)
):
    """Update a document"""
    try:
        result = await service.update_document(doc_id, update_data)
        if not result:
            raise HTTPException(status_code=404, detail="Document not found")
        logger.info(f"Updated document with ID: {doc_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update document {doc_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update document: {str(e)}")


@router.delete("/{doc_id}")
async def delete_document(
        doc_id: str,
        service=Depends(get_es_service)
):
    """Delete a document"""
    try:
        result = await service.delete_document(doc_id)
        if not result:
            raise HTTPException(status_code=404, detail="Document not found")
        logger.info(f"Deleted document with ID: {doc_id}")
        return {"message": f"Document {doc_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document {doc_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


@router.post("/bulk", response_model=BulkOperationResponse)
async def bulk_create_documents(
        documents: List[DocumentCreate],
        service=Depends(get_es_service)
):
    """Bulk create multiple documents"""
    if len(documents) > 1000:
        raise HTTPException(status_code=400, detail="Maximum 1000 documents per bulk operation")

    try:
        result = await service.bulk_create_documents(documents)
        logger.info(f"Bulk create completed: {result['success_count']} successful, {result['error_count']} failed")
        return BulkOperationResponse(**result)
    except Exception as e:
        logger.error(f"Bulk create failed: {e}")
        raise HTTPException(status_code=500, detail=f"Bulk create failed: {str(e)}")