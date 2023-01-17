# Generates multiple choice questions and stores them in database
# Gehua Tong, July 2022

from vstabletop.models import MultipleChoice
from vstabletop.app import db
import random


# Game 1 questions
# Try initiating some MC questions!
def initialize_game1_questions():
    """Defines a list of multiple choice questions

    Returns
    -------
    mcs : list
        List of MultipleChoice database models for game 1
    """
    mcs = [] # List of questions
    mcs.append(MultipleChoice(
        id=101,
        game_number=1,
        uses_images=False,
        question_text="What combination of matrix size and FOV gives you the highest resolution?",
        choiceA = "Large matrix size and small FOV",
        choiceB = "Small matrix size and large FOV",
        choiceC = "Large matrix size and large FOV",
        choiceD = "Small matrix size and small FOV",
        correct_choice = "A",
        difficulty='easy'
    ))
    mcs.append(MultipleChoice(
        id=102,
        game_number=1,
        uses_images=False,
        question_text="What combination of matrix size and FOV gives you the highest resolution?",
        choiceA='Matrix size = 16, FOV = 0.16 cm',
        choiceB='Matrix size = 18, FOV = 0.36 cm',
        choiceC='Matrix size = 25, FOV = 0.25 m',
        choiceD='Matrix size = 250, FOV = 0.25 m',
        correct_choice='A',
        difficulty='medium'
    ))

    mcs.append(MultipleChoice(
        id=103,
        game_number=1,
        uses_images=False,
        question_text="What happens as the zero-fill value is increased?",
        choiceA="The matrix size increases",
        choiceB = "The matrix size decreases",
        choiceC = "The matrix size stays the same",
        choiceD = "The resolution is improved",
        correct_choice="A",
        difficulty="medium"
    ))

    mcs.append(MultipleChoice(
        id=104,
        game_number=1,
        uses_images=False,
        question_text="What min/max window settings would allow the most visual contrast to show up between the two circles (numbers indicate gray level)?",
        main_image_path="./static/img/game1/two_circs_windowing.png",
        choiceA="Min: 0.01; Max: 0.99",
        choiceB="Min: 0.20; Max: 0.40",
        choiceC="Min: 0.60; Max: 0.65",
        choiceD="Min: 0.30; Max: 0.70",
        correct_choice='D',
        difficulty='medium'
    ))

    mcs.append(MultipleChoice(
        id=105,
        game_number=1,
        uses_images=False,
        question_text="Why does acquiring smaller pixels lead to better resolution?",
        choiceA='More pixels means a larger range of gray values are possible',
        choiceB='A small pixel contains more information than a large pixel',
        choiceC='Pixel amount and size have no effect on resolution',
        choiceD='Each pixel represents a smaller amount of space',
        correct_choice='D',
        difficulty='easy'
    ))


    mcs.append(MultipleChoice(
        id=106,
        game_number=1,
        uses_images=True,
        question_text="Which image has the highest resolution?",
        choiceA = "./static/img/game1/cat1.png",
        choiceB = "./static/img/game1/cat2.png",
        choiceC = "./static/img/game1/cat3.png",
        choiceD = "",
        correct_choice="B",
        difficulty='easy'
    ))

    mcs.append(MultipleChoice(
        id=107,
        game_number=1,
        uses_images=True,
        question_text="Which image has the tiniest FOV?",
        choiceA='./static/img/game1/brain1.png',
        choiceB='./static/img/game1/brain2.png',
        choiceC='./static/img/game1/brain3.png',
        choiceD='',
        correct_choice='B',
        difficulty='easy'
    ))

    mcs.append(MultipleChoice(
        id=108,
        game_number=1,
        uses_images=True,
        question_text="Which image has the smallest matrix size?",
        choiceA="./static/img/game1/rose1.png",
        choiceB="./static/img/game1/rose2.png",
        choiceC="./static/img/game1/rose3.png",
        choiceD="",
        correct_choice='A',
        difficulty='medium'
    ))

    mcs.append(MultipleChoice(
        id=109,
        game_number=1,
        uses_images=False,
        question_text="What is the difference between a pixel and a voxel?",
        choiceA="Voxels are larger than pixels and hence contain more information.",
        choiceB="Voxels are sized by volume while pixels are sized by area.",
        choiceC="Voxels make up color images while pixels make up monochrome images.",
        choiceD="Only MR images are made of voxels; all other medical images are made of pixels",
        correct_choice='B',
        difficulty='medium'
    ))

    mcs.append(MultipleChoice(
        id=110,
        game_number=1,
        uses_images=False,
        question_text="What does zero-filling this reduced matrix size image of a pineapple do?",
        main_image_path="./static/img/game1/pineapples.png",
        choiceA="It makes each pixel represent a smaller section of space.",
        choiceB="It makes the fruit more delicious.",
        choiceC="It sets the background values to zero and makes the pineapple stand out.",
        choiceD="It improves the true resolution of the image.",
        correct_choice='A',
        difficulty='hard'
    ))

    return mcs

