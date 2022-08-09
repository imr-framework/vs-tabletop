from flask import Flask, abort, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
from os import environ # this line should go at the top of your file
from flask_socketio import SocketIO, emit
from flask_session import Session

app = Flask(__name__)
app.config["SECRET_KEY"] = "how-i-spin"
app.config["WTF_CSRF_SECRET_KEY"] = "how-i-spin"
app.config["TESTING"] = True
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

#app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)



# App - connect to other libraries to enable stuff
# 1. Enable database through SQLAlchemy
# Add database location
#app.config['SQLALCHEMY_DATABASE_URI'] = 'splite:///myDB.db'
### -> uses DATABASE_URL (connecting to PostgreSQL instead of SQLite IF POSSIBLE, for Heroku deployment)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL') or 'sqlite:///myDB.db'
# Turn off notification at every change
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Create database and bind it to app
db = SQLAlchemy(app)

# 2. Enable Authentication through flask_login
# Login manager
login_manager = LoginManager()
login_manager.init_app(app)

# 3. Enable socketIO
socketio = SocketIO(app, manage_session=False)


def launch_virtualscanner():
    import routes_main
    import routes_game5
    import routes_games
    import routes_game1
    import routes_game3
    import routes_game7
    #app.run()
    socketio.run(app,debug=True,host="0.0.0.0")

if __name__ == '__main__':
    launch_virtualscanner()