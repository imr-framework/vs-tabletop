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
from virtualscanner.server.simulation.bloch.phantom import makeCylindricalPhantom
from virtualscanner.server.simulation.bloch.spingroup_ps import SpinGroup
from virtualscanner.server.ana.T2_mapping import T2_sig_eq
import vstabletop.utils as utils
from vstabletop.info import GAME6_INFO


from scipy.optimize import curve_fit


M0 = 1
SPIN_COLOR_Z = 'dodgerblue'
SPIN_COLOR_XY = 'darkorange'
BG_COLOR = "darkgray"
GRID_COLOR = "white"
COLOR_T1 = "navy"
COLOR_T2 = "red"
COLOR_T1_FIT = "deepskyblue"
COLOR_T2_FIT = "indianred"

N = GAME6_INFO['phantom_n']
FOV = GAME6_INFO['phantom_fov']


def game6_worker_sim(info):
    # Left: demo
    if info['mode'] == 'T1':
        T1 = info['t1_sim']*1e-3
        TI = info['t1_sim_ti']*1e-3
        fig1 = make_t1_spin_plot(t1=T1,mz0=info['t1_sim_mz0']/100)
        fig2 = make_t1_mag_plot(t1=T1,mz0=info['t1_sim_mz0']/100,duration=info['t1_sim_dur']*1e-3)
        fig3 = make_t1_sequence_plot(t1=T1,ti=TI)
    elif info['mode'] == 'T2':
        T2 = info['t2_sim']*1e-3
        TE = info['t2_sim_te']*1e-3
        fig1 = make_t2_spin_plot(t2=T2,mx0=info['t2_sim_mx0']/100)
        fig2 = make_t2_mag_plot(t2=T2,mx0=info['t2_sim_mx0']/100,duration=info['t2_sim_dur']*1e-3)
        fig3 = make_t2_sequence_plot(t2=T2, te=TE)

    graphJSON_left = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON_middle = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON_right = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON_left, graphJSON_middle, graphJSON_right

def make_t1_spin_plot(t1,mz0):
    # Simulate
    N_steps = 100
    mags, __ = simulate_spin(m_first=[0,0,mz0], duration=3*t1, steps=N_steps, pdt1t2=(1,t1,0))

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

def make_t2_spin_plot(t2,mx0):
    # Simulate
    N_steps = 100
    mags, __ = simulate_spin(m_first=[mx0,0,0], duration=3*t2, steps=N_steps, pdt1t2=(1,0,t2))

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

def make_t1_mag_plot(t1,mz0,duration):
    # Simulate
    N_steps = 100
    mags,  times = simulate_spin(m_first=[0,0,mz0], duration=duration, steps=N_steps, pdt1t2=(1,t1,0))
    Mz = np.squeeze(mags[:,2])



    # Include play button and slider from the get-go
    fig = go.Figure(
        data = [go.Scatter(x=times,y=Mz,mode="lines",line=dict(width=2.5,color=SPIN_COLOR_Z))],
        layout = go.Layout(margin=dict(l=5, r=5, b=5, t=5, pad=0))
    )
    fig.update_xaxes(range=[times[0],times[-1]],title="Time (s)")
    fig.update_yaxes(range=[-1,1],title="Mz")

    return fig

