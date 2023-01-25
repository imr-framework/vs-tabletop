from vstabletop.workers.game7_worker import load_3d_model, generate_projection_3d_2d, \
                                            generate_projection_2d_1d, \
                                            game7_prep3d_worker

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
import matplotlib.pyplot as plt
import matplotlib as mpl
from vstabletop.paths import DATA_PATH, IMG_PATH
import random
from vstabletop.info import GAME8_RANDOM_MODELS

# Load model and reveal options
def game8_worker_load(info,default=True):
    if default:
        graphJSON_options = json.dumps(make_blank_plot('image'), cls=plotly.utils.PlotlyJSONEncoder)
        ind_correct = None
        image = None
        return graphJSON_options, ind_correct, image

    if info['mode'] == '3D':
        # 3D mode: load four different models; store the voxels of the correct one;
        #          shuffle,  store index of correct answer
        #          Return: graphJSON_options (all four models displayed on the same plot, shuffled), voxels, index
        names = []
        voxels_list = []
        q = 0
        # Draw 4 models
        while q < 4:
            name, voxels = load_random_model()
            if name not in names:
                q += 1
                names.append(name)
                voxels_list.append(voxels)

        # The first one is the correct answer.
        name_correct = names[0]
        image = voxels_list[0]

        # Shuffle
        np.random.shuffle(names)
        ind_correct = names.index(name_correct)
        fig = make_3D_options_plot(names)
        # Addin the plots from the previous fig?
        graphJSON_options = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
        print("3D generation complete")
    elif info['mode'] == '2D':
        # Start drawing projections of random 3D models until we get 4 different ones
        p = 0
        images_list = []
        while p < 4:
            name, voxels = load_random_model()

            dir = random.choice(['x', 'y', 'z'])
            proj2d = generate_projection_3d_2d(voxels, dir)
            # Check that it's different all previous ones
            add_new = True
            for image_prev in images_list:
                if np.linalg.norm(proj2d - image_prev) < 0.1:
                    add_new = False
            if add_new:
                images_list.append(proj2d)
                p += 1

        # The first one is the correct one
        image = images_list[0]

        # Then, shuffle
        np.random.shuffle(images_list)
        # Find correct index
        ind_correct = None
        for ind, image_shuffled in enumerate(images_list):
            if (image_shuffled == image).all():
                ind_correct = ind
                break

        fig = make_2D_options_plot(images_list)
        graphJSON_options = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
        print("2D generation complete")
    else:
        raise ValueError('Mode not supported; use 3D or 2D')

    return graphJSON_options, ind_correct, image

# Perform user-specified projection and return the plot to be added
def game8_worker_project(info,default=True):
    if default:
        return json.dumps(make_blank_plot('image'), cls=plotly.utils.PlotlyJSONEncoder)
    else:
        if info['mode'] == '2D':
            proj1d = generate_projection_2d_1d(img=info['image'],angle=info['proj1d_angle'])
            proj1d = (proj1d - np.min(proj1d))/(np.max(proj1d) - np.min(proj1d))
            graphJSON_image = plot_projection(proj1d, ['r'], info)
        elif info['mode'] == '3D':
            axes = list('xyz'.replace(info['proj2d_axis'], ''))
            proj2d = generate_projection_3d_2d(voxels=info['image'],axis=info['proj2d_axis'])
            graphJSON_image = plot_projection(proj2d, axes,info)
        else:
            raise ValueError('Mode must be 2D or 3D')

    return graphJSON_image

def load_random_model():
    # Pull model
    name = random.choice(GAME8_RANDOM_MODELS)
    # Get voxels
    voxels = np.load(DATA_PATH / 'solids' / f'{name}.npy')
    voxels = voxels[:100,:100,:100]
    return name, voxels

