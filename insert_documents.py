from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from src.embeddings.embedder import embed_texts


client = QdrantClient(
    url="http://localhost:6333"
)


documents = [
    "Employees must change their password every 90 days.",
    "Passwords must contain at least 12 characters.",
    "Two-factor authentication is required for administrative accounts.",
]


embeddings = embed_texts(documents)


points = []

for index, (text, vector) in enumerate(
    zip(documents, embeddings),
    start=1,
):
    point = PointStruct(
        id=index,
        vector=vector.tolist(),
        payload={
            "text": text,
            "document_id": f"policy_{index}",
            "tenant_id": "tenant_a",
        },
    )

    points.append(point)


client.upsert(
    collection_name="documents",
    points=points,
)


print(f"Inserted {len(points)} documents into Qdrant.")