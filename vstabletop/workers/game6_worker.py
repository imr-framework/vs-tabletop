# Game 6 worker

import numpy as np
from stl import mesh
import plotly.express as px
import plotly.graph_objects as go
import json
import plotly
import stltovoxel
import os
import glob
from skimage.transform import radon
from scipy.spatial.transform import Rotation as R
import matplotlib.pyplot as plt
import matplotlib as mpl
from vstabletop.paths import DATA_PATH, IMG_PATH
from virtualscanner.server.simulation.bloch.phantom import SpheresArrayPlanarPhantom
from virtualscanner.server.simulation.bloch.spingroup_ps import SpinGroup

DEFAULT_TIS = [] # Seconds
DEFAULT_TES = [] # Seconds
SPIN_COLOR_Z = 'dodgerblue'
SPIN_COLOR_XY = 'darkorange'
BG_COLOR = "darkgray"
GRID_COLOR = "white"

def game6_worker_sim(info):
    # Left: demo
    if info['mode'] == 'T1':
        T1 = info['t1_sim']*1e-3
        TI = info['ti_sim']*1e-3
        fig1 = make_t1_spin_plot(t1=T1)
        fig2 = make_t1_mag_plot(t1=T1,mz0=info['t1_sim_mz0']/100)
        fig3 = make_t1_sequence_plot(t1=T1,ti=TI)
    elif info['mode'] == 'T2':
        T2 = info['t2_sim']*1e-3
        TE = info['te_sim']*1e-3
        fig1 = make_t2_spin_plot(t2=T2)
        fig2 = make_t2_mag_plot(t2=T2,mx0=info['t2_sim_mx0']/100)
        fig3 = make_t2_sequence_plot(t2=T2, te=TE)

    graphJSON_left = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON_middle = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON_right = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON_left, graphJSON_middle, graphJSON_right

def make_t1_spin_plot(t1):
    # Simulate
    N_steps = 100
    mags, __ = simulate_spin(m_first=[0,0,0], duration=3*t1, steps=N_steps, pdt1t2=(1,t1,0))

    # Make animated figure
    axis_shared = dict(
        range=[-1.2, 1.2],
        backgroundcolor=BG_COLOR,
        gridcolor=GRID_COLOR,
        showbackground=True,
        showgrid=False,
        zeroline=True,
        zerolinecolor=None)

    mag_frames = [go.Frame(data=[go.Scatter3d(x=[0,mags[u,0]], y=[0,mags[u,1]], z=[0,mags[u,2]],
                           mode='lines', line=dict(width=10, color=SPIN_COLOR_Z))]) \
                 for u in range(N_steps+1)]

    fig = go.Figure(
        data=[go.Scatter3d(x=[0,mags[0,0]], y=[0,mags[0,1]], z=[0,mags[0,2]],
                           mode='lines', line=dict(width=10, color=SPIN_COLOR_Z))],
        layout=go.Layout(
            paper_bgcolor='gainsboro',
            scene=dict(xaxis=axis_shared, yaxis=axis_shared, zaxis=axis_shared, aspectmode="cube"),
            margin=dict(l=5,r=5,b=5,t=5,pad=0),
            updatemenus=[dict(
                type="buttons",
                buttons=[dict(label="Play",
                              method="animate",
                              args=[None,
                                    dict(frame=dict(duration=1,redraw=True),
                                         transition=dict(duration=0))])]
            )]

        ),
        frames=mag_frames,
    )

    return fig

