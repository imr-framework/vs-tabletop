import threading

from flask import flash, render_template, session, redirect, url_for, request
from flask_login import login_required, login_user, logout_user
import plotly
import plotly.graph_objects as go
import utils
from forms import Game5Form
from info import GAMES_DICT
from models import User, Calibration
from __main__ import app, login_manager, db, socketio
import plotly.express as px
import pandas as pd
import json
import numpy as np
from workers.game5_worker import simulate_RF_rotation, generate_static_plot,\
                                  animate_b0_turn_on, simulate_spin_precession,\
                                generate_static_signals, generate_coil_signal

@app.route('/games/5',methods=["GET","POST"])
def game5_view():
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
                           template_game_form=game_form, graphJSON_spin=j1, graphJSON_signal=j2)



def make_default_graphs():
    game5 = session['game5']
    mags = np.zeros((1,3))
    dt = 1
    j1 = generate_static_plot(dt, mags,coil=(game5['coil_dir'] if game5['coil_on'] else None))
    #j1 = json.dumps(f1,cls=plotly.utils.PlotlyJSONEncoder)

    # j2 : signal
    # Make empty plot
    j2 = generate_static_signals(dt=1, signals=np.zeros(1))

    return j1,j2


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
    elif info['id'] == 'rot-frame-button':
        utils.update_session_subdict(session,'game5',{'rot_frame_on':info['checked']})
    elif info['id'] == 'b0_field':
        utils.update_session_subdict(session,'game5',{'b0': 1e-4*info['value']}) # Convert from Gauss to Tesla
    else:
        utils.update_session_subdict(session,'game5',{info['id']:float(info['value'])})

    print(session['game5'])

@socketio.on('update params for Game5')
def update_multiple_parameters(info):
    print(info)
    utils.update_session_subdict(session,'game5',info)
    print(session['game5'])

@socketio.on('reset everything')
def reset_everything():
    # Reset m and update animation
    reset_m()
    # Reset other things
    utils.update_session_subdict(session,'game5',
                                 { 'b0_on': False,
                                   'coil_on': False,
                                   'rot_frame_on': False,
                                   'M_init': np.array([[0],[0],[0]])
                                 })
    socketio.emit('message',{'text': 'Spin and hardware have been reset.','type':''})
    return

def reset_m():
    # Reset spin plot
    game5=session['game5']
    mags_zero = np.zeros((1,3))
    j0 = generate_static_plot(dt=1,mags=mags_zero,coil=(game5['coil_dir'] if game5['coil_on'] else None))
    # Generate static plot and replace current plot with it
    socketio.emit('update spin animation', {'graph':j0,'loop_on':False})
    j1=  generate_static_signals(dt=1, signals=np.zeros(1))
    socketio.emit('update signal animation',{'graph':j1})
    return






@socketio.on('b0 toggled')
def turn_on_b0(info):
    game5 = session['game5']
    # If turned on, play animation of M0 growth
    if info['b0_on']:
        j0 = animate_b0_turn_on(M_final=1, T1=1, coil=(game5['coil_dir'] if game5['coil_on'] else None))
        utils.update_session_subdict(session,'game5',{'M_init':[[0],[0],[1]]})
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
    # Set it
    print("setting Mi")

    Mi = utils.spherical_to_cartesian(session['game5']['m_theta'],
                                 session['game5']['m_phi'],
                                 session['game5']['m_size'])
    utils.update_session_subdict(session, 'game5', {'M_init': Mi})

    # Make the static animation and send it over to frontend
    j1 = generate_static_plot(1,mags=np.transpose(Mi),coil=(game5['coil_dir'] if game5['coil_on'] else None))
    socketio.emit('update spin animation',{'graph':j1,'loop_on':False})

    return

@socketio.on('simulate precession')
def let_spin_precess():
    game5 = session['game5']
    if game5['b0_on']:
        j1, dt, mags = simulate_spin_precession(M_first=game5['M_init'], b0=game5['b0'], rot_frame=game5['rot_frame_on'],
                                      coil=(game5['coil_dir'] if game5['coil_on'] else None))
        print(j1)
        socketio.emit('update spin animation',{'graph':j1, 'loop_on':True})

        #TODO make sure signal gets displayed
        if game5['coil_on']:
            print('receiving Rx signal! ')
            j2 = generate_static_signals(dt, signals=generate_coil_signal(dt,mags,coil_dir=game5['coil_dir']))
            socketio.emit('message',{'text': 'Receiving signal from coil... ','type':'success'})
            socketio.emit('update signal animation', {'graph': j2, 'loop_on': True})


    else: # B0 not on, flash message
        socketio.emit('message',{'text': 'Turn on B0 first.', 'type':'warning'})

    return


@socketio.on('simulate nutation')
def tip_spin_with_rf():
    print("simulating B1")
    game5 = session['game5']
    print(game5)
    if game5['b0_on'] and game5['rot_frame_on']:
        j1, M_last = simulate_RF_rotation(M_first=game5['M_init'], FA=game5['flip_angle'],rf_phase_deg=game5['rf_phase'],
                                  b0=game5['b0'], rot_frame=game5['rot_frame_on'],
                                          coil=(game5['coil_dir'] if game5['coil_on'] else None))

        # Initial M was changed.
        utils.update_session_subdict(session,'game5',{'M_init':np.transpose(M_last)})

        socketio.emit('update spin animation',{'graph':j1, 'loop_on':False})

    else:
        socketio.emit('message',{'text':'Remember to turn on B0 and rotational frame before you play the RF pulse.',
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
    if game5['b0_on']:
        j1, __, __ = simulate_spin_precession(M_first=game5['M_init'], b0=game5['b0'],
                                      rot_frame=info['rot_frame_on'],coil=(game5['coil_dir'] if game5['coil_on'] else None))
        socketio.emit('update spin animation', {'graph': j1, 'loop_on': True})

@socketio.on('rx toggled')
def turn_on_rx_coil(info):
    game5 = session['game5']
    if info['rx_on']:
        # Inform user
        socketio.emit('message',{'text':'Rx coil is on!','type':'success'})
        # Make the static animation and send it over to frontend
        j1 = generate_static_plot(1, mags=np.transpose(game5['M_init']), coil=info['rx_dir'])

        # Display coil with M set to M_init
    else:
        # Inform user
        socketio.emit('message',{'text':'Rx coil is off!','type':''})
        j1 = generate_static_plot(1,mags=np.transpose(game5['M_init']), coil=None)

    socketio.emit('update spin animation', {'graph': j1, 'loop_on': False})




