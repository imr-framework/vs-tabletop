import threading

from flask import flash, render_template, session, redirect, url_for, request
from flask_login import login_required, login_user, logout_user
import plotly
import plotly.graph_objects as go
import utils

from forms import Game5Form
from info import GAMES_DICT, GAME5_INSTRUCTIONS
from models import User, Calibration
from __main__ import app, login_manager, db, socketio
import plotly.express as px
import pandas as pd
import json
import numpy as np
from models import MultipleChoice
from workers.game5_worker import simulate_RF_rotation, generate_static_plot,\
                                  animate_b0_turn_on, simulate_spin_precession,\
                                generate_static_signals, generate_coil_signal

@app.route('/games/5',methods=["GET","POST"])
def game5_view():
    """View function for the main route to Game 5

    Returns
    -------
    str
        HTML view of Game 5
    """
    questions, success_text, uses_images_list = fetch_all_game5_questions()
    print(questions)
    # Form for submitting data - current settings
    game_form = Game5Form()
    j1, j2 = make_default_graphs()

    #if request.method == 'POST':
    #   print(request.form)
    # Older form submission thing - not used anymore
    # if game_form.validate_on_submit():
    #     print('form validated')
    #     if session['game5']['b0_on']:
    #         # Run simulation and display results
    #         # But only if B0 is turned on
    #         # Output animated plots
    #         theta = float(game_form.m_theta_field.data) * np.pi / 180
    #         phi = float(game_form.m_phi_field.data) * np.pi / 180
    #         m0 = float(game_form.m_size_field.data)
    #     else: # If B0 is off, flash message
    #         flash('Remember to turn on B0 before you perform the RF rotation.')

    return render_template('game5.html',template_title="Proton's got moves",template_intro_text="Can you follow on?",
                           template_game_form=game_form, graphJSON_spin=j1, graphJSON_signal=j2,
                           questions=questions,success_text=success_text,uses_images=uses_images_list,
                           instructions=GAME5_INSTRUCTIONS)
                            #TODO use function to store/generate tasks


def make_default_graphs():
    """Make default empty plots to dispaly when Game 5 is first loaded

    Returns
    -------
    graphJSON_spin : str
        JSON representation of
    graphJSON_signal : str
        JSON representation of

    """
    game5 = session['game5']
    mags = np.zeros((1,3))
    graphJSON_spin = generate_static_plot(mags,coil=(game5['coil_dir'] if game5['coil_on'] else None),
                                                     tx=(game5['rf_phase'] if game5['tx_on'] else None))




    #j1 = json.dumps(f1,cls=plotly.utils.PlotlyJSONEncoder)

    # j2 : signal
    # Make empty plot
    graphJSON_signal = generate_static_signals(dt=1, signals=np.zeros(1))

    return graphJSON_spin, graphJSON_signal


@socketio.on('Update param for Game5')
def update_parameter(info):
    """Update session parameters for game 5 on change

    Parameters
    ----------
    info : dict
        Information received through socket
        'id' : id of input field changed
        'value' : new value of input field to update session with
    """

    # Special cases
    if info['value'] in ['a','b','c','d']:
        return


    if info['id'] == 'rx_dir_field-0':
        utils.update_session_subdict(session,'game5',{'coil_dir':'x'})
    elif info['id'] == 'rx_dir_field-1':
        utils.update_session_subdict(session,'game5',{'coil_dir':'y'})
    elif info['id'] in ['mag-x','mag-y','mag-z','mag-0']:
        nothing_in_particular = 0
    elif info['id'] == 'b0_on':
        utils.update_session_subdict(session,'game5',{'b0_on':info['checked']})

    elif info['id'] == 'rx-button':
        utils.update_session_subdict(session,'game5',{'coil_on':info['checked']})
    elif info['id'] == 'tx-button':
        utils.update_session_subdict(session,'game5',{'tx_on':info['checked']})
    elif info['id'] == 'rot-frame-button':
        utils.update_session_subdict(session,'game5',{'rot_frame_on':info['checked']})
    elif info['id'] == 'b0':
        new_M_init = session['game5']['M_init'] * float(info['value']) / 100
        utils.update_session_subdict(session,'game5',{'b0': float(info['value']),'M_init': new_M_init}) # Convert from Gauss to Tesla
    else:
        utils.update_session_subdict(session,'game5',{info['id']:float(info['value'])})

    print(session['game5'])

