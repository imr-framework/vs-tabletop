import threading
from workers.game1_worker import game1_worker
import numpy as np
from flask import flash, render_template, session, redirect, url_for
from flask_login import login_required, login_user, logout_user
import utils
from forms import *
from info import GAMES_DICT
from models import User, Calibration
from __main__ import app, login_manager, db, socketio






@app.route('/games/3',methods=["GET","POST"])
def game3():
    return render_template('game3.html',template_title="Brains, please!",template_intro_text="Of mice and men",
                           template_game_form=None)