def make_t2_spin_plot(t2):
    # Simulate
    N_steps = 100
    mags, __ = simulate_spin(m_first=[1,0,0], duration=3*t2, steps=N_steps, pdt1t2=(1,0,t2))

    # Make animated figure
    axis_shared = dict(
        range=[-1.2, 1.2],
        backgroundcolor=BG_COLOR,
        gridcolor=GRID_COLOR,
        showbackground=True,
        showgrid=False,
        zeroline=True,
        zerolinecolor=None)

    mag_frames = [go.Frame(data=[go.Scatter3d(x=[0, mags[u, 0]], y=[0, mags[u, 1]], z=[0, mags[u, 2]],
                                              mode='lines', line=dict(width=10, color=SPIN_COLOR_XY))]) \
                  for u in range(N_steps)]

    fig = go.Figure(
        data=[go.Scatter3d(x=[0, mags[0, 0]], y=[0, mags[0, 1]], z=[0, mags[0, 2]],
                           mode='lines', line=dict(width=10, color=SPIN_COLOR_XY))],
        layout=go.Layout(
            paper_bgcolor='gainsboro',
            scene=dict(xaxis=axis_shared, yaxis=axis_shared, zaxis=axis_shared, aspectmode="cube"),
            margin=dict(l=5, r=5, b=5, t=5, pad=0),
            updatemenus=[dict(
                type="buttons",
                buttons=[dict(label="Play",
                              method="animate",
                              args=[None,
                                    dict(frame=dict(duration=1, redraw=True),
                                         transition=dict(duration=0))])]
            )]

        ),
        frames=mag_frames,
    )
    return fig

def make_t1_mag_plot(t1,mz0):
    # Simulate
    N_steps = 100
    mags,  times = simulate_spin(m_first=[0,0,mz0], duration=3*t1, steps=N_steps, pdt1t2=(1,t1,0))
    Mz = np.squeeze(mags[:,2])

    # Add an initial segment to times
    init_dur = 0.25*t1
    times = np.insert(times,0,[-init_dur,0])
    Mz = np.insert(Mz,0,[mz0,mz0])

    # Include play button and slider from the get-go
    fig = go.Figure(
        data = [go.Scatter(x=times,y=Mz,mode="lines",line=dict(width=2.5,color=SPIN_COLOR_Z))],
        layout = go.Layout(margin=dict(l=5, r=5, b=5, t=5, pad=0))
    )
    fig.update_xaxes(range=[times[0],times[-1]],title="Time (s)")
    fig.update_yaxes(range=[-1,1],title="Mz")

    return fig

def make_t2_mag_plot(t2,mx0):
    # Simulate
    N_steps = 100
    mags,  times = simulate_spin(m_first=[mx0,0,0], duration=3*t2, steps=N_steps, pdt1t2=(1,0,t2))
    Mxy = np.squeeze(mags[:,0]+1j*mags[:,1])
    Mxy = np.absolute(Mxy)

    # Add an initial segment to times
    init_dur = 0.25*t2
    times = np.insert(times,0,[-init_dur,0])
    Mxy = np.insert(Mxy,0,[mx0,mx0])

    # Include play button and slider from the get-go
    fig = go.Figure(
        data = [go.Scatter(x=times,y=Mxy,mode="lines",line=dict(width=2.5,color=SPIN_COLOR_XY))],
        layout = go.Layout(margin=dict(l=5, r=5, b=5, t=5, pad=0))
    )
    fig.update_xaxes(range=[times[0],times[-1]],title="Time (s)")
    fig.update_yaxes(range=[0,1],title="Mxy")

    return fig

def make_t1_sequence_plot(t1,ti):
    N_steps = 50
    t2 = 0.1*t1
    pdt1t2 = (1,t1,t2)
    # Simulation
    times0 = [-0.25*ti,0]
    mags0 = np.zeros((2,3))
    mags0[:,2] = [1,1]

    # Inversion and recovery
    mags1,  times1 = simulate_spin(m_first=[0,0,-1], duration=ti, steps=N_steps, pdt1t2=pdt1t2)
    times1 += times0[-1]

    # Saturation
    mz1 = mags1[-1,2]
    mags2, times2 = simulate_spin(m_first=[mz1,0,0], duration=3*t2, steps=N_steps,pdt1t2=pdt1t2)
    times2 += times1[-1]

    # Concatenate
    mags = np.concatenate((mags0,mags1,mags2),axis=0)
    times = np.concatenate((times0,times1,times2),axis=0)

    fig = go.Figure()

    # RF
    fig.add_trace(go.Scatter(x=[0,0],y=[-1.5,1.5],mode="lines",line=dict(width=3,color="cyan"),name="RF 180"))
    fig.add_trace(go.Scatter(x=[ti,ti],y=[-1.5,1.5],mode="lines",line=dict(width=3,color="maroon"),name="RF 90"))

    fig.add_trace(go.Scatter(x=times,y=mags[:,0],mode="lines",name="Mx",line=dict(width=2,color=SPIN_COLOR_XY)))
    fig.add_trace(go.Scatter(x=times,y=mags[:,2],mode="lines",name="Mz",line=dict(width=2,color=SPIN_COLOR_Z)))
    fig.update_xaxes(range=[times[0],times[-1]])
    fig.update_yaxes(range=[-1.2,1.2])
    fig.update_layout(margin=dict(l=5, r=5, b=5, t=5, pad=0))

    return fig