@socketio.on('Update params for Game5')
def update_multiple_parameters(info):
    """Instantly update multiple parameters at socket signal from the frontend

    Parameters
    ----------
    info : dict
        Each key-value pair is one to update in session['game5']

    """
    print(info)
    utils.update_session_subdict(session,'game5',info)
    print(session['game5'])

@socketio.on('reset everything')
def reset_everything():
    """Resets the following:
       - m
    """
    reset_m()
    # Reset other things
    utils.update_session_subdict(session,'game5',
                                 { 'b0_on': False,
                                   'coil_on': False,
                                   'tx_on':False,
                                   'rot_frame_on': False,
                                   'M_init': np.array([[0],[0],[0]])
                                 })
    socketio.emit('message',{'text': 'Spin and hardware have been reset.','type':''})
    return

def reset_m():
    # Reset spin plot
    game5=session['game5']
    mags_zero = np.zeros((1,3))
    j0 = generate_static_plot(mags=mags_zero,coil=(game5['coil_dir'] if game5['coil_on'] else None))
    # Generate static plot and replace current plot with it
    socketio.emit('update spin animation', {'graph':j0,'loop_on':False})
    j1 = generate_static_signals(dt=1, signals=np.zeros(1))
    socketio.emit('update signal animation',{'graph':j1})
    return






@socketio.on('b0 toggled')
def turn_on_b0(info):
    game5 = session['game5']
    # If turned on, play animation of M0 growth
    if info['b0_on']:
        m_max = game5['b0']/100
        print(f'm_max is {m_max}')
        j0 = animate_b0_turn_on(M_final=m_max, T1=1, coil=(game5['coil_dir'] if game5['coil_on'] else None),
                                                           tx=(game5['rf_phase'] if game5['tx_on'] else None))
        utils.update_session_subdict(session,'game5',{'M_init':np.array([[0],[0],[m_max]])})
        socketio.emit('update spin animation',{'graph':j0,'loop_on':False})
        socketio.emit('message',{'text': 'B0 is turned on! ', 'type':'success'})
    # If turned off
    else:
        reset_m()
        socketio.emit('message',{'text': 'B0 is turned off. ', 'type':''})


    return

@socketio.on('set initial magnetization')
def set_M_init():
    game5 = session['game5']
    m_max = game5['b0'] / 100

    # Set it
    print("setting Mi")
    Mi = m_max * utils.spherical_to_cartesian(session['game5']['m_theta'],
                                 session['game5']['m_phi'],
                                 session['game5']['m_size'])
    utils.update_session_subdict(session, 'game5', {'M_init': Mi})

    # Make the static animation and send it over to frontend
    j1 = generate_static_plot(mags=np.transpose(Mi),
                              coil=(game5['coil_dir']) if game5['coil_on'] else None,
                              tx=(game5['rf_phase']) if game5['tx_on'] else None)
    j2 = generate_static_signals(dt=1, signals=np.zeros(1))

    socketio.emit('update spin animation',{'graph' : j1,'loop_on':False})
    socketio.emit('update signal animation', {'graph': j2, 'loop_on':False})

    return

@socketio.on('simulate precession')
def let_spin_precess(info):
    game5 = session['game5']
    if info['b0_on']:
        j1, dt, mags = simulate_spin_precession(M_first=game5['M_init'], b0=game5['b0'], rot_frame=game5['rot_frame_on'],
                                      coil=(game5['coil_dir'] if game5['coil_on'] else None),tx=(game5['rf_phase'] if game5['tx_on'] else None))
        socketio.emit('update spin animation',{'graph':j1, 'loop_on':True})

        #TODO scale signal to sin(theta)
        if info['coil_on']:
            j2 = generate_static_signals(dt, signals=generate_coil_signal(mags,coil_dir=game5['coil_dir'],b0=game5['b0']))
            socketio.emit('message',{'text': 'Receiving signal from coil... ','type':'success'})
            socketio.emit('update signal animation', {'graph': j2, 'loop_on': True})


    else: # B0 not on, flash message
        socketio.emit('message',{'text': 'Turn on B0 first.', 'type':'warning'})

    return


