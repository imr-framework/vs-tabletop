


def game4_worker_simulation(mode='bright',info={}):
    # Bright blood
    if mode == 'bright':
        brightJSON1, brightJSON2 = obtain_bright_plots(info)
        return brightJSON1, brightJSON2
    elif mode == 'dark':
        darkJSON1, darkJSON2 = obtain_dark_plots(info)
        return darkJSON1, darkJSON2

def game4_worker_image(mode='bright',info={}):

    img = simulate_flow_image(mode,info)

    # Make plots
    imgJSON = 0

    return imgJSON


# Simulated / animted plots
# TODO
def obtain_bright_plots(info):
    j1, j2 = 0,0
    return j1, j2

# TODO
def obtain_dark_plots(info):
    j1,j2 = 0,0
    return j1, j2

# TODO
def simulate_flow_image(mode,info):
    # Initialize phantom (0 - background, 1 - stationary, 2 - flow)
    if mode == 'dark'