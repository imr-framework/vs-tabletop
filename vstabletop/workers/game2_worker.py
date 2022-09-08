# Game 2 backend functions!
# K-space magiK
import numpy as np
import scipy.fft as fft
import json
import plotly.graph_objects as go
import plotly
from phantominator import shepp_logan
from PIL import ImageOps, Image
from vstabletop.paths import IMG_PATH
import fnmatch
from scipy import ndimage

def game2_worker_convert(input, scale, forward=True):
    # Perform forward or backward, 1D or 2D FT
    if forward:
        if len(input.shape) == 1: # 1D case
            output, outscale = forward_1d(input, scale)
            outtype = 'spectrum'
        elif len(input.shape) == 2: # 2D case
            output, outscale = forward_2d(input, scale)
            outtype = 'kspace'

        else:
            raise ValueError('The input dimension must be 1 or 2')
    else:
        if len(input.shape) == 1: # 1D case
            output, outscale = backward_1d(input, scale)
            outtype = 'signal'
        elif len(input.shape) == 2: # 2D case
            output, outscale = backward_2d(input, scale)
            outtype = 'image'
        else:
            raise ValueError('The input dimension must be 1 or 2')

    # Make figure
    fig = make_graph(output,outscale,outtype)
    #fig.show() # For debugging.

    # Return JSON formatted figure
    graphJSON_output = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON_output, output, outscale

def game2_worker_fetch(type='original',dim=1,name='flat',info={}):
    # Generate a new 1D or 2D image/signal or kspace/spectrum based on user inputs
    fig = go.Figure()
    if dim == 1:
        input, scale = get_1d_data(type,256,[-1,1],name,info)
        if type == 'original':
            fig = make_graph(input,scale,'signal')
        else:
            fig = make_graph(input,scale,'spectrum')
    elif dim == 2:
        input, scale = get_2d_data(type, [256,256],[-1,1,-1,1],name,info)
        if type == 'original':
            fig = make_graph(input,scale,'image')
        else:
            fig = make_graph(input,scale,'kspace')


    #fig.show()

    graphJSON_input = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON_input, input, scale


def make_graph(data,scale,type):
    # Detect data size
    # 1D case
    fig = go.Figure()

    if len(data.shape) == 1:
        print('Making 1D graph')
        if type == 'signal':
            fig.add_trace(go.Scatter(x=scale,y=np.imag(data),mode='lines', name='Imaginary',line=dict(color='red')))
            fig.add_trace(go.Scatter(x=scale, y=np.real(data), mode='lines', name='Real', line=dict(color='blue')))
            fig.update_layout(xaxis_title='Time (seconds)',yaxis_title='Amplitude')
        elif type == 'spectrum':
            fig.add_trace(go.Scatter(x=scale,y=np.angle(data),mode='lines',name='Phase',line=dict(color='gray')))
            fig.add_trace(go.Scatter(x=scale,y=np.absolute(data),mode='lines',name='Amplitude',line=dict(color='navy')))
            fig.update_layout(xaxis_title='Frequency (Hz)',yaxis_title='Amplitude')

    # 2D case
    elif len(data.shape) == 2:
        print('Making 2D graph')
        data = np.absolute(data)

        if np.min(data) == np.max(data):
            print('unity!')
            data = 0.5*np.ones(data.shape)
        else:
           data = ((data - np.min(data))/ (np.max(data)-np.min(data)))

        # Special scaling to display k-space more clearly
        if type == 'kspace':
            epsilon = 1e-4
            data = data*(1-epsilon) + epsilon # range becomes (epsilon, 1)
            data = (np.log(data) - np.log(epsilon)) / np.absolute(np.log(epsilon))# range is back to (0,1)


        fig.add_trace(go.Heatmap(z=data,colorscale='gray',zmin=0.0, zmax=1.0, showscale=False))
        fig.update_layout(yaxis=dict(scaleanchor='x'),
                          plot_bgcolor='rgba(0,0,0,0)',
                          margin=go.layout.Margin(l=0,r=0,b=0,t=0))

        fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)

    return fig

