import os

import psycopg
from dotenv import load_dotenv


load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")
_SCHEMA_READY = False


def database_enabled():
    return bool(DATABASE_URL)


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured")

    return psycopg.connect(DATABASE_URL)


def ensure_schema():
    global _SCHEMA_READY

    if _SCHEMA_READY or not database_enabled():
        return

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS post_memory (
                    id BIGSERIAL PRIMARY KEY,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    record JSONB NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS evaluations (
                    id BIGSERIAL PRIMARY KEY,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    record JSONB NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS trend_cache (
                    cache_key TEXT PRIMARY KEY,
                    cached_at TIMESTAMPTZ NOT NULL,
                    trends JSONB NOT NULL,
                    ranked_trends JSONB NOT NULL
                )
                """
            )

    _SCHEMA_READY = True
