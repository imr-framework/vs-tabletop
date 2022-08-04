import threading

from flask_wtf import form

from workers.game3_worker import game3_worker
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
    form=Game3Form()



    j1, j2 = game3_worker(session['game3']['TR'] / 1000, session['game3']['TE'] / 1000, session['game3']['FA'])
    update_task_progress()

    if form.validate_on_submit():
        print('validate')
        j1, j2 = game3_worker(session['game3']['TR'], session['game3']['TE'], session['game3']['FA'])

    print(session['game3'])
    return render_template('game3.html', template_title="Brains, please!", template_intro_text="Of mice and men",
                           G3Form=form, graphJSON_img = j1, graphJSON_bar = j2)

@socketio.on('Update param for Game3')
def update_parameter(info):
    print(info['id'])
    print('inside update param')
    if info['id'] in ['TR', 'TE', 'FA']:
        info['value'] = float(info['value'])

    elif info['id'] in ['TR']:
        if info['value'] < float(session['game1']['TE']):
            info['value'] = session['game1']['TE']

    elif info['id'] in ['options-0']:
        info['id'] = info['id'][0:7]
        info['value'] = str(info['value'])
        session['game3']['TR'] = 0.5
        session['game3']['TE'] = 0.01

    elif info['id'] in ['options-1']:
        info['id'] = info['id'][0:7]
        info['value'] = str(info['value'])
        session['game3']['TR'] = 4
        session['game3']['TE'] = 0.05

    elif info['id'] in ['options-2']:
        info['id'] = info['id'][0:7]
        info['value'] = str(info['value'])
        session['game3']['TR'] = 4
        session['game3']['TE'] = 0.01

    elif info['id'] in ['P1_q']:
        info['id'] = info['id']
        info['value'] = str(info['value'])

    elif info['id'] in ['P1_q-0']:
        info['id'] = info['id'][0:4]
        info['value'] = str(info['value'])

    elif info['id'] in ['P1_q-1']:
        info['id'] = info['id'][0:4]
        info['value'] = str(info['value'])

    elif info['id'] in ['P2_q-0']:
        info['id'] = info['id'][0:4]
        info['value'] = str(info['value'])

    elif info['id'] in ['P2_q']:
        info['id'] = info['id']
        info['value'] = str(info['value'])

    elif info['id'] in ['P2_q-1']:
        info['id'] = info['id'][0:4]
        info['value'] = str(info['value'])

    session['game3'][info['id']] = info['value']
    print(session['game3'])
    session.modified = True

    session_game3 = {'TR': session['game3']['TR'], 'TE': session['game3']['TE'], 'FA': session['game3']['FA'],
                     'options': session['game3']['options'], 'P1_q': session['game3']['P1_q'], 'P2_q': session['game3']['P2_q']}
    socketio.emit('G3 take session data', {'data': session_game3})

def update_task_progress():
    if session['game3']['current_task'] == 1:
        P1_q = session['game3']['P1_q']
        print(session['game3']['completed_task'])
        if(P1_q == 'T1'):
            session['game3']['completed_task'] = 1
            session['game3']['current_task'] = 2
            print(session['game3']['completed_task'])
        else:
            print("task 1 failed")
    elif session['game3']['current_task'] == 2:
        P2_q = session['game3']['P2_q']
        if(P2_q == 'Contrast Increases'):
            session['game3']['completed_task'] = 2
            session['game3']['current_task'] = 3
        else:
            print('task 2 failed')

