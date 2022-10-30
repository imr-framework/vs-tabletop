
from flask import flash, render_template, session, redirect, url_for
from __main__ import app, login_manager, db, socketio
from vstabletop.workers.game6_worker import game6_worker_sim,game6_worker_map,initialize_phantom, calculate_circle
from vstabletop.forms import Game6Form
import vstabletop.utils as utils
from vstabletop.info import GAME6_INFO

DEFAULT_TIS = [5,10,20,50,100,500] # Seconds
DEFAULT_TES = [8,16,24,32,64,128] # Seconds
@app.route('/games/6',methods=["GET","POST"])
def game6():
    initialize_phantom(session)
    utils.update_session_subdict(session,'game6',{'type':'sim','t1_map_TIs': DEFAULT_TIS,'t2_map_TEs': DEFAULT_TES})
    game6form = Game6Form()
    j1,j2,j3 = game6_worker_sim(session['game6'])


    return render_template('game6.html',template_title="Relaxation station",template_intro_text="Sit back and map",
                           template_game_form=game6form, game_num=6,
                           graphJSON_left=j1, graphJSON_middle=j2, graphJSON_right=j3)

@socketio.on('Change to T1')
def change_to_T1(payload):
    # Deliver plots
    utils.update_session_subdict(session,'game6',{'mode':'T1'})
    if session['game6']['type'] == 'sim':
        j1,j2,j3 = game6_worker_sim(session['game6'])
    else:
        j1,j2,j3 = game6_worker_map(session,update_list={'images':'blank','roi':'blank','map':'blank'},
                                                     display_list=[True,True,True])

    socketio.emit('Update plots',{'plots':{'left':j1, 'middle':j2, 'right':j3},'disp':{'left':True,'middle':True,'right':True}})

@socketio.on('Change to T2')
def change_to_T2(payload):
    utils.update_session_subdict(session,'game6',{'mode':'T2'})

    if session['game6']['type'] == 'sim':
        j4,j5,j6 = game6_worker_sim(session['game6'])
    else:
        j4,j5,j6 = game6_worker_map(session,update_list={'images':'blank','roi':'blank','map':'blank'},
                                                 display_list=[True,True,True])
    socketio.emit('Update plots',{'plots':{'left':j4, 'middle':j5, 'right':j6},'disp':{'left':True,'middle':True,'right':True}})

@socketio.on('Change to simulation mode')
def change_to_simulation():
    utils.update_session_subdict(session,'game6',{'type':'sim'})
    j1,j2,j3 = game6_worker_sim(session['game6'])
    socketio.emit('Update plots',{'plots':{'left':j1, 'middle':j2, 'right':j3},'disp':{'left':True,'middle':True,'right':True}})

@socketio.on("Change to mapping mode")
def change_to_mapping():
    print('changing to mapping')
    utils.update_session_subdict(session,'game6',{'type':'map'})
    # TODO change update list
    j1,j2,j3 = game6_worker_map(session,update_list={'images':'blank','roi':'blank','map':'blank'},
                                                 display_list=[True,True,True])

    socketio.emit('Update plots',{'plots':{'left': j1, 'middle': j2, 'right': j3}, 'disp':{'left':True,'middle':True,'right':True}})

@socketio.on("Scan T1")
def scan_t1(payload):
    ti_array_str = payload['ti_array_text'].split(',')
    ti_array = [float(ti) for ti in ti_array_str]
    utils.update_session_subdict(session,'game6',{'t1_map_TIs':ti_array})

    j1,j2,j3 = game6_worker_map(session,update_list={'images':'new','roi':None,'map':None},display_list=[True,False,False])
    socketio.emit('Update plots', {'plots':{'left': j1, 'middle': j2, 'right': j3}, 'disp':{'left':True,'middle':False,'right':False}})

@socketio.on("Scan T2")
def scan_t2(payload):
    te_array_str = payload['te_array_text'].split(',')
    te_array = [float(te) for te in te_array_str]
    utils.update_session_subdict(session,'game6',{'t2_map_TEs': te_array})

    j1,j2,j3 = game6_worker_map(session,update_list={'images':'new','roi':None,'map':None},display_list=[True,False,False])
    socketio.emit('Update plots', {'plots':{'left': j1, 'middle': j2, 'right': j3}, 'disp':{'left':True,'middle':False,'right':False}})


