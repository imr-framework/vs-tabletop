# Have a choice of multiple images
# 1. Scenery
# 2. Brain
# 3. Cat
from phantominator import shepp_logan
import plotly
import plotly.express as px
import numpy as np
import json

def get_image(fov,n,n_zf,min_level,max_level):
    # Make sure n and n_zf is even
    n += n%2
    n_zf += n_zf%2

    fov_orig = 0.25 # meters
    fov_portion = fov/fov_orig
    n_first = int(np.ceil(0.5*(n / fov_portion)))*2
    img, _, _ = shepp_logan((n_first, n_first, 1), MR=True, zlims=(-.25, .25))
    img = np.squeeze(img)
    # If larger, zerofill
    print(n,n_first)
    if fov_portion > 1:
        # If larger make a smaller one and zerofill in image space
        final_image = np.zeros((n,n))
        ind1 = int(n/2-n_first/2)
        ind2 = int(n/2+n_first/2)
        final_image[ind1:ind2,ind1:ind2] = img
    elif fov_portion < 1:
        # If smaller make larger one to start with and take the center
        ind1 = int(n_first / 2 - n / 2)
        ind2 = int(n_first / 2 + n / 2)
        final_image = img[ind1:ind2,ind1:ind2]
    else:
        final_image = img

    # Zerofill in k-space when needed
    if n_zf is not None:
        if n_zf < n:
            raise ValueError("The zerofill target matrix size should be larger than the acq. matrix size.")
        # Zerofill!
        kspace = np.fft.fftshift(np.fft.fft2(final_image))
        kspace_zf = np.zeros((n_zf,n_zf),dtype=complex)
        ind1 = int(n_zf/2 - n/2)
        ind2 = int(n_zf/2 + n/2)
        kspace_zf[ind1:ind2,ind1:ind2] = kspace
        final_image = np.absolute(np.fft.ifft2(np.fft.fftshift(kspace_zf)))



    # Normalize to between (0,1)
    final_image = (final_image - np.min(final_image)) / (np.max(final_image)-np.min(final_image))

    # Windowing: Normalize levels between (min,max) to (0,1)
    if max_level <= min_level:
        max_level = 1
        min_level = 0
    final_image = (final_image - min_level) / (max_level - min_level)
    final_image[final_image<=0] = 0
    final_image[final_image>=1] = 1

    return final_image


def generate_plot(img):
    fig = px.imshow(img,binary_string=True)
    fig.update(layout_coloraxis_showscale=False)
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)

    return fig

def game1_worker(fov,n,n_zf,min_level,max_level):
    """Receives game 1 user defined inputs and generates a corresponding image
       GT, July 2022

    Parameters
    ----------
    fov : float
        Field-of-view in [meters]
    n : integer
        Final matrix size. Will be converted to the next larger even number if it's odd.
    n_zf : integer
        Zero-filled matrix size. Will be converted to the next larger even number if it's odd.
    min_level : float
        Lower bound for image intensity window. Between zero and one.
    max_level : float
        Upper bound for image intensity window. Between zero and one.
        If max_level is smaller than min_level, (min_level,max_level) will be reset to (0,1)

    Returns
    j1 : str
        JSON string for Plotly use

    -------
    """
    img = get_image(fov,n,n_zf, min_level, max_level)
    fig = generate_plot(img)

    j1 = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    return j1




if __name__ == '__main__':
    j1 = game1_worker(0.12,128,256,0,1)
    print(j1)