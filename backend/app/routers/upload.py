import os

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.document import DocumentCreate
from app.utils.document import index_document

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}

def validate_file(filename: str, file_type: str):
    if file_type not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File type not allowed")

async def extract_text_from_file(file: UploadFile, file_type: str) -> str:
    content = await file.read()
    if file_type == ".txt" or file_type == ".md":
        return content.decode("utf-8")
    elif file_type == ".pdf":
        # For PDF, we need pypdf or similar
        # For simplicity, assume text PDF
        # In real, install pypdf: uv add pypdf
        from pypdf import PdfReader
        from io import BytesIO
        pdf = PdfReader(BytesIO(content))
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
        return text
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

@router.post("/upload", response_model=DocumentCreate)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload and process a document.
    
    Process:
    1. Validate file type and size
    2. Extract text content
    3. Chunk text
    4. Generate embeddings
    5. Store in database
    
    Returns:
        Document metadata and processing confirmation
    """
    # Validate file
    file_type = os.path.splitext(file.filename)[1].lower()
    validate_file(file.filename,file_type)

    # Extract text
    content = await extract_text_from_file(file,file_type)
    if not content.strip():
        raise HTTPException(status_code=400, detail="File is empty")
    
     # Index document (chunk + embed + store)
    try:
        document = await index_document(
            db=db,
            file_name=file.filename,
            full_text=content,
            file_type=file_type
        )
        return DocumentCreate(
            id=document.id,
            file_name=document.file_name,
            file_type=document.file_type,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error indexing document: {str(e)}")
    