def make_empty_graphs():
    fig1 = make_graph(np.zeros(256), scale=np.linspace(-1,1,256),type='signal')
    fig2 = make_graph(np.zeros(256), scale=np.linspace(-1,1,256),type='spectrum')

    j1 = json.dumps(fig1,cls=plotly.utils.PlotlyJSONEncoder)
    j2 = json.dumps(fig2,cls=plotly.utils.PlotlyJSONEncoder)

    return j1, j2


def forward_1d(signal, tmodel):
    """1D forward FFT"""
    print('Forward 1d')
    N = len(signal)
    spectrum = fft.fftshift(fft.fft(signal))
    df = 1/(tmodel[-1] - tmodel[1])
    fmodel = df* (np.arange(-N/2, N/2) + 0.25*(1-(-1)**N))
    return spectrum, fmodel

def backward_1d(spectrum, fmodel):
    """1D backward FFT"""
    print('Backward 1d')

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
        data2d = np.squeeze(img)
    elif name == 'cat':
        data2d = read_image_grayscale(IMG_PATH / 'Game2' / 'beet_cat.png')
    elif name == 'mri-x':
        data2d = read_image_grayscale(IMG_PATH / 'Game2' / 'brain-x.png')
    elif name == 'mri-y':
        data2d = read_image_grayscale(IMG_PATH / 'Game2' / 'brain-y.png')
    elif name == 'mri-z':
        data2d = read_image_grayscale(IMG_PATH / 'Game2' / 'brain-z.png')
    elif name == 'cos':
        data2d = generate_2D_wave(256, 1/info['image_wavelength'], info['image_wave_phase'], info['image_angle'])
    elif name == 'sin':
        data2d = generate_2D_wave(256, 1/info['image_wavelength'], 0.5*np.pi + info['image_wave_phase'], info['image_angle'])
    elif name == 'circ':
        data2d = generate_2D_wave(256, 1/info['image_wavelength'],info['image_wave_phase'], None)
    elif name == 'line-x':
        data2d = generate_2D_line(256,'x',info['image_angle'])
    elif name == 'line-y':
        data2d = generate_2D_line(256,'y',info['image_angle'])
    elif name == 'delta2': # kspace only
        data2d = generate_double_deltas(256, info['kspace_ds_separation'])

    # TODO Perform rotation for general images (nonanalytic)
    if type == 'original':
        if name not in ['sin','cos','circ','flat','delta','line-x','line-y']:
            data2d = ndimage.rotate(data2d,info['image_angle'],reshape=False)
    else:
        if name == 'delta2':
            data2d = ndimage.rotate(data2d, info['kspace_angle'],reshape=False,order=0)
        if name not in ['flat','delta','delta2']:
            data2d = ndimage.rotate(data2d,info['kspace_angle'],reshape=False)

    return data2d, xmodel

def get_1d_data(type, N, range, name, info={}):
    # TODO apply info
    print('Getting 1D data...')
    xmodel = np.linspace(range[0],range[1],N, endpoint=False)
    data1d = np.zeros(xmodel.shape)
    if name == 'flat':
        data1d = np.ones(xmodel.shape)
    elif name == 'delta':
        data1d[int(N/2)] = 1

    scale, shift, phasemod = 0, 0, 0
    if type == 'original':
        scale = info['signal_scale']
        shift = info['signal_shift']
        phasemod = info['signal_phase_mod']
    elif type == 'frequency':
        scale = info['spectrum_scale']
        shift = info['spectrum_shift']
        phasemod = info['spectrum_phase_mod']

    # Scaling
    data1d *= scale
    # Shifting
    data1d = np.roll(data1d, int(round(shift * N)))
    # Phase modulation
    data1d = data1d*np.exp(1j*(phasemod*np.pi/180)*np.arange(0,N))

    return data1d, xmodel

