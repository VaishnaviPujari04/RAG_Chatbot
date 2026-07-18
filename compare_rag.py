import chromadb
from pypdf import PdfReader
import re
import shutil
import os

# ============================================================
# PART 1: Extract and clean text
# ============================================================
reader = PdfReader("notes.pdf")
full_text = ""
for page in reader.pages:
    full_text += page.extract_text() + " "

cleaned_text = re.sub(r'\s+', ' ', full_text).strip()
cleaned_text = re.sub(r'(\d) (\d)\.', r'\1\2.', cleaned_text)


# ============================================================
# PART 2: Both chunking methods (same as before)
# ============================================================
def fixed_size_chunks(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


SECTION_TITLES = [
    "Standard RAG", "Agentic RAG", "RAG with Memory", "Self RAG",
    "Adaptive RAG", "Corrective RAG", "Attention-based RAG",
    "HybridAI RAG", "Cost-Constrained RAG", "XAI RAG"
]

def structure_aware_chunks(text, titles):
    escaped_titles = [re.escape(t) for t in titles]
    pattern = re.compile(
        r'(?=(?<!\d)\d{1,2}\.\s*(?:' + '|'.join(escaped_titles) + r'))'
    )
    raw_chunks = pattern.split(text)
    return [c.strip() for c in raw_chunks if c.strip()]


fixed_chunks = fixed_size_chunks(cleaned_text)
structure_chunks = structure_aware_chunks(cleaned_text, SECTION_TITLES)


# ============================================================
# PART 3: NEW — Add title prefixes to structure-aware chunks
# ============================================================
# We extract the title from the start of each chunk and prepend it
# as a clear labeled header, so the embedding model sees it prominently.
def add_title_prefix(chunks):
    prefixed = []
    for chunk in chunks:
        # Extract the title: everything before the first sentence-ending period
        match = re.match(r'(\d{1,2}\.\s*[A-Za-z\- ]+RAG[^.]*)', chunk)
        if match:
            title = match.group(1).strip()
            prefixed.append(f"[Section: {title}] {chunk}")
        else:
            # Title chunk like "10 RAG Architectures" — keep as is
            prefixed.append(chunk)
    return prefixed

prefixed_structure_chunks = add_title_prefix(structure_chunks)


# ============================================================
# PART 4: Create fresh database with 3 collections
# ============================================================
if os.path.exists("./rag_compare_db"):
    shutil.rmtree("./rag_compare_db")

client = chromadb.PersistentClient(path="./rag_compare_db")

# Clean slate
for name in ["fixed_chunks", "structure_chunks", "prefixed_chunks"]:
    try:
        client.delete_collection(name)
    except:
        pass

fixed_col = client.create_collection("fixed_chunks")
struct_col = client.create_collection("structure_chunks")
prefixed_col = client.create_collection("prefixed_chunks")

# Load all three
fixed_col.add(
    documents=fixed_chunks,
    ids=[f"fixed_{i}" for i in range(len(fixed_chunks))]
)
struct_col.add(
    documents=structure_chunks,
    ids=[f"struct_{i}" for i in range(len(structure_chunks))]
)
prefixed_col.add(
    documents=prefixed_structure_chunks,
    ids=[f"prefixed_{i}" for i in range(len(prefixed_structure_chunks))]
)

print(f"Fixed-size:    {len(fixed_chunks)} chunks")
print(f"Structure:     {len(structure_chunks)} chunks")
print(f"Prefixed:      {len(prefixed_structure_chunks)} chunks")


# ============================================================
# PART 5: Compare all 3 methods
# ============================================================
test_questions = [
    "What is Adaptive RAG and when should I use it?",
    "Which RAG approach is best for noisy data?",
    "How does a system remember previous conversations in RAG?",
    "What is the cheapest way to run a RAG pipeline?",
    "How does RAG explain why a loan was rejected?",
]

for q in test_questions:
    print(f"\n{'='*70}")
    print(f"QUESTION: {q}")
    print(f"{'='*70}")

    fixed_results = fixed_col.query(query_texts=[q], n_results=2)
    struct_results = struct_col.query(query_texts=[q], n_results=2)
    prefixed_results = prefixed_col.query(query_texts=[q], n_results=2)

    print(f"\n  FIXED-SIZE top 2:")
    for i, doc in enumerate(fixed_results['documents'][0]):
        preview = doc[:120].replace('\n', ' ')
        print(f"    {i+1}. {preview}...")

    print(f"\n  STRUCTURE-AWARE top 2:")
    for i, doc in enumerate(struct_results['documents'][0]):
        preview = doc[:120].replace('\n', ' ')
        print(f"    {i+1}. {preview}...")

    print(f"\n  PREFIXED (title-tagged) top 2:")
    for i, doc in enumerate(prefixed_results['documents'][0]):
        preview = doc[:120].replace('\n', ' ')
        print(f"    {i+1}. {preview}...")