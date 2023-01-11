
from flask import flash, render_template, session, redirect, url_for
from vstabletop.forms import *
from __main__ import app, login_manager, db, socketio
from vstabletop.workers.game4_worker import game4_worker_simulation, game4_worker_image
import vstabletop.utils as utils

@app.route('/games/4',methods=["GET","POST"])
def game4():
    # Input fields
    game4form = Game4Form()

    # Default plotss
    # mm/s, mm, ms, deg
    info = session['game4']

    # Create initial plots
    j1, j2 = game4_worker_simulation('bright',info)
    j3, j4 = game4_worker_simulation('dark',info)
    j5 = game4_worker_image(session['game4']['mode'],info)


    return render_template('game4.html',template_title="Fresh Blood",template_intro_text="See how flow changes MR signal!",
                           template_game_form=game4form, game_num=4,
                           graphJSON_top_bright=j1, graphJSON_bottom_bright=j2,
                           graphJSON_top_dark=j3, graphJSON_bottom_dark=j4,
                           graphJSON_image=j5)


# Update session with input parameters
@socketio.on('Update parameter for Game 4')
def update_parameters_game4(info):
    if info['id'] not in ['contrast-type']:
        utils.update_session_subdict(session,'game4',{info['id']:float(info['value'])})
    else:
        utils.update_session_subdict(session,'game4',{'mode':info['value']})

@socketio.on('Flow on')
def turn_on_flow(info):
    mode = info['mode']
    utils.update_session_subdict(session,'game4',{'flow_on':True})

    if mode == 'bright':
        # Run flow simulation
        j1, j2 = game4_worker_simulation(mode, session['game4'])
        socketio.emit('Deliver bright plots',{'graph1':j1,'graph2':j2})
    elif mode == 'dark':
        j3, j4 = game4_worker_simulation(mode, session['game4'])
        socketio.emit('Deliver dark plots', {'graph3': j3,'graph4':j4})



@socketio.on('Flow off')
def turn_off_flow():
    utils.update_session_subdict(session,'game4',{'flow_on':False})

@socketio.on('Simulate flow image')
def update_flow_image(payload):
    info = session['game4']
    for id in ['te','tr','thk','fa']:
        print(payload)
        info[id] = float(payload[id])
    utils.update_session_subdict(session,'game4',info)

    j5 = game4_worker_image(session['game4']['mode'],info)
    socketio.emit('Deliver flow image', {'graph5' : j5})

