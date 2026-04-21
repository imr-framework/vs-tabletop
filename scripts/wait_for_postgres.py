"""
Wait until PostgreSQL accepts connections on DATABASE_URL.

Used by docker_entrypoint.sh before running gunicorn.
"""
from __future__ import annotations

import os
import sys
import time
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import psycopg2


def _ensure_libpq_timeouts(url: str) -> str:
    """Put connect_timeout in the URI so libpq honors it (kwargs alone can hang on some stacks)."""
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    parsed = urlparse(url)
    q = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if "connect_timeout" not in q:
        q["connect_timeout"] = "10"
    return urlunparse(parsed._replace(query=urlencode(q)))


def main():
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        print("DATABASE_URL is empty", file=sys.stderr)
        sys.exit(1)
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    url = _ensure_libpq_timeouts(url)

    deadline = time.time() + float(os.environ.get("DB_WAIT_TIMEOUT", "120"))
    last_err = None
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        try:
            conn = psycopg2.connect(url)
            conn.close()
            print("Database is reachable.", flush=True)
            return
        except Exception as e:
            last_err = e
            if attempt == 1 or attempt % 5 == 0:
                print(f"  still waiting ({attempt}): {e}", flush=True)
            time.sleep(1.0)
    print(f"Timed out waiting for database. Last error: {last_err}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