def initialize_game2_questions():
    mcs = []
    mcs.append(MultipleChoice(
        id = 201,
        game_number = 2,
        uses_images=False,
        question_text="Which statement below is incorrect about the Fourier Transform?",
        choiceA="It is an irreversible process.",
        choiceB="It can be performed as an integral over time or space.",
        choiceC="The FT of the product of two signals is not necessarily the product of its FTs.",
        choiceD="The output of the inverse Fourier transform can be entirely real.",
        correct_choice="A",
        difficulty="hard"
    ))

    mcs.append(MultipleChoice(
        id = 202,
        game_number = 2,
        uses_images=False,
        question_text="What does k stand for in the term “k-space”?",
        choiceA="Key imaging variable",
        choiceB="Kinetic energy conversion",
        choiceC="Spatial frequency",
        choiceD="Coordinates of reconstruction",
        correct_choice="C",
        difficulty="medium"
    ))

    mcs.append(MultipleChoice(
        id = 203,
        game_number = 2,
        uses_images=False,
        question_text="What statement about k-space is correct?",
        choiceA="The middle of k-space represents the edge information and small details on the image",
        choiceB="The periphery of k-space represents the overall signal level of the image",
        choiceC="K-space is artificially created from the acquired image",
        choiceD="K-space is directly sampled and the image is created afterwards with an extra step",
        correct_choice="D",
        difficulty="hard"
    ))

    mcs.append(MultipleChoice(
        id = 204,
        game_number = 2,
        uses_images=False,
        question_text="What happens if I slice the k-space in the following way?",
        main_image_path="./static/img/Game2/slicer.png",
        choiceA="Vertical edges will get blurry",
        choiceB="Horizontal edges will get blurry",
        choiceC="Only vertical edges will be visible",
        choiceD="Only horizontal edges will be visible",
        correct_choice="A",
        difficulty="hard"
    ))

    mcs.append(MultipleChoice(
        id=205,
        game_number = 2,
        uses_images=False,
        question_text="What is incorrect about spatial frequency?",
        choiceA="Low spatial frequencies corresponds to information in the center of image space",
        choiceB="Each point in k-space tells you the amplitude of one spatial frequency",
        choiceC="High spatial frequencies corresponds to thinner stripes",
        choiceD="In 2D, spatial frequency has a direction along which the wave amplitude changes",
        correct_choice="A",
        difficulty="hard"
    ))
    return mcs