def make_3D_options_plot(names):
    layout = go.Layout(
                        margin=dict(l=2, r=2, b=2, t=2, pad=0),
                        paper_bgcolor='gainsboro',
                       title_x=0.5,
                       font_color='black',
                       scene_camera=dict(eye=dict(x=1.25, y=-1.25, z=1)),
                       scene_xaxis_visible=True,
                       scene_xaxis_showticklabels=False,
                       scene_yaxis_visible=True,
                       scene_yaxis_showticklabels=False,
                       scene_zaxis_visible=True,
                       scene_zaxis_showticklabels=False,
    )

    mesh_list = []

    for ind, name in enumerate(names):
        model_info = DATA_PATH / 'solids' / f'{name}.stl'
        x, y, z, I, J, K = load_3d_model(model_info)
        colorscale = [[0, 'lightblue'], [1, 'lightblue']]
        mesh_list.append(go.Mesh3d(
            x=x, y=y, z=z, i=I, j=J, k=K,
            flatshading=True,
            colorscale=colorscale,
            intensity=z,
            name='Phantom',
            showscale=False,
            opacity=0.5,
            alphahull=10, visible=(ind==0)))


    fig = go.Figure(data=mesh_list, layout=layout)  # Add each option

    for ind in range(4):
        fig.data[ind].update(lighting=dict(ambient=0.15,
                                         diffuse=0.9,
                                         fresnel=.1,
                                         specular=1,
                                         roughness=.1,
                                         facenormalsepsilon=0))
        fig.data[ind].update(lightposition=dict(x=3000,
                                              y=3000,
                                              z=10000))

    # Buttons
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                active=0,
                x=0.05,
                y=0.01,
                xanchor = "left",
                yanchor = "bottom",
                buttons=[
                    dict(label="Option A",
                         method="update",
                         args=[{'visible': [True, False, False, False]}]),
                    dict(label="Option B",
                         method="update",
                         args=[{'visible': [False, True, False, False]}]),
                    dict(label="Option C",
                         method="update",
                         args=[{'visible': [False, False, True, False]}]),
                    dict(label="Option D",
                         method="update",
                         args=[{'visible': [False, False, False, True]}])
                ],
            )
        ]
    )

    return fig

def make_2D_options_plot(images_list):
    fig = go.Figure()
    for ind, image in enumerate(images_list):
        proj = np.flipud(np.rot90(image))
        proj = np.flipud(proj)
        fig.add_trace(go.Heatmap(z=proj,colorscale="gray",showscale=False,visible=(ind==0)))
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(scaleanchor='x'), margin=dict(l=5, r=5, b=5, t=5, pad=0))

    # Buttons
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                active=0,
                x=0.05,
                y=0.01,
                xanchor="left",
                yanchor="top",
                buttons=[
                    dict(label="Option A",
                         method="update",
                         args=[{'visible': [True, False, False, False]}]),
                    dict(label="Option B",
                         method="update",
                         args=[{'visible': [False, True, False, False]}]),
                    dict(label="Option C",
                         method="update",
                         args=[{'visible': [False, False, True, False]}]),
                    dict(label="Option D",
                         method="update",
                         args=[{'visible': [False, False, False, True]}])
                ],
            )
        ]
    )
    return fig

def make_blank_plot(type="image"):
    if type == "image":
        fig = go.Figure(go.Heatmap(z=np.zeros((16,16)),colorscale="gray",showscale=False))
        fig.update_layout(plot_bgcolor = 'rgba(0,0,0,0)', yaxis = dict(scaleanchor='x'), height=300)
        fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)

    elif type == "signal":
        fig = go.Figure()
        fig.update_layout(width=500, height=350)
    else:
        raise ValueError("Type must be image or signal")

    fig.update_layout(margin=dict(l=0, r=0, b=0, t=0, pad=0))
    return fig


def plot_projection(proj,axes,info):
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
                          ),height=350)

        fig.add_trace(go.Scatter(x=[5],y=[95],mode="text",text=f'Axis {info["proj2d_axis"]}',
                                 textfont=dict(
                                     color="aquamarine",
                                     size=16),
                                 textposition="bottom right", showlegend=False
                                 ))
        fig.update_traces(showlegend=False)
        fig.update_xaxes(title=axes[0], showticklabels=False, range=[1, proj.shape[0]])
        fig.update_yaxes(title=axes[1], showticklabels=False, range=[1, proj.shape[1]])

    elif len(axes) == 1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=proj,mode='lines',line=dict(width=3,color='darkslateblue')))
        fig.add_trace(go.Scatter(x=[5],y=[0.9],mode="text",text=f'Angle = {info["proj1d_angle"]} deg',
                                 textfont=dict(
                                     color="goldenrod",
                                     size=16),
                                 textposition="bottom right",showlegend=False))

        fig.update_xaxes(title=axes[0])
        fig.update_yaxes(title='Relative amplitude')
        fig.update_layout(
                          margin=go.layout.Margin(
                              l=5,
                              r=5,
                              b=5,
                              t=5
                          ),height=350)
        fig.update_yaxes(range=[0,1])
        fig.update_traces(showlegend=False)

    else:
        fig = go.Figure()

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

