import threading
from vstabletop.workers.game1_worker import game1_worker
import numpy as np
from flask import flash, render_template, session, redirect, url_for, current_app, Blueprint
from flask_login import login_required, login_user, logout_user
import vstabletop.utils as utils
from vstabletop.forms import *
from vstabletop.info import GAMES_DICT, GAME1_BACKGROUND
from vstabletop.info import GAME1_INSTRUCTIONS

#from __main__ import app, login_manager, db, socketio
from .. import socketio
from vstabletop.models import MultipleChoice

questions = []
bp_games = Blueprint('bp_games',__name__, template_folder="templates/games", url_prefix='/games')


#@app.route('/games/1',methods=["GET","POST"])
@bp_games.route('/1',methods=["GET","POST"])
@login_required
def game1():
    """Game 1 view function

    Returns
    -------
    str
        HTML to display on game 1 path
    """
    form=Game1Form()
    all_Qs = MultipleChoice.query.filter_by(game_number=1).all()
    questions, success_text, uses_images = utils.process_all_game_questions(all_Qs)

    j1 = game1_worker(session['game1']['FOV_scale'], session['game1']['Matrix_scale'], session['game1']['zero_fill'],
                      session['game1']['Min_scale'], session['game1']['Max_scale'])

    if form.validate_on_submit():
        print('validate')
        j1 = game1_worker(float(form.FOV_scale.data), int(form.Matrix_scale.data) , int(form.zero_fill.data), float(form.min_scale.data),
                          float(form.max_scale.data))

    return render_template('games/game1.html',template_title="What is in an image?",
                           template_intro_text="Voxels, field-of-views, and resolution ", G1Form = form,
                           graphJSON_img = j1, questions=questions, success_text=success_text, uses_images=uses_images,
                           game_num = 1, background=GAME1_BACKGROUND,instructions=GAME1_INSTRUCTIONS)


@socketio.on('Acquire game 1 image')
def update_image(info):
    print(info)
    j1 = game1_worker(float(info['fov']) * 1e-3, info['n'], info['zerofill'], float(info['window_min']) * 0.01,
                      float(info['window_max']) * 0.01)
    socketio.emit('Deliver image', {'graphData': j1})


