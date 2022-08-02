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
def game1():
    form=Game1Form()

    questions, success_text, uses_images = fetch_all_game1_questions()

    print(questions)
    print(success_text)
    print(uses_images)

    j1 = game1_worker(session['game1']['FOV_scale'], session['game1']['Matrix_scale'], session['game1']['zero_fill'],
                      session['game1']['Min_scale'], session['game1']['Max_scale'])

    if form.validate_on_submit():
        #TODO Update second Matrix scale with the zerofill field.
        print('validate')
        j1 = game1_worker(float(form.FOV_scale.data), int(form.Matrix_scale.data) , int(form.zero_fill.data), float(form.min_scale.data),
                          float(form.max_scale.data))


    return render_template('game1.html',template_title="What is in an image?",
                           template_intro_text="Voxels, field-of-views, and resolution ", G1Form = form,
                           graphJSON_img = j1, questions=questions, success_text=success_text, uses_images=uses_images)


@socketio.on('Update param for Game1')
def update_parameter(info):
    print(session)
    # Update corresponding entry in session
    print(info['id'])
    if info['id'] in ['Matrix_scale', 'zero_fill']:
        info['value'] = int(info['value'])

    elif info['id'] in ['P1_q-0', 'P1_q', 'P1_q-1', 'P1_q-2', 'P1_q-3', 'P2_q', 'P2_q-0', 'P2_q-1', 'P2_q-2', 'a', 'b', 'c', 'd']:
        info['value'] = str(info['value'])

    elif info['id'] in ['FOV_scale', 'Voxel_scale']:
        info['value'] = float(info['value']) / 1000
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

        elif session['game1']['Matrix_scale'] < session['game1']['zero_fill']:
            session['game1']['zero_fill'] = session['game1']['Matrix_scale']

    elif info['id'] == 'zero_fill':
        if session['game1']['Matrix_scale'] > session['game1']['zero_fill']:
            session['game1']['Matrix_scale'] = session['game1']['zero_fill']

        elif session['game1']['Matrix_scale'] < session['game1']['zero_fill']:
            session['game1']['Matrix_scale'] = session['game1']['zero_fill']




    elif info['id'] in ['P1_q']:
        print('changing p1')
        info['id'] = info['id']
        info['value'] = str(info['value'])

    elif info['id'] in ['P1_q-0']:
        print('changing p1-0')
        info['id'] = info['id'][0:4]
        info['value'] = str(info['value'])

    elif info['id'] in ['P1_q-1']:
        print('changing p1-1')
        info['id'] = info['id'][0:4]
        info['value'] = str(info['value'])

    elif info['id'] in ['P1_q-2']:
        print('changing p1-2')
        info['id'] = info['id'][0:4]
        print(info['id'])
        info['value'] = str(info['value'])

    elif info['id'] in ['P1_q-3']:
        print('changing p1-2')
        info['id'] = info['id'][0:4]
        info['value'] = str(info['value'])

    elif info['id'] in ['P2_q']:
        info['id'] = info['id'][0:4]
        info['value'] = str(info['value'])

    elif info['id'] in ['P2_q-0']:
        info['id'] = info['id'][0:4]
        info['value'] = str(info['value'])

    elif info['id'] in ['P2_q-1']:
        info['id'] = info['id'][0:4]
        info['value'] = str(info['value'])

    elif info['id'] in ['P2_q-2']:
        info['id'] = info['id'][0:4]
        info['value'] = str(info['value'])

    elif info['id'] in ['toSlider']:
        session['game1']['Max_scale'] = info['value'] / 100
        print(session['game1']['Max_scale'])

    elif info['id'] in ['fromSlider']:
        session['game1']['Min_scale'] = info['value'] / 100

    print(session['game1'], 'hi')

    #session['game1'][info['id']] = info['value']

    session.modified = True

    socketio.emit('G1 take session data', {'data': session['game1']})

    print(info)
    

def fetch_all_game1_questions():
    uses_images_list = []
    success_text = 10*['Correct! Move on to the next question.']
    for id in range(101,111):
        print(id)
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
                          'correct': corr_array_new.index(True)})

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