@socketio.on('Fit T1')
def fit_t1(payload):
    print(f"T1 fit requested for sphere {payload['sphere']}")
    j1,j2,j3 = game6_worker_map(session,update_list={'images': None, 'roi': 'fit', 'map':None},
                                        display_list=[False,True,False])
    socketio.emit('Update plots', {'plots':{'left': j1, 'middle': j2, 'right': j3}, 'disp':{'left':False,'middle':True,'right':False}})

@socketio.on('Fit T2')
def fit_t2(payload):
    print(f"T2 fit requested for sphere {payload['sphere']}")
    j1,j2,j3 = game6_worker_map(session,update_list={'images': None, 'roi': 'fit', 'map':None},
                                        display_list=[False,True,False])
    socketio.emit('Update plots', {'plots':{'left': j1, 'middle': j2, 'right': j3}, 'disp':{'left':False,'middle':True,'right':False}})

@socketio.on('Map T1')
def map_t1(payload):
    print(f'T1 map calculation requested!')
    j1,j2,j3 = game6_worker_map(session,update_list={'images':None, 'roi': None, 'map': 'new'},
                                        display_list=[False,False,True])
    socketio.emit('Reset T1 map button')
    socketio.emit('Update plots', {'plots':{'left': j1, 'middle': j2, 'right': j3}, 'disp':{'left':False,'middle':False,'right':True}})

@socketio.on('Map T2')
def map_t2(payload):
    print(f'T2 map calculation requested!')
    j1,j2,j3 = game6_worker_map(session,update_list={'images':None, 'roi': None, 'map': 'new'},
                                        display_list=[False,False,True])
    socketio.emit('Reset T2 map button')
    socketio.emit('Update plots', {'plots':{'left': j1, 'middle': j2, 'right': j3}, 'disp':{'left':False,'middle':False,'right':True}})


@socketio.on('Find T1 ROI signal')
def find_T1_ROI_signal(payload):
    ind = int(payload['sphere'])
    # Update session and get the plots
    utils.update_session_subdict(session,'game6',{'current_sphere': ind })
    j1,j2,j3 = game6_worker_map(session,update_list={'images':None,'roi':'new','map':None},display_list=[False,True,False])
    socketio.emit('Update plots', {'plots':{'left': j1, 'middle': j2, 'right': j3}, 'disp':{'left':False,'middle':True,'right':False}})
    # Send message to add corresponding circle to left plot
    c, r = calculate_circle(type="T1",sphere=ind)
    socketio.emit('Add circle to image',{'center': c, 'radius': r})

@socketio.on('Find T2 ROI signal')
def find_T2_ROI_signal(payload):
    ind = int(payload['sphere'])
    utils.update_session_subdict(session, 'game6', {'current_sphere': ind})
    j1, j2, j3 = game6_worker_map(session, update_list={'images': None, 'roi': 'new', 'map': None},
                                  display_list=[False, True, False])
    socketio.emit('Update plots', {'plots': {'left': j1, 'middle': j2, 'right': j3},
                                   'disp': {'left': False, 'middle': True, 'right': False}})
    # Send message to add corresponding circle to left plot
    print(f'calculating circle #{ind}')
    c, r = calculate_circle(type="T2", sphere=ind)
    socketio.emit('Add circle to image', {'center': c, 'radius': r})


@socketio.on('T1 switch to phantom')
@socketio.on('T2 switch to phantom')
def t1_switch_to_phantom():
    j1, j2, j3 = game6_worker_map(session, update_list={'images': None, 'roi': None, 'map': 'phantom'},
                                  display_list=[False, False, True])
    socketio.emit('Update plots', {'plots': {'left': j1, 'middle': j2, 'right': j3},
                                   'disp': {'left': False, 'middle': False, 'right': True}})

@socketio.on('T1 switch to map')
@socketio.on('T2 switch to map')
def t1_switch_to_map():
    j1, j2, j3 = game6_worker_map(session, update_list={'images': None, 'roi': None, 'map': 'mapped'},
                                  display_list=[False, False, True])
    socketio.emit('Update plots', {'plots': {'left': j1, 'middle': j2, 'right': j3},
                                   'disp': {'left': False, 'middle': False, 'right': True}})

@socketio.on('Update parameter for Game 6')
def update_parameters_game4(info):
    utils.update_session_subdict(session,'game6',{info['id']:float(info['value'])})
    print('g6 param updated!',session['game6'])

