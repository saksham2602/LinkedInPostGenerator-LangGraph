import json
import os
from datetime import datetime, timedelta, timezone

from psycopg.types.json import Jsonb

from storage.db import database_enabled, ensure_schema, get_connection


CACHE_FILE = "data/trend_cache.json"
DEFAULT_TTL_MINUTES = 60
CACHE_KEY = "ranked_trends"


def _cache_ttl():
    raw_value = os.getenv("TREND_CACHE_TTL_MINUTES", str(DEFAULT_TTL_MINUTES))

    try:
        minutes = int(raw_value)
    except ValueError:
        minutes = DEFAULT_TTL_MINUTES

    return timedelta(minutes=max(1, minutes))


def _parse_cached_at(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def load_ranked_trend_cache():
    if database_enabled():
        ensure_schema()

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT cached_at, trends, ranked_trends
                    FROM trend_cache
                    WHERE cache_key = %s
                    """,
                    (CACHE_KEY,)
                )

                row = cur.fetchone()

        if not row:
            return None

        cached_at, trends, ranked_trends = row

        if cached_at.tzinfo is None:
            cached_at = cached_at.replace(tzinfo=timezone.utc)

        if datetime.now(timezone.utc) - cached_at > _cache_ttl():
            return None

        if not isinstance(trends, list) or not isinstance(ranked_trends, list):
            return None

        return {
            "trends": trends,
            "ranked_trends": ranked_trends,
            "cached_at": cached_at.isoformat(),
        }

    if not os.path.exists(CACHE_FILE):
        return None

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None

    cached_at = _parse_cached_at(payload.get("cached_at"))

    if not cached_at:
        return None

    if cached_at.tzinfo is None:
        cached_at = cached_at.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) - cached_at > _cache_ttl():
        return None

    trends = payload.get("trends")
    ranked_trends = payload.get("ranked_trends")

    if not isinstance(trends, list) or not isinstance(ranked_trends, list):
        return None

    return {
        "trends": trends,
        "ranked_trends": ranked_trends,
        "cached_at": payload.get("cached_at"),
    }


def save_ranked_trend_cache(trends, ranked_trends):
    if database_enabled():
        ensure_schema()

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO trend_cache (
                        cache_key,
                        cached_at,
                        trends,
                        ranked_trends
                    )
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (cache_key)
                    DO UPDATE SET
                        cached_at = EXCLUDED.cached_at,
                        trends = EXCLUDED.trends,
                        ranked_trends = EXCLUDED.ranked_trends
                    """,
                    (
                        CACHE_KEY,
                        datetime.now(timezone.utc),
                        Jsonb(trends),
                        Jsonb(ranked_trends),
                    )
                )

        return

    os.makedirs("data", exist_ok=True)

    payload = {
        "cached_at": datetime.now(timezone.utc).isoformat(),
        "trends": trends,
        "ranked_trends": ranked_trends,
    }

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
