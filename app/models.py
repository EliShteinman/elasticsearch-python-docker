from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class DocumentStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DRAFT = "draft"


class NewsCategory(str, Enum):
    ALT_ATHEISM = "alt.atheism"
    COMP_GRAPHICS = "comp.graphics"
    COMP_OS_MS_WINDOWS_MISC = "comp.os.ms-windows.misc"
    COMP_SYS_IBM_PC_HARDWARE = "comp.sys.ibm.pc.hardware"
    COMP_SYS_MAC_HARDWARE = "comp.sys.mac.hardware"
    COMP_WINDOWS_X = "comp.windows.x"
    MISC_FORSALE = "misc.forsale"
    REC_AUTOS = "rec.autos"
    REC_MOTORCYCLES = "rec.motorcycles"
    REC_SPORT_BASEBALL = "rec.sport.baseball"
    REC_SPORT_HOCKEY = "rec.sport.hockey"
    SCI_CRYPT = "sci.crypt"
    SCI_ELECTRONICS = "sci.electronics"
    SCI_MED = "sci.med"
    SCI_SPACE = "sci.space"
    SOC_RELIGION_CHRISTIAN = "soc.religion.christian"
    TALK_POLITICS_GUNS = "talk.politics.guns"
    TALK_POLITICS_MIDEAST = "talk.politics.mideast"
    TALK_POLITICS_MISC = "talk.politics.misc"
    TALK_RELIGION_MISC = "talk.religion.misc"


class DocumentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    body: str = Field(..., min_length=1)
    category: NewsCategory
    tags: List[str] = Field(default_factory=list)
    author: Optional[str] = None
    source_url: Optional[str] = None
    status: DocumentStatus = DocumentStatus.ACTIVE


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    body: Optional[str] = Field(None, min_length=1)
    category: Optional[NewsCategory] = None
    tags: Optional[List[str]] = None
    author: Optional[str] = None
    source_url: Optional[str] = None
    status: Optional[DocumentStatus] = None


class DocumentResponse(DocumentBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    total_hits: int
    max_score: Optional[float]
    took_ms: int
    documents: List[DocumentResponse]


class BulkOperationResponse(BaseModel):
    success_count: int
    error_count: int
    errors: List[str]