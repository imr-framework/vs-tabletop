import numpy as np
from plotly import graph_objects as go
import plotly
import plotly.express as px
import json
from virtualscanner.server.simulation.bloch.phantom import SpheresArrayPlanarPhantom
from virtualscanner.server.simulation.bloch.spingroup_ps_t2star import SpinGroupT2star

# Constants (approximate 1.5T values ~ Spees et al., 2001, MRM)
# T1_BLOOD = 2000e-3 # T1 = 2000 ms
# T2_BLOOD = 200e-3 # T2 = 200 ms
# T2s_BLOOD = T2_BLOOD / 6  # Roughly the same ratio as CSF in the Brainweb model
M0 = 1
T2S_RATIO =  1/10

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

#TODO make phantom to be stored in session
def game4_worker_phantom(info):
    t1 = info['T1']*1e-3
    t2 = info['T2']*1e-3
    t2s = t2 * T2S_RATIO
    pd = 1
    #phantom = SpheresArrayPlanarPhantom()
    phantom = 0
    return phantom


# Simulated / animted plots
def simulate_bright_plots(info):
    # Get the raw values
    flow_speed = (info['flow_speed']/100) * 20e-3
    thk = info['bright_thk']*1e-3
    tr = info['bright_tr']*1e-3
    fa = info['bright_fa']
    t1 = info['T1']*1e-3
    t2s = info['T2']*1e-3* T2S_RATIO

    signals, has_partial, ff, pf = signal_model_bright(flow_speed,thk,tr,fa,t1,t2s)

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
    if flow_speed > 0:
        Mxy_list, Mz_list, t_list = generate_bright_signal_curves(Nss,tr,fa,t1,t2s)
    else:
        Mxy_list, Mz_list, t_list = generate_bright_signal_curves(10,tr,fa,t1,t2s)

    j1, j2 = plot_bright_signals(info, signal_partitioned_list, signal_total_list, fraction_list,
                                 Mxy_list, Mz_list, t_list)
    return j1, j2

# TODO
def simulate_dark_plots(info):
    # 90, 180, 90+180 signals
    # x-axis: [0, 1.5 TE]
    # y-axis: signal strength - FID with T2* decay x 2 - [-1,1]

    te = info['dark_te']*1e-3
    v = info['flow_speed']*1e-3
    thk = info['dark_thk']*1e-3
    t1 = info['T1']*1e-3
    t2 = info['T2']*1e-3
    t2s = t2*T2S_RATIO

    d, fraction, alpha1, alpha2, beta = signal_model_dark(v,thk,te,t2,t2s)
    final_signal = fraction * beta + (1-fraction) * alpha2
    Mxy_list_both, Mxy_list_90, Mxy_list_180, t_list = generate_dark_signal_curves(te,t1,t2,t2s) # return them in segments,
    j1, j2 = plot_dark_signals(info,d,fraction,alpha1,alpha2,beta, Mxy_list_both, Mxy_list_90, Mxy_list_180, t_list)
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
    fig1.update_yaxes(range=[0,1])

    fig1.update_layout(margin=dict(l=25,r=25,b=0,t=0),height=150)
    fig1.update_traces(showlegend=False)

    fig2 = go.Figure()

    # Generate the necessary rectangles
    thk = info['bright_thk']
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
    for ind, fraction in enumerate(fraction_list):
        signal = signal_partitioned_list[-1][ind]
        xleft = pos
        xright = pos + thk * fraction
        fig2.add_shape(type='rect', x0=xleft, y0=y0, x1=xright, y1=y1, line=dict(width=0),
                       fillcolor=f"rgb({int(179 * signal)},{int(236 * signal)},{int(255 * signal)})")
        pos = xright

    # flow figure!
    fig2.update_xaxes(range=[0,20])
    fig2.update_yaxes(range=[0,3],visible=False)
    fig2.update_layout(margin=dict(l=25,r=25,b=0,t=0),height=150)
    fig2.update_traces(showlegend=False)

    brightJSON1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    brightJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    return brightJSON1, brightJSON2

