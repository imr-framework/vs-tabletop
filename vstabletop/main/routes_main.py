# routes_main.py
# Gehua Tong, June 2022
# Login, register, and calibration pages for Virtual Scanner Biobus Mode
import numpy as np
from flask import flash, render_template, session, redirect, url_for, request, Blueprint
from flask_login import login_required, login_user, logout_user, current_user
import vstabletop.utils as utils
from vstabletop.forms import *
from vstabletop.info import GAMES_DICT, GAMES_INFO
from vstabletop.models import db, User, Calibration, MultipleChoice, UserAuthEvent
import json
import plotly
import plotly.express as px
import pandas as pd
import re
import logging

from vstabletop.models import MultipleChoice
from vstabletop.auth_clerk import clerk_enabled, clerk_publishable_key, clerk_frontend_api, verify_clerk_token

bp_main = Blueprint('bp_main',__name__, template_folder="templates/main",url_prefix="")
logger = logging.getLogger(__name__)


def _clerk_template_context():
    return {
        "clerk_enabled": clerk_enabled(),
        "clerk_publishable_key": clerk_publishable_key(),
        "clerk_frontend_api": clerk_frontend_api(),
    }


def _safe_username(base):
    base = re.sub(r"[^a-zA-Z0-9_]", "", (base or "player")).lower()
    base = (base or "player")[:10]
    if len(base) < 3:
        base += "user"
    base = base[:10]
    candidate = base
    suffix = 1
    while User.query.filter_by(username=candidate).first() is not None:
        tail = str(suffix)
        candidate = f"{base[:max(1, 10-len(tail))]}{tail}"
        suffix += 1
    return candidate


def _log_auth_event(event_type, provider="local", user=None, email=None):
    """Persist auth event for signup/login/logout."""
    try:
        if user is not None:
            user_id = user.id
            username = user.username
            user_email = email or user.email
        else:
            sess_user = session.get("user") or {}
            user_id = sess_user.get("id")
            username = sess_user.get("username")
            user_email = email
        evt = UserAuthEvent(
            user_id=user_id,
            username=username,
            email=user_email,
            provider=provider,
            event_type=event_type,
        )
        db.session.add(evt)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.warning("[auth-event] failed to log %s/%s: %s", event_type, provider, e)


