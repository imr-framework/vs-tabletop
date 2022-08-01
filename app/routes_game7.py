import threading
from workers.game7_worker import game7_prep3d_worker, game7_projection_worker
import numpy as np
from flask import flash, render_template, session, redirect, url_for
from flask_login import login_required, login_user, logout_user
import utils
from forms import *
from info import GAMES_DICT
from models import User, Calibration
from __main__ import app, login_manager, db, socketio

@app.route('/games/7', methods=["GET","POST"])
def game7():
    form=Game7Form()

    j1, voxels = game7_prep3d_worker(difficulty="all")
    j2, j3 = game7_projection_worker(voxels, session['game7']['proj3d'], session['game7']['proj2d'])

    if form.validate_on_submit():
        print('validate')
        j1, voxels = game7_prep3d_worker(difficulty="all")
        j2, j3 = game7_projection_worker(voxels, session['game7']['proj3d'], session['game7']['proj2d'])

    return render_template('game7.html', template="Projection Imaging", template_intro_text="Placeholder",
                           graphJSON_3dimg = j1, graphJSON_2dimg = j2, graphJSON_1dimg = j3)

@socketio.on('Update param for Game7')
def update_parameter(info):
    print(info['id'])
    if info['id'] in ['proj3d']:
        info['value'] = str(info['value'])

    elif info['id'] in ['proj2d']:
        info['value'] = float(info['value'])

    session['game7'][info['id']] = info['value']
    session.modified = True

    socketio.emit('G7 take session data', {'data': session['game1']})
    print(info)