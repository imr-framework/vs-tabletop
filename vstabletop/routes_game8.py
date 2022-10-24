
from flask import flash, render_template, session, redirect, url_for
from __main__ import app
from vstabletop.forms import Game8Form
from vstabletop.workers.game6_worker import game6_worker_sim

@app.route('/games/8',methods=["GET","POST"])
def game8():
    game8form = Game8Form()

    # Simulate initial


    return render_template('game8.html',template_title="Puzzled by Projection II",template_intro_text="Backward puzzle",
                           template_game_form=game8form,game_num=8)

