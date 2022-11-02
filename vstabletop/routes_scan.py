import json

from flask import flash, render_template, session, redirect, url_for, request
from __main__ import app, login_manager, db, socketio
import os
from pypulseq.Sequence.sequence import Sequence
from pypulseq.calc_duration import calc_duration
from pypulseq.calc_rf_center import calc_rf_center
from vstabletop.paths import DATA_PATH, LOCAL_CONFIG_PATH
import plotly.graph_objects as go
import plotly
from plotly.subplots import make_subplots
from external.marcos_pack.flocra_pulseq.flocra_pulseq_interpreter import PSInterpreter
import external.marcos_pack.marcos_client.experiment as ex
import matplotlib.pyplot as plt
from vstabletop.forms import ScanForm
import vstabletop.utils as utils

import numpy as np
import math

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == 'seq'



@app.route('/scan',methods=["GET","POST"])
def scan():
    scan_form = ScanForm()
    # User uploaded image!
    if request.method == 'POST':
        # uploaded = request.form.get('uploaded')
        print('Uploaded data: ', request.files)

        if 'file' not in request.files:
            print('No file uploaded')
            file = ''
        else:
            file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # filename = secure_filename(file.filename)
            ext = file.filename.split('.')[-1]
            file.save(os.path.join(app.config['UPLOAD_FOLDER_SCAN'], f'user_uploaded.{ext}'))
            socketio.emit("Seq file uploaded")

        else:
            print(f'File: {file.filename}')
            print('File format not allowed')

    return render_template('scan.html',template_form=scan_form, game_num=None)

@socketio.on("Display sequence")
def display_seq(info):
    print("We need to display the sequeunce")
    time_range = [float(info['min']),float(info['max'])]
    # Load seq
    seq = Sequence()
    seq.read(DATA_PATH / "scan" / "user_uploaded.seq")
    all_waveforms = export_waveforms(seq, time_range=time_range) #TODO parametrize

    # Create plot
    fig = make_subplots(rows=6, cols=1,
                        subplot_titles=("RF magnitude","RF phase", "ADC", "Gx", "Gy", "Gz"), shared_xaxes='all')
                      #  row_heights=6*[20])

    fig.add_trace(
        go.Scatter(x=all_waveforms['t_rf'], y=np.absolute(all_waveforms['rf']), mode='lines', name='RF magnitude',
                   line=dict(color='blue', width=2)),
        row=1, col=1)
    fig.add_trace(go.Scatter(x=all_waveforms['t_rf'], y=np.angle(all_waveforms['rf']), mode='lines', name='RF phase',
                             line=dict(color='gray', width=2)),
                  row=2, col=1)
    fig.add_trace(
        go.Scatter(x=all_waveforms['t_adc'], y=np.angle(all_waveforms['adc']), mode='markers', name='ADC with phase',
                   line=dict(color='red', width=2)),
        row=3, col=1)
    fig.add_trace(go.Scatter(x=all_waveforms['t_gx'], y=all_waveforms['gx'], mode='lines', name='Gx',
                             line=dict(color='green', width=2)),
                  row=4, col=1)
    fig.add_trace(go.Scatter(x=all_waveforms['t_gy'], y=all_waveforms['gy'], mode='lines', name='Gy',
                             line=dict(color='orange', width=2)),
                  row=5, col=1)
    fig.add_trace(go.Scatter(x=all_waveforms['t_gz'], y=all_waveforms['gz'], mode='lines', name='Gz',
                             line=dict(color='purple', width=2)),
                  row=6, col=1)

    fig.update_xaxes(title_text="Time (seconds)", row=6, col=1, range=time_range)
    fig.update_yaxes(title_text=all_waveforms['rf_unit'], row=1, col=1)
    fig.update_yaxes(title_text='[rads]', row=2, col=1)
    fig.update_yaxes(title_text='[rads]', row=3, col=1)
    fig.update_yaxes(title_text='[Hz/m]', row=4, col=1)
    fig.update_yaxes(title_text='[Hz/m]', row=5, col=1)
    fig.update_yaxes(title_text='[Hz/m]', row=6, col=1)


    j1 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    # Send graphJSON back
    socketio.emit("Deliver seq plot", {'graph': j1})


