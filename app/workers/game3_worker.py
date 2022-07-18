import numpy as np
import plotly.graph_objects as go
import plotly
import plotly.express as px
from scipy.io import loadmat
import json

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
    graphJSON_bar = get_bargraph_json(TR,TE,FA, ['csf','wm','gm'])

    return graphJSON_image, graphJSON_bar

# TODO @Rishi Use this function below to extract TR, TE, FA for each weighing option
def weighing_options(option):
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
    if np.mod(FA,360) == 0:
        return 0

    theta = FA * np.pi / 180
    E1 = np.exp(-TR/T1) if T2 != 0 else 1
    E2 = np.exp(-TE/T2) if T1 != 0 else 1


    return PD * E2 * np.sin(theta) * (1-E1) / (1-np.cos(theta)*E1)

def get_image_json(TR,TE,FA):
    # Load brainweb model
    brainweb = loadmat('static/data/bw.mat')
    type_slice = brainweb['typemap'][:,:,87]
    # Show image
    px.imshow(type_slice)
    mr_image = np.zeros(type_slice.shape)
    params = brainweb['params']
    for type_ind in range(10):
        mr_image[type_slice == type_ind] = \
            signal_model(params[type_ind,3], params[type_ind,0], params[type_ind,1],
                         TR, TE, FA)
    mr_image = np.transpose(mr_image)
    # Generate image
    fig = px.imshow(mr_image, binary_string=True)
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


def get_bargraph_json(TR,TE,FA,tissue_names):
    full_names = ['Background','Cerebrospinal fluid','Gray matter','White matter','Fat',
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

    graphJSON = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


if __name__ == '__main__':
    # Example usage
    # j1, j2 are to be passed into render_template()
    j1, j2 = game3_worker(TR=0.5,TE=0.02,FA=90)



