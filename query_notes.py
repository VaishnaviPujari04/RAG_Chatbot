import chromadb
from sentence_transformers import SentenceTransformer

# 1. Load the same embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# 2. Connect to the same Chroma database
client = chromadb.PersistentClient(path="chroma_db")

# 3. Get the collection we created earlier
collection = client.get_collection(name="lecture_notes")

# 4. Ask a question
question = "What are neural networks?"

# 5. Convert the question into an embedding
question_embedding = model.encode([question])

# 6. Search Chroma for the most similar chunks
results = collection.query(
    query_embeddings=question_embedding.tolist(),
    n_results=3
)

print("Question:", question)
print("\nTop matching chunks:\n")

for i, document in enumerate(results["documents"][0]):
    print(f"Result {i + 1}:")
    print(document)
    print()