from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str


class RevokePermissionRequest(BaseModel):
    target_user_id: str