def initialize_parameters():
    #session.clear() # This line causes csrf_token to fail validation in the root / login route, so it's disabled
    session['scanningFID'] = False
    session['scanningFA'] = False
    session['calibration'] = {'f0':15e6, 'shimx':0.0, 'shimy':0.0, 'shimz':0.0, 'tx_amp': 0.5, 'rx_gain':3,
                              'autoscale':True, 'show_prev':False,
                              'TR':1, 'readout_dur':0.03, 'N_avg': 1, 'N_rep':1}
    session['display'] = {'autoscale':True, 'show_prev':False}
    session['user'] = {'id':None, 'username':None, 'date_joined':None, 'role':'None', 'game_status':4*[0]}
    session['username_display'] = 'admin'
    session['game1'] = {'FOV_scale': 0.128, 'Matrix_scale': 128, 'Voxel_scale': 0.001,'zero_fill': 128,
                        'Min_scale': 0.1, 'Max_scale': 0.9, 'P1_q': 'No', 'P2_q': 'No', 'P3_q': 'No',
                        'progress': utils.new_progress_of_game(1,MultipleChoice), 'mc_status_list': utils.num_questions_of_game(1,MultipleChoice)*[False],
                        'task_completed':0, 'star_count': 0, 'checked': 0}

    session['game2'] = {'data_left': None, 'scale_left': None, 'data_right': None, 'scale_right': None, 'source': 'preset',
                        'erase_mask': None,
                        # Image parameters
                        'image_wavelength': 1, 'image_wave_phase': 0, 'image_angle': 0,
                        # Signal parameters
                        'signal_scale': 1, 'signal_stretch':1, 'signal_shift': 0, 'signal_phase_mod': 0,
                        # K-space parameters
                        'kspace_angle': 0, 'kspace_ds_separation': 0.25,
                        # Spectrum parameters
                        'spectrum_scale':1, 'spectrum_stretch':1, 'spectrum_shift':0, 'spectrum_phase_mod':0,
                        # Task progress
                        'progress':utils.new_progress_of_game(2,MultipleChoice), 'task_completed': 0, 'mc_status_list': utils.num_questions_of_game(2,MultipleChoice)*[False]
                        }

    session['game3'] = {'options': 'T1', 'TR': 500, 'TE': 10, 'FA':90, 'P1_q': 'No', 'P2_q': 'No', 'P3_q': 'No', 'progress': utils.new_progress_of_game(3,MultipleChoice),
                        'mc_status_list': utils.num_questions_of_game(3,MultipleChoice)*[False], 'current_task': 1, 'completed_task': 0, 'star_count': 0,
                        'task_completed':0}

    session['game4'] = { 'mode':'bright','flow_on': False, 'flow_speed': 50,
                           'bright_thk': 5, 'bright_tr':250, 'bright_fa': 45, 'bright_te': 5,
                           'dark_thk': 5, 'dark_te': 50,
                           'thk':5,'fa':30,'tr':250,'te':5,
                           'T1': 2000, 'T2': 200, # T2s is always set to be the same proportion of T2
                         'progress':utils.new_progress_of_game(4,MultipleChoice),'task_completed':0,
                         'mc_status_list': utils.num_questions_of_game(4,MultipleChoice)*[False],'star_count':0}

    session['game5'] = {'b0_on': False, 'b0': 100.0,'coil_on': False, 'rot_frame_on': False, 'flip_angle': 90, 'rf_phase': 0.0,
                        'coil_dir': 'x', 'm_theta': 0.0, 'm_phi':0.0, 'm_size': 1, 'tx_on': False,
                        'M_init': np.array([[0],[0],[0]]), 'M_target': np.array(([0],[0],[0])),
                        'M_target_on': False,
                        'progress': utils.new_progress_of_game(5,MultipleChoice),
                        'mc_status_list': utils.num_questions_of_game(5,MultipleChoice)*[False],
                        'task_completed': 0}
    session['game6'] = {'mode':'T1', 'task':'sim',
                        't1_phantom':None, 't2_phantom':None, 't1_masks':None, 't2_masks': None,
                        'current_sphere': None,
                        't1_sim': 500, 't1_sim_dur': 1500,'t1_sim_mz0':0,'t1_sim_ti':200,
                        't2_sim': 50, 't2_sim_dur':150, 't2_sim_mx0':100,'t2_sim_te': 25,
                        't1_map_TIs': [], 't2_map_TEs': [],
                        't1_images':None, 't2_images': None,
                        't1_roi_signal': None, 't2_roi_signal': None,
                        't1w_roi_fit': None, 't2_roi_fit': None,
                        't1_map':None,'t2_map':None,
                        'progress':utils.new_progress_of_game(6,MultipleChoice),
                        'mc_status_list':utils.num_questions_of_game(6,MultipleChoice)*[False],
                        'task_completed': 0}
    session['game7'] = {'model':'letterN', 'proj2d_axis': 'z', 'proj1d_angle': 90,
                        'plot3d_visible':False, 'plot2d_visible':False, 'plot1d_visible':False,
                        'lines_on': False,
                        'progress': utils.new_progress_of_game(7,MultipleChoice),
                        'mc_status_list': utils.num_questions_of_game(7,MultipleChoice)*[False],
                        'task_completed': 0
                        }
    session['game8'] = { 'mode': '3D', 'ind_correct': None,
                        'loaded_model': None, 'image': None,
                        'loaded_3D': None, 'loaded_2D': None,
                         'proj2d_axis': 'z', 'proj1d_angle': 90,
                        'num_acquired_2d': 0, 'num_acquired_3d': 0,
                        'num_attempts_2d': 5, 'num_attempts_3d': 2,
                        'progress':utils.new_progress_of_game(8,MultipleChoice),
                         'mc_status_list':utils.num_questions_of_game(8,MultipleChoice)*[False],
                         'task_completed':0}



