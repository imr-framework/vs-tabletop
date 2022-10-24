
from flask import flash, render_template, session, redirect, url_for
from __main__ import app, login_manager, db, socketio
from vstabletop.workers.game6_worker import game6_worker_sim,game6_worker_map
from vstabletop.forms import Game6Form
import vstabletop.utils as utils

@app.route('/games/6',methods=["GET","POST"])
def game6():

    game6form = Game6Form()
    j1,j2,j3 = game6_worker_sim(session['game6'])


    return render_template('game6.html',template_title="Relaxation station",template_intro_text="Sit back and map",
                           template_game_form=game6form, game_num=6,
                           graphJSON_left=j1, graphJSON_middle=j2, graphJSON_right=j3)

@socketio.on('Change to T1')
def change_to_T1(payload):
    # Deliver plots
    utils.update_session_subdict(session,'game6',{'mode':'T1'})
    j1,j2,j3 = game6_worker_sim(session['game6'])
    socketio.emit('Update plots',{'left':j1, 'middle':j2, 'right':j3})

@socketio.on('Change to T2')
def change_to_T2(payload):
    utils.update_session_subdict(session,'game6',{'mode':'T2'})
    j4,j5,j6 = game6_worker_sim(session['game6'])
    socketio.emit('Update plots',{'left':j4, 'middle':j5, 'right':j6})