def initialize_game3_questions():
    mcs = []
    mcs.append(MultipleChoice(
        id = 301,
        game_number=3,
        uses_images=False,
        question_text="Which set of parameters gives you the most T1-weighted scan?",
        choiceA = "TR = 4 s, TE = 2 ms",
        choiceB = "TR = 5 s, TE = 500 ms",
        choiceC = "TR = 900 ms, TE = 5 ms",
        choiceD = "TR = 800 ms, TE = 500 ms",
        correct_choice="C",
        difficulty="medium"
    ))

    mcs.append(MultipleChoice(
        id = 302,
        game_number=3,
        uses_images=False,
        question_text="What does a PD-weighted scan highlight?",
        choiceA = "It highlights tissues with a higher density of protons.",
        choiceB = "It highlights tissues with a lower density of protons",
        choiceC = "It highlights tissues only at a specific density that the imager can specify.",
        choiceD = "It highlights tissues with no protons at all.",
        correct_choice = "A",
        difficulty="easy"
    ))

    mcs.append(MultipleChoice(
        id=303,
        game_number=3,
        uses_images=False,
        question_text="How would substances with small T2 values appear on a T2-weighted scan?",
        choiceA="They would appear bright",
        choiceB="They would appear dark",
        choiceC="They would appear larger than their physical sizes",
        choiceD="They would appear smaller than their physical sizes",
        correct_choice="B",
        difficulty="medium"
    ))

    mcs.append(MultipleChoice(
        id = 304,
        game_number=3,
        question_text="What are T1-weighted images most useful for?",
        choiceA = "Assessing the relative densities of brain tissues",
        choiceB = "Visualizing brain tissue boundaries",
        choiceC = "Detecting deoxygenated hemoglobin",
        choiceD = "Highlighting cerebrospinal fluid",
        correct_choice="B",
        difficulty="easy"
    ))

    mcs.append(MultipleChoice(
        id = 305,
        game_number=3,
        question_text="Using the table, predict which tissue type will be highlighted with a T1w MR contrast:",
        main_image_path = "./static/img/game3/tissue_table.png",
        choiceA = "Gray matter",
        choiceB = "White matter",
        choiceC = "",
        choiceD = "",
        correct_choice="B",
        difficulty="medium"
    ))

    mcs.append(MultipleChoice(
        id = 306,
        game_number=3,
        question_text="Using the table, predict which tissue type will be highlighted with a T2w MR contrast:",
        main_image_path = "./static/img/game3/tissue_table.png",
        choiceA = "Gray matter",
        choiceB = "White matter",
        choiceC = "",
        choiceD = "",
        correct_choice="A",
        difficulty="medium"
    ))

    mcs.append(MultipleChoice(
        id = 307,
        game_number=3,
        question_text="Using the table, predict which tissue type will be highlighted with a PDw MR contrast:",
        main_image_path = "./static/img/game3/tissue_table.png",
        choiceA = "Gray matter",
        choiceB = "White matter",
        choiceC = "",
        choiceD = "",
        correct_choice="A",
        difficulty="medium"
    ))

    return mcs

def initialize_game4_questions():
    """Defines a list of multiple choice questions

    Returns
    -------
    mcs : list
        List of MultipleChoice database models for game 4
    """
    mcs = [] # List of questions
    mcs.append(MultipleChoice(
        id=401,
        game_number=4,
        uses_images=False,
        question_text="How can we visualize blood vessels with MRI?",
        choiceA = "By eliminating signal from background tissues",
        choiceB = "By eliminating signal from blood",
        choiceC = "By eliminating signal from blood vessel walls",
        choiceD = "By performing a maximum intensity projection on any MR image",
        correct_choice = "B",
        difficulty='medium'
    ))

    mcs.append(MultipleChoice(
        id=402,
        game_number=4,
        uses_images=False,
        question_text="Which of the following is false about steady state SPGR?",
        choiceA="The steady state signal is lower than the initial signal",
        choiceB="The fewer RF pulses protons experience, the higher signal they generate",
        choiceC="The steady state signal is dependent on the flip angle",
        choiceD="Fewer RF pulses are needed for moving protons to reach steady state than for stationary protons",
        correct_choice = "D",
        difficulty='hard'
    ))

    mcs.append(MultipleChoice(
        id=403,
        game_number=4,
        uses_images=False,
        question_text="How would you describe the RF pulse pattern in SPGR?",
        choiceA="A train of equally spaced, alpha-degree (alpha < 90) pulses",
        choiceB="A train of equally spaced 180-degree pulses",
        choiceC="A 90-degree pulse followed by equally spaced 180-degree pulses",
        choiceD="An alpha-degree (alpha < 90)  pulse followed by equally-spaced 90-degree pulses",
        correct_choice = "A",
        difficulty="medium"
    ))

    mcs.append(MultipleChoice(
        id=404,
        game_number=4,
        uses_images=False,
        question_text= "Which of the following is true about T2 and T2*?",
        choiceA="Spin echoes generate T2* contrast",
        choiceB="T2* is always longer than T2",
        choiceC="T2 and T2* are the same for moving spins",
        choiceD="T2*-weighted signal is lower than T2-weighted signal",
        correct_choice="D",
        difficulty="hard"
    ))

    mcs.append(MultipleChoice(
        id=405,
        game_number=4,
        uses_images=False,
        question_text="How do you describe the RF pulse pattern in SE?",
        choiceA="90-deg pulse, Δt, 180-deg-pulse, Δt, get signal",
        choiceB="180-deg pulse, Δt1, 90-deg pulse, Δt2, 180-deg pulse, Δt2, get signal",
        choiceC="90-deg pulse,  2Δt, 180-deg pulse, get signal",
        choiceD="90-deg pulse, Δt, 180-deg-pulse, 2Δt, get signal",
        correct_choice="A",
        difficulty="medium"
    ))

    mcs.append(MultipleChoice(
        id=406,
        game_number=4,
        uses_images=False,
        question_text="Which of the following is false about maximum intensity projection?",
        choiceA="It generates a 2D image from a 3D volume",
        choiceB="High signals are emphasized",
        choiceC="You should use it for dark-blood MRA images",
        choiceD="It helps radiologists visualize the shape of a vascular tree",
        correct_choice="C",
        difficulty="hard"
    ))

    return mcs