def make_t2_mag_plot(t2,mx0,duration):
    # Simulate
    N_steps = 100
    mags,  times = simulate_spin(m_first=[mx0,0,0], duration=duration, steps=N_steps, pdt1t2=(1,0,t2))
    Mxy = np.squeeze(mags[:,0]+1j*mags[:,1])
    Mxy = np.absolute(Mxy)


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
    # Magnetization
    fig.add_trace(go.Scatter(x=times,y=mags[:,0],mode="lines",name="Mx",line=dict(width=2,color=SPIN_COLOR_XY)))
    fig.add_trace(go.Scatter(x=times,y=mags[:,2],mode="lines",name="Mz",line=dict(width=2,color=SPIN_COLOR_Z)))
    # Text
    fig.add_trace(go.Scatter(x=[ti/2],y=[-0.25],mode="text",text=['TI'],textfont=dict(color='gray',size=16),textposition="middle center"))

    # Arrow 1
    arrow1 = go.layout.Annotation(dict(
        x=0,
        y=-0.25,
        xref="x", yref="y",
        text="",
        showarrow=True,
        axref="x", ayref='y',
        ax=ti/10,
        ay=-0.25,
        arrowhead=3,
        arrowwidth=1.5,
        arrowcolor='gray', )
    )

    # Arrow 2
    arrow2 = go.layout.Annotation(dict(
        x=ti,
        y=-0.25,
        xref="x", yref="y",
        text="",
        showarrow=True,
        axref="x", ayref='y',
        ax= ti - ti/10,
        ay=-0.25,
        arrowhead=3,
        arrowwidth=1.5,
        arrowcolor='gray', )
    )

    fig.update_layout(
        annotations=[arrow1, arrow2])
    fig.update_xaxes(range=[times[0],times[-1]])
    fig.update_yaxes(range=[-1.2,1.2])
    fig.update_layout(margin=dict(l=5, r=5, b=5, t=5, pad=0))

    return fig

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
    # Magnetizations
    fig.add_trace(go.Scatter(x=times, y=mags[:, 0], mode="lines",line=dict(width=2,color=SPIN_COLOR_XY),name="Mxy"))
    fig.add_trace(go.Scatter(x=times, y=mags[:, 2], mode="lines",line=dict(width=2,color=SPIN_COLOR_Z),name="Mz"))
    # Timing
    fig.add_trace(go.Scatter(x=[te,te],y=[-1.5,1.5],mode="lines",line=dict(width=3,color="gray",dash='dash')))
    fig.add_trace(go.Scatter(x=[te/2],y=[-0.25],mode="text",text=['TE'],textfont=dict(color='gray',size=16),textposition="middle center"))

    # Arrow 1
    arrow1 = go.layout.Annotation(dict(
        x=0,
        y=-0.25,
        xref="x", yref="y",
        text="",
        showarrow=True,
        axref="x", ayref='y',
        ax=te/10,
        ay=-0.25,
        arrowhead=3,
        arrowwidth=1.5,
        arrowcolor='gray', )
    )

    # Arrow 2
    arrow2 = go.layout.Annotation(dict(
        x=te,
        y=-0.25,
        xref="x", yref="y",
        text="",
        showarrow=True,
        axref="x", ayref='y',
        ax=te - te/10,
        ay=-0.25,
        arrowhead=3,
        arrowwidth=1.5,
        arrowcolor='gray', )
    )

    fig.update_layout(
        annotations=[arrow1, arrow2])

    fig.update_xaxes(range=[times[0], times[-1]])
    fig.update_yaxes(range=[-1.2, 1.2])
    fig.update_layout(margin=dict(l=5, r=5, b=5, t=5, pad=0))

    return fig

# Sim helper
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