# Seq helper
def export_waveforms(seq, time_range=(0, np.inf)):
    """
    Plot `Sequence`.
    Parameters
    ----------
    time_range : iterable, default=(0, np.inf)
        Time range (x-axis limits) for all waveforms. Default is 0 to infinity (entire sequence).
    Returns
    -------
    all_waveforms: dict
        Dictionary containing all sequence waveforms and time array(s)
        The keys are listed here:
        't_adc' - ADC timing array [seconds]
        't_rf' - RF timing array [seconds]
        ''
        'adc' - ADC complex signal (amplitude=1, phase=adc phase) [a.u.]
        'rf' - RF complex signal []
        'gx' - x gradient []
        'gy' - y gradient []
        'gz' - z gradient []
    """
    # Check time range validity
    if not all([isinstance(x, (int, float)) for x in time_range]) or len(time_range) != 2:
        raise ValueError('Invalid time range')

    t0 = 0
    adc_t_all = np.array([])
    adc_signal_all = np.array([],dtype=complex)
    rf_t_all =np.array([])
    rf_signal_all = np.array([],dtype=complex)
    rf_t_centers = np.array([])
    rf_signal_centers = np.array([],dtype=complex)
    gx_t_all = np.array([])
    gy_t_all = np.array([])
    gz_t_all = np.array([])
    gx_all = np.array([])
    gy_all = np.array([])
    gz_all = np.array([])


    for block_counter in range(len(seq.dict_block_events)): # For each block
        block = seq.get_block(block_counter + 1)  # Retrieve it
        is_valid = time_range[0] <= t0 <= time_range[1] # Check if "current time" is within requested range.
        if is_valid:
            # Case 1: ADC
            if hasattr(block, 'adc'):
                adc = block.adc # Get adc info
                # From Pulseq: According to the information from Klaus Scheffler and indirectly from Siemens this
                # is the present convention - the samples are shifted by 0.5 dwell # OK

                t = adc.delay + (np.arange(int(adc.num_samples)) + 0.5) * adc.dwell
                adc_t = t0 + t
                adc_signal = np.exp(1j * adc.phase_offset) * np.exp(1j * 2 * np.pi * t * adc.freq_offset)
                adc_t_all = np.append(adc_t_all, adc_t)
                adc_signal_all = np.append(adc_signal_all, adc_signal)

            if hasattr(block, 'rf'):
                rf = block.rf
                tc, ic = calc_rf_center(rf)
                t = rf.t + rf.delay
                tc = tc + rf.delay
                #
                # sp12.plot(t_factor * (t0 + t), np.abs(rf.signal))
                # sp13.plot(t_factor * (t0 + t), np.angle(rf.signal * np.exp(1j * rf.phase_offset)
                #                                         * np.exp(1j * 2 * math.pi * rf.t * rf.freq_offset)),
                #           t_factor * (t0 + tc), np.angle(rf.signal[ic] * np.exp(1j * rf.phase_offset)
                #                                          * np.exp(1j * 2 * math.pi * rf.t[ic] * rf.freq_offset)),
                #           'xb')

                rf_t = t0 + t
                rf = rf.signal * np.exp(1j * rf.phase_offset) \
                                                        * np.exp(1j * 2 * math.pi * rf.t * rf.freq_offset)
                rf_t_all = np.append(rf_t_all, rf_t)
                rf_signal_all = np.append(rf_signal_all, rf)
                rf_t_centers = np.append(rf_t_centers, rf_t[ic])
                rf_signal_centers = np.append(rf_signal_centers, rf[ic])

            grad_channels = ['gx', 'gy', 'gz']
            for x in range(len(grad_channels)): # Check each gradient channel: x, y, and z
                if hasattr(block, grad_channels[x]): # If this channel is on in current block
                    grad = getattr(block, grad_channels[x])
                    if grad.type == 'grad':# Arbitrary gradient option
                        # In place unpacking of grad.t with the starred expression
                        g_t = t0 +  grad.delay + [0, *(grad.t + (grad.t[1] - grad.t[0]) / 2),
                                                 grad.t[-1] + grad.t[1] - grad.t[0]]
                        g = 1e-3 * np.array((grad.first, *grad.waveform, grad.last))
                    else: # Trapezoid gradient option
                        g_t = t0 + np.cumsum([0, grad.delay, grad.rise_time, grad.flat_time, grad.fall_time])
                        g = 1e-3 * grad.amplitude * np.array([0, 0, 1, 1, 0])

                    if grad.channel == 'x':
                        gx_t_all = np.append(gx_t_all, g_t)
                        gx_all = np.append(gx_all,g)
                    elif grad.channel == 'y':
                        gy_t_all = np.append(gy_t_all, g_t)
                        gy_all = np.append(gy_all,g)
                    elif grad.channel == 'z':
                        gz_t_all = np.append(gz_t_all, g_t)
                        gz_all = np.append(gz_all,g)


        t0 += seq.arr_block_durations[block_counter] # "Current time" gets updated to end of block just examined

    all_waveforms = {'t_adc': adc_t_all, 't_rf': rf_t_all, 't_rf_centers': rf_t_centers,
                     't_gx': gx_t_all, 't_gy':gy_t_all, 't_gz':gz_t_all,
                     'adc': adc_signal_all, 'rf': rf_signal_all, 'rf_centers': rf_signal_centers,'gx':gx_all, 'gy':gy_all, 'gz':gz_all,
                     'grad_unit': '[kHz/m]', 'rf_unit': '[Hz]', 'time_unit':'[seconds]'}

    return all_waveforms


@socketio.on("Compile sequence")
def compile_seq():
    # Load seq
    print("Compiling uploaded sequence")
    seq = Sequence()
    seq.read(DATA_PATH / "scan" / "user_uploaded.seq")
    print("Seq read")
    exp = ex.Experiment(lo_freq=5, rx_t=3.125)
    ps = PSInterpreter(grad_t=1)
    try:
        event_dict, params = ps.interpret(str(DATA_PATH / "scan" / "user_uploaded.seq"))
        print("Seq interpreted")
        event_dict['tx1'] = event_dict['tx0']
        event_dict['rx1_en'] = event_dict['rx0_en']
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        socketio.emit("Message",{'type':'danger', 'text': "Interpreter error"})
        return

    try:
        exp.add_flodict(event_dict)
        print("Seq flodict added")
        #exp.plot_sequence()
        #plt.show()
        #print("Seq plotted")
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        socketio.emit("Message", {'type': 'danger', 'text': "Error adding flodict to experiment"})
        return

    try: # Run experiment
        print("running experiment...")
        rxd, msgs = exp.run()
        exp.close_server(only_if_sim=True)
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        socketio.emit("Message", {'type': 'danger', 'text': 'Error compiling / running the experiment'})
        return

    return rxd, msgs

@socketio.on("Update local config with ip")
def update_local_config(payload):
    print(f"Updating ip to {payload['ip-address']}")
    utils.update_local_configuration(payload['ip-address'], LOCAL_CONFIG_PATH)

