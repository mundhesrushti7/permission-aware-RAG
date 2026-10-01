from qdrant_client import QdrantClient

from src.embeddings.embedder import embed_texts
from src.generation.generator import generate_answer


client = QdrantClient(
    url="http://localhost:6333"
)

def answer_question(question: str) -> str:
    """
    Retrieve relevant context and generate an answer.
    """

    question_embedding = embed_texts([question])[0]

    results = client.query_points(
        collection_name="documents",
        query=question_embedding.tolist(),
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