# Map mode
def game6_worker_map(session,update_list,display_list):
    info = session['game6']
    if info['mode'] == 'T1':
        # Perform any updates
        # First
        if update_list['images']=='new':
            t1_images = make_t1_images(info) # Session will get updated
            info['t1_images'] = t1_images
            utils.update_session_subdict(session,'game6',{'t1_images':t1_images})

        elif update_list['images']=='blank':
            info['t1_images'] = None
            utils.update_session_subdict(session,'game6',{'t1_images':None})

        # Second
        if update_list['roi']=='new':
            roi_signal = make_t1_ROI_signal(info) # Session will get updated
            info['t1_roi_signal'] = roi_signal
            utils.update_session_subdict(session,'game6',{'t1_roi_signal': roi_signal})

        elif update_list['roi']=='fit':
            roi_fit = make_t1_ROI_fit(info) # Session will get updated
            print('roi_fit', roi_fit)
            info['t1_roi_fit'] = roi_fit
            utils.update_session_subdict(session,'game6',{'t1_roi_fit': roi_fit})

        elif update_list['roi']=='blank':
            print('Doing it blank')
            info['t1_roi_signal'] = None
            utils.update_session_subdict(session,'game6',{'roi_signal': None})

        # Third
        if update_list['map']=='new':
            map = make_t1_map(info)
            utils.update_session_subdict(session,'game6',{'t1_map': map}) # in ms
        elif update_list['map']=='mapped':
            map = info['t1_map']
        elif update_list['map']=='phantom':
            map = info['t1_phantom'].T1map*1e3
        else:
            map = np.zeros(np.shape(info['t1_phantom'].T1map))

        fig4 = display_t1_images(info) if display_list[0] else None
        fig5 = display_t1_ROI_signal(info,include_fit=(update_list['roi']=='fit')) if display_list[1] else None
        fig6 = display_t1_map(info, map, type=update_list['map']) if display_list[2] else None

    elif info ['mode'] == 'T2':
        # First
        if update_list['images']=='new':
            t2_images = make_t2_images(info) # Session will get updated
            info['t2_images'] = t2_images
            utils.update_session_subdict(session,'game6',{'t2_images':t2_images})
        elif update_list['images']=='blank':
            info['t2_images'] = None
            utils.update_session_subdict(session,'game6',{'t2_images':None})

        # Second
        if update_list['roi'] == 'new':
            roi_signal = make_t2_ROI_signal(info)  # Session will get updated
            info['t2_roi_signal'] = roi_signal
            utils.update_session_subdict(session, 'game6', {'t2_roi_signal': roi_signal})

        elif update_list['roi'] == 'fit':
            roi_fit = make_t2_ROI_fit(info)  # Session will get updated
            print('roi_fit', roi_fit)
            info['t2_roi_fit'] = roi_fit
            utils.update_session_subdict(session, 'game6', {'t2_roi_fit': roi_fit})

        # Third
        if update_list['map']=='new':
            map = make_t2_map(info)
            utils.update_session_subdict(session,'game6',{'t2_map': map}) # in ms
        elif update_list['map']=='mapped':
            map = info['t2_map']
        elif update_list['map']=='phantom':
            map = info['t2_phantom'].T2map*1e3
        else:
            map = np.zeros(np.shape(info['t2_phantom'].T2map))

        fig4 = display_t2_images(info) if display_list[0] else None
        fig5 = display_t2_ROI_signal(info,include_fit=(update_list['roi']=='fit')) if display_list[1] else None
        fig6 = display_t2_map(info, map, type=update_list['map']) if display_list[2] else None

    else:
        raise ValueError('Mode can only be T1 or T2')
    # Make plots
    graphJSON_left = json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON_middle = json.dumps(fig5, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON_right = json.dumps(fig6, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON_left, graphJSON_middle, graphJSON_right

# def make_phantom(mode):
#     # Utilize Virtual Scanner's cylindrical phantom.
#     # T1 array
#     if mode == "T1":
#         myphantom = makeCylindricalPhantom(dim=2,n=32,dir='z',loc=0,fov=0.24,type_params=None)
#         return myphantom.T1map
#     # T2 array
#     elif mode == "T2":
#         myphantom = makeCylindricalPhantom(dim=2,n=32,dir='z',loc=-0.08,fov=0.24,type_params=None)
#         return myphantom.T2map
#     # T2 array
#     else:
#         raise ValueError('This mode is not supported. Use T1 or T2.')

def initialize_phantom(session):
    if session['game6']['t1_phantom'] is None:
        phantom1 = makeCylindricalPhantom(dim=2, n=N, dir='z', loc=0, fov=FOV, type_params=None)
        # Store masks
        t1_masks = [phantom1.type_map == u + 4 for u in range(4)]
        utils.update_session_subdict(session,'game6',{'t1_phantom':phantom1, 't1_masks':t1_masks})

    if session['game6']['t2_phantom'] is None:
        phantom2 = makeCylindricalPhantom(dim=2, n=N, dir='z', loc=-FOV/3, fov=FOV, type_params=None)
        # Store masks
        t2_masks = [phantom2.type_map == u + 8 for u in range(4)]
        utils.update_session_subdict(session,'game6',{'t2_phantom':phantom2,'t2_masks':t2_masks})



    print('Game 6 Phantom initialized')
    return

def make_t1_images(info):
    # Simulate with signal equation
    def model(t1,pd,TI):
        # T1 is an array; TI is one number
        return pd*(1-2*np.exp(-TI/t1)) + pd*np.random.normal(0,0.05,size=(pd.shape))
    t1 = info['t1_phantom'].T1map*1e3
    pd = info['t1_phantom'].PDmap
    TIs = info['t1_map_TIs']
    t1_images = [model(t1,pd,TI) for TI in TIs]

    return t1_images

def make_t2_images(info):
    def model(t2,pd,TE):
        return pd*np.exp(-TE/t2) + pd*np.random.normal(0,0.05,size=(pd.shape))
    t2 = info['t2_phantom'].T2map*1e3
    pd = info['t2_phantom'].PDmap
    TEs = info['t2_map_TEs']
    t2_images = [model(t2,pd,TE) for TE in TEs]

    return t2_images

def make_t1_ROI_signal(info):
    n = info['current_sphere'] # 0(None),1,2,3,4
    if n == 0:
        signal = np.zeros(info['t1_map_TIs'].shape)
        print('No sphere selected')
    else:
        # Extract signal from ROI (average)
        signal = np.array([np.sum(info['t1_masks'][n-1]*t1_image)/np.sum(info['t1_masks'][n-1]) for t1_image in info['t1_images']])

    return signal

def make_t2_ROI_signal(info):
    n = info['current_sphere'] # 0(None),1,2,3,4
    if n == 0:
        signal = np.zeros(info['t2_map_TEs'].shape)
        print('No sphere selected')
    else:
        signal = np.array([np.sum(info['t2_masks'][n-1]*t2_image)/np.sum(info['t2_masks'][n-1]) for t2_image in info['t2_images']])

    return signal

def make_t1_ROI_fit(info):
    popt = make_t1_fit(np.array(info['t1_map_TIs'])*1e-3, info['t1_roi_signal'])
    return popt

def make_t2_ROI_fit(info):
    popt = make_t2_fit(np.array(info['t2_map_TEs'])*1e-3, info['t2_roi_signal'])
    return popt

def make_t1_fit(ti, signal):
    # TI in seconds
    # signal in a.u.
    popt, __ = curve_fit(T1_sig_eq_noTR, ti, signal, p0=(0.75,1.5,0),bounds=([0,0,-np.inf],[1,5,np.inf]))
    return popt

def make_t2_fit(te, signal):
    popt, __ = curve_fit(T2_sig_eq_noTR, te, signal, p0=(0.75,0.05),bounds=([0,0],[1,4]))
    return popt

def make_t1_map(info):
    print("Start T1 mapping")
    # Perform mapping at every location
    images = info['t1_images']
    map = np.zeros(images[0].shape)
    for u in range(images[0].shape[0]):
        for v in range(images[0].shape[1]):
            signal = [images[q][u,v][0] for q in range(len(images))]
            popt = make_t1_fit(np.array(info['t1_map_TIs']) * 1e-3, signal)
            map[u,v] = popt[1]*1e3 # Store in ms
    print("T1 mapping completed")
    return map

def make_t2_map(info):
    print("Start T2 mapping")
    images = info['t2_images']
    map = np.zeros(images[0].shape)
    for u in range(images[0].shape[0]):
        for v in range(images[0].shape[1]):
            signal = [images[q][u,v][0] for q in range(len(images))]
            popt = make_t2_fit(np.array(info['t2_map_TEs'])*1e-3, signal)
            map[u,v] = popt[1]*1e3
    print("T2 mapping completed")
    return map

def display_t1_images(info):
    t1_images = info['t1_images']
    if t1_images is not None:
        fig = go.Figure(
            data=[go.Heatmap(z=np.absolute(np.squeeze(t1_images[0])),colorscale="gray",showscale=False)],
            frames=[go.Frame(data=go.Heatmap(z=np.absolute(np.squeeze(t1_images[u])),
                                             colorscale="gray",
                                             showscale=False),name=f'frame{u}') for u in range(len(t1_images)) ])

        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(scaleanchor='x'),margin=dict(l=5, r=5, b=5, t=5, pad=0))
        fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)

        # Add sliders
        def frame_args(duration):
            return {
                "frame": {"duration": duration},
                "mode": "immediate",
                "fromcurrent": True,
                "transition": {"duration": duration, "easing": "linear"},
            }

        sliders = [
            {
                "pad": {"b": 10, "t": 60},
                "len": 0.9,
                "x": 0.1,
                "y": 0,
                "steps": [
                    {
                        "args": [[f.name], frame_args(duration=500)],
                        "label": f'{info["t1_map_TIs"][k]} ms',
                        "method": "animate",
                    }
                    for k, f in enumerate(fig.frames)
                ],
            }
        ]

        # Layout
        fig.update_layout(
            updatemenus=[
                {
                    "buttons": [
                        {
                            "args": [None, frame_args(50)],
                            "label": "&#9654;",  # play symbol
                            "method": "animate",
                        },
                        {
                            "args": [[None], frame_args(0)],
                            "label": "&#9724;",  # pause symbol
                            "method": "animate",
                        },
                    ],
                    "direction": "left",
                    "pad": {"r": 10, "t": 70},
                    "type": "buttons",
                    "x": 0.1,
                    "y": 0,
                }
            ],
            sliders=sliders
        )


    else:
        fig = make_blank_plot('image')

    return fig


