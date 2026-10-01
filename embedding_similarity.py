from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


model = SentenceTransformer("all-MiniLM-L6-v2")


documents = [
    "Employees must change their password every 90 days.",
    "Passwords must contain at least 12 characters.",
    "Employees should report suspicious emails to the security team.",
]


question = "How often should I change my password?"


document_embeddings = model.encode(documents)
question_embedding = model.encode([question])


similarities = cosine_similarity(
    question_embedding,
    document_embeddings,
)


print("Question:")
print(question)

print("\nSimilarity scores:")

for document, score in zip(documents, similarities[0]):
    print(f"{score:.4f} -> {document}")