def initialize_game5_questions():
    mcs = []

    mcs.append(MultipleChoice(
        id = 501,
        game_number=5,
        uses_images=False,
        question_text="What is the difference between 90-degree and 180-degree RF pulses?",
        choiceA="90-degree pulses are shorter than 180-degree pulses",
        choiceB="90-degree pulses are at a right angle to the spin magnetic moment while 180-degree pulses are antiparallel to it",
        choiceC="90-degree pulses rotate half the number of spins compared to 180-degree pulses",
        choiceD="90-degree pulses tip the equilibrium M to the x-y plane while 180-degree pulses do not",
        correct_choice="D",
        difficulty="medium"
    ))

    mcs.append(MultipleChoice(
        id = 502,
        game_number = 5,
        uses_images=False,
        question_text="Why do we need to apply an RF pulse?",
        choiceA="The spins absorb RF energy and converts it into detectable heat",
        choiceB="The RF pulse allows spins to develop a magnetic moment",
        choiceC="The spin magnetic moments need to be tipped to the x-y plane",
        choiceD="The spins precess around the transmitted RF field to generate emf",
        correct_choice="C",
        difficulty="hard"
    ))

    mcs.append(MultipleChoice(
        id=503,
        game_number=5,
        uses_images=False,
        question_text="What happens to the emf signal when the main magnetic field is turned up?",
        choiceA="The signal oscillates faster",
        choiceB="The signal oscillates more slowly",
        choiceC="The signal decays more over time",
        choiceD="The signal grows more over time",
        correct_choice="A",
        difficulty="easy"
    ))

    mcs.append(MultipleChoice(
        id = 504,
        game_number=5,
        uses_images=False,
        question_text="Which of the four options maximizes the voltage range of the received signal? The initial M is at equilibrium and points along z.",
        choiceA="Using a 5-degree pulse with a phase of 180 degrees",
        choiceB="Using a 85-degree pulse with a phase of 45 degrees",
        choiceC="Using a 179-degree pulse with a phase of 0 degrees",
        choiceD="Using a 225-degree pulse with a phase of 76 degrees",
        correct_choice="B",
        difficulty="hard"
    ))

    return mcs

