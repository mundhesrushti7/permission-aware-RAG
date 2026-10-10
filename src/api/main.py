from fastapi import Depends, FastAPI, HTTPException, status

from src.api.auth import get_current_user, login_user
from src.api.models import (
    LoginRequest,
    LoginResponse,
    QueryRequest,
    QueryResponse,
    RevokePermissionRequest,
)
from src.auth.permissions import revoke_user_access
from src.rag.pipeline import answer_question


app = FastAPI(
    title="Permission-Aware RAG API",
    description="Secure multi-tenant Retrieval-Augmented Generation service.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest):
    """Authenticate a user and return an access token."""
    return login_user(credentials)


@app.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    """Return the identity of the authenticated user."""
    return current_user


@app.post("/query", response_model=QueryResponse)
def query(
    request: QueryRequest,
    current_user: dict = Depends(get_current_user),
):
    """Answer a question using only documents the authenticated user can access."""
    answer = answer_question(
        question=request.question,
        user_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"],
        user_roles=current_user["roles"],
    )

    return QueryResponse(answer=answer)


@app.post("/documents/{document_id}/permissions/revoke")
def revoke_permission(
    document_id: str,
    request: RevokePermissionRequest,
    current_user: dict = Depends(get_current_user),
):
    """Revoke a user's access to a document."""

    try:
        revoke_user_access(
            document_id=document_id,
            target_user_id=request.target_user_id,
            actor_user_id=current_user["user_id"],
            actor_tenant_id=current_user["tenant_id"],
            actor_roles=current_user["roles"],
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    return {
        "message": "User access revoked successfully.",
        "document_id": document_id,
        "target_user_id": request.target_user_id,
    }