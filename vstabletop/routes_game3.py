from workers.game3_worker import game3_worker
from flask import flash, render_template, session, redirect, url_for
from flask_login import login_required, login_user, logout_user
import vstabletop.utils as utils
from vstabletop.forms import *
from vstabletop.info import GAMES_DICT, GAME3_BACKGROUND
from __main__ import app, login_manager, db, socketio

# TODO
from vstabletop.models import MultipleChoice
questions = []


@app.route('/games/3',methods=["GET","POST"])
@login_required
def game3():
    form=Game3Form()

    questions, success_text, uses_images = fetch_all_game3_questions()
    print(questions)

    j1, j2 = game3_worker(session['game3']['TR'] / 1000, session['game3']['TE'] / 1000, session['game3']['FA'])

    update_task_progress()

    if form.validate_on_submit():
        print('validate')
        j1, j2 = game3_worker(session['game3']['TR'] / 1000, session['game3']['TE'] / 1000, session['game3']['FA'])

    print(session['game3'])
    return render_template('game3.html', template_title="Brains, please!", template_intro_text="",
                           G3Form=form, graphJSON_img = j1, graphJSON_bar = j2, questions = questions,
                           success_text=success_text, uses_images=uses_images, game_num=3,background=GAME3_BACKGROUND)

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
        session['game3']['TR'] = 500
        session['game3']['TE'] = 14
        session['game3']['FA'] = 90

    elif info['id'] in ['options-1']:
        info['id'] = info['id'][0:7]
        info['value'] = str(info['value'])
        session['game3']['TR'] = 4000
        session['game3']['TE'] = 100
        session['game3']['FA'] = 90


    elif info['id'] in ['options-2']:
        info['id'] = info['id'][0:7]
        info['value'] = str(info['value'])
        session['game3']['TR'] = 9000
        session['game3']['TE'] = 20
        session['game3']['FA'] = 90


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

    elif info['id'] in ['P3_q-0']:
        info['id'] = info['id'][0:4]
        info['value'] = str(info['value'])

    elif info['id'] in ['P3_q-1']:
        info['id'] = info['id'][0:4]
        info['value'] = str(info['value'])

    elif info['id'] in ['P3_q-2']:
        info['id'] = info['id'][0:4]
        info['value'] = str(info['value'])

    elif info['id'] in ['P3_q']:
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
        if(P1_q == 'T1w'):
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
    elif session['game3']['P3_q'] == "CSF":
        if session['game3']['current_task'] == 3:
            P3_q = session['game3']['P3_q']
            if (P3_q == 'CSF'):
                print('correct ans for 3rd')
                session['game3']['completed_task'] = 3
            else:
                print('task 3 failed')

    session['game3']['progress'].num_steps_complete = session['game3']['completed_task']
    print(session['game3']['progress'])
    session['game3']['progress'].update_stars()
    socketio.emit('renew stars', {'stars': session['game3']['progress'].num_stars})

def fetch_all_game3_questions():
    uses_images_list = []
    all_Qs = MultipleChoice.query.filter_by(game_number=3).all()
    success_text = len(all_Qs) * ['Correct! Move on to the next question.']
    for Q in all_Qs:
        qdata = Q.get_randomized_data()
        uses_images_list.append(Q.uses_images)

        corr_array = [l==qdata[2] for l in ['A','B','C','D']]
        corr_array_new = []
        qchoices = []
        for ind in range(len(qdata[1])):
            if len(qdata[1][ind]) != 0:
                qchoices.append(qdata[1][ind])
                corr_array_new.append(corr_array[ind])

        questions.append({'text': qdata[0],
                          'choices': qchoices,
                          'correct': corr_array_new.index(True),
                          'main_image_path': Q.main_image_path})

        # success_text[0] = "You got the first answer correct!"
        print(questions, 'printing questions')
    return questions, success_text, uses_images_list

@socketio.on("game 3 question answered")
def update_mc_progress(msg):
    status = session['game3']['mc_status_list']
    status[int(msg['ind'])] = bool(msg['correct'])

    utils.update_session_subdict(session, 'game3', {'mc_status_list': status})

    session['game3']['progress'].num_correct = sum(status)
    session['game3']['progress'].update_stars()

    print('Game 3 progress updated: ', session['game3']['progress'])

    socketio.emit('renew stars', {'stars': session['game3']['progress'].num_stars})

    print('star request sent')

@socketio.on("Updating choice for Game 3")
def update_choice(info):
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

