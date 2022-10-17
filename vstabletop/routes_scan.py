
from flask import flash, render_template, session, redirect, url_for
from __main__ import app, login_manager, db, socketio



@app.route('/scan',methods=["GET","POST"])
def scan():
    return render_template('scan.html',template_game_form=None, game_num=None)

