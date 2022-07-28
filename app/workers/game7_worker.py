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


def game7_projection_worker(voxels, proj3d_axis, proj2d_angle):
    """Generates 2D and 1D projections of the given raster representation of a 3D model

    Parameters
    ----------
    voxels : np.ndarray
        Voxel representation of 3D model
    proj3d_axis : str
        Axis along which the volume is projected.
        One of 'x', 'y', 'z'
    proj2d_angle : float
        Projection angle in [degrees]

    Returns
    -------
    graphJSON_2D : str
        JSON representation of 2D projection Plotly figure
    graphJSON_1D : str
        JSON representation of 1D projection Plotly figure
    """

    # update all three images
    # inputs: model choice, angle(s),
    # outputs: graphs
    proj2d = generate_projection_3d_2d(voxels,proj3d_axis)
    proj1d = generate_projection_2d_1d(proj2d,proj2d_angle)

    axes = list('xyz'.replace(proj3d_axis,''))

    graphJSON_2D = plot_projection(proj2d,axes)
    graphJSON_1D = plot_projection(proj1d,['r'])

    return graphJSON_2D,graphJSON_1D

def game7_prep3d_worker(difficulty="all",name=None):
    """Loads random or specified STL file and returns rasterized 3D image and 3D model plot

    Parameters
    ----------
    difficulty : str
        Difficulty of game. Default = 'all' (no filtering)
        Other possible values : 'easy','medium','hard' - suffixes to file names for selective loading
    name : str
        Name of specified phantom. Default = None
        The 3D model {name}.stl will be loaded

    Returns
    -------
    graphJSON_3D : str
        JSON representation of 3D model figure
    voxels : np.ndarray
        3D array; rasterized representation of 3D model
    """

    # Pre-loads a 3D model and calculates its voxel representation
    # To speed up things

    # Convert model name to path
    if name is not None:
        model_info = f'./static/data/solids/{name}.stl'
    else:
       model_info, name = get_random_model(difficulty="all")


    print(f'Using model: {name}')
    graphJSON_3D = get_3d_model_plot(model_info)
    voxels = convert_stls_to_voxels([model_info],resolution=100)

    return graphJSON_3D, voxels


def get_random_model(difficulty="all"):
    """ Generates and returns a random STL path with optional difficulty filter

    Parameters
    ----------
    difficulty : bool
        Difficulty of game. Default = 'all' (no filtering)
        Other possible values : 'easy','medium','hard' - suffixes to file names for selective loading

    Returns
    -------
    path : str
        Path to STL file
    name : str
        Name of STL file loaded
    """

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



def get_3d_model_plot(model_info):
    """Loads STL of given path, displays it in Plotly, and returns JSON string of figure

    Parameters
    ----------
    model_info : str
        Path to requested STL model

    Returns
    -------
    graphJSON : str
        JSON representation of 3D model Plotly figure

    """
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

    fig.show()

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def load_3d_model(model_info):
    """Loads STL into mesh representation

    Parameters
    ----------
    model_info : str
        Path to requested STL model

    Returns
    -------
    X, Y, Z, I, J, K : np.ndarray
        Arrays representing the 3D mesh
        Inputs for constructing a Plotly.graph_objects.Mesh3d object

    """
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
    # Invert voxels so 1 in model => no signal (0); 0 in model => water signal (1)
    voxels = 1 - voxels
    proj2d = np.sum(voxels,'xyz'.index(axis))
    return proj2d


def generate_projection_2d_1d(img,angle):
    """Generates 1D projection from 2D image

    Parameters
    ----------
    img : np.ndarray
        2D grayscale image to undergo projection
    angle : float
        Angle of projection in [degrees]

    Returns
    -------
    proj1d : np.ndarray
        1D normalized array of projection
    """

    # Use Radon transform
    # Generate 1D projection of 2D image
    proj1d = radon(img,[angle])
    # Normalize and make it 1D
    proj1d = proj1d.flatten() / np.max(proj1d)

    return proj1d

def plot_projection(proj,axes):
    """Make 2D or 1D projection plot

    Parameters
    ----------
    proj : np.ndarray
        2D projected image or 1D projected curve
    axes : np.ndarray
        Length-2 or length-1 array
        If length-2, a 2D projection is displayed
          with x-axis labeled axes[0] and y-axis labeled axes[1]
        If length-1, a 1D projection is displayed
          with x-axis labeled axes[0]

    Returns
    -------
    graphJSON : str
        JSON representation of Plotly figure

    """
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

    fig.show()

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def stl2mesh3d(stl_mesh):
    """Convert STL to Mesh3D for display
    Author : @empet
    (https://chart-studio.plotly.com/~empet/15276/converting-a-stl-mesh-to-plotly-gomes/#/)
    # stl_mesh is read by nympy-stl from a stl file; it is  an array of faces/triangles (i.e. three 3d points)
    # this function extracts the unique vertices and the lists I, J, K to define a Plotly mesh3d
    # the array stl_mesh.vectors.reshape(p*q, r) can contain multiple copies of the same vertex;
    # extract unique vertices from all mesh triangles

    Parameters
    ----------
    stl_mesh : numpy-stl Mesh object

    Returns
    -------
    vertices : array_like
        Mesh vertice representation 
    I, J, K : array_like
        Information for determining triangulation of the vertices data

    """
    p, q, r = stl_mesh.vectors.shape #(p, 3, 3)
    vertices, ixr = np.unique(stl_mesh.vectors.reshape(p*q, r), return_inverse=True, axis=0)
    I = np.take(ixr, [3*k for k in range(p)])
    J = np.take(ixr, [3*k+1 for k in range(p)])
    K = np.take(ixr, [3*k+2 for k in range(p)])
    return vertices, I, J, K

def convert_stls_to_voxels(input_file_paths, resolution=100):
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
    for path in input_file_paths:
        mesh_obj = mesh.Mesh.from_file(path)
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