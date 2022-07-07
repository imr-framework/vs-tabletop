import threading

from flask import flash, render_template, session, redirect, url_for
from flask_login import login_required, login_user, logout_user
import utils
from forms import *
from info import GAMES_DICT
from models import User, Calibration
from __main__ import app, login_manager, db, socketio
@app.route('/games/1',methods=["GET","POST"])
def game1():
    form=Game1Form()
    if form.validate_on_submit():
        print(form.FOV_scale.data)
        print(form.Matrix_scale.data)
        print(form.Voxel_scale.data)



    return render_template('game1.html',template_title="What is in an image?",
                           template_intro_text="Voxels, field-of-views, and resolution ",template_game_form=None, G1Form = form)


@socketio.on('Update param for Game1')
def update_parameter(info):
    print(info)