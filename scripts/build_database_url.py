"""
Build DATABASE_URL for Docker (URL-safe credentials + stable libpq options).

If POSTGRES_HOST is set: postgresql://user:pass@host:port/db?sslmode=disable&connect_timeout=10
Otherwise: use DATABASE_URL from the environment (Heroku-style), only normalizing postgres://.
"""
from __future__ import annotations

import os
import sys
from urllib.parse import parse_qsl, quote_plus, urlencode, urlparse, urlunparse


def _with_query(url: str, extra: dict[str, str]) -> str:
    parsed = urlparse(url)
    pairs = list(parse_qsl(parsed.query, keep_blank_values=True))
    keys = {k for k, _ in pairs}
    for k, v in extra.items():
        if k not in keys:
            pairs.append((k, v))
    return urlunparse(parsed._replace(query=urlencode(pairs)))


def main() -> None:
    host = os.environ.get("POSTGRES_HOST", "").strip()
    if host:
        user = os.environ.get("POSTGRES_USER", "").strip()
        password = os.environ.get("POSTGRES_PASSWORD", "")
        db = os.environ.get("POSTGRES_DB", "").strip()
        if not user or not db:
            print("POSTGRES_USER and POSTGRES_DB are required when POSTGRES_HOST is set.", file=sys.stderr)
            sys.exit(1)
        port = (os.environ.get("POSTGRES_INTERNAL_PORT") or "5432").strip() or "5432"
        u = quote_plus(user)
        p = quote_plus(password)
        url = f"postgresql://{u}:{p}@{host}:{port}/{db}"
        url = _with_query(url, {"sslmode": "disable", "connect_timeout": "10"})
        print(url)
        return

    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        print("Set POSTGRES_HOST + POSTGRES_* for Docker, or DATABASE_URL.", file=sys.stderr)
        sys.exit(1)
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    print(url)


if __name__ == "__main__":
    main()
