from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")

sentences = [
    "How do I reset my password?",
    "I forgot my password. How can I change it?",
    "What is the weather like today?"
]

embeddings = model.encode(sentences)

similarity_matrix = cosine_similarity(embeddings)

print("Cosine similarity matrix:")
print(similarity_matrix)