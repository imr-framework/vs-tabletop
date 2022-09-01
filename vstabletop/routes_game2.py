from vstabletop.workers.game2_worker import make_empty_graphs, game2_worker_fetch, \
                                            game2_worker_convert, make_graph,\
                                            convert_2d_drawing, convert_1d_drawing

from flask import flash, render_template, session, redirect, url_for
from urllib.request import urlopen

from forms import Game2Form
import vstabletop.utils as utils
from vstabletop.paths import DATA_PATH

from __main__ import app, login_manager, db, socketio

# Games
@app.route('/games/2',methods=["GET","POST"])
def game2():
    G2Form = Game2Form()
    j1, j2 = make_empty_graphs()

    return render_template('game2.html',template_title="K-space magik",template_intro_text="Can you find your way?",
                           template_game_form=G2Form, graphJSON_left=j1, graphJSON_right=j2,
                           game_num=2)

# Socket
@socketio.on('Request signal')
def generate_new_signal(payload):
    print(f"Signal [{payload['name']}] requested")
    graphJSON, data, scale = game2_worker_fetch('original',1,name=payload['name'])
    # Save state to session
    utils.update_session_subdict(session,'game2',{'data_left': data, 'scale_left': scale})
    socketio.emit('Deliver signal',{'graph': graphJSON})

# Socket
@socketio.on('Request image')
def generate_new_image(payload):
    print(f"Image [{payload['name']}] requested")
    graphJSON, data, scale = game2_worker_fetch('original',2,name=payload['name'])
    utils.update_session_subdict(session,'game2',{'data_left': data, 'scale_left': scale})
    socketio.emit('Deliver image',{'graph': graphJSON})


# Socket
@socketio.on('Request spectrum')
def generate_new_spectrum(payload):
    print(f"Spectrum [{payload['name']}] requested")
    graphJSON, data, scale = game2_worker_fetch('frequency',1,name=payload['name'])
    utils.update_session_subdict(session,'game2',{'data_right': data, 'scale_right': scale})
    socketio.emit('Deliver spectrum',{'graph': graphJSON})


# Socket
@socketio.on('Request kspace')
def generate_new_kspace(payload):
    print(f"Kspace [{payload['name']}] requested")
    graphJSON, data, scale = game2_worker_fetch('frequency',2,name=payload['name'])
    utils.update_session_subdict(session,'game2',{'data_right': data, 'scale_right': scale})
    socketio.emit('Deliver kspace',{'graph':  graphJSON})

@socketio.on('Perform forward transform')
def forward_transform():
    # Use current session info
    input = session['game2']['data_left']
    scale = session['game2']['scale_left']


    graphJSON, data, scale = game2_worker_convert(input, scale, forward=True)

    utils.update_session_subdict(session,'game2',{'data_right': data, 'scale_right': scale})

    if len(input.shape) == 2:
        socketio.emit('Deliver kspace',{'graph': graphJSON})
    elif len(input.shape) == 1:
        socketio.emit('Deliver spectrum',{'graph':graphJSON})

@socketio.on('Perform backward transform')
def backward_transform():
    # Use current session info
    input = session['game2']['data_right']
    scale = session['game2']['scale_right']

    graphJSON, data, scale = game2_worker_convert(input, scale, forward=False)

    # Update session too.
    utils.update_session_subdict(session,'game2',{'data_left': data, 'scale_left': scale})


    if len(input.shape) == 2:
        socketio.emit('Deliver image',{'graph': graphJSON})
    elif len(input.shape) == 1:
        socketio.emit('Deliver signal',{'graph':graphJSON})


@socketio.on('Send 2D drawing')
def process_2D_drawing(payload):
    # Read data url and save as png file
    img_url = payload['url']
    with urlopen(img_url) as response:
        data = response.read()
    with open(DATA_PATH / 'Game2' / 'drawing2D.png','wb') as f:
        f.write(data)

    graphJSON, data, scale = convert_2d_drawing(DATA_PATH / 'Game2' / 'drawing2D.png', 'image')
    utils.update_session_subdict(session,'game2',{'data_left': data, 'scale_left': scale})
    socketio.emit('Deliver image', {'graph': graphJSON})


@socketio.on('Send 1D drawing')
def process_1d_drawing(payload):
    img_url = payload['url']
    with urlopen(img_url) as response:
        data = response.read()
    with open(DATA_PATH / 'Game2' / 'drawing1D.png','wb') as f:
        f.write(data)

    graphJSON, data, scale = convert_1d_drawing(DATA_PATH / 'Game2' / 'drawing1D.png', 'image')
    utils.update_session_subdict(session,'game2',{'data_left': data, 'scale_left': scale})
    socketio.emit('Deliver image', {'graph': graphJSON})