def plot_dark_signals(info,d,fraction,alpha1,alpha2,beta, Mxy_list_both, Mxy_list_90, Mxy_list_180, t_list):
    te = info['dark_te']
    dist = d*1e3

    # Top figure
    fig1 = go.Figure()

    # Add in signals
    for u in range(len(t_list)):
        fig1.add_trace(go.Scatter(x=1e3*t_list[u], y=np.absolute(Mxy_list_both[u]), mode='lines', line=dict(width=3, color='green')))
        fig1.add_trace(go.Scatter(x=1e3*t_list[u], y=np.absolute(Mxy_list_90[u]), mode='lines', line=dict(width=3, color='darkcyan')))
        fig1.add_trace(go.Scatter(x=1e3*t_list[u], y=np.absolute(Mxy_list_180[u]), mode='lines', line=dict(width=3, color='greenyellow')))

    # Add in 90 and 180 vertical lines
    fig1.add_trace(go.Scatter(x=[0,0], y=[-0.1,1], mode='lines', line=dict(width=5, color='orange'))) # 90
    fig1.add_trace(go.Scatter(x=[te/2,te/2], y=[0,1], mode='lines', line=dict(width=5, color='orange'))) # 180

    fig1.update_xaxes(range=[-0.1*te, 1.5*te],title="Time (ms)")
    fig1.update_yaxes(range=[-0.1,1])
    fig1.update_layout(margin=dict(l=25, r=25, b=0, t=0), height=150)
    fig1.update_traces(showlegend=False)


    # Bottom figure
    fig2 = go.Figure()
    # Generate the necessary rectangles
    thk = info['dark_thk']
    y0, y1 = 1, 2

    # Flow rectangle
    fig2.add_shape(type='rect',x0=-1,y0=y0,x1=dist+1.5*thk,y1=y1,line=dict(width=0),fillcolor="navy")

    # Partial rectangle
    # Slice rectangle
    fig2.add_vline(x=0,line_width=2.5,line_dash='dot',line_color="goldenrod")
    fig2.add_vline(x=thk,line_width=2.5,line_dash='dot',line_color="goldenrod")
    fig2.add_vrect(x0=0, x1=thk, fillcolor="goldenrod",opacity=0.5,layer="below",line_width=0)

    # Flow rectangles
    # There are 5 timepoints
    # Use buttons to control

    # Time point 3 : s (TE/2)+
    if dist < thk:
        print(f'd: {dist}')
        # 180 only
        fig2.add_shape(type="rect",x0=0,y0=y0,x1=dist,y1=y1,line=dict(width=1),fillcolor="navy")
        # 180 + 90
        fig2.add_shape(type="rect",x0=dist,y0=y0,x1=thk,y1=y1,line=dict(width=1),fillcolor=f"rgb({int(179 * alpha1)},{int(236 * alpha1)},{int(255 * alpha1)})")
        # 90 only
        fig2.add_shape(type="rect",x0=thk,y0=y0,x1=dist+thk,y1=y1,line=dict(width=1),fillcolor=f"rgb({int(179 * alpha1)},{int(236 * alpha1)},{int(255 * alpha1)})")
    else:
        fig2.add_shape(type="rect",x0=d,y0=y0,x1=d+thk,y1=y1,line=dict(width=0),fillcolor=f"rgb({int(179 * alpha1)},{int(236 * alpha1)},{int(255 * alpha1)})")

    fig2.update_xaxes(range=[-1,dist+1.5*thk],title="Distance (mm)")
    fig2.update_yaxes(range=[0,3],visible=False)

    fig2.update_layout(margin=dict(l=25, r=25, b=0, t=0),height=150)
    fig2.update_traces(showlegend=False)

    darkJSON1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    darkJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    return darkJSON1, darkJSON2

def signal_model_dark(v,thk,te,t2,t2s):
    # Calculate distance
    d = v * te/2
    if d < thk: # Incomplete outflow
        fraction = (thk - d)/thk
    else: # Complete outflow
        fraction = 0
    alpha1, alpha2, beta = signal_SE(t2, t2s, te)

    return d, fraction, alpha1, alpha2, beta


