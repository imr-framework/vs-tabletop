import threading
from workers.game7_worker import game7_prep3d_worker, game7_projection_worker, game7_empty_plots_worker, \
    get_2D_proj_graph, get_1D_proj_graph, projections_to_images
import numpy as np
from flask import flash, render_template, session, redirect, url_for
from flask_login import login_required, login_user, logout_user
import utils
from forms import *
from info import GAMES_DICT, GAME7_INSTRUCTIONS, GAME7_RANDOM_MODELS, GAME7_BACKGROUND
from models import User, Calibration, MultipleChoice
from __main__ import app, login_manager, db, socketio
import random

@app.route('/games/7', methods=["GET","POST"])
@login_required
def game7():
    # Viewing function for game 7
    form=Game7Form()
    j1, j2, j3 = game7_empty_plots_worker()

    utils.update_session_subdict(session,'game7',{'plot3d_visible':False, 'plot2d_visible':False, 'plot1d_visible':False})
    questions, success_text, uses_images = fetch_all_game7_questions()

    if form.validate_on_submit():
        print('validated')
        #print(form)
        if form.phantom_type_field.data == 'random':
            j1, voxels = game7_prep3d_worker(difficulty="all")
        else:
            j1, voxels = game7_prep3d_worker(name=form.phantom_type_field.data)

        j2, j3 = game7_projection_worker(voxels, session['game7']['proj2d_axis'],
                                                 session['game7']['proj1d_angle'])

    return render_template('game7.html',G7Form=form, template_title="Puzzled by Projection",
                           template_intro_text="Forward puzzle", instructions=GAME7_INSTRUCTIONS,
                            graphJSON_3dimg = j1, graphJSON_2dimg = j2, graphJSON_1dimg = j3,
                           questions=questions, success_text=success_text, uses_images=uses_images,
                           game_num=7, background=GAME7_BACKGROUND)



@socketio.on('Update param for Game7')
def update_parameter(info):
    if info['id'] == 'proj1d_angle':
        info['value'] = float(info['value'])
    elif info['id'] in ['proj_2d_axis','proj_2d_axis-1','proj_2d_axis-2']:
        info['id'] = 'proj2d_axis'
    elif info['id'] == 'model':
        info['value'] = str(info['value'])
    utils.update_session_subdict(session, 'game7', {info['id']:info['value']})


@socketio.on('Request 3D model')
def update_3d_model():
    print('3D model requested')
    # Generate the 3D model
    j1, __, __ = get_updated_plots()
    __, j2, j3 = game7_empty_plots_worker()

    # Also nullify the other 2
    socketio.emit('Deliver 3D model',{'graph1':j1,
                                      'graph2':j2,
                                      'graph3':j3})

    utils.update_session_subdict(session,'game7',{'plot3d_visible':True,
                                                  'plot2d_visible':False,
                                                  'plot1d_visible':False})

@socketio.on('Request 2D projection')
def update_2d_proj():
    # Check if 3D is visible
    if session['game7']['plot3d_visible']:
        __, j2, __ = get_updated_plots()
        socketio.emit('Deliver 2D projection',{'graph': j2})
        utils.update_session_subdict(session, 'game7', {'plot2d_visible': True})
    else:
        flash("Choose a 3D model first!")

@socketio.on('Request 1D projection')
def update_1d_proj():
    # Check if both 3D and 2D are visible
    if session['game7']['plot3d_visible'] and session['game7']['plot2d_visible']:
        __, __, j3 = get_updated_plots()
        socketio.emit("Deliver 1D projection",{'graph': j3})
        utils.update_session_subdict(session, 'game7', {'plot1d_visible': True})
    else:
        flash("Generate the 2D projection first!")

@socketio.on('Toggle line display')
def toggle_line():
    session['game7']['lines_on'] = not session['game7']['lines_on']
    session.modified = True
    send_plots()


@socketio.on('Update line direction')
def update_proj2d_direction(msg):
    utils.update_session_subdict(session,'game7', {'proj2d_axis': msg['dir']})
    send_plots()

