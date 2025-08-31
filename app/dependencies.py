from fastapi import HTTPException

# This will be set by main.py during startup
_es_service = None

def set_es_service(service):
    global _es_service
    _es_service = service

def get_es_service():
    if _es_service is None:
        raise HTTPException(status_code=500, detail="Elasticsearch service not initialized")
    return _es_service