# TODO display image stored in session
def display_t2_images(info):
    t2_images = info['t2_images']
    if t2_images is not None:
        fig = go.Figure(
            data=[go.Heatmap(z=np.absolute(np.squeeze(t2_images[0])), colorscale="gray", showscale=False)],
            frames=[go.Frame(data=go.Heatmap(z=np.absolute(np.squeeze(t2_images[u])),
                                             colorscale="gray",
                                             showscale=False), name=f'frame{u}') for u in range(len(t2_images))])

        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(scaleanchor='x'),
                          margin=dict(l=5, r=5, b=5, t=5, pad=0))
        fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)

        # Add sliders
        def frame_args(duration):
            return {
                "frame": {"duration": duration},
                "mode": "immediate",
                "fromcurrent": True,
                "transition": {"duration": duration, "easing": "linear"},
            }

        sliders = [
            {
                "pad": {"b": 10, "t": 60},
                "len": 0.9,
                "x": 0.1,
                "y": 0,
                "steps": [
                    {
                        "args": [[f.name], frame_args(duration=500)],
                        "label": f'{info["t2_map_TEs"][k]} ms',
                        "method": "animate",
                    }
                    for k, f in enumerate(fig.frames)
                ],
            }
        ]

        # Layout
        fig.update_layout(
            updatemenus=[
                {
                    "buttons": [
                        {
                            "args": [None, frame_args(50)],
                            "label": "&#9654;",  # play symbol
                            "method": "animate",
                        },
                        {
                            "args": [[None], frame_args(0)],
                            "label": "&#9724;",  # pause symbol
                            "method": "animate",
                        },
                    ],
                    "direction": "left",
                    "pad": {"r": 10, "t": 70},
                    "type": "buttons",
                    "x": 0.1,
                    "y": 0,
                }
            ],
            sliders=sliders
        )

    else:
        fig = make_blank_plot('image')
    return fig

