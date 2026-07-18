import chromadb

# 1. Create a local database. 
# This will create a folder on your computer called 'my_chroma_db' to save the data.
client = chromadb.PersistentClient(path="./my_chroma_db")

# 2. Create a "collection" (think of this like a table in a normal SQL database)
# If it already exists, get_or_create prevents errors if you run the script twice.
collection = client.get_or_create_collection(name="my_notes")

# 3. Add our documents to the database.
# Notice: we just give it the raw text! Chroma will embed it for us behind the scenes.
collection.add(
    documents=[
        "The cat sat on the mat.",
        "A feline rested on the rug.",
        "I love programming in Python."
    ],
    ids=["id1", "id2", "id3"]  # Every document in a DB needs a unique ID
)

print("Documents added to the database!")

# 4. Now, let's ask a question. 
# We will search for the 2 most relevant documents.
results = collection.query(
    query_texts=["What did the animal do?"],
    n_results=2 
)

# 5. Print what the database found
print("\nTop 2 matches for 'What did the animal do?':")
print(results['documents'])