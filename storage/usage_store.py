import json
import os
from datetime import date

from storage.db import database_enabled, ensure_schema, get_connection


USAGE_FILE = "data/generation_usage.json"
DEFAULT_DAILY_GENERATION_LIMIT = 5


def get_generation_limit():
    raw_limit = os.getenv(
        "POST_GENERATION_DAILY_LIMIT",
        str(DEFAULT_DAILY_GENERATION_LIMIT)
    )

    try:
        return int(raw_limit)
    except ValueError:
        return DEFAULT_DAILY_GENERATION_LIMIT


def _today_key():
    return date.today().isoformat()


def _load_local_usage():
    if not os.path.exists(USAGE_FILE):
        return {}

    with open(USAGE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_generation_usage():
    limit = get_generation_limit()
    today = _today_key()

    if database_enabled():
        ensure_schema()

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT usage_count
                    FROM generation_usage
                    WHERE usage_date = %s
                    """,
                    (today,)
                )
                row = cur.fetchone()

        used = row[0] if row else 0
    else:
        usage = _load_local_usage()
        used = int(usage.get(today, 0))

    remaining = None if limit <= 0 else max(0, limit - used)

    return {
        "date": today,
        "used": used,
        "limit": limit,
        "remaining": remaining,
        "allowed": limit <= 0 or used < limit,
    }


def assert_generation_allowed():
    usage = get_generation_usage()

    if usage["allowed"]:
        return usage

    raise RuntimeError(
        "Daily post generation limit reached "
        f"({usage['used']}/{usage['limit']} used for {usage['date']}). "
        "Increase POST_GENERATION_DAILY_LIMIT or try again tomorrow."
    )


def record_generation():
    today = _today_key()

    if database_enabled():
        ensure_schema()

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO generation_usage (usage_date, usage_count, updated_at)
                    VALUES (%s, 1, NOW())
                    ON CONFLICT (usage_date)
                    DO UPDATE SET
                        usage_count = generation_usage.usage_count + 1,
                        updated_at = NOW()
                    RETURNING usage_count
                    """,
                    (today,)
                )
                used = cur.fetchone()[0]

        limit = get_generation_limit()
        return {
            "date": today,
            "used": used,
            "limit": limit,
            "remaining": None if limit <= 0 else max(0, limit - used),
            "allowed": limit <= 0 or used < limit,
        }

    os.makedirs("data", exist_ok=True)

    usage = _load_local_usage()
    usage[today] = int(usage.get(today, 0)) + 1

    with open(USAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(usage, f, indent=2)

    return get_generation_usage()
