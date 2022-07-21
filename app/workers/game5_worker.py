# Generates simulation & plots for Game 5: Proton's got moves
import numpy as np
from virtualscanner.server.simulation.bloch.spingroup_ps import SpinGroup
import plotly
import plotly.graph_objects as go
import plotly.express as px
import json
from pypulseq.make_block_pulse import make_block_pulse
from scipy.spatial.transform import Rotation as R
GAMMA_BAR = 42.58e6

# Game 5
def simulate_RF_rotation(M_first, FA, rf_phase_deg, b0, rot_frame=False,coil=None):
    """Simulates RF nutation plot of single magnetization vector given settings

    Parameters
    ----------
    M_first : array_like
        Length-3 array of initial magnetization
    FA : float
        Flip angle in [degrees]
    rf_phase_deg : float
        RF phase in [degrees]
    b0 : float
        Main field strength in [tesla]
    rot_frame : bool
        Whether rotational frame of reference is turned on
    coil : bool
        Whether receive coil is turned on

    Returns
    -------
    graphJSON : str
        JSON string of static plot to be converted into animation by Plotly.js
    last_mag : np.ndarray
        Length 3 array of the last magnetization value (for updating M_init session variable)
    """

    M_first = np.reshape(M_first,(3,1))

    print('B1 sim - M_first is given as: ', M_first)
    rf_phase = rf_phase_deg * np.pi / 180
    flip = FA * np.pi / 180
    rf_dur = 100*1e-6
    df = b0*GAMMA_BAR
    # Simulate block RF pulse
    if rot_frame:
        spin = SpinGroup(pdt1t2=(1,0,0), df=0) # No relaxation
        rf_freq = 0
    else:
        spin = SpinGroup(pdt1t2=(1,0,0), df=df)
        rf_freq = df

    spin.m = M_first # [3,1]
    rf = make_block_pulse(flip_angle=flip, duration=rf_dur)
    rfdt = rf.t[1] - rf.t[0]
    rf_time = np.array(rf.t) - rfdt

    pulse_shape = np.exp(1j*(-2*np.pi*rf_freq*rf_time + rf_phase))*rf.signal/GAMMA_BAR
    # Add phase to RF
    __, mags = spin.apply_rf_store(pulse_shape=pulse_shape, grads_shape=np.zeros((3,len(rf.signal))),dt=rfdt)
    mags = np.transpose(mags)

    graphJSON = generate_static_plot(mags, coil)
    last_mag = mags[-1,:]

    return graphJSON, last_mag

def simulate_spin_precession(M_first, b0, rot_frame=False, coil=None):
    """"Simulates spin precession plot of single magnetization vector given settings

    Parameters
    ----------
    M_first : array_like
        Length-3 array of initial magnetization value
    b0 : float
        Main field strength in [tesla]
    rot_frame : bool
        Whether rotational frame of reference is turned on
    coil : bool
        Whether receive coil is turned on

    Returns
    -------
    graphJSON : str
        JSON string of static plot to be converted into animation by Plotly.js
    dt : float
        Time resolution of simulated data
    mags : np.ndarray
        N x 3 array of simulated magnetization (for use in generating coil signal)
    """

    M_first = np.reshape(M_first,(3,1))

    # b0 - tesla
    df = b0*GAMMA_BAR
    if rot_frame:
        spin = SpinGroup(pdt1t2=(1,0,0),df=0)
    else:
        spin = SpinGroup(pdt1t2=(1,0,0),df=df)
    spin.m = M_first
    # Let it precess
    sim_dur = 1e-8
    tmodel = np.linspace(0,sim_dur,1000)
    dt = tmodel[1]-tmodel[0]
    mags = np.zeros((len(tmodel),3))
    for q in range(len(tmodel)):
        spin.delay(dt)
        mags[q,:] = np.squeeze(spin.get_m())

    graphJSON = generate_static_plot(mags, coil)

    return graphJSON, dt, mags

def animate_b0_turn_on(M_final=1, T1=1, coil=None):
    """Simulates M0 growth when main field is turned on

    Parameters
    ------
    M_final : float
        Final magnetization value to be reached
    T1 : float
        T1 value for M0 growth
    coil : bool
        Whether receive coil is turned on

    Returns
    -------
    graphJSON : str
        JSON string of static plot to be converted into animation by Plotly.js
    """

    duration = 6*T1
    spin = SpinGroup(pdt1t2=(M_final,T1,0))
    spin.m[2,0] = 0 # Set initial Mz to zero
    N_steps = 100
    mags = np.zeros((N_steps,3))
    tmodel = np.linspace(0,duration,N_steps,endpoint=False)
    dt = tmodel[1] - tmodel[0]
    for q in range(N_steps):
        spin.delay(dt)
        mags[q,:] = np.squeeze(spin.get_m())
    graphJSON = generate_static_plot(mags,coil)

    return graphJSON