def generate_bright_signal_curves(n,tr,fa,t1,t2s):
    theta = fa * np.pi / 180
    # Generate a segment for each TR
    tmodel = np.linspace(0, tr, 100)
    Mxy_list = []
    Mz_list = []
    t_list = []
    last_mz = 1
    for rep in range(n):
        Mz = (last_mz*np.cos(theta) - M0)*np.exp(-tmodel/t1) + M0
        Mxy = last_mz * np.sin(theta)*np.exp(-tmodel/t2s)
        Mxy_list.append(Mxy)
        Mz_list.append(Mz)
        t_list.append(tmodel + tr*rep)
        last_mz = Mz[-1]

    return Mxy_list, Mz_list, t_list


def generate_dark_signal_curves(te,t1,t2,t2s):
    # Time points simulated per TE
    ppte = 200

    Mxy_list_both = []
    Mxy_list_90 = []
    Mxy_list_180 = []
    t_list = []

    #TODO also simulate 90 only and 180 only

    # Simulate
    # sg1 - both
    sg1 = SpinGroupT2star(loc=np.array([0,0,0]),pdt1t2=(1,t1,t2),t2star=t2s,num_spins=30)
    # sg2 - first
    sg2 = SpinGroupT2star(loc=np.array([0,0,0]),pdt1t2=(1,t1,t2),t2star=t2s,num_spins=30)
    # sg3 - second
    sg3 = SpinGroupT2star(loc=np.array([0,0,0]),pdt1t2=(1,t1,t2),t2star=t2s,num_spins=30)

    # Before t = 0
    Mxy_list_both.append(np.array([0,0]))
    Mxy_list_90.append(np.array([0,0]))
    Mxy_list_180.append(np.array([0,0]))
    t_list.append(np.array([-te/10,0]))

    # Ideal 90 deg RF
    Mxy1_both = np.zeros(int(ppte/2 + 1),dtype=complex)
    Mxy1_90 = np.zeros(int(ppte/2 + 1),dtype=complex)
    Mxy1_180 = np.zeros(int(ppte/2 + 1),dtype=complex)

    sg1.apply_ideal_RF(rf_phase=0,fa=np.pi/2,f_low=-np.Inf, f_high=np.Inf,gradients=np.array([0,0,0]))
    sg2.apply_ideal_RF(rf_phase=0,fa=np.pi/2,f_low=-np.Inf, f_high=np.Inf,gradients=np.array([0,0,0]))

    # First segment: from right after 90 to just before 180
    Mxy1_both[0] = sg1.get_m_signal()
    Mxy1_90[0] = sg2.get_m_signal()
    Mxy1_180[0] = sg3.get_m_signal()

    # Apply small delay increments to collect free precession signal
    # Use 100 points
    t_list.append(np.linspace(0,te/2,int(ppte/2)))
    dt1 = t_list[1][1] -  t_list[1][0]
    for n in range(int(ppte/2)):
        # sg1.delay(dt1)
        # sg2.delay(dt1)
        # sg3.delay(dt1)
        [sg.delay(dt1) for sg in [sg1,sg2,sg3]]
        Mxy1_both[n+1] = sg1.get_m_signal()
        Mxy1_90[n+1] = sg2.get_m_signal()
        Mxy1_180[n+1] = sg3.get_m_signal()

    Mxy_list_both.append(Mxy1_both)
    Mxy_list_90.append(Mxy1_90)
    Mxy_list_180.append(Mxy1_180)

    # Ideal 180 deg RF
    Mxy2_both = np.zeros(int(ppte/4)+1,dtype=complex)
    Mxy2_90 = np.zeros(int(ppte/4)+1,dtype=complex)
    Mxy2_180 = np.zeros(int(ppte/4)+1,dtype=complex)

    sg1.apply_ideal_RF(rf_phase=np.pi/2,fa=np.pi,f_low=-np.Inf, f_high=np.Inf,gradients=np.array([0,0,0]))
    sg3.apply_ideal_RF(rf_phase=np.pi/2,fa=np.pi,f_low=-np.Inf, f_high=np.Inf,gradients=np.array([0,0,0]))

    # Second segment: from right after 180 to 3/4 TE
    Mxy2_both[0] = sg1.get_m_signal()
    Mxy2_90[0] = sg2.get_m_signal()
    Mxy2_180[0] = sg3.get_m_signal()

    # Apply small delay increments to collect free precession signal
    t_list.append(np.linspace(te/2,te*3/4,int(ppte/4)))
    dt2 = t_list[2][1] - t_list[2][0]
    for n in range(int(ppte/4)):
        [sg.delay(dt2) for sg in [sg1,sg2,sg3]]
        #sg1.delay(dt2)
        Mxy2_both[n+1] = sg1.get_m_signal()
        Mxy2_90[n+1] = sg2.get_m_signal()
        Mxy2_180[n+1] = sg3.get_m_signal()

    Mxy_list_both.append(Mxy2_both)
    Mxy_list_90.append(Mxy2_90)
    Mxy_list_180.append(Mxy2_180)

    # Third segment: from 3/4 TE to 3/2 TE
    Mxy3_both = np.zeros(int(ppte/4+ppte/2), dtype=complex)
    Mxy3_90 = np.zeros(int(ppte/4+ppte/2), dtype=complex)
    Mxy3_180 = np.zeros(int(ppte/4+ppte/2), dtype=complex)

    t_list.append(np.linspace(te*3/4,te*3/2,int(ppte/4+ppte/2)))

    dt3 = t_list[3][1] - t_list[3][0]
    for n in range(int(ppte/4+ppte/2)):
        #sg1.delay(dt3)
        Mxy3_both[n] = sg1.get_m_signal()
        Mxy3_90[n] = sg2.get_m_signal()
        Mxy3_180[n] = sg3.get_m_signal()
        [sg.delay(dt3) for sg in [sg1,sg2,sg3]]


    Mxy_list_both.append(Mxy3_both)
    Mxy_list_90.append(Mxy3_90)
    Mxy_list_180.append(Mxy3_180)

    return Mxy_list_both, Mxy_list_90, Mxy_list_180, t_list

