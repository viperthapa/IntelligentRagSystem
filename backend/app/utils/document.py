import asyncio

from typing import List,Tuple

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, bindparam, Integer

import google.genai as genai

from app.config import settings
from app.models.document import Document, DocumentChunk

# ─── Configuration ───────────────────────────────────────────────────────────────
DATABASE_URL = settings.DATABASE_URL

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
EMBEDDING_DIMENSION = settings.EMBEDDING_DIMENSION

CHUNK_SIZE = 900
CHUNK_OVERLAP = 180

genai_client = genai.Client(api_key=settings.GEMINI_API_KEY)

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Initialize models

# ─── TEXT SPLITTER (your original function) ────────────────────────────────────
def split_text_into_chunks(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> list[str]:
    """
    Splits text into overlapping chunks using RecursiveCharacterTextSplitter
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )

    chunks = splitter.split_text(text)
    return chunks


# ─── EMBEDDING FUNCTION ────────────────────────────────────────────────────────
async def embed_texts(texts: List[str]) -> List[List[float]]:
    loop = asyncio.get_running_loop()

    embeddings = await loop.run_in_executor(
        None,
        lambda: embedding_model.encode(
            texts,
            normalize_embeddings=True
        )
    )

    return embeddings.tolist()
# ─── Vector Store Operations ────────────────────────────────────────────────────

async def index_document(
        db: AsyncSession,
        file_name: str,
        full_text: str,
        file_type: str = None
    ) -> int:
        """Chunk → Embed → Store → Return document id"""
        chunks = split_text_into_chunks(full_text)
        if not chunks:
            raise ValueError("No text chunks were created from the document.")
        
        # Create document record
        doc = Document(
            file_name=file_name,
            file_type=file_type,
            content=full_text,
        )
        db.add(doc)
        await db.flush() 

        # Bulk create chunk records
        embeddings = await embed_texts(chunks)

        # Create chunk records
        chunk_objects = [
            DocumentChunk(
                document_id=doc.id,
                chunk_text=chunk_text,
                embedding=embedding,
                chunk_index=i
            )
            for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings))
        ]

        db.add_all(chunk_objects)
        await db.commit()
        await db.refresh(doc)
        
        return doc


async def retrieve_chunks(
        query: str,
        session: AsyncSession,
        document_id: int | None = None,
        top_k: int = 5,
        min_similarity: float = 0.1  # Lowered from 0.65 to 0.1 for better matching
    ) -> List[Tuple[str, float]]:
        """
        Returns: list of (chunk_text, cosine_similarity)
        Higher similarity = more relevant (cosine ∈ [-1, 1])
        """
        # Convert query_vector to string format for PostgreSQL pgvector
        query_vector = (await embed_texts([query]))[0]
        vector_str = "[" + ",".join(str(float(v)) for v in query_vector) + "]"

        if document_id is None:
            stmt = text("""
                SELECT
                    chunk_text,
                    1 - (embedding <=> CAST(:q_vec AS vector)) AS similarity
                FROM document_chunks
                ORDER BY embedding <=> CAST(:q_vec AS vector)
                LIMIT CAST(:top_k AS integer)
            """).bindparams(
                bindparam("q_vec", value=vector_str),
                bindparam("top_k", value=top_k, type_=Integer)
            )
            result = await session.execute(stmt)
        else:
            stmt = text("""
                SELECT
                    chunk_text,
                    1 - (embedding <=> CAST(:q_vec AS vector)) AS similarity
                FROM document_chunks
                WHERE document_id = CAST(:doc_id AS integer)
                ORDER BY embedding <=> CAST(:q_vec AS vector)
                LIMIT CAST(:top_k AS integer)
            """).bindparams(
                bindparam("q_vec", value=vector_str),
                bindparam("doc_id", value=document_id, type_=Integer),
                bindparam("top_k", value=top_k, type_=Integer)
            )
            result = await session.execute(stmt)

        rows = result.fetchall()

        for i, row in enumerate(rows[:3]):  # Show first 3 rows
            print(f"Row {i}: similarity={row[1]:.4f}, text_length={len(row[0])}")

        # Extract and filter results - relaxed filters for debugging
        filtered_results = []
        for row in rows:
            chunk_text = row[0]
            similarity = float(row[1])
            # More lenient filters
            if (
                similarity >= min_similarity
                and len(chunk_text.strip()) > 10 
            ):
                filtered_results.append((chunk_text, similarity))

        return filtered_results


async def generate_answer(query: str, context_chunks: List[Tuple[str, float]]) -> str:
    """Generate answer using Gemini"""
    if not context_chunks:
        return "I couldn't find relevant information to answer your question."
    
    context = "\n\n".join([f"[Relevance: {sim:.2f}]\n{text}" for text, sim in context_chunks])
    prompt = f"""Based on the following context, answer the question.
        Context:
        {context}
        Question: {query}
        Answer:"""
    
    response = genai_client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    return response.text