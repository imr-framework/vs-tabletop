"""
Create application database tables (and optional default admin user).

Usage (PostgreSQL):
  export DATABASE_URL="postgresql://USER:PASS@HOST:5432/DBNAME"
  python scripts/init_db.py

Optional:
  INIT_ADMIN=1   Create default admin / 123456 if missing (dev convenience only).
"""
from __future__ import annotations

import os
import sys

# Repo root on sys.path when run as: python scripts/init_db.py
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from vstabletop import create_app  # noqa: E402
from vstabletop.models import db, User  # noqa: E402


def main():
    init_admin = os.environ.get("INIT_ADMIN", "").lower() in {"1", "true", "yes"}
    app = create_app()
    uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    print("Using database URI:", uri)

    with app.app_context():
        db.create_all()
        print("Tables created (create_all).")

        if init_admin:
            if User.query.filter_by(username="admin").first() is None:
                u = User(username="admin")
                u.set_password("123456")
                db.session.add(u)
                db.session.commit()
                print('Created default user "admin" (password: 123456). Change this in production.')
            else:
                print('User "admin" already exists; skipping.')


if __name__ == "__main__":
    main()
