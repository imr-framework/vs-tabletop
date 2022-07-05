import plotly
import pandas as pd
import plotly.express as px
import json
import numpy as np
import threading
from __main__ import app, socketio
import ctypes

# Share functionalities to allow the exiting of threads
class ThreadStop():
    def get_id(self):
        if hasattr(self,'_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id
    def raise_exception(self):
        thread_id = self.get_id()
        resu = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
        if resu > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,0)

# Use socket ...
class SignalPlotsThread(threading.Thread, ThreadStop):
    def __init__(self,f0):
        self.f0 = f0
        print(f'Calling this with f0={self.f0}')
        self.delay = 1 # second
        self.thread_stop_event = threading.Event()
        super(SignalPlotsThread, self).__init__()

    def randomPlotsGenerator(self):
        while not self.thread_stop_event.isSet():
            j1,j2 = get_fake_calibration_plots(self.f0)
            socketio.emit('plots served',{'fid':j1,'spectrum':j2})
            socketio.sleep(self.delay)

    def set_f0(self,new_f0):
        self.f0 = new_f0

    def run(self):
        self.randomPlotsGenerator()

class FlipAnglePlotThread(threading.Thread, ThreadStop):
    def __init__(self, tx_amp_90, tx_amp_max, Npts):
        self.delay = 0.5 # seconds
        self.thread_stop_event = threading.Event()
        self.tx_amp_90 = tx_amp_90
        self.tx_amp_max = tx_amp_max
        self.Npts = Npts
        self.pointIndex = 1
        super(FlipAnglePlotThread,self).__init__()

    def flipPlotGenerator(self):
        while not self.thread_stop_event.isSet():
            # Once all points are plotted, the thread stops itself
            if self.pointIndex > self.Npts:
                self.pointIndex = self.Npts
            j3 = get_fake_fa_plot(self.tx_amp_90, self.tx_amp_max, self.Npts, self.pointIndex)
            self.pointIndex += 1
            socketio.emit('fa plot served', {'fa_signal': j3})
            socketio.sleep(self.delay)

    def run(self):
        self.flipPlotGenerator()


def get_fake_fa_plot(tx_amp_90, tx_amp_max, n_points, up_to_index):
    tx_model, signal = generate_Tx_signal_plot(tx_amp_90, tx_amp_max, n_points, up_to_index)
    df2 = pd.DataFrame({'tx_model':tx_model, 'tx_signal':signal})
    fig_fa_calib = px.scatter(df2, x='tx_model',y='tx_signal')
    fig_fa_calib.update_xaxes(range=[0,tx_amp_max])
    fig_fa_calib.update_yaxes(range=[-1.25,1.25])
    graphJSON = json.dumps(fig_fa_calib,cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def get_fake_calibration_plots(f0):
    #print(f'fake plots to be generated with  f0={f0}')
    tmodel, fid = generate_fake_fid(f0)
    dt = tmodel[1] - tmodel[0]
    fmodel = np.linspace(-0.5*(1/dt),0.5*(1/dt),len(fid),endpoint=False)
    spectrum = generate_spectrum_from_fake_fid(fid)
    df = pd.DataFrame({'t':tmodel, 'fid':fid, 'f':fmodel, 'spectrum':spectrum})

    fig_fid = px.line(df,x='t',y='fid')
    fig_spectrum = px.line(df,x='f',y='spectrum')

    graphJSON1 = json.dumps(fig_fid,cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON2 = json.dumps(fig_spectrum,cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON1, graphJSON2



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


def generate_fake_fid(f0):
    tmodel = np.linspace(0,1,1000,endpoint=False)
    signal = 30*np.exp(-tmodel)*np.cos((f0 - 15e6)*tmodel) + (np.random.rand(len(tmodel))-0.5)
    return tmodel, signal

def generate_spectrum_from_fake_fid(fid):
    spectrum = np.absolute(np.fft.fftshift(np.fft.fft(fid)))
    return spectrum

def generate_Tx_signal_plot(tx_amp_90, tx_amp_max, n_points, up_to_index):
    tx_model = np.linspace(0,tx_amp_max,n_points)
    tx_model = tx_model[0:up_to_index]
    signal = np.sin((tx_model/tx_amp_90)*np.pi/2)
    return tx_model, signal
