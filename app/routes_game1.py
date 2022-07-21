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


@app.route('/games/1',methods=["GET","POST"])
def game1():
    form=Game1Form()

    j1 = game1_worker(session['game1']['FOV_scale'], session['game1']['Matrix_scale'], session['game1']['zero_fill'],
                      session['game1']['Min_scale'], session['game1']['Max_scale'])

    if form.validate_on_submit():
        #TODO Update second Matrix scale with the zerofill field.

        j1 = game1_worker(float(form.FOV_scale.data), int(form.Matrix_scale.data) , int(form.zero_fill.data), float(form.min_scale.data),
                          float(form.max_scale.data))


    return render_template('game1.html',template_title="What is in an image?",
                           template_intro_text="Voxels, field-of-views, and resolution ", G1Form = form,
                           graphJSON_img = j1)


@socketio.on('Update param for Game1')
def update_parameter(info):
    # Update corresponding entry in session
    if info['id'] in ['Matrix_scale', 'zero_fill']:
        info['value'] = int(info['value'])

    else:
        info['value'] = float(info['value'])

    session['game1'][info['id']] = info['value']
    session.modified = True
    # If zero fill is changed, then matrix size = zero fill(smaller)
    # If FOV got changed, change matrix size based on FOV and voxel size

    if info['id'] == 'FOV_scale':
        print('yes')
        session['game1']['Matrix_scale'] = int(np.round(float(session['game1']['FOV_scale'])/(float(session['game1']['Voxel_scale']))))
        session['game1']['Voxel_scale'] = session['game1']['FOV_scale']/session['game1']['Matrix_scale']

    # Matrix Size is kept the same, voxel size increases.
    if info['id'] == 'Voxel_scale':
        print('printing VS')
        session['game1']['Matrix_scale'] = int(np.round_(float(session['game1']['FOV_scale'])/float(session['game1']['Voxel_scale'])))
        session['game1']['FOV_scale'] = session['game1']['Matrix_scale']* session['game1']['Voxel_scale']

    if info['id'] == 'Matrix_scale':
        print('printing MS')
        session['game1']['Voxel_scale'] = float(session['game1']['FOV_scale'])/(float(session['game1']['Matrix_scale']))

    if info['id'] == 'zero_fill':
        if session['game1']['Matrix_scale'] > session['game1']['zero_fill']:
            session['game1']['Matrix_scale'] = session['game1']['zero_fill']

    print(session['game1'])

    socketio.emit('G1 take session data', {'data': session['game1']})

    print(info)
    
