import threading

from flask import flash, render_template, session, redirect, url_for
from flask_login import login_required, login_user, logout_user
import utils
from forms import *
from info import GAMES_DICT
from models import User, Calibration
from __main__ import app, login_manager, db, socketio


# Games
@app.route('/games/1',methods=["GET","POST"])
def game1():
    return render_template('game1.html',template_title="What is in an image?",template_intro_text="Voxels, field-of-views, and resolution ",template_game_form=None)


@app.route('/games/2',methods=["GET","POST"])
def game2():
    return render_template('game2.html',template_title="K-space magik",template_intro_text="Can you find your way?",template_game_form=None)


@app.route('/games/3',methods=["GET","POST"])
def game3():
    return render_template('game3.html',template_title="Brains, please!",template_intro_text="Of mice and men",
                           template_game_form=None)


@app.route('/games/4',methods=["GET","POST"])
def game4():
    game4form = Game4Form()
    if game4form.validate_on_submit():
        # Run simulation
        print(f"Slice thickness selected: {game4form.thk_field.data} mm")
    #if 'fov_field' in request.form:
    #    print(f"I have got the fov = {request.form['fov_field']} mm data!")

    return render_template('game4.html',template_title="Fresh Blood",template_intro_text="See how flow changes MR signal!",
                           template_game_form=game4form)


@app.route('/games/6',methods=["GET","POST"])
def game6():
    return render_template('game6.html',template_title="Relaxation station",template_intro_text="Sit back and map",template_game_form=None)


@app.route('/games/7',methods=["GET","POST"])
def game7():
    return render_template('game7.html',template_title="Puzzled by Projection I",template_intro_text="Forward puzzle",template_game_form=None)


@app.route('/games/8',methods=["GET","POST"])
def game8():
    return render_template('game8.html',template_title="Puzzled by Projection II",template_intro_text="Backward puzzle",template_game_form=None)
