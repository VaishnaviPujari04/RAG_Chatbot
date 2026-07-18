import chromadb
from sentence_transformers import SentenceTransformer

# 1. Load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# 2. Read the notes file
with open("sample_notes.txt", "r", encoding="utf-8") as file:
    text = file.read()

# 3. Split the text into chunks
# For now, we split by blank lines.
chunks = text.split("\n\n")

# Remove empty chunks if any exist
chunks = [chunk.strip() for chunk in chunks if chunk.strip()]

print("Number of chunks:", len(chunks))

# 4. Convert chunks into embeddings
embeddings = model.encode(chunks)

print("Embeddings shape:", embeddings.shape)

# 5. Create/connect to a persistent Chroma database
client = chromadb.PersistentClient(path="chroma_db")

# 6. Create a collection
# Think of a collection like a table/folder inside the vector database.
collection = client.get_or_create_collection(name="lecture_notes")

# 7. Add chunks to Chroma
ids = [f"chunk_{i}" for i in range(len(chunks))]

collection.add(
    ids=ids,
    documents=chunks,
    embeddings=embeddings.tolist()
)

print("Ingestion complete!")
print("Stored chunks in Chroma database.")