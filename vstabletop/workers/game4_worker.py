import numpy as np
from plotly import graph_objects as go
import plotly
import plotly.express as px
import json

# Constants (approximate 1.5T values ~ Spees et al., 2001, MRM)
T1_BLOOD = 2000e-3 # T1 = 2000 ms
T2_BLOOD = 200e-3 # T2 = 200 ms
T2s_BLOOD = T2_BLOOD / 6  # Roughly the same ratio as CSF in the Brainweb model
M0 = 1

def game4_worker_simulation(mode='bright',info={}):
    # Bright blood
    if mode == 'bright':
        j1, j2 = simulate_bright_plots(info)
    # Dark blood
    elif mode == 'dark':
        j1, j2 = simulate_dark_plots(info)
    else:
        raise ValueError('Mode does not exist.')
    return j1, j2

def game4_worker_image(mode='bright',info={}):
    img = simulate_flow_image(mode,info)
    fig = go.Figure(go.Heatmap(z=img, colorscale='gray', showscale=False))
    fig.update_traces(showlegend=False)
    fig.update_layout(yaxis=dict(scaleanchor='x'),
                      plot_bgcolor='rgba(0,0,0,0)',
                      margin=go.layout.Margin(
                          l=5,
                          r=5,
                          b=5,
                          t=5
                      ))
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)

    # Make plots
    imgJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return imgJSON

# Simulated / animted plots
def simulate_bright_plots(info):
    # Get the raw values
    signals, has_partial, ff, pf = signal_model_bright(info['flow_speed'],
                                                       info['bright_thk'],
                                                       info['bright_tr'] ,
                                                       info['bright_fa'])
    # Calculate data for each step
    Nss = len(signals)
    fraction_list = ff*np.ones(signals.shape)
    if has_partial:
        fraction_list[-1] = pf

    signal_partitioned_list = [np.zeros(signals.shape)]
    signal_total_list = [0]
    for u in range(Nss):
        mask = (np.arange(Nss) < u+1)
        signal_total_list.append(np.sum(signals*mask*fraction_list))
        signal_partitioned_list.append(signals*mask)

    # Generate Mxy and Mz curves
    Mxy_list, Mz_list, t_list = generate_bright_signal_curves(Nss + 1,
                                                              info['bright_tr'],
                                                              info['bright_fa'])


    j1, j2 = plot_bright_signals(info, signal_partitioned_list, signal_total_list, fraction_list,
                                 Mxy_list, Mz_list, t_list)
    return j1, j2

# TODO
def simulate_dark_plots(info):
    # 90, 180, 90+180 signals

    # 90
    j1, j2 = plot_dark_signals(info)
    return j1, j2

# TODO
def simulate_flow_image(mode,info):
    if mode == 'empty':
        return np.zeros((256,256))

    # Initialize phantom (0 - background, 1 - stationary, 2 - flow)


    return None

def plot_bright_signals(info, signal_partitioned_list, signal_total_list, fraction_list, Mxy_list, Mz_list, t_list):
    fig1 = go.Figure()
    for u in range(len(t_list)):
        fig1.add_trace(go.Scatter(x=t_list[u], y=Mz_list[u], mode='lines',line=dict(width=3,color='navy')))
        fig1.add_trace(go.Scatter(x=t_list[u], y=Mxy_list[u], mode='lines', line=dict(width=3,color='green')))

    fig1.update_xaxes(range=[t_list[0][0],t_list[-1][-1]])
    fig1.update_yaxes(range=[-1,1])

    fig1.update_layout(margin=dict(l=25,r=25,b=0,t=0),height=150)
    fig1.update_traces(showlegend=False)

    fig2 = go.Figure()

    # Generate the necessary rectangles
    thk = info['bright_thk']*1e3
    y0, y1 = 1,2
    # Background rectangle
    # Flow rectangle
    fig2.add_shape(type='rect',x0=0,y0=y0,x1=20,y1=y1,line=dict(width=0),fillcolor="navy")

    # Partial rectangle
    # Slice rectangle
    fig2.add_vline(x=10-thk/2,line_width=2.5,line_dash='dot',line_color="goldenrod")
    fig2.add_vline(x=10+thk/2,line_width=2.5,line_dash='dot',line_color="goldenrod")
    fig2.add_vrect(x0=10-thk/2, x1=10+thk/2, fillcolor="goldenrod",opacity=0.5,layer="below",line_width=0)

    # Signal rectangles
    pos = 10 - thk / 2
    print('list', signal_partitioned_list)
    for ind, fraction in enumerate(fraction_list):
        signal = signal_partitioned_list[-1][ind]
        xleft = pos
        xright = pos + thk * fraction
        fig2.add_shape(type='rect', x0=xleft, y0=y0, x1=xright, y1=y1, line=dict(width=0),
                       fillcolor=f"rgb({int(179 * signal)},{int(236 * signal)},{int(255 * signal)})")
        pos = xright

    # flow figure!
    fig2.update_xaxes(range=[0,20])
    fig2.update_yaxes(range=[0,3])
    fig2.update_layout(margin=dict(l=25,r=25,b=0,t=0),height=150)
    fig2.update_traces(showlegend=False)

    brightJSON1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    brightJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    return brightJSON1, brightJSON2

