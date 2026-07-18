# RAG Chatbot — Chat With Your Notes

A Retrieval-Augmented Generation (RAG) application that lets users ask questions about a PDF document. The system extracts text from a PDF, splits it into meaningful chunks, stores embeddings in ChromaDB, retrieves relevant context, and uses Groq's Llama model to generate grounded answers.

## Features

- PDF text extraction with `pypdf`
- Text cleaning for PDF whitespace issues
- Structure-aware chunking based on document sections
- Semantic search using embeddings and ChromaDB
- Context-aware answers generated with Groq Llama
- FastAPI REST API
- Interactive Swagger API documentation
- Browser-based chat UI
- Environment-variable based API-key handling

## Architecture

```text
PDF Notes
   ↓
Text Extraction and Cleaning
   ↓
Structure-Aware Chunking
   ↓
Embeddings + ChromaDB Vector Store
   ↓
User Question
   ↓
Semantic Retrieval of Relevant Chunks
   ↓
Groq Llama LLM
   ↓
Grounded Answer + Retrieved Sources

