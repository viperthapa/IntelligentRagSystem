from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class DocumentCreate(BaseModel):
    id: Optional[int]
    file_name: str
    file_type: str 

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    question: str
    document_id: int
    top_k: int = 5

class ChatResponse(BaseModel):
    response: str