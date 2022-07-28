import numpy as np
import plotly.graph_objects as go
import plotly
import plotly.express as px
from scipy.io import loadmat
import json

#TODO fix brain upside donw thing

def game3_worker(TR,TE,FA):
    """Generate brainweb brain image using sequence parameters

    Parameters
    ----------
    TR : float
        Repetition time [seconds]
    TE : float
        Echo time [seconds]
    FA : float
        Flip angle [degrees]

    Returns
    -------
    graphJSON_image : str
        JSON string of the brain image
    graphJSON_bar : str
        JSON string of the signal bars

    """
    graphJSON_image = get_image_json(TR,TE,FA)
    graphJSON_bar = get_bargraph_json(TR,TE,FA, ['csf','wm','gm'])# Shows three tissue types
    # All possible tissue types:
    # ['bkg','csf','gm','wm','fat','muscle/skin','skin','skull','glial','connective']

    return graphJSON_image, graphJSON_bar

def weighing_options(option):
    """Generate sequence parameters for different qualitative scans

    Parameters
    ----------
    option : str
        Sequence type; the following options are enabled:
            'PDw' : proton density weighted (long TR, short TE, FA = 90 deg)
            'T1w' : T1 weighted (medium TR, short TE, FA = 90 deg)
            'T2w' : T2 weighted (long TR, medium TE, FA = 90 deg)

    Returns
    -------
    TR : float
        Repetition time in [seconds]
    TE : float
        Echo time in [seconds]
    FA : float
        Flip angle in [degrees]
    """

    TR, TE, FA = 0,0,0
    if option == 'PDw':
        TR = 4000e-3
        TE = 10e-3
        FA = 90
    elif option == 'T1w':
        TR = 500e-3
        TE = 10e-3
        FA = 90
    elif option == 'T2w':
        TR = 4000e-3
        TE = 50e-3
        FA = 90

    return TR, TE, FA

def signal_model(PD,T1,T2,TR,TE,FA):
    """Signal model for a spoiled GRE sequence

    Parameters
    ----------
    PD : float
        Proton density of tissue (arbitrary units; use of range 0 - 1 recommended)
    T1 : float
        T1 value of tissue in [seconds]
    T2 : float
        T2 value of tissue in [seconds]
    TR : float
        Repetition time of sequence in [seconds]
    TE : float
        Echo time of sequence in [seconds]
    FA : float
        Flip angle of sequence in [degrees]

    Returns
    -------
    S : float
        Signal level
    """

    if np.mod(FA,360) == 0:
        return 0
    theta = FA * np.pi / 180
    E1 = np.exp(-TR/T1) if T2 != 0 else 1
    E2 = np.exp(-TE/T2) if T1 != 0 else 1
    S = PD * E2 * np.sin(theta) * (1-E1) / (1-np.cos(theta)*E1)

    return S

def get_image_json(TR,TE,FA):
    """Gets JSON string of Brainweb image based on sequence parameters

    Parameters
    ----------
    TR : float
        Repetition time in [seconds]
    TE : float
        Echo time in [seconds]
    FA : float
        Flip angle in [degrees]

    Returns
    -------
    graphJSON : str
        JSON string for Plotly.js
    """

    # Load brainweb model
    brainweb = loadmat('static/data/bw.mat')
    type_slice = brainweb['typemap'][:,:,87]
    # Show image
    px.imshow(type_slice)
    mr_image = np.zeros(type_slice.shape)
    params = brainweb['params']
    for type_ind in range(10):
        mr_image[type_slice == type_ind] = \
            signal_model(params[type_ind,3], params[type_ind,0]/1e3, params[type_ind,1]/1e3,
                         TR, TE, FA)
    mr_image = np.transpose(mr_image)
    # Generate image
    fig = px.imshow(mr_image, binary_string=True)
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)

    #fig.show()

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def get_bargraph_json(TR,TE,FA,tissue_names):
    """Generate bar plot JSON given sequence parameters and tissue types to plot

    Parameters
    ----------
    TR : float
        Repetition time in [seconds]
    TE : float
        Echo time in [seconds]
    FA : float
        Flip angle in [degrees]
    tissue_names : list
        List of tissue types to display:
        {'bkg','csf','gm','wm','fat','muscle/skin','skin','skull','glial','connective'}

    Returns
    -------
    graphJSON : str
        JSON string of bar plot of relative tissue signals for Plotly.js
    """

    full_names = ['Background','CSF','GM','WM','Fat',
                  'Muscle/skin', 'Skin', 'Skull', 'Glia','Connective Tissue']

    brainweb = loadmat('static/data/bw.mat')
    p = brainweb['params']
    names = [nl[0] for nl in brainweb['names'][0]]
    names_for_plot = [full_names[u] for u in [names.index(name) for name in tissue_names]]

    pdict = {names[i]:p[i] for i in range(len(names))}
    signals = [signal_model(pdict[t][3], pdict[t][0]/1e3, pdict[t][1]/1e3,TR,TE,FA) for t in tissue_names]

    # Plot
    fig = go.Figure(go.Bar(x=names_for_plot,y=signals,marker=dict(color=np.arange(len(names)),colorscale="Viridis")))
    fig.update_layout(xaxis=dict(tickfont=dict(size=48)),yaxis=dict(tickfont=dict(size=48)))

    #fig.show()

    graphJSON = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

if __name__ == '__main__':
    # Example usage
    # j1, j2 are to be passed into render_template()



    j1, j2 = game3_worker(TR=0.5,TE=0.05,FA=90)



