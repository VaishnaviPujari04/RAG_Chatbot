from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader
import chromadb
import re
import os
import shutil

load_dotenv()

# ============================================================
# Setup
# ============================================================
DB_PATH = "./rag_app_db"
UPLOAD_DIR = "./uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY was not found. Add it to your .env file.")

groq_client = Groq(api_key=api_key)
chroma_client = chromadb.PersistentClient(path=DB_PATH)

# Track whether a document has been uploaded and indexed yet
app_state = {
    "document_ready": False,
    "filename": None,
    "chunk_count": 0
}


# ============================================================
# Text extraction and chunking
# ============================================================
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            full_text += page_text + " "

    cleaned = re.sub(r'\s+', ' ', full_text).strip()
    return cleaned


def general_chunk_text(text, chunk_size=800, overlap=150):
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size

        if end < text_length:
            search_zone_start = max(start, end - 100)
            search_zone = text[search_zone_start:end]
            last_period = search_zone.rfind('.')

            if last_period != -1:
                end = search_zone_start + last_period + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap
        if start >= text_length:
            break

    return chunks


def index_document(pdf_path, filename):
    """Extract, chunk, and store a PDF's content in ChromaDB."""

    # Clear any previously indexed document (single-user MVP behavior)
    try:
        chroma_client.delete_collection("notes")
    except Exception:
        pass

    collection = chroma_client.create_collection("notes")

    text = extract_text_from_pdf(pdf_path)

    if len(text) < 50:
        raise ValueError("Could not extract readable text from this PDF. It may be a scanned image.")

    chunks = general_chunk_text(text)

    collection.add(
        documents=chunks,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )

    app_state["document_ready"] = True
    app_state["filename"] = filename
    app_state["chunk_count"] = len(chunks)

    return len(chunks)


# ============================================================
# FastAPI app
# ============================================================
app = FastAPI(title="RAG Chatbot")


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


class UploadResponse(BaseModel):
    message: str
    filename: str
    chunks_created: int


@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    save_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        with open(save_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {e}")

    try:
        chunk_count = index_document(save_path, file.filename)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {e}")

    return UploadResponse(
        message="Document uploaded and indexed successfully.",
        filename=file.filename,
        chunks_created=chunk_count
    )


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not app_state["document_ready"]:
        raise HTTPException(
            status_code=400,
            detail="No document has been uploaded yet. Please upload a PDF first."
        )

    collection = chroma_client.get_collection("notes")

    results = collection.query(
        query_texts=[request.question],
        n_results=3
    )
    retrieved_chunks = results["documents"][0]

    context = "\n\n---\n\n".join(retrieved_chunks)

    prompt = f"""You are a helpful assistant that answers questions based ONLY on the provided context.

If the context does not contain enough information to answer the question, say exactly:
"I don't have enough information to answer that based on the available documents."

Do not use general knowledge. Do not treat example questions inside the context as facts.

CONTEXT:
{context}

QUESTION:
{request.question}

ANSWER:
"""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        answer = response.choices[0].message.content

    except Exception as error:
        print(f"Groq API error: {error}")
        raise HTTPException(
            status_code=500,
            detail="Unable to generate an answer right now. Check your API key, network connection, or Groq quota."
        )

    return ChatResponse(answer=answer, sources=retrieved_chunks)


@app.get("/status")
def status():
    return app_state


@app.get("/")
def root():
    return {"message": "RAG Chatbot is running. Go to /ui to use the app."}


@app.get("/ui")
def ui():
    return FileResponse("index.html")