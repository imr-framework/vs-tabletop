
from flask import flash, render_template, session, redirect, url_for
from flask_login import login_required, login_user, logout_user
import utils
from forms import *
from info import GAMES_DICT
from models import User, Calibration
from __main__ import app, login_manager, db, socketio





@app.route('/games/8',methods=["GET","POST"])
def game8():
    return render_template('game8.html',template_title="Puzzled by Projection II",template_intro_text="Backward puzzle",
                           template_game_form=None,game_num=8)
