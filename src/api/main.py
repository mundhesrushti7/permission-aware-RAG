from fastapi import FastAPI


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