def initialize_game6_questions():
    mcs = []

    mcs.append(MultipleChoice(
        id=601,
        game_number=6,
        uses_images=False,
        question_text="Which of the following is true about T1?",
        choiceA="T1 refers to transverse relaxation",
        choiceB="T1 relaxation causes Mz to approach zero",
        choiceC="T1 relaxation causes Mz to approach its equilibrium value",
        choiceD="T1 can be mapped by varying TEs",
        correct_choice="C",
        difficulty="medium"

    ))

    mcs.append(MultipleChoice(
        id=602,
        game_number=6,
        uses_images=False,
        question_text="Which of the following is false about T2?",
        choiceA="T2 decay is caused by dephasing of spins",
        choiceB="T2 decay happens in the x-y plane",
        choiceC="T2 refers to the time taken to decrease Mxy by about 63%",
        choiceD="T2 has units of [radians/Tesla]",
        correct_choice="D",
        difficulty="medium"
    ))

    mcs.append(MultipleChoice(
        id=603,
        game_number=6,
        uses_images=False,
        question_text="Which of the following describes an IRSE sequence?",
        choiceA=" 90 RF, wait for T, 180 RF, wait for 2T, acquire",
        choiceB="180 RF, wait for 5T, 90 RF, wait for T, acquire",
        choiceC="90 RF, wait for T, 180 RF, wait for T, acquire, wait for T, 270 RF, wait for T, acquire",
        choiceD="90 RF, wait for T, 90 RF, wait for T, acquire",
        correct_choice="B",
        difficulty="hard"
    ))

    mcs.append(MultipleChoice(
        id=604,
        game_number=6,
        uses_images=False,
        question_text="Which of the following describes a TSE sequence?",
        choiceA="90 RF, wait for T, 180 RF, wait for T, acquire, wait for T, 180 RF, wait for T, acquire",
        choiceB="180 RF, wait for T, 90 RF, wait for T, 180 RF, acquire",
        choiceC="180 RF, wait for T, 90 RF, wait for T, acquire",
        choiceD="90 RF, wait for 2T, acquire",
        correct_choice="A",
        difficulty="hard"
    ))

    mcs.append(MultipleChoice(
        id=605,
        game_number=6,
        uses_images=False,
        question_text="What does curve fitting accomplish?",
        choiceA="It converts one image into a parameter (T1 or T2) map.",
        choiceB="It fits the T1 or T2 signal model to the mapping data acquired at different timings.",
        choiceC="It draws a straight line through T1 or T2 mapping data for each voxel.",
        choiceD="It traces tissue boundaries to perform a segmentation based on T1 or T2 maps",
        correct_choice="A",
        difficulty="hard"
    ))

    mcs.append(MultipleChoice(
        id=606,
        game_number=6,
        uses_images=False,
        question_text="How can we get data to perform T2 mapping?",
        choiceA="Apply an IRSE sequence with different TEs",
        choiceB="Apply a TSE sequence with different TEs",
        choiceC="Apply a TSE sequence with different TIs",
        choiceD="Apply an IRSE sequence with different TRs",
        correct_choice="B",
        difficulty="medium"
    ))

    mcs.append(MultipleChoice(
        id=607,
        game_number=6,
        uses_images=False,
        question_text="What is Mz at t = 100 ms after a 180-degree pulse has been applied at t = 0 on a tissue type with T1 = 300 ms?",
        choiceA="-43.3% M0",
        choiceB="+27.4% M0",
        choiceC="0",
        choiceD="+91.0% M0",
        correct_choice="A",
        difficulty="hard"
    ))


    return mcs

def initialize_game7_questions():
    mcs = []

    # Questions without images (conceptual)
    mcs.append(MultipleChoice(
        id = 701,
        game_number = 7,
        uses_images = False,
        question_text = "How many numbers are needed to locate a point in space?",
        choiceA = "9",
        choiceB = "3",
        choiceC = "42",
        choiceD = "2",
        correct_choice = "B",
        difficulty = "easy"
    ))

    mcs.append(MultipleChoice(
        id = 702,
        game_number = 7,
        uses_images = False,
        question_text = "What of the following is true when you perform a 2D projection of a perfect 3D sphere?",
        choiceA ="The projection will have the same gray value across the image",
        choiceB = "The projection lines will bend to conform to the circular shape",
        choiceC = "The projection will be the same from any angle",
        choiceD = "The projection will be the same only when it’s pointing along the x, y, or z axis. ",
        correct_choice = "C",
        difficulty = "medium"
    ))

    mcs.append(MultipleChoice(
        id = 703,
        game_number = 7,
        uses_images = False,
        question_text = "What happens when you perform a 1D projection of a rectangle?",
        choiceA = "The left, right, top, and bottom views are going to be the same",
        choiceB = "The left/right views are the same, and the top/bottom views are the same",
        choiceC = "The projection is always going to have right-angled corners",
        choiceD = "The projection depends on how the rectangle is oriented in the x-y plane",
        correct_choice = "D",
        difficulty = "hard"
    ))

    # Questions with images


    return mcs