@socketio.on('Update param for Game1')
def update_parameter(info):
    """Update session parameters in response to frontend message
    """

    # print(session)
    # Update corresponding entry in session
    print(info['id'], 'id', info['value'], 'value')
    if info['id'] in ['Matrix_scale', 'zero_fill']:
        info['value'] = int(info['value'])
    elif info['id'] in ['P1_q-0', 'P1_q', 'P1_q-1', 'P1_q-2', 'P1_q-3', 'P2_q', 'P2_q-0', 'P2_q-1', 'P2_q-2', 'a', 'b',
                        'c', 'd']:
        info['value'] = str(info['value'])
    elif info['id'] in ['FOV_scale', 'Voxel_scale']:
        info['value'] = float(info['value']) / 1000
    elif info['id'] in ['flexCheckChecked1', 'flexCheckChecked2', 'flexCheckChecked3', 'flexCheckChecked4']:
        info['value']
    elif info['value'] not in ['a', 'b', 'c', 'd']:
        try:
            info['value'] = float(info['value'])
        except:
            print('Value cannot be converted to float')

    session['game1'][info['id']] = info['value']
    session.modified = True

    # If zero fill is changed, then matrix size = zero fill(smaller)
    # If FOV got changed, change matrix size based on FOV and voxel size

    if info['id'] == 'FOV_scale':
        print('FOV changed')
        print('Old:', session['game1'])
        session['game1']['Matrix_scale'] = int(
            np.round(float(session['game1']['FOV_scale']) / (float(session['game1']['Voxel_scale']))))
        session['game1']['Voxel_scale'] = session['game1']['FOV_scale'] / session['game1']['Matrix_scale']

        if session['game1']['Matrix_scale'] > session['game1']['zero_fill']:
            session['game1']['zero_fill'] = session['game1']['Matrix_scale']

        elif session['game1']['Matrix_scale'] < session['game1']['zero_fill']:
            session['game1']['Matrix_scale'] = session['game1']['zero_fill']

        print('New:', session['game1'])

    # Matrix Size is kept the same, voxel size increases.
    elif info['id'] == 'Voxel_scale':

        print('printing VS')
        session['game1']['Matrix_scale'] = int(
            np.round_(float(session['game1']['FOV_scale']) / float(session['game1']['Voxel_scale'])))
        session['game1']['FOV_scale'] = session['game1']['Matrix_scale'] * session['game1']['Voxel_scale']

        if session['game1']['Matrix_scale'] > session['game1']['zero_fill']:
            session['game1']['zero_fill'] = session['game1']['Matrix_scale']

        elif session['game1']['Matrix_scale'] < session['game1']['zero_fill']:
            session['game1']['Matrix_scale'] = session['game1']['zero_fill']

    elif info['id'] == 'Matrix_scale':
        print('printing MS')
        session['game1']['Voxel_scale'] = float(session['game1']['FOV_scale']) / (
            float(session['game1']['Matrix_scale']))
        session['game1']['zero_fill'] = session['game1']['Matrix_scale']


    elif info['id'] == 'zero_fill':
        if session['game1']['Matrix_scale'] > session['game1']['zero_fill']:
            session['game1']['Matrix_scale'] = session['game1']['zero_fill']

    elif info['id'] == 'toSlider':
        session['game1']['Max_scale'] = info['value'] / 100

    elif info['id'] == 'fromSlider':
        session['game1']['Min_scale'] = info['value'] / 100

    elif info['id'] == "toInput":
        if (info['value'] > 100):
            info['value'] = 100
        session['game1']['Max_scale'] = info['value'] / 100

    elif info['id'] == "fromInput":
        session['game1']['Min_scale'] = info['value'] / 100

    session.modified = True

    session_game1 = {'Matrix_scale': session['game1']['Matrix_scale'], 'FOV_scale': session['game1']['FOV_scale'],
                     'Voxel_scale': session['game1']['Voxel_scale'],
                     'zero_fill': session['game1']['zero_fill'], 'Min_scale': session['game1']['Min_scale'],
                     'Max_scale': session['game1']['Max_scale']}

    socketio.emit('G1 take session data', {'data': session_game1})


@socketio.on("Updating choice for Game 1")
def update_Choice(info):
    print(info)
    if info['choice'] == 'a':
        info['choice'] = 0
    elif info['choice'] == 'b':
        info['choice'] = 1
    elif info['choice'] == 'c':
        info['choice'] = 2
    elif info['choice'] == 'd':
        info['choice'] = 3
    if info['choice'] in questions[0]['correct']:
        print('correct')
        socketio.emit("Correct")
    else:
        print("No")


@socketio.on('Reset param for Game1')
def reset():
    session['game1']['Matrix_scale'] = 128
    session['game1']['zero_fill'] = 128
    session['game1']['Voxel_scale'] = 1.00
    session['game1']['FOV_scale'] = .128
    session.modified = True
    print('reset')
    print(session['game1'])

    j1 = game1_worker(session['game1']['FOV_scale'], session['game1']['Matrix_scale'], session['game1']['zero_fill'],
                      session['game1']['Min_scale'], session['game1']['Max_scale'])

    socketio.emit('Recreate Image', {'data': j1})


@socketio.on('game 1 question answered')
def update_mc_progress(msg):
    status = session['game1']['mc_status_list']
    print(status, "status")
    status[int(msg['ind'])] = bool(msg['correct'])

    utils.update_session_subdict(session, 'game1', {'mc_status_list': status})

    session['game1']['progress'].num_correct = sum(status)
    session['game1']['progress'].update_stars()

    print('Game 1 progress updated: ', session['game1']['progress'])

    socketio.emit('renew stars', {'stars': session['game1']['progress'].num_stars})



@socketio.on('game1 update progress')
def game1_update_progress(msg):
    task = int(msg['task'])
    # Only update if there is progress (no backtracking)
    if task > session['game1']['task_completed']:
        utils.update_session_subdict(session, 'game1', {'task_completed': task})
        print('Task ', session['game1']['task_completed'], ' completed for game 1')

        # Update database object
        session['game1']['progress'].num_steps_complete = task
        session['game1']['progress'].update_stars()
        print('Game 1 progress updated: ', session['game1']['progress'])
        socketio.emit('renew stars', {'stars': session['game1']['progress'].num_stars})
