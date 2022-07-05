# Generates simulation & plots for Game 5: Proton's got moves
import numpy as np
from pypulseq.make_block_pulse import make_block_pulse
from virtualscanner.server.simulation.rf_sim.rf_simulations import simulate_rf
from virtualscanner.server.simulation.bloch.spingroup_ps import SpinGroup
import plotly
import plotly.graph_objects as go
import plotly.express as px


# Game 5
def simulate_spin_action(M_first):
    simulated_data = np.zeros((1,100))
    return simulated_data


def animate_b0_turn_on(M_final=1, T1=1):
    """
    Parameters
    ------
    M_final : float
        Final magnetization value to be reached
    Returns
    -------

    """
    duration = 6*T1
    spin = SpinGroup(pdt1t2=(M_final,T1,0))
    spin.m[2,0] = 0 # Set initial Mz to zero
    N_steps = 100
    mags = np.zeros((N_steps,3))
    tmodel = np.linspace(0,duration,N_steps,endpoint=False)
    dt = tmodel[1] - tmodel[0]
    for q in range(N_steps):
        spin.delay(dt)
        mags[q,:] = np.squeeze(spin.get_m())

    return animate_spin_action(tmodel,mags,settings={})


def animate_spin_action(times, mags, settings):

    bgcolor = "darkgray"
    gridcolor = "white"
    spincolor = "darkorange"

    fig = go.Figure(
        data = [go.Scatter3d(x=[mags[0,0]],y=[mags[0,1]],z=[mags[0,2]])],
        layout = go.Layout(
            title = "let's spin",
            updatemenus=[dict(
                type = "buttons",
                buttons = [dict(label="Play",
                                method = "animate",
                                args=[None,{
                                    "frame":{"duration":20},
                                    "fromcurrent": True,
                                    "transition": {"duration": 10}
                                }])])]
        ),
        frames = [go.Frame(data=go.Scatter3d(x=[0,mags[q,0]],y=[0,mags[q,1]],z=[0,mags[q,2]],mode='lines',
                                             line=dict(width=10, color=spincolor) )) for q in range(mags.shape[0])]
        )

    axis_shared = dict(
        range=[-1, 1],
        backgroundcolor=bgcolor,
        gridcolor=gridcolor,
        showbackground=True,
        zerolinecolor=None,
        autorange=False)
    fig.update_layout(scene=dict(xaxis=axis_shared, yaxis=axis_shared,zaxis=axis_shared),
                     width=1000, margin=dict(r=10, l=10,b=10, t=10))


    fig.show()
    return


def make_spin_action_plot(simulated_data):
    a = simulated_data
    graphJSON = 0
    return graphJSON


if __name__ == '__main__':
    animate_b0_turn_on()