def generate_coil_signal(mags,coil_dir):
    """Converts magnetization to emf in receive coil

    Parameters
    ----------
    mags : array_like
        N x 3 array of magnetization evolution
    coil_dir : str
        Coil orientation; one of {'x', 'y'}

    Returns
    -------
    signals : np.ndarray
        Simulated normalized real emf signal
    """

    if coil_dir == 'x':
        signals = -np.diff(mags[:,0])
    elif coil_dir == 'y':
        signals = -np.diff(mags[:,1])
    else:
        raise ValueError("Coil direction must be x or y")

    if np.max(np.absolute(signals)) != 0:
        signals = signals / np.max(np.absolute(signals)) # Normalized to [-1,1]

    return signals

def generate_static_plot(mags, coil=None):
    """Generates a static 3D plot of magnetization trajectory to be animated with Plotly.js

    Parameters
    ----------
    mags : array_like
        Length-3 or N x 3 array of magnetization evolution
    coil : bool
        Whether receive coil is turned on

    Returns
    -------
    graphJSON : str
        JSON string of static plot with coordinate lines, layout, and axis options set
    """

    if len(mags.shape) == 1:
        mags = np.reshape(mags, (1, len(mags)))

    bgcolor = "darkgray"
    gridcolor = "white"
    spincolor = "darkorange"

    axis_shared = dict(
        range=[-1.2, 1.2],
        backgroundcolor=bgcolor,
        gridcolor=gridcolor,
        showbackground=True,
        showgrid=False,
        zeroline=True,
        zerolinecolor=None)

    fig = go.Figure(
        data=[go.Scatter3d(x=mags[:,0], y=mags[:,1], z= mags[:,2],
                           mode='lines', line=dict(width=10, color=spincolor))],
        layout=go.Layout(
            paper_bgcolor='gainsboro',
            scene=dict(xaxis=axis_shared, yaxis=axis_shared, zaxis=axis_shared, aspectmode="cube"),
            margin=dict(r=10, l=10, b=10, t=10),
            uirevision=True)
    )

    # Zero lines and plane
    fig.add_trace(go.Mesh3d(x=[1, -1, -1, 1], y=[1, -1, 1, -1], z=[0, 0, 0, 0], color='green', opacity=0.2))
    fig.add_trace(
        go.Scatter3d(x=[-1, 1], y=[0, 0], z=[0, 0], mode='lines', line=dict(width=5, dash='dash', color='gray')))
    fig.add_trace(
        go.Scatter3d(x=[0, 0], y=[-1, 1], z=[0, 0], mode='lines', line=dict(width=5, dash='dash', color='gray')))

    # Add in RF receive coil
    if coil is not None:
        coil_x, coil_y, coil_z = generate_coil_trace(scale=0.2,displacement=1.1)
        coil_rot_angle = 0
        if coil == 'y':
            coil_rot_angle = 90
        coil_x, coil_y, coil_z = rotate_trace_by_z(coil_x,coil_y,coil_z,coil_rot_angle)

        # Add coil shape!
        fig.add_trace(
            go.Scatter3d(x=coil_x,y=coil_y,z=coil_z,mode='lines',
                         line=dict(color='red',width=12))
        )
    else:
        fig.add_trace(go.Scatter3d(x=[],y=[],z=[]))

    fig.update_traces(showlegend=False)


    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def generate_static_signals(dt, signals):
    """Generates a static 2D plot of emf signal to be animated with Plotly.js

    Parameters
    ----------
    dt : float
        Time resolution in [seconds]
    signals : array_like
        Real signal array

    Returns
    -------
    graphJSON : str
        JSON string of static plot with set style and axes

    """
    bgcolor = "black"
    signalcolor = "chartreuse"
    times = 1e3*dt*np.arange(len(signals)) # converted to ms
    fig = go.Figure(data=[go.Scatter(x=times,y=signals,mode='lines',
                                     line=dict(width=2,color=signalcolor))],
                    layout = go.Layout(
                    xaxis=dict(range=[times[0],times[-1]],showgrid=False,title='Time (ms)'),
                    yaxis=dict(range=[-1,1],showgrid=False),
                    plot_bgcolor=bgcolor,
                    margin = dict(r=10, l=10, b=10, t=10))
    )
    graphJSON = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def generate_coil_trace(scale=0.2,displacement=1.1):
    """Make 3D trace of RF coil shape for display

    Parameters
    ----------
    scale : float
        Radius of coil in the magnetization vector plot
    displacement : float
        How removed coil is from origin

    Returns
    -------
    cx, cy, cz : array_like
        Three arrays containing the x, y, and z coordinates of the coil trace
    """
    u = scale / np.sqrt(5)
    d = displacement
    # Beginning rung
    cy1 = [u,u]
    cz1 = [-2*u,0]
    # Ending rung
    cy3 = [-u,-u]
    cz3 = [0,-2*u]

    # Incomplete circle - radial coordinates
    th0 = np.arctan(-2)
    th1 = np.arctan(2) + np.pi
    thetas = np.linspace(th0,th1,100)
    cy2, cz2 = scale*np.cos(thetas), scale*np.sin(thetas)
    cz2 += scale

    # Concatenate
    cy = np.concatenate((cy1,cy2,cy3))
    cz = np.concatenate((cz1,cz2,cz3))
    cx = d*np.ones(cz.shape)

    return cx, cy, cz