#@app.route('/logout')
@bp_main.route('/logout')
def logout():
    # Save user progress (Game 5 example)

    nums = [1,5]

    for num in nums:
        prog = session[f'game{num}']['progress']
        db.session.add(prog)
        try:
            db.session.commit()
            print("Progress saved!")
            print(prog)
        except Exception as e:
            print("Failed to save progress to database")
            print(e)
            db.session.rollback()


    user_for_log = current_user if current_user.is_authenticated else None
    _log_auth_event("logout", provider="local", user=user_for_log)
    logout_user()
    session.clear()
    # Force Clerk sign-out on next login page load to prevent auto re-login.
    return redirect(url_for("bp_main.login", logged_out="1"))

# Home
#@app.route('/index')
@bp_main.route('/index',methods=["GET","POST"])
@login_required
def index():
    return render_template("main/index.html",template_dict_games=GAMES_DICT,template_dict_info=GAMES_INFO)


# Login page
#@app.route('/',methods=["GET","POST"])
@bp_main.route('/',methods=["GET","POST"])
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('bp_main.index'))
    # Keep landing page accessible, but initialize session state only once.
    if 'user' not in session:
        initialize_parameters()
    return render_template('main/landing.html')


#@app.route('/login',methods=["GET","POST"])
@bp_main.route('/login',methods=["GET","POST"])
def login():
    if request.args.get("switch_account") == "1":
        logout_user()
        session.clear()
        initialize_parameters()

    if current_user.is_authenticated and request.args.get("logged_out") != "1":
        return redirect(url_for('bp_main.index'))
    login_form = Login_Form()

    if login_form.validate_on_submit():
        print('login validated')
        session['username_display'] = login_form.username_field.data
        session.modified = True
        # If login successful, redirect to main page
        # Check login against database
        user = User.query.filter_by(username=login_form.username_field.data).first()
        if user is not None and user.check_password(login_form.password_field.data):
            login_user(user)
            print('login success')
            flash("Login successful, welcome!")
            _log_auth_event("login", provider="local", user=user)
            session['user']['id'] = user.id
            session['user']['username'] = user.username
            session['user']['date_joined'] = user.joined_at
            session['user']['role'] = 'student'
            if user.username == 'admin':
                session['user']['role'] = 'administrator'

            session['game5']['progress'].user_id = user.id # Attach progress to user

            session.modified = True

            return redirect('index')
        # If login fails, show error message
        else:
            print('login failed')
            flash('Wrong credentials - login failed')
            return redirect(url_for('bp_main.login'))

    return render_template("main/login.html",template_login_form=login_form, **_clerk_template_context())

# template_title='login',
#                            template_intro_text="Log into Virtual Scanner Biobus",



# Register page
#@app.route('/register',methods=['GET','POST'])
@bp_main.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('bp_main.index'))
    reg_form = Register_Form()
    if reg_form.validate_on_submit(): #define user with data from form here:
        user = User(username=reg_form.username_field.data) # set user's password here:
        user.set_password(reg_form.password_field.data)
        db.session.add(user)
        try:
            db.session.commit()
            _log_auth_event("signup", provider="local", user=user)
        except:
            db.session.rollback()
        return redirect(url_for('bp_main.login'))
    elif request.method == 'POST' and not clerk_enabled():
        flash('Form is not validated; check your passwords!', 'danger')

    return render_template('main/register.html', title='Register', template_form=reg_form, **_clerk_template_context())


