# Utility functions


# Save parameters into config.py
def update_configuration(params,config_path):
    """
    Inputs
    ------
    params : dict
        Hardware parameters set on the calibration page
    """
    with open(config_path,'r+') as f:
        new_config = f"LARMOR_FREQ = {float(params['f0'])/1e6} \n"
        new_config += 'RF_MAX = 7661.29 \n'
        new_config += f"RF_PI2_FRACTION = {params['tx_amp']} \n"

        new_config += "GX_MAX = 8.0e6 \n"  # System maximum X gradient strength, in Hz/m
        new_config += "GY_MAX = 9.2e6 \n"  # System maximum Y gradient strength, in Hz/m
        new_config += "GZ_MAX = 10e6 \n"  # System maximum Z gradient strength, in Hz/m

        new_config += f"SHIM_X = {params['shimx']} \n" # -1 to 1
        new_config += f"SHIM_Y = {params['shimy']} \n" # -1 to 1
        new_config += f"SHIM_Z = {params['shimz']} \n" # -1 to 1

        new_config += "MGH_PATH = 'PATH/TO/mgh/DIR' \n"
        new_config += "LOG_PATH = 'PATH/TO/PROGRAM/LOG/DIR' \n"
        new_config += "SEQ_PATH = 'PATH/TO/SEQ/FILES/DIR' \n"
        new_config += "DATA_PATH = 'PATH/TO/DATA/OUTPUT/DIR'"

        f.write(new_config)
        f.close()

def update_session_subdict(sess,first_key, params):
    for second_key in params.keys():
        sess[first_key][second_key] = params[second_key]
    sess.modified = True

def read_configuration(config_path):
    # TODO read configuration parameters from config.py
    f0 = 0
    return f0