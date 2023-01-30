from flask import Flask, abort, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
from os import environ # this line should go at the top of your file
from flask_socketio import SocketIO, emit
from flask_session import Session
#from vstabletop.main.paths import IMG_PATH, DATA_PATH

socketio = SocketIO(manage_session=False)
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    # Register blueprints TODO for all files
    from .models import db, User
    from .main.routes_main import bp_main
    from .games.routes_game1 import bp_games
    from .paths import IMG_PATH, DATA_PATH

    app.register_blueprint(bp_main)
    app.register_blueprint(bp_games)

    # Set up config
    app.config["SECRET_KEY"] = "how-i-spin"
    app.config["WTF_CSRF_SECRET_KEY"] = "how-i-spin"
    app.config["TESTING"] = True
    app.config['SESSION_TYPE'] = 'filesystem'
    # Add database location and settings
    #vstabletop.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)
    # Add database location
    #vstabletop.config['SQLALCHEMY_DATABASE_URI'] = 'splite:///myDB.db'
    ### -> uses DATABASE_URL (connecting to PostgreSQL instead of SQLite IF POSSIBLE, for Heroku deployment)
    app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL') or 'sqlite:///myDB.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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

    return app