@bp_main.route('/auth/clerk/session', methods=['POST'])
def clerk_session_login():
    if not clerk_enabled():
        return {"ok": False, "error": "Clerk auth is disabled."}, 400
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return {"ok": False, "error": "Missing bearer token."}, 401
    token = auth_header.split(" ", 1)[1]
    try:
        claims = verify_clerk_token(token)
    except Exception as e:
        logger.warning("Clerk session verification failed: %s", e)
        return {"ok": False, "error": "Invalid token."}, 401

    clerk_id = claims.get("sub")
    if not clerk_id:
        return {"ok": False, "error": "Token missing subject."}, 401

    payload = request.get_json(silent=True) or {}
    email = payload.get("email") or claims.get("email_address")
    preferred_username = payload.get("username") or payload.get("name") or (email.split("@")[0] if email else None)

    user = User.query.filter_by(clerk_user_id=clerk_id).first()
    if user is None and email:
        user = User.query.filter_by(email=email).first()

    if user is None:
        user = User(username=_safe_username(preferred_username), email=email, clerk_user_id=clerk_id)
        # local password login is optional for Clerk users
        user.set_password(clerk_id)
        db.session.add(user)
        db.session.commit()
        _log_auth_event("signup", provider="clerk", user=user, email=email)
        logger.info("[Clerk] provisioned new local user id=%s username=%r", user.id, user.username)
    else:
        updated = False
        if not user.clerk_user_id:
            user.clerk_user_id = clerk_id
            updated = True
        if email and user.email != email:
            user.email = email
            updated = True
        if updated:
            db.session.commit()
            logger.info("[Clerk] updated local user id=%s username=%r", user.id, user.username)
        else:
            logger.info("[Clerk] reused existing local user id=%s username=%r", user.id, user.username)

    # Clerk flow can hit this endpoint before landing/login initialized session keys.
    if "user" not in session or "game5" not in session:
        initialize_parameters()

    login_user(user)
    _log_auth_event("login", provider="clerk", user=user, email=email)
    session['user']['id'] = user.id
    session['user']['username'] = user.username
    session['user']['date_joined'] = user.joined_at
    session['user']['role'] = 'administrator' if user.username == 'admin' else 'student'
    session['game5']['progress'].user_id = user.id
    session.modified = True
    return {"ok": True, "redirect": url_for('bp_main.index')}


@bp_main.route('/auth/clerk/logout', methods=['POST'])
def clerk_logout():
    user_for_log = current_user if current_user.is_authenticated else None
    _log_auth_event("logout", provider="clerk", user=user_for_log)
    logout_user()
    session.clear()
    return {"ok": True}

# TODO calibration tunings - #4 save to file
# 4. "Save to file" / "Load" buttons split the current "load previous" one
#     save to file - > outputs as config file apart from config.py
#     load - > load a config file to (a) config.py (b) session

#@app.route('/calibration',methods=["GET","POST"])
@bp_main.route('calibration',methods=["GET","POST"])

def calibration():
    #if request.method == 'POST':
     #   print(request.form['xshim'])
    calib_form = Calibration_Form()
    display_opts_form = Display_Opts_Form()

    # Deal with calibration parameters
    if calib_form.validate_on_submit():
        print('Calibration validated')
        # Save to database
        # Change to : save to yaml / xml /... file format.
        new_calibration = Calibration(f0=calib_form.f0_field.data, shimx=calib_form.shimx_field.data,
                                      shimy=calib_form.shimy_field.data, shimz=calib_form.shimz_field.data,
                                      tx_amp=calib_form.tx_amp_field.data)
        params = new_calibration.get_config_dict()
        utils.update_configuration(params,"config.py")

        # TODO call save to config file format function here...

        db.session.add(new_calibration)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        # Update session with hardware parameters
        utils.update_session_subdict(session,'calibration', params)
        print(f"session f0 updated to {session['calibration']['f0']}")

        # Sequence parameters (all times are converted to seconds)
        params_seq = {'TR': calib_form.tr_field.data / 1e3,
                      'readout_dur': calib_form.readout_time_field.data / 1e3,
                      'N_avg': calib_form.num_avg_field.data,
                      'N_rep': calib_form.num_rep_field.data}
        # Update session with sequence parameters
        utils.update_session_subdict(session, 'calibration', params_seq)

        flash(f"Parameters saved: f0 = {params['f0']}, shimx = {params['shimx']}, shimy={params['shimy']}, \
          tx amp = {params['tx_amp']}; sequence settings : TR = {params_seq['TR']} s, readout duration = {params_seq['readout_dur']} s, \
          number of averages {params_seq['N_avg']}, number of repetitions {params_seq['N_rep']}")

    # Default plots with no content to be displayed initially
    j1, j2, j3 = get_empty_calibration_plots()

    return render_template("main/calibration.html", template_intro_text="Let's calibrate the scanner!",
                           template_calibration_form=calib_form, template_disp_form=display_opts_form,
                           graphJSON_left=j1, graphJSON_center=j2,graphJSON_right=j3)

