# Generates multiple choice questions and stores them in database
# Gehua Tong, July 2022

from vstabletop.app import db
from models import MultipleChoice
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
    from models import initialize_users

    mc_list = initialize_game1_questions()
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


    print(MultipleChoice.query.filter_by(game_number=3).all())

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