@socketio.on('simulate nutation')
def tip_spin_with_rf(msg):
    game5 = session['game5']
    #if game5['b0_on'] and game5['rot_frame_on']:
    if msg['b0_on'] and msg['rot_frame_on']:
        j1, M_last = simulate_RF_rotation(M_first=game5['M_init'], FA=game5['flip_angle'],rf_phase_deg=game5['rf_phase'],
                                  b0=game5['b0'], rot_frame=game5['rot_frame_on'],
                                          coil=(game5['coil_dir'] if game5['coil_on'] else None),
                                            tx=(game5['rf_phase'] if game5['tx_on'] else None))
        # Initial M was changed.
        utils.update_session_subdict(session,'game5',{'M_init':np.transpose(M_last)})

        socketio.emit('update spin animation',{'graph':j1, 'loop_on':False})

    else:
        socketio.emit('message',{'text':'Remember to turn on both B0 and rotating frame.',
                                 'type':'warning'})

    return


@socketio.on('rot frame toggled')
def turn_on_rot_frame(info):
    game5 = session['game5']
    if info['rot_frame_on']:
        # Display message
        socketio.emit('message',{'text':'Rotational frame is turned on.', 'type':'success'})
    else:
        socketio.emit('message',{'text':'Rotational frame is turned off.', 'type':''})

    # Also: rerun precession sim
    if info['b0_on']:
        j1, __, __ = simulate_spin_precession(M_first=game5['M_init'], b0=game5['b0'],
                                      rot_frame=info['rot_frame_on'],coil=(game5['coil_dir'] if game5['coil_on'] else None),
                                                                           tx=(game5['rf_phase'] if game5['tx_on'] else None))
        socketio.emit('update spin animation', {'graph': j1, 'loop_on': True})

@socketio.on('tx toggled')
def turn_on_tx_coil(info):
    game5 = session['game5']


    if info['tx_on']:
        socketio.emit('message',{'text': 'RF transmit field is on!', 'type': 'success'})
    else:
        socketio.emit('message',{'text': 'RF transmit field is off!', 'type':''})


    j1 = generate_static_plot(mags=np.transpose(game5['M_init']),
                              coil=(game5['coil_dir']) if game5['coil_on'] else None,
                              tx=(game5['rf_phase']) if info['tx_on'] else None)
    socketio.emit('update spin animation', {'graph': j1, 'loop_on': False})


@socketio.on('rx toggled')
def turn_on_rx_coil(info):
    game5 = session['game5']
    if info['rx_on']:
        # Inform user
        socketio.emit('message',{'text':'Rx coil is on!','type':'success'})
        # Make the static animation and send it over to frontend
        # Display coil with M set to M_init
    else:
        # Inform user
        socketio.emit('message',{'text':'Rx coil is off!','type':''})


    j1 = generate_static_plot(mags=np.transpose(game5['M_init']),
                              coil=(info['rx_dir']) if info['rx_on'] else None,
                              tx=(game5['rf_phase']) if game5['tx_on'] else None)

    socketio.emit('update spin animation', {'graph': j1, 'loop_on': False})




# Get game 5 questions!
def fetch_all_game5_questions():
    all_Qs = MultipleChoice.query.filter_by(game_number=5).all()
    print(all_Qs)
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

# TODO
@socketio.on("game 5 question answered")
def update_mc_progress(msg):
    # Updates session multiple choice status & progress object
    # Tells frontend to update # stars displayed.

    status = session['game5']['mc_status_list']
    status[int(msg['ind'])] = bool(msg['correct'])
    # Update current list
    utils.update_session_subdict(session,'game5',
                                 {'mc_status_list': status})

    # Update progress
    session['game5']['progress'].num_correct = sum(status)
    session['game5']['progress'].update_stars()

    print('Game 5 progress updated: ', session['game5']['progress'])

    # Change stars display
    socketio.emit('renew stars',{'stars': session['game5']['progress'].num_stars})

