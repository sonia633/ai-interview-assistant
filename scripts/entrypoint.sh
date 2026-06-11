#!/usr/bin/env bash
set -e

echo "==> Waiting for database..."
python - <<'PY'
import os, time
import psycopg2
host = os.getenv("POSTGRES_HOST", "db")
port = int(os.getenv("POSTGRES_PORT", "5432"))
user = os.getenv("POSTGRES_USER", "interview")
pwd  = os.getenv("POSTGRES_PASSWORD", "interview")
db   = os.getenv("POSTGRES_DB", "interview_db")
for attempt in range(30):
    try:
        psycopg2.connect(host=host, port=port, user=user, password=pwd, dbname=db).close()
        print("Database is ready.")
        break
    except Exception as e:
        print(f"  db not ready ({attempt+1}/30): {e}")
        time.sleep(2)
else:
    raise SystemExit("Database never became available")
PY

echo "==> Running Alembic migrations..."
alembic upgrade head

echo "==> Starting Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
