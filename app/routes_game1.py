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


from models import MultipleChoice

questions = []

@app.route('/games/1',methods=["GET","POST"])
@login_required
def game1():
    form=Game1Form()

    questions, success_text, uses_images = fetch_all_game1_questions()

    print(questions)
    print(success_text)
    print(uses_images)

    j1 = game1_worker(session['game1']['FOV_scale'], session['game1']['Matrix_scale'], session['game1']['zero_fill'],
                      session['game1']['Min_scale'], session['game1']['Max_scale'])

    update_task_progress()

    if form.validate_on_submit():
        #TODO Update second Matrix scale with the zerofill field.
        print('validate')
        j1 = game1_worker(float(form.FOV_scale.data), int(form.Matrix_scale.data) , int(form.zero_fill.data), float(form.min_scale.data),
                          float(form.max_scale.data))

    return render_template('game1.html',template_title="What is in an image?",
                           template_intro_text="Voxels, field-of-views, and resolution ", G1Form = form,
                           graphJSON_img = j1, questions=questions, success_text=success_text, uses_images=uses_images,
                           game_num = 1)


@socketio.on('Update param for Game1')
def update_parameter(info):
    print(session)
    # Update corresponding entry in session
    print(info['id'], 'id', info['value'], 'value')
    if info['id'] in ['Matrix_scale', 'zero_fill']:
        info['value'] = int(info['value'])

    elif info['id'] in ['P1_q-0', 'P1_q', 'P1_q-1', 'P1_q-2', 'P1_q-3', 'P2_q', 'P2_q-0', 'P2_q-1', 'P2_q-2', 'a', 'b', 'c', 'd']:
        info['value'] = str(info['value'])

    elif info['id'] in ['FOV_scale', 'Voxel_scale']:
        info['value'] = float(info['value']) / 1000
    elif info['id'] in ['flexCheckChecked1', 'flexCheckChecked2', 'flexCheckChecked3', 'flexCheckChecked4']:
        info['value']
    else:
        info['value'] = float(info['value'])

    session['game1'][info['id']] = info['value']
    session.modified = True

    # If zero fill is changed, then matrix size = zero fill(smaller)
    # If FOV got changed, change matrix size based on FOV and voxel size

    if info['id'] == 'FOV_scale':
        print('FOV changed')
        print('Old:',session['game1'])
        session['game1']['Matrix_scale'] = int(np.round(float(session['game1']['FOV_scale'])/(float(session['game1']['Voxel_scale']))))
        session['game1']['Voxel_scale'] = session['game1']['FOV_scale']/session['game1']['Matrix_scale']

        if session['game1']['Matrix_scale'] > session['game1']['zero_fill']:
            session['game1']['zero_fill'] = session['game1']['Matrix_scale']

        elif session['game1']['Matrix_scale'] < session['game1']['zero_fill']:
            session['game1']['Matrix_scale'] = session['game1']['zero_fill']

        print('New:',session['game1'])

    # Matrix Size is kept the same, voxel size increases.
    elif info['id'] == 'Voxel_scale':

        print('printing VS')
        session['game1']['Matrix_scale'] = int(np.round_(float(session['game1']['FOV_scale'])/float(session['game1']['Voxel_scale'])))
        session['game1']['FOV_scale'] = session['game1']['Matrix_scale']* session['game1']['Voxel_scale']

        if session['game1']['Matrix_scale'] > session['game1']['zero_fill']:
            session['game1']['zero_fill'] = session['game1']['Matrix_scale']

        elif session['game1']['Matrix_scale'] < session['game1']['zero_fill']:
            session['game1']['Matrix_scale'] = session['game1']['zero_fill']

    elif info['id'] == 'Matrix_scale':
        print('printing MS')
        session['game1']['Voxel_scale'] = float(session['game1']['FOV_scale'])/(float(session['game1']['Matrix_scale']))

        if session['game1']['Matrix_scale'] > session['game1']['zero_fill']:
            print("changing")
            session['game1']['zero_fill'] = session['game1']['Matrix_scale']


    elif info['id'] == 'zero_fill':
        if session['game1']['Matrix_scale'] > session['game1']['zero_fill']:
            session['game1']['Matrix_scale'] = session['game1']['zero_fill']

    elif info['id'] == 'toSlider':
        session['game1']['Max_scale'] = info['value'] / 100

    elif info['id'] == 'fromSlider':
        session['game1']['Min_scale'] = info['value'] / 100

    elif info['id'] == "toInput":
        if(info['value'] > 100):
            info['value'] = 100
        session['game1']['Max_scale'] = info['value'] / 100

    elif info['id'] == "fromInput":
        session['game1']['Min_scale'] = info['value'] / 100

    session.modified = True


    session_game1 = {'Matrix_scale': session['game1']['Matrix_scale'], 'FOV_scale': session['game1']['FOV_scale'], 'Voxel_scale': session['game1']['Voxel_scale'],
                     'zero_fill':session['game1']['zero_fill'],'Min_scale': session['game1']['Min_scale'],'Max_scale': session['game1']['Max_scale']}

    socketio.emit('G1 take session data', {'data': session_game1})

    #socketio.emit('G1 take session data', {'data': session['game1']})


    

def fetch_all_game1_questions():
    uses_images_list = []
    success_text = 10*['Correct! Move on to the next question.']
    for id in range(101,111):
        Q = MultipleChoice.query.get(id)

        qdata = Q.get_randomized_data()
        uses_images_list.append(Q.uses_images)

        corr_array = [l==qdata[2] for l in ['A','B','C','D']]
        corr_array_new = []
        qchoices = []
        for ind in range(len(qdata[1])):
            if len(qdata[1][ind])!=0:
                qchoices.append(qdata[1][ind])
                corr_array_new.append(corr_array[ind])

        questions.append({'text': qdata[0],
                          'choices':qchoices,
                          'correct': corr_array_new.index(True),
                          'main_image_path': Q.main_image_path})

    # TODO Rishi replace success text as needed
    success_text[0] = "You got the first answer correct!"
    success_text[1] = "You got the second answer correct!"

    return questions, success_text, uses_images_list

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

def update_task_progress():
    if session['game1']['current_task'] == 1:
        # check if task 1 is complete
        fov = session['game1']['FOV_scale']
        if (fov >= 0.2 and fov <= 0.3):
            session['game1']['Matrix_scale'] = 128
            session['game1']['completed_task'] = 1
            session['game1']['current_task'] = 2
            print(session['game1']['completed_task'])
        else:
            print("task 1 failed")
    elif session['game1']['current_task'] == 2:
        if session['game1']['Matrix_scale'] > 300:
            session['game1']['completed_task'] = 2
            session['game1']['current_task'] = 3
            print(session['game1']['completed_task'])
        else:
            print("Task 2 failed")
    elif session['game1']['current_task'] == 3:
        print('Updating Matrix size')

        if session['game1']['zero_fill'] == 400:
            session['game1']['completed_task'] = 3
            session['game1']['current_task'] = 4
            print(session['game1']['completed_task'])
        else:
            print("Task 3 failed")
    elif session['game1']['current_task'] == 4:
        if session['game1']['Min_scale'] < 0.02 and session['game1']['Max_scale'] > 0.98:
            session['game1']['completed_task'] = 4
            print(session['game1']['completed_task'])
        else:
            print("Task 4 failed")

    session['game1']['progress'].num_steps_complete = session['game1']['completed_task']
    print(session['game1']['progress'])
    session['game1']['progress'].update_stars()
    socketio.emit('renew stars', {'stars': session['game1']['progress'].num_stars})

