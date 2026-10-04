from fastapi import Depends, FastAPI

from src.api.auth import get_current_user, login_user
from src.api.models import LoginRequest, LoginResponse

app = FastAPI(
    title="Permission-Aware RAG API",
    description="Secure multi-tenant Retrieval-Augmented Generation service.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    """
    Return the health status of the API.
    """
    return {
        "status": "ok",
    }


@app.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest):
    """
    Authenticate a user and return an access token.
    """
    return login_user(credentials)

    

@app.get("/me")
def get_me(
    current_user: dict = Depends(get_current_user),
):
    """
    Return the identity of the authenticated user.
    """
    return current_user