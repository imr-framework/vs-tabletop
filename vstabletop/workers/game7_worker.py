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
from scipy.spatial.transform import Rotation as R
import matplotlib.pyplot as plt
import matplotlib as mpl
from vstabletop.paths import DATA_PATH, IMG_PATH

def game7_projection_worker(voxels, proj3d_axis, proj2d_angle, lines=False, lines_angle=90):
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

    graphJSON_2D = plot_projection(proj2d,axes,lines,lines_angle)
    graphJSON_1D = plot_projection(proj1d,['r'],lines,lines_angle)

    return graphJSON_2D,graphJSON_1D

def game7_prep3d_worker(difficulty="all",name=None,lines=False,line_dir='z'):
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
        model_info = DATA_PATH / 'solids' / f'{name}.stl'
        #model_info = f'./static/data/solids/{name}.stl'
    else:
       model_info, name = get_random_model(difficulty="all")


    print(f'Using model: {name}')
    graphJSON_3D = get_3d_model_plot(model_info,lines,line_dir)
    #voxels = convert_stls_to_voxels([model_info],resolution=100)
    #voxels = np.load(f'./static/data/solids/{name}.npy')
    voxels = np.load(DATA_PATH / 'solids' / f'{name}.npy')
    print(f'Loaded {name}.npy')



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
    #all_stl_paths = glob.glob(f'./static/data/solids/*{level}.stl')
    all_stl_paths = glob.glob(DATA_PATH / 'solids' / f'*{level}.stl')
    # Draw random integer
    index = np.random.randint(0,len(all_stl_paths))
    path = all_stl_paths[index]

    #name = path.removeprefix('./static/data/solids').removeprefix('/').removeprefix('\\').removesuffix('.stl')
    name = path.removeprefix(DATA_PATH / 'solids').removeprefix('/').removeprefix('\\').removesuffix('.stl').removeprefix('\"')

    return path, name



def get_3d_model_plot(model_info,lines=False,line_dir='z'):
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
    if model_info is None:
        x,y,z,I,J,K = [],[],[],[],[],[]
    else:
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

    layout = go.Layout(paper_bgcolor='gainsboro',
                       title_x=0.5,
                       font_color='black',
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
        margin=dict(
            l=5,
            r=5,
            b=5,
            t=5,
            pad=0
        ),
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
                pad={"r": 1, "t": 1},
                showactive=True,
                x=0,
                xanchor="left",
                y=0,
                yanchor="top"
            ),
        ]
    )

    # TODO add projection direction lines
    #full_fig = fig.full_figure_for_development()
    #print(full_fig.layout.xaxis.range)

    if lines:
        proj_line_width = 3
        proj_line_color = 'indigo'
        # Generate
        xmin, xmax = np.min(x), np.max(x)
        ymin, ymax = np.min(y), np.max(y)
        zmin, zmax = np.min(z), np.max(z)

        if line_dir == 'z':
            xgrid = np.linspace(xmin,xmax,5)
            ygrid = np.linspace(ymin,ymax,5)
            for x0 in xgrid:
                for y0 in ygrid:
                    fig.add_trace(go.Scatter3d(x=[x0,x0],y=[y0,y0],z=[zmin,zmax],mode='lines',
                                               line=dict(width=proj_line_width,color=proj_line_color)))
        elif line_dir =='y':
            xgrid = np.linspace(xmin,xmax,5)
            zgrid = np.linspace(zmin,zmax,5)
            for x0 in xgrid:
                for z0 in zgrid:
                    fig.add_trace(go.Scatter3d(x=[x0,x0],y=[ymin,ymax],z=[z0,z0],mode='lines',
                                               line=dict(width=proj_line_width,color=proj_line_color)))
        elif line_dir =='x':
            ygrid = np.linspace(ymin,ymax,5)
            zgrid = np.linspace(zmin,zmax,5)
            for y0 in ygrid:
                for z0 in zgrid:
                    fig.add_trace(go.Scatter3d(x=[xmin,xmax],y=[y0,y0],z=[z0,z0],mode='lines',
                                               line=dict(width=proj_line_width,color=proj_line_color)))

        fig.update_traces(showlegend=False)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    #fig.show()

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

    # Cut corners
    voxels = cut_cylindrical_corners(voxels)

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

    return np.flip(proj1d)

def plot_projection(proj,axes,lines=False,lines_angle=90):
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
        proj = np.rot90(proj)
        proj = np.flipud(proj)
        #fig = px.imshow(proj, binary_string=True)

        fig = go.Figure(go.Heatmap(z=proj,colorscale='gray',showscale=False))
        fig.update_layout(yaxis=dict(scaleanchor='x'),
                          plot_bgcolor='rgba(0,0,0,0)',
                          margin=go.layout.Margin(
                              l=0,
                              r=0,
                              b=0,
                              t=0
                          ))
