# Game 7 worker
# Gehua Tong, July 2022

import numpy as np
from stl import mesh
import plotly.express as px
import plotly.graph_objects as go
import json
import plotly
import stltovoxel
import os
import glob
from skimage.transform import radon


def game7_projection_worker(voxels, proj3d_axis, proj2d_angle): # update all three images
    # inputs: model choice, angle(s),
    # outputs: graphs
    proj2d = generate_projection_3d_2d(voxels,proj3d_axis)
    proj1d = generate_projection_2d_1d(proj2d,proj2d_angle)

    axes = list('xyz'.replace(proj3d_axis,''))

    graphJSON_2D = plot_projection(proj2d,axes)
    graphJSON_1D = plot_projection(proj1d,['r'])

    return graphJSON_2D,graphJSON_1D

def game7_prep3d_worker(difficulty="all",name=None):
    # TODO enable non-random option
    # Pre-loads a 3D model and calculates its voxel representation
    # To speed up things

    # Convert model name to path
    if name is not None:
        model_info = f'./static/data/solids/{name}.stl'
    else:
       model_info, name = get_random_model(difficulty="all")


    print(f'Using model: {name}')
    graphJSON_3D = get_3d_model_plot(model_info)
    voxels = process_3d_model(model_info)

    return graphJSON_3D, voxels

def get_random_model(difficulty="all"):
    # Generates and returns a random stl path
    # Set difficulty filter
    level = ''
    if difficulty != 'all':
        level += f'{difficulty}'
        raise NotImplementedError("Changes in difficulty are yet to be included!")

    # Get all stl paths in static/data/solids
    all_stl_paths = glob.glob(f'./static/data/solids/*{level}.stl')
    # Draw random integer
    index = np.random.randint(0,len(all_stl_paths))
    path = all_stl_paths[index]

    name = path.removesuffix(f'{difficulty}.stl').removeprefix('./static/data/solids/')

    return path, name

def process_user_image():
    # TODO implement later - user can upload image. It gets converted to grayscale and can be projected.
    img = 0
    return img

def process_3d_model(model_info):
    # Load blank cylinder and get background info
    vol = convert_files_simple(model_info,resolution=100)
    return vol


def get_3d_model_plot(model_info):
    x,y,z,I,J,K = load_3d_model(model_info)

    colorscale = [[0, 'lightblue'], [1, 'lightblue']]
    mesh3D = go.Mesh3d(
        x=x, y=y, z=z, i=I, j=J, k=K,
        flatshading=True,
        colorscale=colorscale,
        intensity=z,
        name='Phantom',
        showscale=False,
        opacity=1,
        alphahull=10)

    title = "Model"
    layout = go.Layout(paper_bgcolor='gainsboro',
                       title_text=title, title_x=0.5,
                       font_color='black',
                       width=800,
                       height=800,
                       scene_camera=dict(eye=dict(x=1.25, y=-1.25, z=1)),
                       scene_xaxis_visible=False,
                       scene_yaxis_visible=False,
                       scene_zaxis_visible=False)

    fig = go.Figure(data=[mesh3D], layout=layout)
    fig.data[0].update(lighting=dict(ambient=0.15,
                                     diffuse=0.9,
                                     fresnel=.1,
                                     specular=1,
                                     roughness=.1,
                                     facenormalsepsilon=0))
    fig.data[0].update(lightposition=dict(x=3000,
                                          y=3000,
                                          z=10000))
    # Transparency buttons
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=list([
                    dict(
                        label="Opaque",
                        args=[{"opacity":[1]}],
                        method="update",
                    ),
                    dict(
                        label="Transparent",
                        args=[{"opacity":[0.5]}],
                        method="update"
                    )
                ]),
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.11,
                xanchor="left",
                y=1.1,
                yanchor="top"
            ),
        ]
    )

    # Comment out later
    fig.show()

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def load_3d_model(model_info):
    meshy = mesh.Mesh.from_file(model_info)
    vertices, I, J, K = stl2mesh3d(meshy)
    X,Y,Z = vertices.T
    return X,Y,Z,I,J,K


def generate_projection_3d_2d(voxels,axis):
    """Perform 2D projection of 3D volume data

    Parameters
    ----------
    voxels : np.ndarray
        3D array (Nx,Ny,Nz) of data
    axis : str
        Axis along which the volume is projected.
        One of 'x', 'y', 'z'

    Returns
    -------
    proj2d : np.ndarray
        2D projected image
    """
    # Invert voxels
    voxels = 1 - voxels
    proj2d = np.sum(voxels,'xyz'.index(axis))
    return proj2d


def generate_projection_2d_1d(img,angle):
    # Use Radon transform
    # Generate 1D projection of 2D image
    proj1d = radon(img,[angle])
    # Normalize and make it 1D
    proj1d = proj1d.flatten() / np.max(proj1d)

    return proj1d

def plot_projection(proj,axes):
    # Generates JSON string of a projection plot
    if len(axes) == 2:
        fig = px.imshow(np.rot90(proj), binary_string=True)
        fig.update_xaxes(title=axes[0],showticklabels=False)
        fig.update_yaxes(title=axes[1],showticklabels=False)
    elif len(axes) == 1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=proj,mode='lines',line=dict(width=3,color='darkslateblue')))
        fig.update_xaxes(title=axes[0])
        fig.update_yaxes(title='Relative amplitude')
    else:
        fig = go.Figure()

    # TODO comment out later
    fig.show()

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

# Helper functions
def stl2mesh3d(stl_mesh):
    """Convert STL to Mesh3D for display
    (https://chart-studio.plotly.com/~empet/15276/converting-a-stl-mesh-to-plotly-gomes/#/)
    """
    p, q, r = stl_mesh.vectors.shape #(p, 3, 3)
    vertices, ixr = np.unique(stl_mesh.vectors.reshape(p*q, r), return_inverse=True, axis=0)
    I = np.take(ixr, [3*k for k in range(p)])
    J = np.take(ixr, [3*k+1 for k in range(p)])
    K = np.take(ixr, [3*k+2 for k in range(p)])
    return vertices, I, J, K

def convert_files_simple(input_file_path, resolution=100):
    """Modified function from stltovoxel to output rasterized volume directly

    Parameters
    ----------
    input_file_path : str
        Path to STL file
    resolution : int
        Matrix size of rasterized volume will be resolution + 1

    Returns
    -------
    vol : np.ndarray
        3D array - rasterized boolean volume representation of 3D model
    """
    meshes = []
    mesh_obj = mesh.Mesh.from_file(input_file_path)
    org_mesh = np.hstack((mesh_obj.v0[:, np.newaxis], mesh_obj.v1[:, np.newaxis], mesh_obj.v2[:, np.newaxis]))
    meshes.append(org_mesh)
    parallel = False
    vol, scale, shift = stltovoxel.convert_meshes(meshes, resolution, parallel)
    vol = np.swapaxes(vol,0,2)
    return vol


if __name__ == "__main__":
    proj3d_axis = 'y' # Can only be x, y, or z
    proj2d_angle = 45 # degrees

    # Replace name with any included in the /static/data/solids folde
    j1, voxels = game7_prep3d_worker(name='letterY')
    j2, j3 = game7_projection_worker(voxels, proj3d_axis, proj2d_angle)

    # j1, j2, and j3 are the 3D, 2D, and 1D plots, respectively.


    # Right now fig.show() is called for all 3 graphs.
    # It needs to be disabled in actual GUI usage.