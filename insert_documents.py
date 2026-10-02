from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from src.embeddings.embedder import embed_texts


client = QdrantClient(
    url="http://localhost:6333"
)


documents = [
    {
        "text": "Employees must change their password every 90 days.",
        "tenant_id": "tenant_a",
    },
    {
        "text": "Passwords must contain at least 12 characters.",
        "tenant_id": "tenant_a",
    },
    {
        "text": "Two-factor authentication is required for administrative accounts.",
        "tenant_id": "tenant_a",
    },
    {
        "text": "Employees receive their salary on the last working day of the month.",
        "tenant_id": "tenant_b",
    },
    {
        "text": "Employees are entitled to 20 days of annual leave.",
        "tenant_id": "tenant_b",
    },
    {
        "text": "Health benefits are available to full-time employees.",
        "tenant_id": "tenant_b",
    },
]


texts = [document["text"] for document in documents]

embeddings = embed_texts(texts)

points = []

for index, (document, vector) in enumerate(
    zip(documents, embeddings),
    start=1,
):
    point = PointStruct(
        id=index,
        vector=vector.tolist(),
        payload={
            "text": document["text"],
            "document_id": f"policy_{index}",
            "tenant_id": document["tenant_id"],
        },
    )

    points.append(point)


client.upsert(
    collection_name="documents",
    points=points,
)


print(f"Inserted {len(points)} documents into Qdrant.")