# Intelligent RAG System

An intelligent Retrieval-Augmented Generation (RAG) system built with FastAPI backend and React frontend. This system allows users to upload documents (PDF, TXT, MD), process them into chunks, generate embeddings, store them in a vector database, and query them via a chat interface.

## Backend

The backend is built with FastAPI and uses PostgreSQL with pgvector for vector storage. It leverages LangChain for text splitting, Sentence Transformers for embeddings, and Google's Gemini for answer generation.

### Installation

1. **Prerequisites:**
   - Python 3.13 or higher
   - PostgreSQL with pgvector extension
   - Google Gemini API key

2. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd IntelligentRagSystem/backend
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   # or if using uv
   uv sync
   ```

4. **Environment Setup:**
   Rename a `.env.example` to `.env`
   Update the credentials for postgres database,gemini key and embeding model

5. **Database Setup:**
   - Ensure PostgreSQL is running with pgvector extension installed.
 
6. **Run the server:**
   ```bash
   uvicorn main:app --reload
   ```
   The API will be available at `http://localhost:8000`.

### Chunks

Text documents are split into overlapping chunks using LangChain's `RecursiveCharacterTextSplitter`. The default configuration is:
- Chunk size: 900 characters
- Chunk overlap: 180 characters
- Separators: `["\n\n", "\n", " ", ""]`

This ensures semantic coherence while allowing for efficient retrieval.

### Embeddings

Embeddings are generated using the `all-MiniLM-L6-v2` model from Sentence Transformers. The process:
1. Text chunks are encoded into 384-dimensional vectors.
2. Embeddings are normalized for cosine similarity calculations.
3. Asynchronous processing is used to avoid blocking the event loop.

### Store

Document chunks and their embeddings are stored in PostgreSQL using pgvector:
- `Document` table: Stores document metadata (file_name, file_type, content).
- `DocumentChunk` table: Stores individual chunks with their embeddings and document references.
- Vector similarity search uses cosine distance for retrieval.

### Chat Working Methods

The chat functionality follows these steps:
1. **Query Processing:** User question is embedded using the same model.
2. **Retrieval:** Top-k most similar chunks are retrieved from the vector store (default k=5).
3. **Context Assembly:** Retrieved chunks are ranked by similarity and formatted as context.
4. **Answer Generation:** Google's Gemini 2.5-flash model generates answers based on the context and question.
5. **Response:** The generated answer is returned to the user.

API Endpoints:
- `POST /api/upload`: Upload and process documents.
- `POST /api/chat`: Query documents with questions.

## Frontend

The frontend is a React application providing a user interface for document upload and chat interaction.

### Installation

1. **Prerequisites:**
   - Node.js 16 or higher
   - npm or yarn

2. **Navigate to frontend directory:**
   ```bash
   cd frontend/ragapp
   ```

3. **Install dependencies:**
   ```bash
   npm install
   ```

4. **Start the development server:**
   ```bash
   npm start
   ```
   The app will be available at `http://localhost:3000`.

### Features

- Document upload interface supporting PDF, TXT, and MD files.
- Chat interface for querying uploaded documents.
- Responsive design with Tailwind CSS.