# Create numerical phantoms
from virtualscanner.server.simulation.bloch.phantom import SpheresArrayPlanarPhantom
import numpy as np
from scipy.io import savemat, loadmat
from vstabletop.paths import DATA_PATH
import matplotlib.pyplot as plt

def create_and_save_game4_phantom_mask():
    # Flow phantom mask for Game 4
    fov = 256e-3
    n = 256
    centers = [[0,-fov/5,0],[0,fov/5,0]]
    radii = [fov/8,fov/8]
    # 0 - background; 1 - flow sphere 1; 2 - flowing sphere 2; 3 - background cylinder
    # (PD, T1, T2)
    type_params =  {0:(0,0,0),1.0:(1,4,2),2:(2,4,2),3:(3,4,2)}
    phantom = SpheresArrayPlanarPhantom(centers, radii, type_params, fov, n, dir='z',R=fov/2,loc=(0,0,0))
    # Save as mat file
    savemat(DATA_PATH / 'game4_phantom.mat',{'type_map':phantom.type_map, 'names':['background','sphere1','sphere2','cylinder']})
    return


def load_game4_phantom(T1,T2,T2s,speed):
    data = loadmat(DATA_PATH / 'game4_phantom.mat')
    map = data['type_map']
    # Extract mask for main cylinder
    static = (map == 3)
    # Extract mask for flow
    flow = (map == 1) + (map == 2)
    # Return: masks
    phantom_dict= {'static': static,'flow': flow}
    return phantom_dict


if __name__ == "__main__":
    #create_and_save_game4_phantom_mask()
    phantom_dict = load_game4_phantom(T1=1000,T2=200,T2s=50,speed=3) # speed in meters/second


