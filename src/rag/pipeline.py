from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchValue

from src.embeddings.embedder import embed_texts
from src.generation.generator import generate_answer


client = QdrantClient(
    url="http://localhost:6333"
)

def answer_question(
    question: str,
    tenant_id: str,
) -> str:    
    """
    Retrieve relevant context and generate an answer.
    """

    question_embedding = embed_texts([question])[0]


    query_filter = Filter(
    must=[
        FieldCondition(
            key="tenant_id",
            match=MatchValue(
                value=tenant_id,
            ),
        )
    ]
    )

    results = client.query_points(
    collection_name="documents",
    query=question_embedding.tolist(),
    query_filter=query_filter,
    limit=3,
    )

    retrieved_texts = []

    for result in results.points:
        retrieved_texts.append(
            result.payload["text"]
        )


    context = "\n\n".join(retrieved_texts)


    prompt = f"""
    Context:
    {context}

    Question:
    {question}

    Answer:
    """

    answer = generate_answer(prompt)

    return answer