#
# # When client says RUN, we run.
# @socketio.on('run scans')
# def pump_out_fake_plots(payload):
#     # Parse parameters and save to session
#     utils.update_session_subdict(session,'calibration',payload)
#     # Initiate the thread only if we are not scanning now
#     if not session.get('scanningFID'): # If FID plots are not running, create thread to do that.
#         print("MAKING A NEW THREAD")
#         calib_thread = SignalPlotsThread(session['calibration']['f0'])
#         calib_thread.start()
#         session['scanningFID'] = True
#         session.modified = True
#     else:
#         print('we are in else')
#         for th in threading.enumerate():
#             if hasattr(th,'f0'):
#                 th.set_f0(session['calibration']['f0'])
#
#     socketio.emit('take this',{'data':'THE SOCKET IS WORKING'})
#
# # When client says STOP, we stop.
# @socketio.on('stop scans')
# def stop_the_fake_plots(message):
#     print(message['data'])
#     for th in threading.enumerate():
#         if hasattr(th,'f0'):
#             th.raise_exception()
#             th.join()
#         if hasattr(th,'tx_amp_90'): # FA thread
#             th.raise_exception()
#             th.join()
#
#     session['scanningFID'] = False
#     session.modified = True
#     session['scanningFA'] = False
#     session.modified = True
#
#
# # Run FA calibration
# @socketio.on('run FA')
# def run_fake_FA_calibration(message):
#     print(message['data'])
#     # Get a FA plot
#     if not session.get('scanningFA'):
#         fa_thread = FlipAnglePlotThread(tx_amp_90=3, tx_amp_max=10, Npts=50)
#         # Preset - TODO incorporate as options?
#         fa_thread.start()
#         session['scanningFA'] = True
#         session.modified = True
#
#
# @socketio.on('zero shims')
# def zero_shims(message):
#     print(message['data'])
#     # This is another example of updating the session with newly zeroed shim values
#     utils.update_session_subdict(session,'calibration',{'shimx':0.0,'shimy':0.0,'shimz':0.0})
#
# #  Rishi: this decorated function (the "@" line is the decorator) does the following:
# #        1. It is run when socketio receives 'update single param' from the client
# #        2. The data being sent over is passed as the "info" parameter
# #        3. If the info is central frequency, f0, it scales it by 1e6 for unit conversion from MHz to Hz
# #        4. A Python dictionary, param, is created where the key is still the id and the value is converted into float
# #        5. It updates the session dictionary using a function from utils.py
# #        6. It finds a thread that has the f0 attribute and updates its f0
# #           (this is for continuously updating the leftmost plot on the calibration page)
#
# # Update signal parameters on change
# @socketio.on('update single param')
# def update_parameter(info):
#     if info['id'] == 'f0':
#         info['value'] = float(info['value'])*1e6
#     param = {info['id']:float(info['value'])}
#     utils.update_session_subdict(session,'calibration',param)
#     # TODO This line is needed to update session variables
#     # Update thread
#     for th in threading.enumerate():
#         if hasattr(th, 'f0'):
#             th.set_f0(session['calibration']['f0'])


# Dev route for new features
#@app.route('/examples',methods=['POST','GET'])
@bp_main.route('/examples',methods=['POST','GET'])
def example_elements():
    return render_template('main/examples.html',template_title="UI Element Examples",
                           template_intro_text="For developer use")





def get_empty_calibration_plots():
    df = pd.DataFrame({'t':[],'fid':[],'f':[],'spectrum':[]})
    df2 = pd.DataFrame({'tx_model':[], 'tx_signal':[]})

    fig_fid = px.line(df,x='t',y='fid')
    fig_spectrum = px.line(df,x='f',y='spectrum')
    fig_fa_calib = px.scatter(df2, x='tx_model',y='tx_signal')
    graphJSON1 = json.dumps(fig_fid,cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON2 = json.dumps(fig_spectrum,cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON3 = json.dumps(fig_fa_calib,cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON1, graphJSON2, graphJSON3
