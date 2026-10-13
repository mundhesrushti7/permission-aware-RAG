# Permission-Aware Multi-Tenant RAG

A Retrieval-Augmented Generation (RAG) system that answers questions using retrieved documents while enforcing tenant isolation and role-based access control.

## Project Status

Core implementation complete; evaluation and documentation in progress.

## Features

- Document ingestion, chunking, and embedding generation
- Semantic retrieval using Qdrant
- Tenant-level isolation and role-based document access control
- JWT-based authentication
- Permission and retrieval audit logging
- Safe fallback when authorized context is unavailable or judged irrelevant
- Automated tests for authentication, permissions, retrieval, and API behavior

## Architecture

The system follows this request flow:

1. A user authenticates and receives a JWT.
2. The API identifies the user, tenant, and roles.
3. The RAG pipeline retrieves candidate documents from Qdrant.
4. Tenant and document-permission checks restrict which documents can be used.
5. Authorized document context is checked for relevance to the question.
6. The generation model produces an answer from the accepted context.
7. Retrieval and permission-related events can be recorded for auditing.

### Technology Stack

- **API:** FastAPI
- **Vector database:** Qdrant
- **Relational database:** PostgreSQL
- **Embeddings:** Sentence Transformers
- **Generation:** Hugging Face Transformers
- **Authentication:** JWT
- **Testing:** pytest

## Evaluation

The current authorization evaluation includes five predefined cases covering:

- Employee access to an authorized password policy
- Employee denial for salary and admin-only policies
- Admin access to the admin policy
- Cross-tenant denial for an employee

**Latest recorded evaluation:**

- Cases passed: 5/5
- Authorization accuracy: 100%
- Forbidden document leaks in these cases: 0

These results apply to the five defined evaluation cases and do not guarantee security for every possible input or permission configuration.

The automated test suite previously completed with **66 passed and 1 non-fatal warning**.

## Running Locally

### Prerequisites

- Python 3.12
- Docker Desktop
- Git

PostgreSQL and Qdrant run in Docker containers. The project uses PostgreSQL for identity and audit data and Qdrant for vector search.

### 1. Clone the repository

```powershell
git clone https://github.com/mundhesrushti7/permission-aware-RAG.git
cd permission-aware-RAG
```

### 2. Create and activate the virtual environment

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root. Set the PostgreSQL connection URL and a strong, private JWT signing secret.

```dotenv
DATABASE_URL=postgresql://<username>:<password>@localhost:5432/<database_name>
JWT_SECRET_KEY=<your-private-secret>
```

Replace the placeholders with the credentials and database name configured for your local PostgreSQL instance. Do not commit `.env` or share real secrets.

### 5. Start PostgreSQL and Qdrant

If you have already created the project's Docker containers, start them with:

```powershell
docker start permission-rag-postgres
docker start permission-rag-qdrant
```

If you are setting up from scratch, create PostgreSQL and Qdrant containers first, using the ports and database credentials that match your `.env` configuration.

### 6. Initialize PostgreSQL tables

Run this command from the repository root:

```powershell
@'
from src.db.identity_schema import create_identity_tables
from src.db.schema import (
    create_audit_logs_table,
    create_permission_audit_logs_table,
)

create_identity_tables()
create_audit_logs_table()
create_permission_audit_logs_table()

print("Database tables initialized")
'@ | python
```

This initializes the tenant, user, role, user-role mapping, retrieval-audit, and permission-audit tables.

### 7. Create the Qdrant collection

```powershell
python create_collection.py
```

This creates the `documents` collection used for semantic retrieval. Run it when the collection does not already exist.

### 8. Insert sample policy documents

```powershell
python insert_documents.py
```

This embeds and inserts the sample policy documents with tenant and permission metadata. Run it when you need to populate a fresh collection; avoid rerunning it blindly in an existing environment.

### 9. Run the tests

```powershell
python -m pytest -v
```

### 10. Start the API

```powershell
uvicorn src.api.main:app --reload
```

Open the interactive API documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

Use the configured demo identities to test authenticated requests and verify that tenant isolation and document permissions are enforced.

7. Open Swagger UI at `http://127.0.0.1:8000/docs`.

## Limitations

- Relevance checking uses a language model and may make incorrect decisions.
- The current authorization evaluation contains only five predefined cases.
- Passing tests do not constitute a formal security audit.

## Future Improvements

- Expand adversarial and permission-revocation tests.
- Evaluate retrieval quality and answer faithfulness separately from authorization.
- Improve relevance-check reliability based on measured failures.