def plot_dark_signals(info):
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=[0,1], y=[1,1], mode='lines', line=dict(width=3, color='dodgerblue')))
    fig1.update_xaxes(range=[0,1])
    fig1.update_yaxes(range=[0, 1])
    fig1.update_layout(margin=dict(l=25, r=25, b=0, t=0), height=150)
    fig1.update_traces(showlegend=False)
    fig2 = go.Figure()
    # Generate the necessary rectangles
    thk = info['dark_thk'] * 1e3
    y0, y1 = 1, 2
    # Background rectangle
    fig2.add_shape(type='rect', x0=0, y0=y0, x1=20, y1=y1, line=dict(width=0), fillcolor="navy")
    fig2.add_vrect(x0=10 - thk / 2, x1=10 + thk / 2, fillcolor="DarkOrange", opacity=0.5, layer="above", line_width=0)
    fig2.update_xaxes(range=[0, 20])
    fig2.update_yaxes(range=[0, 1])
    fig2.update_layout(margin=dict(l=25, r=25, b=0, t=0),height=150)
    fig2.update_traces(showlegend=False)

    darkJSON1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    darkJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    return darkJSON1, darkJSON2

def signal_model_dark(v,thk,te):
    return 0


def generate_bright_signal_curves(n,tr,fa):
    theta = fa * np.pi / 180
    # Generate a segment for each TR
    tmodel = np.linspace(0, tr, 100)
    Mxy_list = []
    Mz_list = []
    t_list = []
    last_mz = 1
    for rep in range(n):
        Mz = (last_mz*np.cos(theta) - M0)*np.exp(-tmodel/T1_BLOOD) + M0
        Mxy = last_mz * np.sin(theta)*np.exp(-tmodel/T2s_BLOOD)
        Mxy_list.append(Mxy)
        Mz_list.append(Mz)
        t_list.append(tmodel + tr*rep)
        last_mz = Mz[-1]

    return Mxy_list, Mz_list, t_list


def signal_model_bright(v,thk,tr,fa):
    # v [m/s]
    # thk [m]
    # tr [s]
    # fa [deg]
    # Simulate up to the nth pulse
    theta = fa * np.pi / 180
    has_partial = False

    d = v*tr
    num_pulse_to_ss = int(np.ceil(thk/d))
    num_full_slices = int(np.floor(thk/d))
    full_frac= d/thk # full slice fraction
    part_frac = 1 - num_full_slices * full_frac # Partial slice fraction

    signals = (num_pulse_to_ss)*[0]

    # Full part
    for n in range(num_full_slices):
        # Find the proportions and number of pulses applied to each
        # Apply signal equation to find total signal
        signals[n] = signal_nonSS(n, T1_BLOOD,tr,theta)

    # Partial
    if num_pulse_to_ss > num_full_slices:
        has_partial = True
        signals[num_pulse_to_ss - 1] = signal_nonSS(num_pulse_to_ss, T1_BLOOD,tr,theta)

    signals = np.array(signals)
    return signals, has_partial, full_frac, part_frac

def signal_nonSS(Nrf,t1,tr,theta): # Fa in radians, theta in degrees
    E1 = np.exp(-tr/t1)
    E2 = np.exp(-5e-3/T2s_BLOOD)
    q = E1*np.cos(theta)
    Mze = M0*(1-E1)/(1-q)
    signal = (Mze + (q**(Nrf-1))*(M0-Mze))*np.sin(theta)*E2
    return signal

def signal_SE(t2,t2s,te):
    signal_both = np.exp(-te/t2)
    signal_90only = np.exp(-te/t2s)
    signal_180only = 0
    return [signal_both, signal_90only, signal_180only]

if __name__ == "__main__":
    # signals, has_partial,ff,pf = signal_model_bright(1.2e-3,10e-3,1,30)
    # print(signals)
    # print(has_partial)
    # print(ff)
    # print(pf)
    #
    info = {'flow_speed':5e-3, 'bright_thk':10e-3,'bright_tr':1,'bright_fa':30}
    j1, j2 = game4_worker_simulation('bright',info)

