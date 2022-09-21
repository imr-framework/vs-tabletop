# routes_main.py
# Gehua Tong, June 2022
# Login, register, and calibration pages for Virtual Scanner Biobus Mode
import numpy as np
import threading
from flask import flash, render_template, session, redirect, url_for, request
from flask_login import login_required, login_user, logout_user
import vstabletop.utils as utils
from vstabletop.forms import *
from vstabletop.info import GAMES_DICT, GAMES_INFO
# TODO
from vstabletop.models import User, Calibration
from vstabletop.fake_data_generator import get_fake_calibration_plots, SignalPlotsThread, FlipAnglePlotThread, get_empty_calibration_plots
from __main__ import app, login_manager, db, socketio


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
                        'progress': utils.new_progress_of_game(1), 'mc_status_list': utils.num_questions_of_game(1)*[False],
                        'current_task': 1, 'completed_task': 0, 'star_count': 0, 'checked': 0}
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
                        'progress':utils.new_progress_of_game(2), 'task_completed': 0, 'mc_status_list': utils.num_questions_of_game(2)*[False]
                        }

    session['game3'] = {'options': 'T1', 'TR': 500, 'TE': 10, 'FA':90, 'P1_q': 'No', 'P2_q': 'No', 'P3_q': 'No', 'progress': utils.new_progress_of_game(3),
                        'mc_status_list': utils.num_questions_of_game(1)*[False], 'current_task': 1, 'completed_task': 0, 'star_count': 0}
    session['game4'] = {

                         'progress':utils.new_progress_of_game(4),'task_completed':0,
                        }
    session['game5'] = {'b0_on': False, 'b0': 100.0,'coil_on': False, 'rot_frame_on': False, 'flip_angle': 90, 'rf_phase': 0.0,
                        'coil_dir': 'x', 'm_theta': 0.0, 'm_phi':0.0, 'm_size': 1, 'tx_on': False,
                        'M_init': np.array([[0],[0],[0]]), 'M_target': np.array(([0],[0],[0])),
                        'M_target_on': False,
                        'progress': utils.new_progress_of_game(5), 'mc_status_list': utils.num_questions_of_game(5)*[False],
                        'task_completed': 0}
    session['game6'] = {'progress':utils.new_progress_of_game(6)}
    session['game7'] = {'model':'letterN', 'proj2d_axis': 'z', 'proj1d_angle': 90,
                        'plot3d_visible':False, 'plot2d_visible':False, 'plot1d_visible':False,
                        'lines_on': False,
                        'progress': utils.new_progress_of_game(7),'mc_status_list': utils.num_questions_of_game(7)*[False],
                        'task_completed': 0
                        }
    session['game8'] = {'progress':utils.new_progress_of_game(8)}

# Login callback (required)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

@app.route('/logout')
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


    logout_user()
    return redirect(url_for("landing"))

# Home
@app.route('/index')
@login_required
def index():
    return render_template("index.html",template_dict_games=GAMES_DICT,template_dict_info=GAMES_INFO)


# Login page
@app.route('/',methods=["GET","POST"])
def landing():
    initialize_parameters()
    return render_template('landing.html')


@app.route('/login',methods=["GET","POST"])
def login():
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
            return redirect(url_for('login'))

    return render_template("login.html",template_login_form=login_form)

# template_title='login',
#                            template_intro_text="Log into Virtual Scanner Biobus",



# Register page
@app.route('/register',methods=['GET','POST'])
def register():
    reg_form = Register_Form()
    print('on register page...')

    if request.method == 'POST':
        print(request.form)

    if reg_form.validate_on_submit(): #define user with data from form here:
        print("Validated!")
        user = User(username=reg_form.username_field.data) # set user's password here:
        user.set_password(reg_form.password_field.data)
        db.session.add(user)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        return redirect(url_for('login'))
    else:
        print("Failed to validate")
        flash('Form is not validated; check your passwords!')

    return render_template('register.html', title='Register', template_form=reg_form)

# TODO calibration tunings - #4 save to file
# 4. "Save to file" / "Load" buttons split the current "load previous" one
#     save to file - > outputs as config file apart from config.py
#     load - > load a config file to (a) config.py (b) session

@app.route('/calibration',methods=["GET","POST"])
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

    return render_template("calibration.html", template_intro_text="Let's calibrate the scanner!",
                           template_calibration_form=calib_form, template_disp_form=display_opts_form,
                           graphJSON_left=j1, graphJSON_center=j2,graphJSON_right=j3)




# When client says RUN, we run.
@socketio.on('run scans')
def pump_out_fake_plots(payload):
    # Parse parameters and save to session
    utils.update_session_subdict(session,'calibration',payload)
    # Initiate the thread only if we are not scanning now
    if not session.get('scanningFID'): # If FID plots are not running, create thread to do that.
        print("MAKING A NEW THREAD")
        calib_thread = SignalPlotsThread(session['calibration']['f0'])
        calib_thread.start()
        session['scanningFID'] = True
        session.modified = True
    else:
        print('we are in else')
        for th in threading.enumerate():
            if hasattr(th,'f0'):
                th.set_f0(session['calibration']['f0'])

    socketio.emit('take this',{'data':'THE SOCKET IS WORKING'})

# When client says STOP, we stop.
@socketio.on('stop scans')
def stop_the_fake_plots(message):
    print(message['data'])
    for th in threading.enumerate():
        if hasattr(th,'f0'):
            th.raise_exception()
            th.join()
        if hasattr(th,'tx_amp_90'): # FA thread
            th.raise_exception()
            th.join()

    session['scanningFID'] = False
    session.modified = True
    session['scanningFA'] = False
    session.modified = True


# Run FA calibration
@socketio.on('run FA')
def run_fake_FA_calibration(message):
    print(message['data'])
    # Get a FA plot
    if not session.get('scanningFA'):
        fa_thread = FlipAnglePlotThread(tx_amp_90=3, tx_amp_max=10, Npts=50)
        # Preset - TODO incorporate as options?
        fa_thread.start()
        session['scanningFA'] = True
        session.modified = True


@socketio.on('zero shims')
def zero_shims(message):
    print(message['data'])
    # This is another example of updating the session with newly zeroed shim values
    utils.update_session_subdict(session,'calibration',{'shimx':0.0,'shimy':0.0,'shimz':0.0})

#  Rishi: this decorated function (the "@" line is the decorator) does the following:
#        1. It is run when socketio receives 'update single param' from the client
#        2. The data being sent over is passed as the "info" parameter
#        3. If the info is central frequency, f0, it scales it by 1e6 for unit conversion from MHz to Hz
#        4. A Python dictionary, param, is created where the key is still the id and the value is converted into float
#        5. It updates the session dictionary using a function from utils.py
#        6. It finds a thread that has the f0 attribute and updates its f0
#           (this is for continuously updating the leftmost plot on the calibration page)

# Update signal parameters on change
@socketio.on('update single param')
def update_parameter(info):
    if info['id'] == 'f0':
        info['value'] = float(info['value'])*1e6
    param = {info['id']:float(info['value'])}
    utils.update_session_subdict(session,'calibration',param)
    # TODO This line is needed to update session variables
    # Update thread
    for th in threading.enumerate():
        if hasattr(th, 'f0'):
            th.set_f0(session['calibration']['f0'])


# Dev route for new features
@app.route('/examples',methods=['POST','GET'])
def example_elements():
    return render_template('examples.html',template_title="UI Element Examples",
                           template_intro_text="For developer use")