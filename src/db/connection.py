import psycopg


DATABASE_URL = (
    "host=localhost "
    "port=5432 "
    "dbname=rag_db "
    "user=rag_user "
    "password=rag_password"
)


def get_connection():
    """
    Open and return a connection to PostgreSQL.
    """
    return psycopg.connect(DATABASE_URL)