def display_t1_ROI_signal(info,include_fit):
    TIs = info['t1_map_TIs']
    signal = info['t1_roi_signal']
    if signal is None:
        fig = make_blank_plot('signal')
    else:
        fig = go.Figure(go.Scatter(
            x = TIs,
            y = signal,
            mode="markers",
            marker=dict(color=COLOR_T1,size=10),
            name="Signal",
            showlegend=True
        ))
    # TODO
    if include_fit:
        # Plot the fit curve using the signal equation
        timodel = np.linspace(0,TIs[-1],100)
        timodel_input = timodel*1e-3
        a,b,c = info['t1_roi_fit']

        fig.add_trace(go.Scatter(x=timodel,y=T1_sig_eq_noTR(timodel_input,a,b,c),mode="lines",
                                 line=dict(width=2,color=COLOR_T1_FIT),name="Fit",showlegend=True))
        # Add text of T1
        fig.add_trace(go.Scatter(x=[timodel[0]],y=[1],mode="text",
                                 text=[f'T1 = {int(np.round(b*1e3))} ms'],
                                 textfont=dict(
                                     color=COLOR_T1_FIT,
                                     size=16),
                                 textposition="bottom right",showlegend=False))


    fig.update_layout(margin=dict(l=5, r=5, b=5, t=5, pad=0))
    return fig


