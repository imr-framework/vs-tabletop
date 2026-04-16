import matplotlib

# Must run before any module imports matplotlib.pyplot (e.g. workers). Socket.IO and
# Flask run matplotlib from background threads; macOS GUI backend crashes (NSWindow).
matplotlib.use("Agg")

import os
import secrets
from flask import Flask, abort, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
from flask_socketio import SocketIO, emit
from flask_session import Session
#from vstabletop.main.paths import IMG_PATH, DATA_PATH


def _database_uri():
    """Resolve SQLAlchemy database URI: Postgres via DATABASE_URL, else local SQLite."""
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        return "sqlite:///myDB.db"
    # Heroku-style URLs use postgres:// which SQLAlchemy does not accept for psycopg2.
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    return url


# Use threading mode to avoid gevent/eventlet websocket stack incompatibilities.
# This keeps Socket.IO stable for local dev and single-instance deployments.
socketio = SocketIO(manage_session=False, async_mode="threading")
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    from .auth_clerk import clerk_enabled, clerk_publishable_key, clerk_frontend_api
    # Register blueprints TODO for all files
    from .models import db, User
    from .main.routes_main import bp_main
    from .games.routes_game1 import bp_games
    from .paths import IMG_PATH, DATA_PATH

    app.register_blueprint(bp_main)
    app.register_blueprint(bp_games)

    # Security-sensitive settings are configured by environment for deployment.
    secret_key = os.environ.get("SECRET_KEY", "").strip() or secrets.token_urlsafe(32)
    app.config["SECRET_KEY"] = secret_key
    app.config["WTF_CSRF_SECRET_KEY"] = os.environ.get("WTF_CSRF_SECRET_KEY", "").strip() or secret_key
    app.config["TESTING"] = os.environ.get("TESTING", "0").lower() in {"1", "true", "yes"}
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_FILE_DIR"] = os.environ.get("SESSION_FILE_DIR", "/tmp/flask_session")
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax")
    app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SESSION_COOKIE_SECURE", "1").lower() in {"1", "true", "yes"}
    # Add database location and settings
    #vstabletop.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)
    # Add database location
    #vstabletop.config['SQLALCHEMY_DATABASE_URI'] = 'splite:///myDB.db'
    ### -> uses DATABASE_URL for PostgreSQL; falls back to SQLite when unset
    app.config["SQLALCHEMY_DATABASE_URI"] = _database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}
    # more configuration
    UPLOAD_FOLDER = IMG_PATH
    app.config['UPLOAD_FOLDER_GAME2'] = UPLOAD_FOLDER / 'Game2'
    app.config['UPLOAD_FOLDER_SCAN'] = DATA_PATH / 'scan'
    # Enable flask-session
    Session(app)

    # Bind database to vstabletop
    db.init_app(app)

    # Enable Authentication through flask_login
    login_manager.init_app(app)

    # 3. Enable socketIO
    #socketio = SocketIO(app, manage_session=False)
    socketio.init_app(app)

    @app.context_processor
    def inject_clerk_context():
        return {
            "clerk_enabled": clerk_enabled(),
            "clerk_publishable_key": clerk_publishable_key(),
            "clerk_frontend_api": clerk_frontend_api(),
        }

    return app

