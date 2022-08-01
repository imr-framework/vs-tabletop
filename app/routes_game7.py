import threading
from workers.game7_worker import game7_prep3d_worker, game7_projection_worker, game7_empty_plots_worker
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

    #j1, voxels = game7_prep3d_worker(difficulty="all")
    #j2, j3 = game7_projection_worker(voxels, session['game7']['proj3d'], session['game7']['proj2d'])


    #j1, voxels = game7_prep3d_worker(name='letterC')
    #j2, j3 = game7_projection_worker(voxels, proj3d_axis, proj2d_angle)

    j1, j2, j3 = game7_empty_plots_worker()

    if form.validate_on_submit():
        print('validated')
        print(form)
        if form.phantom_type_field.data == 'random':
            j1, voxels = game7_prep3d_worker(difficulty="all")
        else:
            j1, voxels = game7_prep3d_worker(name=form.phantom_type_field.data)

        j2, j3 = game7_projection_worker(voxels,
                                         form.proj_2d_axis_field.data,
                                         float(form.proj_1d_angle_field.data))
                                         #session['game7']['proj3d'], session['game7']['proj2d'])

    return render_template('game7.html',G7Form=form, template_title="Projection Imaging",
                           template_intro_text="Forward puzzle",
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