#                          width=500,height=350)
        if lines:
            theta = lines_angle * np.pi / 180
            # Add projection lines!
            line_ys = np.linspace(-20,proj.shape[1]+21,9)
            for y in line_ys:
                xs = np.array([-20,proj.shape[0]+21])
                ys = np.array([y,y])
                xy = np.array([xs-proj.shape[0]/2,ys-proj.shape[1]/2])
                R = np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])
                rotxys = np.matmul(R,xy)
                rxs = rotxys[0,:]+proj.shape[0]/2
                rys = rotxys[1,:]+proj.shape[1]/2
                fig.add_trace(go.Scatter(x=rxs, y=rys,mode='lines',
                                         line=dict(width=1,color='lime')))

        fig.update_traces(showlegend=False)
        fig.update_xaxes(title=axes[0], showticklabels=False, range=[1, proj.shape[0]])
        fig.update_yaxes(title=axes[1], showticklabels=False, range=[1, proj.shape[1]])

    elif len(axes) == 1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=proj,mode='lines',line=dict(width=3,color='darkslateblue')))
        fig.update_xaxes(title=axes[0])
        fig.update_yaxes(title='Relative amplitude')
        fig.update_layout( margin=go.layout.Margin(
                              l=0,
                              r=0,
                              b=0,
                              t=0
                          ))

    else:
        fig = go.Figure()

    #fig.show()

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

def convert_stl_to_voxels(input_file_path, resolution=100):
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
    vol, scale, shift = stltovoxel.convert_meshes(meshes, resolution, parallel=False)
    vol = np.swapaxes(vol,0,2)

    return vol

def game7_empty_plots_worker():
    j1 = get_3d_model_plot(None, False, 'z')
    j2 = plot_projection(np.zeros((256,256)),['',''],lines=False)
    j3 = plot_projection([],['r'],lines=False)

    return j1, j2, j3


def cut_cylindrical_corners(voxels):
    # Get rid of corners so projection looks cleaner
    r = voxels.shape[0]/2
    cx,cy = voxels.shape[0]/2, voxels.shape[1]/2

    indx, indy, indz = np.meshgrid(np.arange(voxels.shape[0]),np.arange(voxels.shape[1]),np.arange(voxels.shape[2]))
    inside = np.sqrt(np.square(indx - cx) + np.square(indy - cy)) < r*0.95

    # Generate bool matrix judging if a point is outside
    return voxels * inside

def get_2D_proj_graph(name,dir):
    # Generate arrays for challenge answer options (2D)
    #voxels = np.load(f'./static/data/solids/{name}.npy')
    voxels = np.load(DATA_PATH / 'solids' / f'{name}.npy')
    proj2d = generate_projection_3d_2d(voxels,dir)
    return proj2d

def get_1D_proj_graph(name,dir,angle):
    # Generate arrays for challenge answer options (1D)
    #voxels = np.load(f'./static/data/solids/{name}.npy')
    voxels = np.load(DATA_PATH / 'solids' / f'{name}.npy')

    proj2d = generate_projection_3d_2d(voxels,dir)
    proj1d = generate_projection_2d_1d(proj2d,angle)
    return proj1d

def projections_to_images(g_list_2d, g_list_1d):
    # Save numpy arrays to plots / images
    print('Received g_list_2d')

    for q in range(3):
        print('The true view of the data ...')
        print(g_list_1d[q].shape)

        # 1D
        fig = plt.figure()
        ax = plt.subplot(111)
        ax.plot(g_list_1d[q])
        ax.set_axis_off()
        #fig.savefig(f'./static/img/game7/im1d-{q}.jpg')
        fig.savefig(IMG_PATH / 'game7' / f'im1d-{q}.jpg')

        # 2D
        #plt.imsave(f'./static/img/game7/im2d-{q}.jpg', np.flipud(g_list_2d[q].T),cmap=mpl.cm.gray)
        plt.imsave(IMG_PATH / 'game7' / f'im2d-{q}.jpg', np.flipud(g_list_2d[q].T),cmap=mpl.cm.gray)





if __name__ == "__main__":
    proj3d_axis = 'z' # Can only be x, y, or z
    proj2d_angle = 90 # degrees

    L = False
    # Replace name with any included in the /static/data/solids folder
    j1, voxels = game7_prep3d_worker(name='g7_set1_typeA',lines=L,line_dir='y')
    j2, j3 = game7_projection_worker(voxels, proj3d_axis, proj2d_angle,lines=L,lines_angle=45)

    # j1, j2, and j3 are the 3D, 2D, and 1D plots, respectively.

    # Right now fig.show() is called for all 3 graphs.
    # It needs to be disabled in actual GUI usage.