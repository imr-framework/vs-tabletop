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
    # Viewing function for game 7
    form=Game7Form()
    j1, j2, j3 = game7_empty_plots_worker()

    if form.validate_on_submit():
        print('validated')
        print(form)
        if form.phantom_type_field.data == 'random':
            j1, voxels = game7_prep3d_worker(difficulty="all")
        else:
            j1, voxels = game7_prep3d_worker(name=form.phantom_type_field.data)

        j2, j3 = game7_projection_worker(voxels, session['game7']['proj2d_axis'],
                                                 session['game7']['proj1d_angle'])

    return render_template('game7.html',G7Form=form, template_title="Projection Imaging",
                           template_intro_text="Forward puzzle", instructions=get_instructions_game7(),
                            graphJSON_3dimg = j1, graphJSON_2dimg = j2, graphJSON_1dimg = j3)



@socketio.on('Update param for Game7')
def update_parameter(info):
    if info['id'] == 'proj1d_angle':
        info['value'] = float(info['value'])
    elif info['id'] in ['proj_2d_axis','proj_2d_axis-1','proj_2d_axis-2']:
        info['id'] = 'proj2d_axis'
    elif info['id'] == 'model':
        info['value'] = str(info['value'])
    utils.update_session_subdict(session, 'game7', {info['id']:info['value']})
    print(session['game7'])


@socketio.on('Request 3D model')
def update_3d_model():
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

    j1,j2,__ = get_updated_plots()
    __, j20, j3 = game7_empty_plots_worker()

    if session['game7']['plot3d_visible']:
        socketio.emit("Deliver 3D model",{'graph1':j1,
                                      'graph2':j20,
                                      'graph3':j3})

    if session['game7']['plot2d_visible']:
        socketio.emit("Deliver 2D projection",{'graph':j2})

def get_updated_plots():
    j1, voxels = game7_prep3d_worker(name=session['game7']['model'],lines=session['game7']['lines_on'],
                                     line_dir=session['game7']['proj2d_axis'])
    j2, j3 = game7_projection_worker(voxels, session['game7']['proj2d_axis'],
                                     session['game7']['proj1d_angle'],lines=session['game7']['lines_on'],
                                     lines_angle=session['game7']['proj1d_angle'])
    return j1, j2, j3



def get_instructions_game7():
    instr = {
        'step1': ['Select a 3D model and load it',
                  'Change the 2D projection axis and hit "show/hide lines" each time ',
                  'Press "2D projection after selecting each of the 3 axes. What do you observe?'
                  'Using the "transparent" button, explore different views of the phantom. Can you replicate the 3 projections?',
                  'If we cannot see the model, are 3 projections enough for us to figure out the complete 3D structure?'] ,
        'step2': ['a','b','c'],
        'step3': ['d','e','f']
    }
    return instr


