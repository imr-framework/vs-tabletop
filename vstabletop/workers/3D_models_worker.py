# Module to deal with generating and converting 3D models for games 7 and 8
# Gehua Tong, July 2022
from vstabletop.workers.game7_worker import convert_stl_to_voxels
import glob
import numpy as np
from os import path

# Run this script to convert any new STLs to npy

def convert_all_stls_to_npy():
    print("Converting all stl files without npy counterparts in static/data/solids folder to npy...")
    print("This might take a while.")
    # Find all stls
    # Convert each and safe to npy
    all_stl_paths = glob.glob(f'./static/data/solids/*.stl')
    for ind in range(len(all_stl_paths)):

        # Converts if it doesn't exist
        if path.exists(all_stl_paths[ind].removesuffix('.stl') + '.npy'):
            print(f"{(all_stl_paths[ind].removesuffix('.stl') + '.npy')} has an npy counterpart!")

        else:
            name = all_stl_paths[ind].removesuffix('.stl').removeprefix('./static/data/solids').removeprefix('/').removeprefix('\\')
            print(f'Converting model: {name}')
            vol = convert_stl_to_voxels(all_stl_paths[ind], resolution=100)
            np.save(f'./static/data/solids/{name}.npy',vol)



# Classes for models
class Cylinder:
    def __init__(self):
        self.size = 0
        self.cutout = None

    def write_openscad(self):
        scad_code = ""
        return scad_code

class CylinderHalfCircles(Cylinder): # With half circle
    def __init__(self,):
        super().__init__()


    def initialize_elements(self):
        print("Not implemented")

class CylinderFifthWalls(Cylinder):
    def __init__(self):
        super().__init__()

    def initialize_elements(self):
        print("Not implemented")


if __name__ == "__main__":
    convert_all_stls_to_npy()