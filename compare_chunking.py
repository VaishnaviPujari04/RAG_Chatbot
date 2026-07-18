from pypdf import PdfReader
import re

reader = PdfReader("notes.pdf")
full_text = ""
for page in reader.pages:
    full_text += page.extract_text() + " "


cleaned_text = re.sub(r'\s+', ' ', full_text).strip()

# Fix: join digits that got split apart by a stray space, e.g. "1 0." -> "10."
cleaned_text = re.sub(r'(\d) (\d)\.', r'\1\2.', cleaned_text)
idx = cleaned_text.find("XAI RAG")
print("Raw characters right before 'XAI RAG':")
print(repr(cleaned_text[idx-15:idx+10]))

def fixed_size_chunks(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


# Fix: explicit known section titles instead of a guessed generic pattern
SECTION_TITLES = [
    "Standard RAG",
    "Agentic RAG",
    "RAG with Memory",
    "Self RAG",
    "Adaptive RAG",
    "Corrective RAG",
    "Attention-based RAG",
    "HybridAI RAG",
    "Cost-Constrained RAG",
    "XAI RAG"
]

def structure_aware_chunks(text, titles):
    escaped_titles = [re.escape(t) for t in titles]
    # (?<!\d) = "only match if the character BEFORE this is NOT a digit"
    pattern = re.compile(
        r'(?=(?<!\d)\d{1,2}\.\s*(?:' + '|'.join(escaped_titles) + r'))'
    )
    raw_chunks = pattern.split(text)
    return [c.strip() for c in raw_chunks if c.strip()]

fixed_chunks = fixed_size_chunks(cleaned_text)
structure_chunks = structure_aware_chunks(cleaned_text, SECTION_TITLES)

print(f"=== FIXED-SIZE CHUNKING ({len(fixed_chunks)} chunks) ===\n")
for i, c in enumerate(fixed_chunks):
    print(f"--- Fixed Chunk {i+1} ---\n{c}\n")

print(f"\n=== STRUCTURE-AWARE CHUNKING ({len(structure_chunks)} chunks) ===\n")
for i, c in enumerate(structure_chunks):
    print(f"--- Structure Chunk {i+1} ---\n{c[:400]}\n")