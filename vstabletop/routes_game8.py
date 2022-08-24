
from flask import flash, render_template, session, redirect, url_for
from __main__ import app


@app.route('/games/8',methods=["GET","POST"])
def game8():
    return render_template('game8.html',template_title="Puzzled by Projection II",template_intro_text="Backward puzzle",
                           template_game_form=None,game_num=8)
