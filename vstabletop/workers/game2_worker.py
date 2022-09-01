# Game 2 backend functions!
# K-space magiK
import numpy as np
import scipy.fft as fft
import json
import plotly.graph_objects as go
import plotly
from phantominator import shepp_logan


def game2_worker_convert(input, scale, forward=True):
    # Perform forward or backward, 1D or 2D FT
    if forward:
        if len(input.shape) == 1: # 1D case
            output, outscale = forward_1d(input, scale)
        elif len(input.shape) == 2: # 2D case
            output, outscale = forward_2d(input, scale)
        else:
            raise ValueError('The input dimension must be 1 or 2')
    else:
        if len(input.shape) == 1: # 1D case
            output, outscale = backward_1d(input, scale)
        elif len(input.shape) == 2: # 2D case
            output, outscale = backward_2d(input, scale)
        else:
            raise ValueError('The input dimension must be 1 or 2')

    # Make figure
    fig = make_graph(output,outscale)
    #fig.show() # For debugging.

    # Return JSON formatted figure
    graphJSON_output = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON_output, output, outscale

def game2_worker_fetch(type='original',dim=1,name='flat',info={}):
    # Generate a new 1D or 2D image/signal or kspace/spectrum based on user inputs
    fig = go.Figure()
    if dim == 1:
        input, scale = get_1d_data(type,256,[-1,1],name)
    elif dim == 2:
        input, scale = get_2d_data(type, [256,256],[-1,1,-1,1],name)


    fig = make_graph(input,scale)
    #fig.show()

    graphJSON_input = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON_input, input, scale


def make_graph(data,scale):
    # Detect data size
    # 1D case
    fig = go.Figure()
    if len(data.shape) == 1:
        print('Making 1D graph')
        fig.add_trace(go.Scatter(x=scale,y=np.real(data),mode='lines'))
        fig.add_trace(go.Scatter(x=scale,y=np.imag(data),mode='lines'))

    # 2D case
    elif len(data.shape) == 2:
        print('Making 2D graph')
        fig.add_trace(go.Heatmap(z=np.absolute(data),colorscale='gray',showscale=False))
        fig.update_layout(yaxis=dict(scaleanchor='x'),
                          plot_bgcolor='rgba(0,0,0,0)',
                          margin=go.layout.Margin(l=0,r=0,b=0,t=0))
    return fig

def make_empty_graphs():
    fig1 = make_graph(np.zeros(256), scale=np.linspace(-1,1,256))
    fig2 = make_graph(np.zeros((256,256)),scale=[np.linspace(-1,1,256),np.linspace(-1,1,256)])

    j1 = json.dumps(fig1,cls=plotly.utils.PlotlyJSONEncoder)
    j2 = json.dumps(fig2,cls=plotly.utils.PlotlyJSONEncoder)

    return j1, j2


def forward_1d(signal, tmodel):
    """1D forward FFT"""
    N = len(signal)
    spectrum = fft.fftshift(fft.fft(signal))
    df = 1/(tmodel[-1] - tmodel[1])
    fmodel = df* (np.arange(-N/2, N/2) + 0.25*(1-(-1)**N))
    return spectrum, fmodel

def backward_1d(spectrum, fmodel):
    """1D backward FFT"""
    N = len(spectrum)
    signal = (fft.ifft(fft.ifftshift(spectrum)))
    dt = 1/(fmodel[-1] - fmodel[1])
    tmodel = dt* (np.arange(-N/2, N/2) + 0.25*(1-(-1)**N))
    return signal, tmodel

def forward_2d(imspace, xmodel):
    """2D forward FFT"""
    kspace = fft.fftshift(fft.fft2(imspace))
    dx = 1/(xmodel[0][-1] - xmodel[0][0])
    dy = 1/(xmodel[1][-1] - xmodel[1][0])
    Nx, Ny = imspace.shape
    kmodel = []
    kmodel.append(dx * (np.arange(-Nx/2, Nx/2) + 0.25*(1-(-1)**Nx)))
    kmodel.append(dy * (np.arange(-Ny/2, Ny/2) + 0.25*(1-(-1)**Ny)))
    return kspace, kmodel

def backward_2d(kspace, kmodel):
    """2D backward FFT"""
    imspace = fft.ifft2(fft.ifftshift(kspace))
    dkx = 1/(kmodel[0][-1] - kmodel[0][0])
    dky = 1/(kmodel[1][-1] - kmodel[1][0])
    Nx, Ny = kspace.shape
    xmodel = []
    xmodel.append(dkx * (np.arange(-Nx/2, Nx/2) + 0.25*(1-(-1)**Nx)))
    xmodel.append(dky * (np.arange(-Ny/2, Ny/2) + 0.25*(1-(-1)**Ny)))
    return imspace, xmodel

# Create data

def get_2d_data(type, N,range,name,info={}):
    """Get a specific type of 2D data

    N : array-like
        Matrix size (Nx, Ny)
    range : array-like
        Length 4: physical extent is (range[0],range[1]) for first axis
                                 and (range[2],range[3]) for second axis
    name : str
        Type of 2D data to generate
    info : dict

    """
    print('Getting 2D data...')
    xmodel = []
    xmodel.append(np.linspace(range[0],range[1],N[0], endpoint=False))
    xmodel.append(np.linspace(range[2],range[3],N[1], endpoint=False))

    data2d = np.zeros((N[0],N[1]))
    if name == 'flat':
        data2d = np.ones(data2d.shape)
    elif name == 'delta':
        data2d[int(N[0]/2),int(N[1]/2)] = 1
    elif name == 'shepp-logan':
        img, _, _ = shepp_logan((N[0], N[1], 1), MR=True, zlims=(-.25, .25))
        if type == 'original':
            data2d = np.squeeze(img)
        elif type == 'frequency':
            data2d = fft.fftshift(fft.fft2(np.squeeze(img)))

    elif name == 'deltas':
        for loc in info['delta_locs']:
            indx = int(np.round(N[0] * (loc[0] - range[0]) / (range[1] - range[0])))
            indy = int(np.round(N[1] * (loc[1] - range[2]) / (range[3] - range[2])))
            data2d[indx,indy] = 1

    return data2d, xmodel

def get_1d_data(type, N, range, name, info={}):
    print('Getting 1D data...')
    xmodel = np.linspace(range[0],range[1],N, endpoint=False)
    data1d = np.zeros(xmodel.shape)
    if name == 'flat':
        data1d = np.ones(xmodel.shape)
    elif name == 'delta':
        data1d[int(N/2)] = 1
    elif name == 'deltas':
        for loc in info['delta_locs']:
            ind = int(np.round(N*(loc - range[0])/(range[1]-range[0])))
            data1d[ind] = 1

    return data1d, xmodel



if __name__ == '__main__':
    j0 = game2_worker_fetch(dim=2, name='shepp-logan')
    #data1d, scale = get_1d_data(256, [-1,1], 'flat')
    #data2d, scale = get_2d_data([256,256],[-1,1,-1,1],'delta')
    #j1 = game2_worker_convert(data2d, scale, forward=True)