
from flask import flash, render_template, session, redirect, url_for
from flask_login import login_required, login_user, logout_user
import utils
from forms import *
from info import GAMES_DICT
from models import User, Calibration
from __main__ import app, login_manager, db, socketio
# Games
@app.route('/games/2',methods=["GET","POST"])
def game2():
    return render_template('game2.html',template_title="K-space magik",template_intro_text="Can you find your way?",
                           template_game_form=None, game_num=2)

