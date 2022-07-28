# Module to deal with generating and converting 3D models for games 7 and 8
# Gehua Tong, July 2022


def convert_all_stls_to_npy():
    # Find all stls
    # Convert each and safe to npy
    pathlist = []
    return pathlist


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