# TODO
def make_t2_sequence_plot(t2,te):
    N_steps = 50
    pdt1t2 = (1, 0, t2)
    # Simulation
    times0 = [-0.25 * te, 0]
    mags0 = np.zeros((2, 3))
    mags0[:, 2] = [1, 1]

    # Inversion and recovery
    mags1, times1 = simulate_spin(m_first=[1, 0, 0], duration=1.5*te, steps=N_steps, pdt1t2=pdt1t2)
    times1 += times0[-1]

    # Concatenate
    mags = np.concatenate((mags0, mags1), axis=0)
    times = np.concatenate((times0, times1), axis=0)

    fig = go.Figure()

    # RF
    fig.add_trace(go.Scatter(x=[0, 0], y=[-1.5, 1.5], mode="lines", line=dict(width=3, color="maroon"),name="RF 90"))

    fig.add_trace(go.Scatter(x=times, y=mags[:, 0], mode="lines",line=dict(width=2,color=SPIN_COLOR_XY),name="Mxy"))
    fig.add_trace(go.Scatter(x=times, y=mags[:, 2], mode="lines",line=dict(width=2,color=SPIN_COLOR_Z),name="Mz"))
    fig.update_xaxes(range=[times[0], times[-1]])
    fig.update_yaxes(range=[-1.2, 1.2])
    fig.update_layout(margin=dict(l=5, r=5, b=5, t=5, pad=0))

    return fig

def simulate_spin(m_first, duration, steps, pdt1t2):
    spin = SpinGroup(pdt1t2=pdt1t2)
    spin.m =  np.array([[0.0], [0.0], [1.0]]) # need to re-initialize to make float value assignment possible
    spin.m[:, 0] = m_first # Set initial M
    mags = np.zeros((steps+1, 3))
    mags[0,:] = np.squeeze(spin.m)
    tmodel = np.linspace(0, duration, steps + 1, endpoint=True)
    dt = tmodel[1] - tmodel[0]
    for q in range(steps):
        spin.delay(dt)
        mags[q+1, :] = np.squeeze(spin.get_m())
    return mags, tmodel


# TODO
def game6_worker_map(info):
    # Make phantom
    pht = make_phantom_from(info)

    # Simulate mapping images using signal model
    if info['mode'] == 'T1':
        fig4 = make_t1_images(pht,ti_array=DEFAULT_TIS)
        fig5 = make_t1_ROI_signal()
        fig6 = make_t1_map()
    elif info ['mode'] == 'T2':
        fig4 = make_t2_images(pht, te_array=DEFAULT_TES)
        fig5 = make_t2_ROI_signal()
        fig6 = make_t2_map()
    # Make plots
    graphJSON_left = json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON_middle = json.dumps(fig5, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON_right = json.dumps(fig6, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON_left, graphJSON_middle, graphJSON_right

# TODO
def make_phantom_from(info):
    # T1 array
    # T2 array
    #myphantom = SpheresArrayPlanarPhantom()
    myphantom = None
    return myphantom

# TODO
def make_t1_images(phantom,ti_array):
    fig = go.Figure()
    return fig

# TODO
def make_t2_images(phantom,te_array):
    fig = go.Figure()
    return fig

# TODO
def make_t1_ROI_signal():
    fig = go.Figure()
    return fig

# TODO
def make_t2_ROI_signal():
    fig = go.Figure()
    return fig

# TODO
def make_t1_map():
    fig = go.Figure()
    return fig

# TODO
def make_t2_map():
    fig = go.Figure()
    return fig

