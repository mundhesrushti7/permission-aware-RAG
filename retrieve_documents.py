from qdrant_client import QdrantClient
from src.embeddings.embedder import embed_texts


client = QdrantClient(
    url="http://localhost:6333"
)


question = "How often should I change my password?"


question_embedding = embed_texts([question])[0]


results = client.query_points(
    collection_name="documents",
    query=question_embedding.tolist(),
    limit=3,
)


print("Question:")
print(question)

print("\nRetrieved documents:")

for result in results.points:
    print(f"\nScore: {result.score:.4f}")
    print(f"Document: {result.payload['document_id']}")
    print(f"Text: {result.payload['text']}")