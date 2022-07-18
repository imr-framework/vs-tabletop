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
from workers.game5_worker import simulate_RF_rotation, animate_spin_action, generate_static_plot,\
                                 generate_M0_growth

@app.route('/games/5',methods=["GET","POST"])
def game5():
    # Form for submitting data - current settings
    game_form = Game5Form()
    j1, j2 = make_default_graphs()
    print(j1)

    if request.method == 'POST':
        print(request.form)

    if game_form.validate_on_submit():
        print('form validated')
        if session['game5']['b0_on']:
            # Run simulation and display results
            # But only if B0 is turned on
            # Output animated plots
            theta = float(game_form.m_theta_field.data) * np.pi / 180
            phi = float(game_form.m_phi_field.data) * np.pi / 180
            m0 = float(game_form.m_size_field.data)
            M_first = spherical_to_cartesian(theta,phi,m0)

            rfdt, mags = simulate_RF_rotation(M_first=M_first, FA=float(game_form.flip_angle_field.data),
                                      rf_phase_deg = float(game_form.flip_angle_field.data),
                                      b0=float(game_form.b0_field.data),
                                      rot_frame=game_form.rot_frame_onoff_field.data)

            j1 = generate_static_plot(rfdt, mags)
        else: # If B0 is off, flash message
            flash('Remember to turn on B0 before you perform the RF rotation.')

    return render_template('game5.html',template_title="Proton's got moves",template_intro_text="Can you follow on?",
                           template_game_form=game_form, graphJSON_spin=j1, graphJSON_m=j2)


def spherical_to_cartesian(theta,phi,m0):
    # theta, phi are in radians
    M = m0*np.array([[np.sin(theta)*np.cos(phi)],[np.sin(theta)*np.sin(phi)],[np.cos(theta)]])
    return M


def make_default_graphs():
    tmodel = np.linspace(0,1,100)
    t = tmodel
    Mx = np.zeros(tmodel.shape)
    My = np.zeros(tmodel.shape)
    Mz = np.ones(tmodel.shape)
    # J1 : vector
    # Color variables
    bgcolor = "darkgray"
    gridcolor = "white"
    spincolor = "darkorange"
    f1 = go.Figure(data=go.Scatter3d(x=[0,0],y=[0,0],z=[0,1],mode='lines',line=dict(width=10,color=spincolor)))
    f1.add_trace(go.Mesh3d(x=[1,-1,-1,1],y=[1,-1,1,-1],z=[0,0,0,0],color='green',opacity=0.2))
    f1.add_trace(go.Scatter3d(x=[-1,1],y=[0,0],z=[0,0],mode='lines',line=dict(width=5,dash='dash',color='gray')))
    f1.add_trace(go.Scatter3d(x=[0,0],y=[-1,1],z=[0,0],mode='lines',line=dict(width=5,dash='dash',color='gray')))
    f1.update_traces(showlegend=False)
    f1.update_layout(paper_bgcolor='gainsboro')

    axis_shared = dict(
            range=[-1,1],
            backgroundcolor=bgcolor,
            gridcolor=gridcolor,
            showbackground=True,
            showgrid=False,
            zeroline=True,
            zerolinecolor=None)

    f1.update_layout(scene=dict(xaxis=axis_shared, yaxis=axis_shared,zaxis=axis_shared),
                     width=500, height=500, margin=dict(r=10, l=10,b=10, t=10),
                     scene_aspectmode='cube')

    mags = np.zeros((1,3))
    dt = 1
    j1 = generate_static_plot(dt, mags)
    #j1 = json.dumps(f1,cls=plotly.utils.PlotlyJSONEncoder)

    # j2,j3,j4 : M
    f2 = go.Figure()
    f2.add_trace(go.Scatter(x=t,y=Mx))
    f2.add_trace(go.Scatter(x=t,y=My))
    f2.add_trace(go.Scatter(x=t,y=Mz))

    j2 = json.dumps(f2,cls=plotly.utils.PlotlyJSONEncoder)

    return j1,j2


@socketio.on('Update param for Game5')
def update_parameter(info):
    # Special cases
    if info['id'] == 'rx_dir_field-0':
        utils.update_session_subdict(session,'game5',{'coil_dir':'x'})
    elif info['id'] == 'rx_dir_field-1':
        utils.update_session_subdict(session,'game5',{'coil_dir':'y'})
    elif info['id'] in ['mag-x','mag-y','mag-z','mag-0']:
        utils.update_session_subdict(session,'game5',{})
    elif info['id'] == 'b0_on':
        utils.update_session_subdict(session,'game5',{'b0_on':info['checked']})
        generate_M0_growth(info['checked'])


    elif info['id'] == 'rx-button':
        utils.update_session_subdict(session,'game5',{'coil_on':info['checked']})
    elif info['id'] == 'rot-frame-button':
        utils.update_session_subdict(session,'game5',{'rot_frame_on':info['checked']})
    else:
        utils.update_session_subdict(session,'game5',{info['id']:float(info['value'])})

    print(session)

@socketio.on('reset magnetization')
def reset_m():
    mags_zero = np.zeros((1,3))
    j0 = generate_static_plot(dt=1,mags=mags_zero)
    # Generate static plot and replace current plot with it
    socketio.emit('reset mags', {'graph':j0})
    return

