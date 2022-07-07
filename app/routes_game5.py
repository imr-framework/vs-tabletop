import threading

from flask import flash, render_template, session, redirect, url_for
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
from workers.simulation_workers import simulate_RF_rotation

@app.route('/games/5',methods=["GET","POST"])
def game5():
    # Form for submitting data - current settings
    game_form = Game5Form()

    if game_form.validate_on_submit():
        print('form validated')
        # Run simulation and display results
        # Output animated plots
        #j1 = simulate_RF_rotation()

    j1, j2 = make_default_graphs()

    return render_template('game5.html',template_title="Proton's got moves",template_intro_text="Can you follow on?",
                           template_game_form=game_form, graphJSON_spin=j1, graphJSON_m=j2)

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


    f1 = go.Figure(data=go.Cone(x=[0],y=[0],z=[0.8],u=[0],v=[0],w=[0.2],
                                sizemode='scaled',sizeref=1,colorscale=[[0,spincolor],[1,spincolor]],
                                showscale=False,anchor='tail'))

    f1.add_trace(go.Scatter3d(x=[0,0],y=[0,0],z=[0,1],mode='lines',line=dict(width=10,color=spincolor)))

    f1.update_layout(paper_bgcolor='gainsboro')

    axis_shared = dict(
            range=[-1,1],
            backgroundcolor=bgcolor,
            gridcolor=gridcolor,
            showbackground=True,
            zerolinecolor=None)

    f1.update_layout(scene=dict(xaxis=axis_shared, yaxis=axis_shared,zaxis=axis_shared),
                     width=700, margin=dict(r=10, l=10,b=10, t=10))


    j1 = json.dumps(f1,cls=plotly.utils.PlotlyJSONEncoder)

    # j2,j3,j4 : M
    f2 = go.Figure()
    f2.add_trace(go.Scatter(x=t,y=Mx))
    f2.add_trace(go.Scatter(x=t,y=My))
    f2.add_trace(go.Scatter(x=t,y=Mz))

    j2 = json.dumps(f2,cls=plotly.utils.PlotlyJSONEncoder)

    return j1,j2