def initialize_game8_questions():
    mcs = []

    # Questions without images (conceptual)
    mcs.append(MultipleChoice(
        id=801,
        game_number=8,
        uses_images=False,
        question_text="Which of the following is a pair of forward and inverse processes?",
        choiceA="Baking a cake and eating it",
        choiceB="Growing a tree from a seed and harvesting a seed from that tree",
        choiceC="Making a piece of art and selling it to buy more paint",
        choiceD="Putting together a LEGO house and taking it apart",
        correct_choice="D",
        difficulty="easy"
    ))

    mcs.append(MultipleChoice(
        id=802,
        game_number=8,
        uses_images=False,
        question_text="Which of the following is not a way to sample k-space in a non-cartesian manner?",
        choiceA="Sample points with the same spacing across x and across y",
        choiceB="Sample points regularly along a line that crosses the center of k-space, rotate the line, and then sample it again",
        choiceC="Sample points randomly so more points are sampled from the center of k-space",
        choiceD="Sample points along a spiral",
        correct_choice="A",
        difficulty="medium"
    ))

    mcs.append(MultipleChoice(
        id=803,
        game_number=8,
        uses_images=False,
        question_text="Which of the following is not a way to process and reconstruct raw MRI data?",
        choiceA="Performing an IFFT on it",
        choiceB="Convert 1D radial data lines to the spatial domain and perform backprojection",
        choiceC="Use gridding and then perform an IFFT",
        choiceD="Bake it at 450F for 40 minutes",
        correct_choice="D",
        difficulty="easy"
    ))

    return mcs


def refresh_database_and_add_questions(mcs):
    db.drop_all() # Gets rid of database structure as well
    db.create_all()# Re-create tables
    for mc in mcs:
        db.session.add(mc)
        try:
            db.session.commit()
        except:
            db.session.rollback()


def draw_random_question(game_number):
    myQs = MultipleChoice.query.filter_by(game_number=game_number).all()
    Q = random.sample(myQs,1)[0]
    return Q

def get_all_questions(game_number):
    # Returns a list of all questions for specified game
    return MultipleChoice.query.filter_by(game_number=game_number).all( )


if __name__ == "__main__":
    # Note: the questions are set so the question text must be unique
    #       if you try to add the same question (i.e. with the same unique questioning text) twice
    #           only the first time will count
    #           if you need to modify the question, delete the local file myDB.db first.
    #                     It gets regenerated when you call the function db.create_all().

    # Input questions into database
    from vstabletop.models import initialize_users

    mc_list = initialize_game1_questions()
    mc_list += initialize_game2_questions()
    mc_list += initialize_game3_questions()
    mc_list += initialize_game5_questions()
    mc_list += initialize_game7_questions()
    refresh_database_and_add_questions(mc_list)
    initialize_users() # adds admin back into database

    # Get first and second question for unlocking purposes
    # First question
    #print(MultipleChoice.query.get(101).get_randomized_data())
    # Second question
    #print(MultipleChoice.query.get(102).get_randomized_data())


    #print(MultipleChoice.query.filter_by(game_number=3).all())

    # Example querying of database
    # All Game 1 questions

    # Get all game 1 questions
    # print('All questions for game 1: ')
    # q = MultipleChoice.query.filter_by(game_number=1).all()
    # print(q)
    #
    # # Get the first game 1 question that is easy
    # print('The first easy question for game 1: ')
    # q2 = MultipleChoice.query.filter_by(game_number=1,difficulty='easy').first_or_404() # Only gets first!!
    # print(q2)
    #
    # # Get one random question (game number not specified)
    # print('Random question from any game: ')
    # q3 = MultipleChoice.query.all()
    # print(random.sample(q3,1))
    #
    # # Check answer
    # my_question = q2
    # # Check answer by text
    # print(my_question.check_answer('Pixel amount and size have no effect on resolution'))
    #
    # # Shuffle A,B,C,D choices
    # print(my_question.get_randomized_data())