@socketio.on('Pull random model')
def get_random_mystery_model(msg):
    print("Generating random model now")
    # Pull model
    name =  random.choice(GAME7_RANDOM_MODELS)
    # Update current model; display only 3D model and hide projections
    session['game7']['model'] = name
    update_3d_model()
    # Return options and correct choice
    set_names = []
    for other in GAME7_RANDOM_MODELS:
        if other[6] == name[6]:
            set_names.append(other)

    # Generate random directions for the correct answer
    # 2D
    dir0 = random.choice(['x','y','z'])
    # 1D
    ang0 = random.choice([0,45,90,135,180])

    # Update session
    utils.update_session_subdict(session,'game7',{'proj2d_axis':dir0, 'proj1d_angle':ang0})

    # Graphs ready to display (plotly, simpler style)
    g_list_2d = [get_2D_proj_graph(name,dir0)]
    g_list_1d = [get_1D_proj_graph(name,dir0,ang0)]

    # Generate wrong answers
    # 2D
    while len(g_list_2d)<3:
        # For 2D, only choose other things in the set
        name_new = random.choice(set_names)
        dir_new = random.choice(['x','y','z'])
        if name_new != name or dir_new != dir0:
            g_temp_2d = get_2D_proj_graph(name_new,dir_new)
            for g_list_2d_opt in g_list_2d:
                if np.linalg.norm(g_list_2d_opt-g_temp_2d) > 0.1:
                    g_list_2d.append(g_temp_2d)
                else:
                    print("The graphs are too similar; redraw! 2D")
    # 1D
    while len(g_list_1d)<3:
        # For 1D, choose any model
        name_new = random.choice(GAME7_RANDOM_MODELS)
        dir_new = random.choice(['x','y','z'])
        ang_new = random.choice([0,45,90,135,180])
        if name_new != name or dir_new != dir0 or ang_new != ang0:
            g_temp_1d = get_1D_proj_graph(name_new,dir_new,ang_new)
            for g_list_1d_opt in g_list_1d:
                if np.linalg.norm(g_list_1d_opt - g_temp_1d) > 0.1:
                    g_list_1d.append(g_temp_1d)
                else:
                    print("The curves are too similar; redraw! 1D")

    # TODO Shuffle (the list, and the correct choice)
    perm2 = np.random.permutation(3)
    perm1 = np.random.permutation(3)

    corrects_2d = [True,False,False]
    corrects_1d = [True,False,False]
    g_list_2d = [g_list_2d[ind] for ind in perm2]
    corr_2d = [corrects_2d[ind] for ind in perm2]
    g_list_1d = [g_list_1d[ind] for ind in perm1]
    corr_1d = [corrects_1d[ind] for ind in perm1]

    # Save images to file
    projections_to_images(g_list_2d, g_list_1d)

    socketio.emit('display new challenge',{
        'corr_2d': corr_2d.index(True),
        'corr_1d': corr_1d.index(True),
        'type': msg['type'],
        'axis':  dir0,
        'angle':  ang0
    })





def send_plots():
    j1,j2,j3 = get_updated_plots()
    __, j20, j30 = game7_empty_plots_worker()
    if session['game7']['plot3d_visible']:
        socketio.emit("Deliver 3D model",{'graph1':j1,
                                      'graph2':j20,
                                      'graph3':j30})
    if session['game7']['plot2d_visible']:
        socketio.emit("Deliver 2D projection",{'graph':j2})
    if session['game7']['plot1d_visible']:
        socketio.emit("Deliver 1D projection",{'graph':j3})


def get_updated_plots():
    j1, voxels = game7_prep3d_worker(name=session['game7']['model'],lines=session['game7']['lines_on'],
                                     line_dir=session['game7']['proj2d_axis'])
    j2, j3 = game7_projection_worker(voxels, session['game7']['proj2d_axis'],
                                     session['game7']['proj1d_angle'],lines=session['game7']['lines_on'],
                                     lines_angle=session['game7']['proj1d_angle'])
    return j1, j2, j3



# Get game 7 questions!
def fetch_all_game7_questions():
    all_Qs = MultipleChoice.query.filter_by(game_number=7).all()
    questions = []
    uses_images_list = []
    success_text = len(all_Qs)*['Correct! Move on to the next question.']
    for Q in all_Qs:
        print(Q)
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

    #success_text[0] = "You got the first answer correct!"

    return questions, success_text, uses_images_list


@socketio.on("game 7 question answered")
def update_mc_progress(msg):
    # Updates session multiple choice status & progress object
    # Tells frontend to update # stars displayed.

    status = session['game7']['mc_status_list']
    status[int(msg['ind'])] = bool(msg['correct'])
    # Update current list
    utils.update_session_subdict(session,'game7',
                                 {'mc_status_list': status})

    # Update progress
    session['game7']['progress'].num_correct = sum(status)
    session['game7']['progress'].update_stars()

    #print('Game 7 progress updated: ', session['game7']['progress'])

    # Change stars display
    socketio.emit('renew stars',{'stars': session['game7']['progress'].num_stars})

@socketio.on('game7 update progress')
def game7_update_progress(msg):
    task = int(msg['task'])

    # Only update if there is progress (no backtracking)
    if task > session['game7']['task_completed']:
        utils.update_session_subdict(session, 'game7', {'task_completed': task})
        #print('Task ', session['game7']['task_completed'],' completed for game 7')

        # Update database object
        session['game7']['progress'].num_steps_complete = task
        session['game7']['progress'].update_stars()
        #print('Game 7 progress updated: ', session['game7']['progress'])
        socketio.emit('renew stars',{'stars': session['game7']['progress'].num_stars})

@socketio.on('Eye control changed')
def eye_control_changed():
    print('Eye control released! ')
    send_plots()
