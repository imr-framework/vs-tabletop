
from flask import flash, render_template, session, redirect, url_for
from vstabletop.forms import Game8Form
from vstabletop.workers.game8_worker import game8_worker_project, game8_worker_load
import vstabletop.utils as utils
from vstabletop.info import GAME8_INSTRUCTIONS, GAME8_BACKGROUND
from vstabletop.models import MultipleChoice

from .. import socketio
from .routes_game1 import bp_games

@bp_games.route('/8',methods=["GET","POST"])
def game8():
    info = session['game8']
    j1 = game8_worker_project(info, default=True)
    j2, __, __ = game8_worker_load(info,default=True)
    game8form = Game8Form()
    all_Qs = MultipleChoice.query.filter_by(game_number=8).all()
    questions, success_text, uses_images = utils.process_all_game_questions(all_Qs)

    return render_template('games/game8.html',template_title="Puzzled by Projection II",template_intro_text="Backward puzzle",
                           template_game_form=game8form,game_num=8,
                           graphJSON_image=j1, graphJSON_options=j2,
                            questions=questions, success_text=success_text, uses_images=uses_images,
                           instructions=GAME8_INSTRUCTIONS, background=GAME8_BACKGROUND)


@socketio.on("Draw new 3D model")
def get_new_3D_model():
    print("New 3D model requested")

    info = session['game8']
    info['mode'] = "3D"
    j2, ind_correct, image = game8_worker_load(info,default=False)
    print("correct option:", ind_correct)
    utils.update_session_subdict(session,'game8',{'mode': '3D', 'ind_correct':ind_correct, 'image': image,
                                                  'num_acquired_3d': 0})

    socketio.emit('Wipe all attempt plots')
    # Get plot back to page
    socketio.emit("Deliver options plot", {'graph': j2})
    socketio.emit("Message", {'text': 'New 3D model loaded!'})


@socketio.on("Draw new 2D image")
def get_new_2D_model():
    print("New 2D model requested")

    info = session['game8']
    info['mode'] = "2D"
    j2, ind_correct, image = game8_worker_load(info,default=False)

    utils.update_session_subdict(session,'game8',{'mode':'2D', 'ind_correct':ind_correct,'image': image,
                                                  'num_acquired_2d': 0})

    socketio.emit('Wipe all attempt plots')
    # Get plot back to page
    socketio.emit("Deliver options plot", {'graph': j2})
    socketio.emit("Message", {'text': 'New 2D image loaded!'})


@socketio.on('Get 1D projection')
def get_1d_projection(payload):

    info = session['game8']
    info['proj1d_angle'] = float(payload['angle'])
    info['mode'] = '2D'
    # Check if we are at limits
    if attempt_at_limit('2D'):
        socketio.emit("Message", {'text': 'You have exhausted your attempts for 1D projections.'})
        return
    else:
        # Make the projection!
        num_attempts_sofar = info['num_acquired_2d']
        j1 = game8_worker_project(info,default=False)
        utils.update_session_subdict(session,'game8',{'num_acquired_2d': num_attempts_sofar + 1})
        socketio.emit('Deliver attempt plot', {'mode': '2D', 'graph': j1, 'attempt': num_attempts_sofar + 1})

@socketio.on('Get 2D projection')
def get_2d_projection(payload):
    info = session['game8']
    info['proj2d_axis'] = payload['axis']
    info['mode'] = '3D'
    if attempt_at_limit('3D'):
        socketio.emit("Message", {'text': 'You have exhausted your attempts for 2D projections.'})
        return
    else:
        num_attempts_sofar = info['num_acquired_3d']
        j1 = game8_worker_project(info,default=False)
        utils.update_session_subdict(session,'game8',{'num_acquired_3d': num_attempts_sofar + 1})
        socketio.emit('Deliver attempt plot', {'mode': '3D', 'graph': j1, 'attempt': num_attempts_sofar + 1})


@socketio.on('Update parameter for game 8')
def update_parameter(info):
    update_dict = {}
    if info['id'] == 'proj1d_angle':
        update_dict = {'proj1d_angle': float(info['value'])}
    elif info['id'] == 'proj2d_axis':
        update_dict = {'proj2d_axis': info['value']}

    utils.update_session_subdict(session, 'game8', update_dict)

@socketio.on("Reset attempts without changing question")
def reset_attempts():
    #j1 = game8_worker_project({}, default=True)
    socketio.emit('Wipe all attempt plots')

    utils.update_session_subdict(session,'game8',{'num_acquired_3d': 0, 'num_acquired_2d': 0})

    socketio.emit("Message", {'text': 'Attempts reset.'})


def attempt_at_limit(mode):
    if mode == "2D":
        return session['game8']['num_acquired_2d'] == session['game8']['num_attempts_2d']
    elif mode == "3D":
        return session['game8']['num_acquired_3d'] == session['game8']['num_attempts_3d']
    else:
        return True



@socketio.on("Answer submitted")
def check_answer(answer):
    if int(session['game8']['ind_correct']) == int(answer['choice']):
        socketio.emit("Correct")
    else:
        socketio.emit("Wrong")


@socketio.on("game 8 question answered")
def update_mc_progress(msg):
    status = session['game8']['mc_status_list']
    status[int(msg['ind'])] = bool(msg['correct'])

    utils.update_session_subdict(session, 'game8', {'mc_status_list': status})

    session['game8']['progress'].num_correct = sum(status)
    session['game8']['progress'].update_stars()

    print('Game 8 progress updated: ', session['game8']['progress'])

    socketio.emit('renew stars', {'stars': session['game8']['progress'].num_stars})

    print('star request sent')

@socketio.on('game8 update progress')
def game8_update_progress(msg):
    task = int(msg['task'])
    # Only update if there is progress (no backtracking)
    if task > session['game8']['task_completed']:
        utils.update_session_subdict(session, 'game8', {'task_completed': task})
        print('Task ', session['game8']['task_completed'], ' completed for game 8')

        # Update database object
        session['game8']['progress'].num_steps_complete = task
        session['game8']['progress'].update_stars()
        print('Game 8 progress updated: ', session['game8']['progress'])
        socketio.emit('renew stars', {'stars': session['game8']['progress'].num_stars})