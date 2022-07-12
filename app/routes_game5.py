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
from workers.game5_worker import simulate_RF_rotation, animate_spin_action

@app.route('/games/5',methods=["GET","POST"])
def game5():
    # Form for submitting data - current settings
    game_form = Game5Form()
    j1, j2 = make_default_graphs()

    if request.method == 'POST':
        print(request.form)

    if game_form.validate_on_submit():
        print('form validated')
        # Run simulation and display results
        # Output animated plots
        theta = float(game_form.m_theta_field.data) * np.pi / 180
        phi = float(game_form.m_phi_field.data) * np.pi / 180
        m0 = float(game_form.m_size_field.data)
        M_first = spherical_to_cartesian(theta,phi,m0)

        rfdt, mags = simulate_RF_rotation(M_first=M_first, FA=float(game_form.flip_angle_field.data),
                                  rf_phase_deg = float(game_form.flip_angle_field.data),
                                  b0=float(game_form.b0_field.data),
                                  rot_frame=game_form.rot_frame_onoff_field.data)
        #j1 = animate_spin_action(rfdt, mags)

    return render_template('game5.html',template_title="Proton's got moves",template_intro_text="Can you follow on?",
                           template_game_form=game_form, graphJSON_spin=j1, graphJSON_m=j2)


# TODO
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


    # TODO: add : semitransparent xy plane; centered x/y/z axis lines


    #f1 = go.Figure(data=go.Cone(x=[0],y=[0],z=[0.8],u=[0],v=[0],w=[0.2],
    #                            sizemode='scaled',sizeref=1,colorscale=[[0,spincolor],[1,spincolor]],
    #                            showscale=False,anchor='tail'))

    f1 = go.Figure(data=go.Scatter3d(x=[0,0],y=[0,0],z=[0,1],mode='lines',line=dict(width=10,color=spincolor)))
    f1.update_layout(paper_bgcolor='gainsboro')

    axis_shared = dict(
            range=[-1,1],
            backgroundcolor=bgcolor,
            gridcolor=gridcolor,
            showbackground=True,
            zerolinecolor=None)

    f1.update_layout(scene=dict(xaxis=axis_shared, yaxis=axis_shared,zaxis=axis_shared),
                     width=500, margin=dict(r=10, l=10,b=10, t=10))


    j1 = json.dumps(f1,cls=plotly.utils.PlotlyJSONEncoder)

    # j2,j3,j4 : M
    f2 = go.Figure()
    f2.add_trace(go.Scatter(x=t,y=Mx))
    f2.add_trace(go.Scatter(x=t,y=My))
    f2.add_trace(go.Scatter(x=t,y=Mz))

    j2 = json.dumps(f2,cls=plotly.utils.PlotlyJSONEncoder)

    return j1,j2


@socketio.on('Update param for Game5')
def update_parameter(info):
    print(info)