def read_image_grayscale(data_path, N=None):
    try:
        im = Image.open(data_path)
    except:
        print('Data path problems!')

    if N is not None:
        im = im.resize(N)
    else:
        # Resize image to within 600 x 600 pixels
        maxside = np.max([im.width,im.height])
        if maxside > 600:
            new_width = int(round((600/maxside)*im.width))
            new_height = int(round((600/maxside)*im.height))
            im = im.resize((new_width,new_height))

    data = np.array(ImageOps.grayscale(im))
    data = np.flipud(data)
    return data

def convert_2d_drawing(data_path,target='image'):
    # Read PNG file and process
    data = read_image_grayscale(data_path)

    # Create graph, update session, and send back to frontend
    scale = [np.linspace(-1,1,data.shape[0]),np.linspace(-1,1,data.shape[1])]
    fig = make_graph(data,scale,target)
    graphJSON = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON, data, scale

def convert_1d_drawing(data_path,target='signal'):
    image = read_image_grayscale(data_path)
    image = np.flipud(image)
    data = np.zeros(image.shape[1])
    # Detect lowest non-white point of each column
    for u in range(image.shape[1]): # For each column
        # Find last row that has non-white point
        col = image[:,u]
        q = np.argwhere(col!=255)
        if len(q) == 0:
            data[u] = 0
        else:
            data[u]  = (400 - q[0])-200
    data /= 200
    scale = np.linspace(-1,1,400)

    fig = make_graph(data,scale,target)
    graphJSON = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON, data, scale

# TODO match size of erase mask and current k-space
def retrieve_erase_mask(shape):
    # Make a mask from the png file according to requested shape
    erase_data = read_image_grayscale(IMG_PATH / 'Game2' / 'erase.png', (shape[1],shape[0]))
    erase_mask = (erase_data > 0)

    return erase_mask

# Helper functions
def generate_2D_wave(N,k,phase,theta):
    """
    Parameters
    ----------
    N : integer
        Size of output image (N x N)
    k : float
        Spatial frequency
        Range : 0.5 ~ 20 per FOV (corresponds to wavelength of 0.05 - 2 FOV)
    phase : float
        Phase of wave (helps generate sin / cos / anything in between)
        Phase = 0 : cosine wave
        Phase = 1/4 wavelength : sine wave
    theta : float
        Rotation angle in degrees
        If theta = None, a radial wave is generated
    """
    if k < 0.5:
        k = 0.5
        print('Using k = 0.5')
    elif k > 20:
        k = 20
        print('Using k = 20')


    # Generate meshgrid
    model = np.linspace(-0.5,0.5,N,endpoint=False)
    X,Y = np.meshgrid(model,model)
    if theta is not None:
        theta *= -np.pi / 180
        R = X*np.cos(theta) + Y*np.sin(theta)
    else:
        R = np.sqrt(X**2 + Y**2)

    data = np.cos(2*np.pi*k*R + phase)

    return data

def generate_2D_line(N,axis,theta):
    theta *= -np.pi/180
    if axis == 'y':
        theta += np.pi/2
    model = np.linspace(-0.5, 0.5, N, endpoint=False)
    X, Y = np.meshgrid(model, model)
    R = X * np.cos(theta) + Y * np.sin(theta)
    data = 1*(np.sqrt((X-R*np.cos(theta))**2 + (Y-R*np.sin(theta))**2) < (1/N))
    # if axis == 'x':
    #     data[int(N/2),:] = 1
    # elif axis == 'y':
    #     data[:,int(N/2)] = 1
    # else:
    #     raise ValueError('Requested axis must be x or y ')
    return data


def generate_double_deltas(N,sep):
    """
    N: size
    sep: separation (0-1 of FOV)
    """
    data = np.zeros((N,N))
    data[int(round(N/2)),int(round(N/2 - N*sep/2))] = 1
    data[int(round(N/2)),int(round(N/2 + N*sep/2))] = 1
    return data