def signal_model_bright(v,thk,tr,fa,t1,t2s):
    # v [m/s]
    # thk [m]
    # tr [s]
    # fa [deg]
    # Simulate up to the nth pulse

    theta = fa * np.pi / 180

    if v > 0:
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
            signals[n] = signal_nonSS(n, t1, t2s, tr,theta)

        # Partial
        if num_pulse_to_ss > num_full_slices:
            has_partial = True
            signals[num_pulse_to_ss - 1] = signal_nonSS(num_pulse_to_ss, t1, t2s, tr,theta)
    else: # Case of zero flow - simulate 10 pulses
        full_frac = 1
        part_frac = 0
        signals = [signal_nonSS(10,t1, t2s, tr, theta)]
        has_partial = False

    print('signals: ',signals)

    signals = np.array(signals)
    return signals, has_partial, full_frac, part_frac

def signal_nonSS(Nrf,t1,t2s,tr,theta): # Fa in radians, theta in degrees
    E1 = np.exp(-tr/t1)
    E2 = np.exp(-5e-3/t2s)
    q = E1*np.cos(theta)
    Mze = M0*(1-E1)/(1-q)
    signal = (Mze + (q**(Nrf-1))*(M0-Mze))*np.sin(theta)*E2
    return signal

def signal_SE(t2,t2s,te):
    signal_half_90only = np.exp(-0.5*te/t2s)
    signal_full_90only = np.exp(-te/t2s)
    signal_full_both = np.exp(-te/t2)
    return signal_half_90only, signal_full_90only, signal_full_both


if __name__ == "__main__":
    # signals, has_partial,ff,pf = signal_model_bright(1.2e-3,10e-3,1,30)
    # print(signals)
    # print(has_partial)
    # print(ff)
    # print(pf)
    #
    info = {'flow_speed':5e-3, 'bright_thk':10e-3,'bright_tr':1,'bright_fa':30}
    j1, j2 = game4_worker_simulation('bright',info)

