from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

sentences = [
    "The cat sat on the mat.",
    "A feline rested on the rug.",
    "I love programming in Python.",
]

embeddings = model.encode(sentences)

print(type(embeddings))
print(embeddings.shape)
print(embeddings[0][:10])

import numpy as np

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

sim_cat_feline = cosine_similarity(embeddings[0], embeddings[1])
sim_cat_python = cosine_similarity(embeddings[0], embeddings[2])

print("cat/mat vs feline/rug similarity:", sim_cat_feline)
print("cat/mat vs python similarity:", sim_cat_python)