def rotate_trace_by_z(cx,cy,cz,rot):
    """Helper function for visualizing RF coil
       Rotates the trace by z so that it can be placed at any direction on the xy plane

    Parameters
    ----------
    cx : array_like
        length-N array of x coordinates of coil trace
    cy : array_like
        length-N array of y coordinates of coil trace
    cz : array_like
        length-N array of z coordinates of coil trace
    rot : float
        Rotation angle (counterclockwise around z) in [degrees]

    Returns
    -------
    cx_new, cy_new, cz_new : array_like
        Rotated coordinates of trace
    """

    r = R.from_rotvec((rot*np.pi/180)*np.array([0,0,1]))
    vecs = np.transpose(np.array([cx,cy,cz]))
    vecs_new = r.apply(vecs)
    cx_new = vecs_new[:,0]
    cy_new = vecs_new[:,1]
    cz_new = vecs_new[:,2]

    return cx_new,cy_new,cz_new

def animate_spin_action(dt, mags):
    """Generates Plotly animation with play button for preview (not for frontend use)

    Parameters
    ----------
    dt : float
        Time resolution in [seconds]
    mags : np.ndarray
        N x 3 array of magnetization vector to be animated
        N : number of time points
        3 : Mx/My/Mz dimension

    Returns
    -------
    graphJSON : str
        JSON string of animated plot
    """

    bgcolor = "darkgray"
    gridcolor = "white"
    spincolor = "darkorange"

    axis_shared = dict(
            range=[-1,1],
            backgroundcolor=bgcolor,
            gridcolor=gridcolor,
            showbackground=True,
            showgrid=False,
            zeroline=True,
            zerolinecolor=None)

    frame_layout = go.Layout(dict(
        scene=dict(xaxis=axis_shared,yaxis=axis_shared,zaxis=axis_shared,
                   aspectmode="cube"),
    ))

    fig = go.Figure(
        data = [go.Scatter3d(x=[0,mags[0,0]],y=[0,mags[0,1]],z=[0,mags[0,2]],
                             mode='lines', line=dict(width=10, color=spincolor))],
        layout = go.Layout(
            scene=dict(xaxis=axis_shared, yaxis=axis_shared, zaxis=axis_shared,aspectmode="cube"),
            width=500, height=500, margin=dict(r=10, l=10, b=10, t=10),

            # Update menus for play button - useful in preview
            updatemenus=[dict(
                type = "buttons",
                buttons = [dict(label="Play",
                                method = "animate",
                                args=[None,{
                                    "frame":{"duration":dt*1000},
                                    "fromcurrent": True,
                                    "transition": {"duration": 0},
                                }])])]

        ),
            frames = [go.Frame(data=[go.Scatter3d(
                                    x=[0,mags[q,0]],y=[0,mags[q,1]],z=[0,mags[q,2]],
                                    mode='lines', line=dict(width=10, color=spincolor)),
                                 ],layout=frame_layout) for q in range(mags.shape[0])]
        )

    fig.add_trace(go.Mesh3d(x=[1,-1,-1,1],y=[1,-1,1,-1],z=[0,0,0,0],color='green',opacity=0.2))
    fig.add_trace(go.Scatter3d(x=[-1,1],y=[0,0],z=[0,0],mode='lines',line=dict(width=5,dash='dash',color='gray')))
    fig.add_trace(go.Scatter3d(x=[0,0],y=[-1,1],z=[0,0],mode='lines',line=dict(width=5,dash='dash',color='gray')))
    fig.update_traces(showlegend=False)
    fig.show()

    graphJSON = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


if __name__ == '__main__':
    # Examples of making plots
    # Nutation
    j0, lastmag1 = simulate_RF_rotation(M_first=[[0],[0],[1]],FA=90,rf_phase_deg=0,b0=0.001,rot_frame=True)
    # Precession
    j1, dt1, mags1 = simulate_spin_precession(M_first=[[0],[0],[1]], b0=0.001, rot_frame=False)
    # Static plot of one time point
    mags_zero = np.zeros((1,3))
    j2 = generate_static_plot(mags=mags_zero,coil=None)

    # Examples of making coil shapes
    cx,cy,cz = generate_coil_trace(scale=0.2,displacement=1.2)
    cx2,cy2,cz2 = rotate_trace_by_z(cx,cy,cz,90)
    fig = go.Figure(go.Scatter3d(x=cx,y=cy,z=cz,mode='lines'))
    fig.add_trace(go.Scatter3d(x=cx2,y=cy2,z=cz2,mode='lines'))
    fig.show()
