# 📚 RAG Chatbot — Chat With Your Documents

A Retrieval-Augmented Generation (RAG) application that lets users upload any PDF and ask questions about its content. The system extracts text from the PDF, splits it into meaningful chunks, stores embeddings in a vector database, retrieves the most relevant chunks for a given question, and uses an LLM (Groq/Llama) to generate a grounded, context-aware answer.

Built as a hands-on learning project to understand the core mechanics of RAG systems: embeddings, vector similarity search, chunking strategies, and retrieval-augmented prompting — rather than just calling an LLM directly.

---

## 🚀 Features

- **Upload any PDF** and chat with its contents
- Automatic text extraction from PDF files (`pypdf`)
- Text cleaning to handle PDF whitespace/formatting quirks
- General-purpose, sentence-aware chunking with overlap
- Semantic search using sentence embeddings + ChromaDB (vector database)
- Context-grounded answer generation using Groq's Llama 3.1 model
- FastAPI REST backend with interactive Swagger docs
- Simple browser-based chat UI (upload → index → chat)
- Clear error handling (invalid files, missing documents, LLM failures)
- Environment-variable based secret management (`.env`)

---

## 🏗️ Architecture

```
Uploaded PDF
   ↓
Text Extraction (pypdf)
   ↓
Text Cleaning (regex)
   ↓
Sentence-Aware Chunking (with overlap)
   ↓
Embeddings + ChromaDB Vector Store
   ↓
User Question
   ↓
Semantic Retrieval (cosine similarity, top-k chunks)
   ↓
Groq Llama 3.1 (context-grounded generation)
   ↓
Answer + Retrieved Sources (returned to UI)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend framework | FastAPI |
| Vector database | ChromaDB |
| Embeddings | Sentence-Transformers (`all-MiniLM-L6-v2`) |
| LLM | Groq API (Llama 3.1 8B Instant) |
| PDF parsing | pypdf |
| Frontend | HTML, CSS, vanilla JavaScript |
| Secrets management | python-dotenv |

---

## 📦 Setup

### 1. Clone the repository

```bash
git clone https://github.com/VaishnaviPujari04/RAG_Chatbot.git
cd RAG_Chatbot
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

**Mac/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root (copy from `.env.example`):

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get a free Groq API key at [console.groq.com](https://console.groq.com).

⚠️ **Never commit your real `.env` file.** It's already excluded via `.gitignore`.

### 5. Run the application

```bash
python -m uvicorn app:app --port 8002
```

### 6. Use the app

Open the chat UI:

```
http://127.0.0.1:8002/ui
```

Open the API docs (Swagger):

```
http://127.0.0.1:8002/docs
```

---

## 💬 How to Use

1. Open the chat UI in your browser.
2. Upload a PDF using the upload box at the top.
3. Wait for the "indexed successfully" confirmation message.
4. Ask questions about the document's content in the chat box.
5. Upload a different PDF anytime to start a new session — the previous document's index is cleared automatically.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/upload` | Upload and index a PDF document |
| POST | `/chat` | Ask a question about the currently indexed document |
| GET | `/status` | Check whether a document is currently indexed |
| GET | `/ui` | Serve the browser chat interface |
| GET | `/docs` | Interactive Swagger API documentation |

### Example: `/chat` request

```json
{
  "question": "What is Adaptive RAG?"
}
```

### Example: `/chat` response

```json
{
  "answer": "Adaptive RAG adapts its retrieval strategy based on query complexity...",
  "sources": [
    "5. Adaptive RAG The system adapts retrieval strategy based on query complexity...",
    "..."
  ]
}
```

---

## 🧠 What I Learned Building This

- How text embeddings represent meaning as vectors, and how cosine similarity measures semantic closeness
- Why chunking strategy significantly affects retrieval quality — fixed-size chunking can cut sentences/sections apart, while structure-aware chunking preserves meaning
- How to debug real chunking edge cases (regex splitting numbers like "10." incorrectly, PDF whitespace artifacts, merged words from font-based text extraction)
- Why documents with highly similar internal topics (e.g., 10 sections all about "RAG") can confuse pure semantic search, and how prefixing chunks with section titles partially mitigates this
- The difference between a chatbot that "knows" everything in its context window versus a RAG system that retrieves only relevant pieces on demand — and why this matters for scale, cost, and control
- How to structure a FastAPI backend with proper error handling, request/response models, and file upload support
- Safe API key management using `.env` files and `.gitignore`

---

## ⚠️ Known Limitations

- **No persistent storage on free-tier deployment** — uploaded PDFs and their vector index may be cleared when the server restarts or sleeps (relevant if deployed on free hosting tiers like Render).
- **Single active document at a time** — uploading a new PDF replaces the previous one; there's no multi-document or multi-user session support yet.
- **Retrieval can be imperfect on topically similar documents** — when many sections of a document discuss closely related concepts (e.g., multiple "types of X"), the embedding model can sometimes rank a related-but-wrong section higher than the correct one.
- **Can misinterpret example text as fact** — if a document contains a rhetorical example (e.g., "User: What is the capital of France?" used as a sample question), the LLM may occasionally treat retrieved example text as a direct answer to unrelated questions.
- **Scanned/image-based PDFs are not supported** — text extraction requires the PDF to have actual embedded text, not scanned images (no OCR).

---

## 🔮 Future Improvements

- [ ] Hybrid search (keyword + semantic) to improve retrieval on topically similar sections
- [ ] Re-ranking retrieved chunks before sending to the LLM
- [ ] Similarity-score thresholds to reject unrelated questions more reliably
- [ ] Multi-document support (query across several uploaded files)
- [ ] Persistent vector storage using a hosted vector DB (e.g., Pinecone) for reliable multi-session use
- [ ] Source highlighting in the UI (show which exact chunk text contributed to the answer)
- [ ] OCR support for scanned PDFs

---

## 📄 License

This project was built for educational purposes as part of a personal learning journey into RAG systems and AI application development.