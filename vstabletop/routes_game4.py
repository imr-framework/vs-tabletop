
from flask import flash, render_template, session, redirect, url_for
from vstabletop.forms import *
from __main__ import app, login_manager, db, socketio


@app.route('/games/4',methods=["GET","POST"])
def game4():
    game4form = Game4Form()
    if game4form.validate_on_submit():
        # Run simulation
        print(f"Slice thickness selected: {game4form.thk_field.data} mm")
    #if 'fov_field' in request.form:
    #    print(f"I have got the fov = {request.form['fov_field']} mm data!")

    return render_template('game4.html',template_title="Fresh Blood",template_intro_text="See how flow changes MR signal!",
                           template_game_form=game4form, game_num=4)
