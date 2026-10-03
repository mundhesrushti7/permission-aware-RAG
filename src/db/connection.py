import psycopg

from src.config import DATABASE_URL


def get_connection():
    """
    Open and return a connection to PostgreSQL.
    """
    return psycopg.connect(DATABASE_URL)
