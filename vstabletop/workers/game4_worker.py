import numpy as np
from plotly import graph_objects as go
import plotly
import plotly.express as px
import json
from virtualscanner.server.simulation.bloch.spingroup_ps_t2star import SpinGroupT2star
from vstabletop.workers.phantom_worker import load_game4_phantom
from scipy.io import savemat
# Constants (approximate 1.5T values ~ Spees et al., 2001, MRM)
# T1_BLOOD = 2000e-3 # T1 = 2000 ms
# T2_BLOOD = 200e-3 # T2 = 200 ms
# T2s_BLOOD = T2_BLOOD / 6  # Roughly the same ratio as CSF in the Brainweb model
M0 = 1
T2S_RATIO =  1/10
BRIGHT_TE = 5e-3

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
    image = simulate_flow_image(mode,info)
    # Normalize?

    #fig = go.Figure(go.Heatmap(z=np.squeeze(image), colorscale='gray',zmin=np.min(image), zmax=np.max(image), showscale=True))
    fig = go.Figure(go.Heatmap(z=np.squeeze(image),colorscale='gray',zmin=0,zmax=1,showscale=True))
    fig.update_traces(showlegend=False)
    fig.update_layout(updatemenus=[dict(type="buttons",direction="down",
                                         buttons=list([
                                             dict(
                                                 args=[{"zmin": 0, "zmax":1}],
                                                 label="Full range",
                                                 method="restyle"
                                             ),
                                             dict(
                                                 args=[{"zmin":np.min(image),"zmax":np.max(image)}],
                                                 label="Normalized",
                                                 method="restyle"
                                             )
                                         ]),
                                        pad={"r":0,"t":15},
                                        showactive=True,
                                        x=0.05,
                                        xanchor="left",
                                        y=1.1,
                                        yanchor="top"

                                        )],
                      yaxis=dict(scaleanchor='x'),
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
    flow_speed = (info['flow_speed']/100) * 20e-3
    thk = info['bright_thk']*1e-3
    tr = info['bright_tr']*1e-3
    te = info['bright_te']*1e-3
    fa = info['bright_fa']
    t1 = info['T1']*1e-3
    t2s = info['T2']*1e-3* T2S_RATIO

    signals, has_partial, ff, pf = signal_model_bright(flow_speed,thk,tr,te,fa,t1,t2s)

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
    else:
        # Load & unit-convert parameters
        flow_speed = (info['flow_speed'] / 100) * 20e-3

        if not info['flow_on']:
            flow_speed = 0
            print('Flow is off!')

        thk = info['thk'] * 1e-3
        tr = info['tr'] * 1e-3
        te = info['te'] * 1e-3
        fa = info['fa']
        theta = fa * np.pi / 180
        t1 = info['T1'] * 1e-3
        t2 = info['T2'] * 1e-3
        t2s = t2 * T2S_RATIO

        # Load phantom
        phantom_dict = load_game4_phantom(T1=1000, T2=200, T2s=50, speed=3)

        if mode == "bright":
            print('simulating bright image')
            signals, has_partial, ff, pf = signal_model_bright(flow_speed,thk,tr,te,fa,t1,t2s)
            fraction_list = ff * np.ones(signals.shape)
            if has_partial:
                fraction_list[-1] = pf

            flow_signal = sum(signals * fraction_list)
            static_signal = signal_SS(t1,t2s,tr,te,theta)

            if flow_speed == 0:
                flow_signal = static_signal

        elif mode == "dark":
            print('simulating dark image')
            d, fraction, alpha1, alpha2, beta = signal_model_dark(flow_speed,thk,te,t2,t2s)

            flow_signal = beta * fraction + alpha2 * (1-fraction)
            static_signal = beta


        else:
            raise ValueError("Unsupported mode. Use one of {'empty','bright','dark'}")

        print('signals...')
        print('static:', static_signal)
        print('flow:', flow_signal)
        image = phantom_dict['static'] * static_signal + phantom_dict['flow'] * flow_signal

    savemat('simulated_image_game4.mat',{'image':image})

    return image

def plot_bright_signals(info, signal_partitioned_list, signal_total_list, fraction_list, Mxy_list, Mz_list, t_list):
    te_ms = info['bright_te']
    fig1 = go.Figure()

    for u in range(len(t_list)):
        times =  np.array(t_list[u])*1e3 # Convert to ms
        te_ind = int(np.round(te_ms / (times[1]-times[0])))


        if u == 0:
            namez = "Mz"
            namexy = "Mxy"
            namerf = "Pulse"
            namete = "Echo time"
            namesignal = "Signal"
        else:
            namez=""
            namexy=""
            namerf = ""
            namete = ""
            namesignal = ""
        # RF pulse
        fig1.add_trace(go.Scatter(x=2*[times[0]],y=[0,3],mode="lines",line=dict(width=5,color="orange"),name=namerf))
        fig1.add_trace(go.Scatter(x=times, y=Mz_list[u], mode='lines',line=dict(width=3,color='navy'),name=namez))
        fig1.add_trace(go.Scatter(x=times, y=Mxy_list[u], mode='lines', line=dict(width=3,color='green'),name=namexy))
        fig1.add_trace(go.Scatter(x=2*[times[0]+te_ms],y=[0,3],mode="lines",line=dict(width=1,color='gray'),name=namete))
        fig1.add_trace(go.Scatter(x=[times[te_ind]],y=[Mxy_list[u][te_ind]],mode="markers",
                                  marker=dict(size=[8],color="aquamarine",line_color="green"),name=namesignal))

    labels_to_show_in_legend = ["Mz", "Mxy",'Pulse',"Echo time","Signal"]
    for trace in fig1['data']:
        if (not trace['name'] in labels_to_show_in_legend):
            trace['showlegend'] = False

    fig1.update_xaxes(range=[t_list[0][0]*1e3,t_list[-1][-1]*1e3],title="Time (ms)")
    fig1.update_yaxes(range=[0,1])

    fig1.update_layout(margin=dict(l=0,r=0,b=0,t=0),height=150)
    #fig1.update_traces(showlegend=False)


    # Figure out: flow diagram
    fig2 = go.Figure()
    # Generate the necessary rectangles
    thk = info['bright_thk']
    y0, y1, yc = 1,2,1.5
    # Slice rectangle
    fig2.add_vline(x=10+thk/2,line_width=2.5,line_dash='dot',line_color="goldenrod")
    fig2.add_trace(go.Scatter(x=2*[10-thk/2],y=[0,3],mode="lines",line=dict(width=2.5,dash='dot',color="goldenrod"),name="Slice"))
    fig2.add_vrect(x0=10-thk/2, x1=10+thk/2, fillcolor="goldenrod",opacity=0.5,layer="below",line_width=0)
    # Flow rectangle
    fig2.add_shape(type='rect',x0=0,y0=y0,x1=20,y1=y1,line=dict(width=0),fillcolor="black",layer="below")

    # Signal rectangles
    pos = 10 - thk / 2

    if fraction_list[-1] != fraction_list[0]:
        n_rect = len(fraction_list)
    else:
        n_rect = len(fraction_list) + 1

    d = thk*fraction_list[0]

    traces = get_bright_flow_plot_traces(n_rect,d,thk, signal_partitioned_list[-1])
    traces[0].visible=True
    traces[1].visible=True
    [fig2.add_trace(trace) for trace in traces]
    print(f'total number of rectangle traces: {len(traces)}')
    print(f'total number of traces: {len(fig2.data)}')

    # for ind, fraction in enumerate(fraction_list):
    #     signal = signal_partitioned_list[-1][ind]
    #     xleft = pos
    #     xright = pos + thk * fraction
    #     xcenter = 0.5*(xleft + xright)
    #     fig2.add_trace(go.Scatter(x=[xleft,xright,xright,xleft],y=[y0,y0,y1,y1],
    #                               mode="lines",line=dict(width=0),fill="toself",
    #                               fillcolor=color_map(signal),showlegend=False))
    #     if ind == 0:
    #         showtext = True
    #     else:
    #         showtext = False
    #     fig2.add_trace(go.Scatter(x=[xcenter],y=[yc],mode="text",name="# pulses",text=ind+1,textfont=dict(family='Arial Black',size=15,color="chocolate"),
    #                               textposition="middle center",showlegend=showtext))
    #     pos = xright

    # flow figure!
    fig2.update_xaxes(range=[0,20],title="Distance (mm)",showgrid=False)
    fig2.update_yaxes(range=[0,3],visible=False,showgrid=False)
    fig2.update_layout(margin=dict(l=25,r=25,b=100,t=0),height=150)

    print(signal_partitioned_list)



    # Sliders
    steps = []

    #time_names = ["0-", "0+", "(TE/2)-", "(TE/2)+", "TE"]
    #time_names = [f"{m}TR" for m in range(1,n_rect+1)]
    time_names = [0]
    for m in range(1,n_rect+1):
        time_names += [f'RF{m}',f'TR{m}']
    time_names.append(f'RF{n_rect+1}')

    n_traces = n_rect + 1

    for i in range(len(time_names)):
        step = dict(
            method="update",
            args=[{"visible": [False] * len(fig2.data)}],
            label=time_names[i]
        )
        step["args"][0]["visible"][0] = True
        step["args"][0]["visible"][1+i*2*n_traces:1+(i+1)*2*n_traces] = 2*n_traces*[True]
        # Turn on the 6 traces for the current time point
        steps.append(step)

    sliders = [dict(
        active=0,
        currentvalue={"visible": False},
        pad={"t": 50},
        steps=steps,
        transition={"duration": 100, "easing": "cubic-in-out"}
    )]

    fig2.update_layout(sliders=sliders)



    #fig2.update_traces(showlegend=False)

    brightJSON1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    brightJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    return brightJSON1, brightJSON2

def plot_dark_signals(info,d,fraction,alpha1,alpha2,beta, Mxy_list_both, Mxy_list_90, Mxy_list_180, t_list):
    te = info['dark_te']
    dist = d*1e3

    # Top figure
    fig1 = go.Figure()
    # Add in 90 and 180 vertical lines
    fig1.add_trace(go.Scatter(visible=True,x=2*[0], y=[-0.1,1], mode='lines', line=dict(width=5, color='red'),name="RF 90")) # 90
    fig1.add_trace(go.Scatter(visible=True,x=2*[te/2], y=[0,1], mode='lines', line=dict(width=5, color='orange'),name="RF 180")) # 180
    # Add TE line
    fig1.add_trace(go.Scatter(visible=True,x=2*[te], y=[0,3], mode="lines", line=dict(width=3, color='gray'), name='TE'))

    all_times = 1e3*np.array(t_list).flatten()

    flatten_lambda = lambda lst: list(item for sublist in lst for item in sublist)

    all_times = 1e3*np.array(flatten_lambda(t_list))
    all_Mxy_both = np.absolute(np.array(flatten_lambda(Mxy_list_both)))
    all_Mxy_90 = np.absolute(np.array(flatten_lambda(Mxy_list_90)))
    all_Mxy_180 = np.absolute(np.array(flatten_lambda(Mxy_list_180)))


    # TODO
    fig1.add_trace(go.Scatter(visible=True,x=all_times, y=all_Mxy_both, mode='lines', line=dict(width=3, color='green'),name="Both"))
    fig1.add_trace(go.Scatter(visible=True,x=all_times, y=all_Mxy_90, mode='lines', line=dict(width=3, color='darkcyan'),name="90 only"))
    fig1.add_trace(go.Scatter(visible=True,x=all_times, y=all_Mxy_180, mode='lines', line=dict(width=3, color='greenyellow'),name="180 only"))

    te_ind = np.where(all_times==(np.sign(all_times-te)*np.min(np.absolute(all_times - te)) + te))[0][0]

    # Add signal dots
    fig1.add_trace(go.Scatter(visible=True,x=[all_times[te_ind]], y=[all_Mxy_both[te_ind]], mode="markers",
                              marker=dict(size=[8], color="aquamarine", line_color="green"), name="Signal",showlegend=True))
    # Add signal dots
    fig1.add_trace(go.Scatter(visible=True,x=[all_times[te_ind]], y=[all_Mxy_90[te_ind]], mode="markers",
                              marker=dict(size=[8], color="aquamarine", line_color="green"), name="",showlegend=False))
    # Add signal dots
    fig1.add_trace(go.Scatter(visible=True,x=[all_times[te_ind]], y=[all_Mxy_180[te_ind]], mode="markers",
                             marker=dict(size=[8], color="aquamarine", line_color="green"), name="",showlegend=False))

    # Styling
    fig1.update_xaxes(range=[-0.1*te, 1.5*te],title="Time (ms)")
    fig1.update_yaxes(range=[-0.1,1],title='Signal')
    fig1.update_layout(margin=dict(l=100, r=100, b=0, t=0),height=150)


    # Dropdown button
    fig1.update_layout(
        updatemenus=[
            dict(
                buttons=list([
                    dict(
                        args=[{'visible': 9 * [True],'showlegend':[True,True,True,True,True,True,True,False,False]}],
                        label="all",
                        method="update"
                    ),
                    dict(
                        args=[{"visible": [True,True,True,True,False,False,True,False,False],'showlegend':[True,True,True,True,False,False,True,False,False]}],
                        label="90 + 180",
                        method="update"
                    ),
                    dict(
                        args=[{"visible": [True,False,True,False,True,False,False,True,False],'showlegend':[True,True,True,False,True,False,False,True,False]}],
                        label="90 only",
                        method="update"
                    ),
                    dict(
                        args=[{"visible": [False,True,True,False,False,True,False,False,True],'showlegend':[True,True,True,False,False,True,False,False,True]}],
                        label="180 only",
                        method="update"
                    )
                ]),
                direction="down",
                pad={"r":15,"t":0},
                showactive=True,
                x=0,
                xanchor="right",
                y=1,
                yanchor="bottom"
            )
            # dict(
            #     type="buttons",
            #     direction="right",
            #      pad={"l":5,"t":0,"b":2},
            #     showactive=True,
            #     x=0,
            #     xanchor="left",
            #     y=1,
            #     yanchor="bottom",
            #     buttons=[
            #         {
            #             "args":[None,{'frame':{"duration":10,"redraw":False},"fromcurrent":True,"transition":{"duration":5,"easing":"linear"}}],
            #             "label": "Play",
            #             "method": "animate"
            #         },
            #         {
            #             "args":[[None],{"frame":{"duration":0,"redraw":False},
            #                             "mode": "immediate",
            #                             "transition": {"duration":0}}],
            #             "label":"Pause",
            #             "method":"animate"
            #         }
            #     ]
            # )
        ]
    )

    # Frames
    # data_acc_all = []
    # for ind, t in enumerate(all_times):
    #     data_acc = []
    #     data_acc.append(go.Scatter(x=all_times[:ind],y=all_Mxy_both[:ind],mode="lines", line=dict(width=3, color='green')))
    #     data_acc.append(go.Scatter(x=all_times[:ind],y=all_Mxy_90[:ind],mode="lines", line=dict(width=3, color='darkcyan')))
    #     data_acc.append(go.Scatter(x=all_times[:ind],y=all_Mxy_180[:ind],mode="lines", line=dict(width=3, color='greenyellow')))
    #     if all_times[ind] >= 0:
    #         data_acc.append(go.Scatter(visible=True,x=2*[0], y=[-0.1,1], mode='lines', line=dict(width=5, color='red')))
    #     if all_times[ind] >= te/2:
    #         data_acc.append(go.Scatter(visible=True, x=2 * [te / 2], y=[0, 1], mode='lines', line=dict(width=5, color='orange')))
    #     if all_times[ind] >= te:
    #         data_acc.append(go.Scatter(visible=True,x=2*[te], y=[0,3], mode="lines", line=dict(width=3, color='gray')))
    #     data_acc_all.append(data_acc)
    # fig1.frames = [go.Frame(data=data_acc) for data_acc in data_acc_all]


    # Bottom figure
    fig2 = go.Figure()
    # Generate the necessary rectangles
    thk = info['dark_thk']
    y0, y1, yc = 1, 2, 1.5

    # Flow rectangle
    fig2.add_trace(go.Scatter(x=[-1,2*dist+1.5*thk,2*dist+1.5*thk,-1],y=[y0,y0,y1,y1],mode="lines",
                              line=dict(width=0),fill="toself",fillcolor="black",showlegend=False))

    # Partial rectangle
    # Slice rectangle
    fig2.add_vrect(x0=0, x1=thk, fillcolor="goldenrod",opacity=0.5,layer="below",line_width=0)

    # Flow rectangles
    # There are 5 timepoints
    # Use buttons to control
    traces = []
    # Time point 3

    # Signals
    signals=[[0,0,0],[0,1,0],[0,alpha1,0],[alpha1,alpha1,0],[beta,alpha2,0]]

    if dist < thk:
        # Time point 1 (0-)
        seg_both = [0,0]
        seg_90 = [0,0]
        seg_180 = [0,0]
        signal_both, signal_90, signal_180 = tuple(signals[0])
        [traces.append(trace) for trace in get_dark_flow_plot_traces(seg_both, seg_90, seg_180, signal_both, signal_90, signal_180)]

        # Time point 2 (0+)
        seg_both = [0,0]
        seg_90 = [0,thk]
        seg_180 = [0,0]
        signal_both, signal_90, signal_180 = tuple(signals[1])
        [traces.append(trace) for trace in get_dark_flow_plot_traces(seg_both, seg_90, seg_180, signal_both, signal_90, signal_180)]

        # Time point 3 ((TE/2)-)
        seg_both = [0,0]
        seg_90 = [dist, thk+dist]
        seg_180=[0,0]
        signal_both, signal_90, signal_180 = tuple(signals[2])
        [traces.append(trace) for trace in get_dark_flow_plot_traces(seg_both, seg_90, seg_180, signal_both, signal_90, signal_180)]

        # Time point 4 ((TE/2)+)
        seg_both = [dist, thk]
        seg_90 = [thk, dist + thk]
        seg_180 = [0, dist]
        signal_both, signal_90, signal_180 = tuple(signals[3])
        [traces.append(trace) for trace in get_dark_flow_plot_traces(seg_both, seg_90, seg_180, signal_both, signal_90, signal_180)]

        # Time point 5 (TE)
        seg_both = [2*dist,dist+thk]
        seg_90 = [dist+thk,2*dist+thk]
        seg_180 = [dist,2*dist]
        signal_both, signal_90, signal_180 = tuple(signals[4])
        [traces.append(trace) for trace in get_dark_flow_plot_traces(seg_both, seg_90, seg_180, signal_both, signal_90, signal_180)]


    else:
        # Time point 1 (0-)
        seg_both = [0, 0]
        seg_90 = [0, 0]
        seg_180 = [0, 0]
        signal_both, signal_90, signal_180 = tuple(signals[0])
        [traces.append(trace) for trace in get_dark_flow_plot_traces(seg_both, seg_90, seg_180, signal_both, signal_90, signal_180)]

        # Time point 2 (0+)
        seg_both=[0,0]
        seg_90 = [0,thk]
        seg_180 = [0,0]
        signal_both, signal_90, signal_180 = tuple(signals[1])
        [traces.append(trace) for trace in get_dark_flow_plot_traces(seg_both, seg_90, seg_180, signal_both, signal_90, signal_180)]

        # Time point 3 ((TE/2)-)
        seg_both = [0, 0]
        seg_90 = [dist, dist+thk]
        seg_180 = [0, 0]
        signal_both, signal_90, signal_180 = tuple(signals[2])
        [traces.append(trace) for trace in get_dark_flow_plot_traces(seg_both, seg_90, seg_180, signal_both, signal_90, signal_180)]

        # Time point 4 ((TE/2)+)
        seg_both = [0,0]
        seg_90 = [dist,dist+thk]
        seg_180 = [0,thk]
        signal_both, signal_90, signal_180 = tuple(signals[3])
        [traces.append(trace) for trace in get_dark_flow_plot_traces(seg_both, seg_90, seg_180, signal_both, signal_90, signal_180)]

        # Time point 5 (TE)
        seg_both = [0, 0]
        seg_90 = [2*dist,2*dist+thk]
        seg_180 = [dist,dist+thk]
        signal_both, signal_90, signal_180 = tuple(signals[4])
        [traces.append(trace) for trace in get_dark_flow_plot_traces(seg_both, seg_90, seg_180, signal_both, signal_90, signal_180)]

    for trace in traces:
        fig2.add_trace(trace)


    # Slice boundaries
    fig2.add_trace(go.Scatter(x=2*[0],y=[0,3],mode="lines",line=dict(width=2.5,dash='dot',color='goldenrod'),name='Slice',showlegend=False))
    fig2.add_trace(go.Scatter(x=2*[thk],y=[0,3],mode="lines",line=dict(width=2.5,dash='dot',color='goldenrod'),name='Slice',showlegend=True))

    # Figure styling
    fig2.update_xaxes(range=[-1,2*dist+1.5*thk],title="Distance (mm)",showgrid=False)
    fig2.update_yaxes(range=[0,3],visible=False,showgrid=False)
    #fig2.update_traces(showlegend=False)

    # Slider
    steps = []

    time_names = ["0-","0+","(TE/2)-","(TE/2)+","TE"]
    for i in range(5):
        step = dict(
            method="update",
            args=[{"visible": [False]*len(fig2.data)}],
            label=time_names[i]
        )
        step["args"][0]["visible"][0] = True
        step["args"][0]["visible"][-1:-3:-1] = [True,True]

        step["args"][0]["visible"][6*i+1:6*i+7] = 6*[True]
        # Turn on the 6 traces for the current time point
        steps.append(step)


    sliders = [dict(
        active=0,
        currentvalue={"visible": False},
        pad={"t":50},
        steps=steps,
        transition={"duration":100,"easing":"cubic-in-out"}
    )]
    fig2.update_layout(sliders=sliders)
    fig2.update_layout(margin=dict(l=25, r=25, b=100, t=0),height=200)




    # Convert to JSON
    darkJSON1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    darkJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    return darkJSON1, darkJSON2

def get_bright_flow_plot_traces(n_rect,d,thk,signals):
    # n_rect: total number of signal rectangles (the last one will be invisible if thk/d is an integer)
    # signal values for 1, 2, 3, ... n_ss RF pulses
    traces = []
    # For each frame, we make n_rect + 1 rectangular traces and their associated text labels
    # This makes (n_rect + 1)*2 - 1 labels (the zero / void doesn't have a label; any labels of void rectangles are made invisible)
    n_frames = 2*(n_rect + 1)
    #for fr in range(n_frames):

    if len(signals) < n_rect:
        signals = np.append(signals, 0)
    signals = np.concatenate(([0], signals))

    print(f'n_rect is {n_rect}')

    for fr in range(n_frames):
        if fr >= 2*n_rect:
            fr = fr - 2
        # Calculate divisions
        divs = thk*np.ones(n_rect)
        if (fr%2) == 0: # First set
            print('even',fr)
            divs[0:int(fr/2)] = d*np.arange(1,int(fr/2)+1)
        else:
            print('odd',fr)
            divs[0:int((fr+1)/2)] = d*np.arange(0,int((fr+1)/2))
        print(divs)

        print("Final signals: ",signals )

        # For each rectangle
        left = 0
        for u in range(n_rect+1):
            xleft = left
            if u < n_rect:
                xright = divs[u]
            else:
                xright = thk
            left = xright

            print('xleft and xright before centering',xleft,xright)

            xleft += 10 - thk / 2
            xright += 10 - thk / 2
            xcenter = 0.5*(xleft + xright)

            traces.append(go.Scatter(visible=False,x=[xleft, xright, xright, xleft], y=[1, 1, 2, 2],
                       mode="lines", line=dict(width=0), fill="toself",
                       fillcolor=color_map(signals[u]), showlegend=False))

            traces.append(go.Scatter(visible=False,x=[xcenter],y=[1.5],mode="text",name="# pulses",
                                     text=(u if bool(xleft!=xright) else ""),textfont=dict(family='Arial Black',size=15,color="chocolate"),
                                     textposition="middle center",showlegend=False))



    return traces



def get_dark_flow_plot_traces(seg_both,seg_90,seg_180,signal_both,signal_90,signal_180):
    traces = []
    y_vec = [1,1,2,2]
    yc = 1.5

    text_both = "90+180" if seg_both[0] != seg_both[1] else ""
    text_90 = "90 only" if seg_90[0] != seg_90[1] else ""
    text_180 = "180 only" if seg_180[0] != seg_180[1] else ""


    # 180 + 90
    traces.append(go.Scatter(visible=False,x=[seg_both[0], seg_both[1], seg_both[1], seg_both[0]], y=y_vec, mode="lines", line=dict(width=0),
                              fill="toself", fillcolor=color_map(signal_both), showlegend=False))
    traces.append(go.Scatter(visible=False,x=[np.mean(seg_both)], y=[yc], mode="text", name="history", text=text_both,
                              textfont=dict(family='Arial Black', size=15, color="green"),
                              textposition="middle center", showlegend=False))

    # 90 only
    traces.append(go.Scatter(visible=False,x=[seg_90[0], seg_90[1], seg_90[1], seg_90[0]], y=y_vec, mode="lines", line=dict(width=0),
                              fill="toself", fillcolor=color_map(signal_90), showlegend=False))
    traces.append(go.Scatter(visible=False,x=[np.mean(seg_90)], y=[yc], mode="text", name="history", text=text_90,
                              textfont=dict(family='Arial Black', size=15, color="darkcyan"),
                              textposition="middle center", showlegend=False))

    # 180 only
    traces.append(go.Scatter(visible=False,x=[seg_180[0],seg_180[1],seg_180[1],seg_180[0]], y=y_vec, mode="lines", line=dict(width=0), fill="toself",
                              fillcolor=color_map(signal_180), showlegend=False))
    traces.append(go.Scatter(visible=False,x=[np.mean(seg_180)], y=[yc], mode="text", name="history", text=text_180,
                              textfont=dict(family='Arial Black', size=15, color="greenyellow"),
                              textposition="middle center", showlegend=False))


    return traces



def signal_model_dark(v,thk,te,t2,t2s):
    """
    Parameters
    ----------
    v : float
        Flow speed [m/s]
    thk : float
        Slice thickness in [m]
    te : float
        Echo time in [s]
    t2 : float
        T2 in [s]
    t2s : float
        T2* in [s]

    Returns
    -------
    d : float
        Distance travelled between 90 and 180 pulses
    fraction : float
        Fraction of slice experience both 90 and 180 pulses (0-1)
    """
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

def signal_model_bright(v,thk,tr,te,fa,t1,t2s):
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
            signals[n] = signal_nonSS(n, t1, t2s, tr, te,theta)

        # Partial
        if num_pulse_to_ss > num_full_slices:
            has_partial = True
            signals[num_pulse_to_ss - 1] = signal_nonSS(num_pulse_to_ss, t1, t2s, tr, te, theta)
    else: # Case of zero flow - simulate 10 pulses
        full_frac = 1
        part_frac = 0
        signals = [signal_nonSS(10, t1, t2s, tr, te, theta)]
        has_partial = False

    print('signals: ',signals)

    signals = np.array(signals)
    return signals, has_partial, full_frac, part_frac

def signal_nonSS(Nrf,t1,t2s,tr,te,theta): # Fa in radians, theta in degrees
    E1 = np.exp(-tr/t1)
    E2 = np.exp(-te/t2s)
    q = E1*np.cos(theta)
    Mze = M0*(1-E1)/(1-q)
    signal = (Mze + (q**(Nrf-1))*(M0-Mze))*np.sin(theta)*E2
    return signal

def signal_SS(t1,t2s,tr,te,theta):
    E1 = np.exp(-tr/t1)
    E2 = np.exp(-te/t2s)
    q = E1*np.cos(theta)
    signal = E2*np.sin(theta)*M0*(1-E1)/(1-q)
    return signal

def signal_SE(t2,t2s,te):
    signal_half_90only = np.exp(-0.5*te/t2s)
    signal_full_90only = np.exp(-te/t2s)
    signal_full_both = np.exp(-te/t2)
    return signal_half_90only, signal_full_90only, signal_full_both

def color_map(intensity):
    return f"rgb({int(179 * intensity)},{int(236 * intensity)},{int((255-139) * intensity)+139})"

if __name__ == "__main__":
    # signals, has_partial,ff,pf = signal_model_bright(1.2e-3,10e-3,1,30)
    # print(signals)
    # print(has_partial)
    # print(ff)
    # print(pf)
    #
    info = {'flow_speed':5e-3, 'bright_thk':10e-3,'bright_tr':1,'bright_fa':30}
    j1, j2 = game4_worker_simulation('bright',info)

