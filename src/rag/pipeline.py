from qdrant_client import QdrantClient
from qdrant_client.models import (
    FieldCondition,
    Filter,
    MatchAny,
    MatchValue,
)
from src.audit.audit_logger import log_retrieval
from src.auth.acl import is_document_allowed
from src.embeddings.embedder import embed_texts
from src.generation.generator import generate_answer


client = QdrantClient(
    url="http://localhost:6333"
)


def retrieve_documents(
    question: str,
    user_id: str,
    tenant_id: str,
    user_roles: list[str],
    limit: int = 3,
):
    """
    Retrieve documents belonging only to the specified tenant.
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
    ],
    should=[
        FieldCondition(
            key="allowed_users",
            match=MatchAny(
                any=[user_id],
            ),
        ),
        FieldCondition(
            key="allowed_roles",
            match=MatchAny(
                any=user_roles,
                ),
            ),
        ],
    )

    results = client.query_points(
        collection_name="documents",
        query=question_embedding.tolist(),
        query_filter=query_filter,
        limit=limit,
    )

    authorized_results = []

    for result in results.points:
        document = result.payload

        if is_document_allowed(
            document,
            user_id=user_id,
            user_tenant_id=tenant_id,
            user_roles=user_roles,
        ):
            authorized_results.append(result)

    returned_document_ids = [
        result.payload["document_id"]
        for result in authorized_results
    ]

    log_retrieval(
        user_id=user_id,
        tenant_id=tenant_id,
        query=question,
        returned_document_ids=returned_document_ids,
        model="rag-model",
    )
    return authorized_results


def answer_question(
    question: str,
    user_id: str,
    tenant_id: str,
    user_roles: list[str],
) -> str:
    """
    Retrieve relevant context and generate an answer.
    """

    results = retrieve_documents(
        question,
        user_id=user_id,
        tenant_id=tenant_id,
        user_roles=user_roles,
    )

    retrieved_texts = []

    for result in results:
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