#!/usr/bin/env bash
set -euo pipefail

# Compose sets POSTGRES_HOST=db and POSTGRES_*; other deployments use DATABASE_URL.
export DATABASE_URL="$(python3 /app/scripts/build_database_url.py)"
if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "Could not resolve DATABASE_URL; cannot start."
  exit 1
fi

echo "Waiting for database..."
python3 /app/scripts/wait_for_postgres.py

if [[ "${AUTO_DB_INIT:-0}" == "1" ]]; then
  echo "Running DB init (create_all)..."
  python3 /app/scripts/init_db.py
fi

exec "$@"
