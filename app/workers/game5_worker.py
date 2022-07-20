# Generates simulation & plots for Game 5: Proton's got moves
import numpy as np
from pypulseq.make_block_pulse import make_block_pulse
from virtualscanner.server.simulation.rf_sim.rf_simulations import simulate_rf
from virtualscanner.server.simulation.bloch.spingroup_ps import SpinGroup
import plotly
import plotly.graph_objects as go
import plotly.express as px
from pypulseq.opts import Opts
import json
from pypulseq.make_block_pulse import make_block_pulse
from scipy.spatial.transform import Rotation as R

GAMMA_BAR = 42.58e6


# Game 5
def simulate_RF_rotation(M_first, FA, rf_phase_deg, b0, rot_frame=False,coil=None):
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
    #TODO
    return generate_static_plot(rfdt, mags, coil), mags[-1,:]

def simulate_spin_precession(M_first, b0, rot_frame=False, coil=None):
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

    return generate_static_plot(dt, mags, coil), dt, mags

def animate_b0_turn_on(M_final=1, T1=1, coil=None):
    """
    Parameters
    ------
    M_final : float
        Final magnetization value to be reached
    Returns
    -------
    graphJSON : str
        JSON string of Plotly figure

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

    return generate_static_plot(dt,mags,coil)

def animate_spin_action(dt, mags, settings={}):
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

    #Arrow at the end
    #go.Cone(x=[mags[q, 0]], y=[mags[q, 1]], z=[mags[q, 2]],
    #        u=[0.2 * mags[q, 0]], v=[0.2 * mags[q, 1]], w=[0.2 * mags[q, 2]],
    #        sizemode='scaled', sizeref=1, colorscale=[[0, spincolor], [1, spincolor]],
    #        showscale=False, anchor='tip')



    #plotly.offline.plot(fig, auto_play=True)

    fig.add_trace(go.Mesh3d(x=[1,-1,-1,1],y=[1,-1,1,-1],z=[0,0,0,0],color='green',opacity=0.2))
    fig.add_trace(go.Scatter3d(x=[-1,1],y=[0,0],z=[0,0],mode='lines',line=dict(width=5,dash='dash',color='gray')))
    fig.add_trace(go.Scatter3d(x=[0,0],y=[-1,1],z=[0,0],mode='lines',line=dict(width=5,dash='dash',color='gray')))
    fig.update_traces(showlegend=False)

    fig.show()


    j1 = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    return j1


def generate_static_plot(dt, mags, coil=None):
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


    j1 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return j1

def generate_static_signals(dt, signals):
    bgcolor = "black"
    gridcolor = "gainsboro"
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
    j1 = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    return j1




def make_spin_action_plot(simulated_data):
    a = simulated_data
    graphJSON = 0
    return graphJSON


def generate_coil_trace(scale,displacement):
    """
    scale - radius of coil
    displacement - how removed coil is from origin
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
    # rot [degrees] (counterclockwise)
    r = R.from_rotvec((rot*np.pi/180)*np.array([0,0,1]))
    vecs = np.transpose(np.array([cx,cy,cz]))
    vecs_new = r.apply(vecs)
    cx_new = vecs_new[:,0]
    cy_new = vecs_new[:,1]
    cz_new = vecs_new[:,2]

    return cx_new,cy_new,cz_new


def generate_coil_signal(dt, mags,coil_dir):
    if coil_dir == 'x':
        signals = -np.diff(mags[:,0])
    elif coil_dir == 'y':
        signals = -np.diff(mags[:,1])
    else:
        raise ValueError("Coil direction must be x or y")

    if np.max(np.absolute(signals)) != 0:
        signals = signals / np.max(np.absolute(signals)) # Normalized to [-1,1]

    return signals


if __name__ == '__main__':
    #dt, mags = simulate_RF_rotation(M_first=[[0],[0],[1]],FA=90,rf_phase_deg=0,b0=0.001,rot_frame=True)
    #mags = np.zeros((1,3))
    #dt = 1
    #dt, mags = simulate_spin_precession(M_first=[[0],[0],[1]], b0=0.001, rot_frame=False)
    #print(mags.shape)
    #generate_static_plot(dt, mags)
    cx,cy,cz = generate_coil_trace(scale=0.2,displacement=1.2)
    cx2,cy2,cz2 = rotate_trace_by_z(cx,cy,cz,90)
    fig = go.Figure(go.Scatter3d(x=cx,y=cy,z=cz,mode='lines'))
    fig.add_trace(go.Scatter3d(x=cx2,y=cy2,z=cz2,mode='lines'))
    fig.show()
