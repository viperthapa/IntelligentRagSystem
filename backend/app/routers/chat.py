import google.generativeai as genai

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.schemas.document import ChatRequest, ChatResponse
from app.utils.document import generate_answer, retrieve_chunks

router = APIRouter()

genai.configure(api_key=settings.GEMINI_API_KEY )
model = genai.GenerativeModel('gemini-1.5-flash')

@router.post("/chat", response_model=ChatResponse)
async def chat_with_document(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    chunks = await retrieve_chunks(
        session=db,
        query=request.question,
        document_id=request.document_id,
        top_k=request.top_k
    )
    if not chunks:
        raise HTTPException(status_code=404, detail="No relevant document chunks found.")
    
      # Generate answer
    answer = await generate_answer(request.question, chunks)
    return ChatResponse(response=answer)