# TODO
def display_t2_ROI_signal(info,include_fit):
    TEs = info['t2_map_TEs']
    signal = info['t2_roi_signal']
    if signal is None:
        fig = make_blank_plot('signal')
    else:
        fig = go.Figure(go.Scatter(
            x=TEs,
            y=signal,
            mode="markers",
            marker=dict(color=COLOR_T2, size=10),
            name="Signal",
            showlegend=True
        ))
    # TODO
    if include_fit:
        # Plot the fit curve using the signal equation
        temodel = np.linspace(0, TEs[-1], 100)
        temodel_input = temodel * 1e-3
        a, b = info['t2_roi_fit']

        fig.add_trace(go.Scatter(x=temodel, y=T2_sig_eq_noTR(temodel_input, a, b), mode="lines",
                                 line=dict(width=2, color=COLOR_T2_FIT), name="Fit", showlegend=True))
        # Add text of T1
        fig.add_trace(go.Scatter(x=[temodel[0]], y=[1], mode="text",
                                 text=[f'T2 = {int(np.round(b * 1e3))} ms'],
                                 textfont=dict(
                                     color=COLOR_T2_FIT,
                                     size=16),
                                 textposition="bottom right", showlegend=False))

    fig.update_layout(margin=dict(l=5, r=5, b=5, t=5, pad=0))
    return fig


def display_t1_map(info,map,type):
    # Display = "phantom" or "map"
    if type == "blank":
        return make_blank_plot('image')
    fig = go.Figure()
    fig.add_trace(go.Heatmap(z=np.squeeze(map),colorscale='viridis', showscale=True,  colorbar={"title":"T1 (ms)"}))
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)',yaxis=dict(scaleanchor='x'),margin=dict(l=5, r=5, b=5, t=5, pad=0))
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)

    return fig

def display_t2_map(info,map,type):
    # Display = "phantom" or "map"
    if type == "blank":
        return make_blank_plot('image')
    fig = go.Figure()
    fig.add_trace(go.Heatmap(z=np.squeeze(map),colorscale='viridis', showscale=True,  colorbar={"title":"T2 (ms)"}))
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)',yaxis=dict(scaleanchor='x'),margin=dict(l=5, r=5, b=5, t=5, pad=0))
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)

    return fig

def make_blank_plot(type="image"):
    if type == "image":
        fig = go.Figure(go.Heatmap(z=np.zeros((16,16)),colorscale="gray",showscale=False))
        fig.update_layout(plot_bgcolor = 'rgba(0,0,0,0)', yaxis = dict(scaleanchor='x'))
        fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)

    elif type == "signal":
        fig = go.Figure()
        fig.update_layout(margin=dict(l=5,r=5,b=5,t=5,pad=0))
    else:
        raise ValueError("Type must be image or signal")
    return fig

def calculate_circle(type,sphere):
    # Scaling : from [-FOV/2, FOV/2] to [0,N]
    N = GAME6_INFO['phantom_n']
    FOV = GAME6_INFO['phantom_fov']
    r = N/8
    c = (np.array(list(GAME6_INFO[f'{type.lower()}_array_centers'][sphere-1])) + FOV/2) * ((N-1)/FOV)

    return list(c), r

def T1_sig_eq_noTR(X,a,b,c):
    # X : TI
    # a : PD
    # b : T1
    # c (offset, not used)
    return a * (1 - 2 * np.exp(- X / b)) # + c

def T2_sig_eq_noTR(X,a,b):
    # a : PD
    # b : T2
    return a * np.exp(-X/b)
