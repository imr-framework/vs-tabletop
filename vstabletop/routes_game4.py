
from flask import flash, render_template, session, redirect, url_for
from vstabletop.forms import *
from __main__ import app, login_manager, db, socketio
from vstabletop.workers.game4_worker import game4_worker_simulation, game4_worker_image
import vstabletop.utils as utils

@app.route('/games/4',methods=["GET","POST"])
def game4():
    game4form = Game4Form()
    if game4form.validate_on_submit():
        # Run simulation
        print(f"Slice thickness selected: {game4form.thk_field.data} mm")

    # Default plotss
    info = {'flow_speed':2e-3, 'bright_thk':10e-3,'bright_tr':1,'bright_fa':30,
            'dark_thk':10e-3}
    j1, j2 = game4_worker_simulation('bright',info)
    j3, j4 = game4_worker_simulation('dark',info)
    j5 = game4_worker_image('empty')


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
        print(session['game4'])

@socketio.on('Flow on')
def turn_on_flow():
    utils.update_session_subdict(session,'game4',{'flow_on':True})

@socketio.on('Flow off')
def turn_off_flow():
    utils.update_session_subdict(session,'game4',{'flow_on':False})

