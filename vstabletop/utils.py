import numpy as np
from vstabletop.models import Progress
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


def spherical_to_cartesian(theta,phi,m0):
    # theta, phi are in degrees
    theta *= np.pi / 180
    phi *= np.pi / 180
    M = m0*np.array([[np.sin(theta)*np.cos(phi)],[np.sin(theta)*np.sin(phi)],[np.cos(theta)]])
    return M

def num_questions_of_game(num, mc_model):
    #return len(MultipleChoice.query.filter_by(game_number=num).all())
    return len(mc_model.query.filter_by(game_number=num).all())


def new_progress_of_game(num, mc_model):
    num_steps_dict = {1:4, 2:4, 3:3, 4:4, 5:4, 6:4, 7:5, 8:3}
    num_mc = num_questions_of_game(num, mc_model)
    return Progress(game_number=num, num_stars=0,
                    num_questions=num_mc, num_correct=0,
                    num_steps_total=num_steps_dict[num],num_steps_complete=0) # No user id attached yet

def process_all_game_questions(all_Qs):
    questions = []
    uses_images_list = []
    success_text = len(all_Qs) * ['Correct! Move on to the next question.']
    for Q in all_Qs:
        qdata = Q.get_randomized_data()
        uses_images_list.append(Q.uses_images)
        corr_array = [l == qdata[2] for l in ['A', 'B', 'C', 'D']]
        corr_array_new = []
        qchoices = []
        for ind in range(len(qdata[1])):
            if len(qdata[1][ind]) != 0:
                qchoices.append(qdata[1][ind])
                corr_array_new.append(corr_array[ind])

        questions.append({'text': qdata[0],
                          'choices': qchoices,
                          'correct': corr_array_new.index(True),
                          'main_image_path': Q.main_image_path})

    return questions, success_text, uses_images_list


# def fetch_all_game_questions(num):
