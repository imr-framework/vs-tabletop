# Generates multiple choice questions and stores them in database
# Gehua Tong, July 2022

from app import db
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
        question_text="What happens as the zero-fill value is increased?",
        choiceA="The matrix size increases",
        choiceB = "The matrix size decreases",
        choiceC = "The matrix size stays the same",
        choiceD = "The resolution is improved",
        correct_choice="A",
        difficulty="medium"
    ))
    mcs.append(MultipleChoice(
        id=103,
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
        id=104,
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
        id=105,
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
        main_image_path="./static/img/pineapples.png",
        choiceA="It makes each pixel represent a smaller section of space.",
        choiceB="It makes the fruit more delicious.",
        choiceC="It sets the background values to zero and makes the pineapple stand out.",
        choiceD="It improves the true resolution of the image.",
        correct_choice='A',
        difficulty='hard'
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
    from models import initialize_users

    mc_list = initialize_game1_questions()
    refresh_database_and_add_questions(mc_list)
    initialize_users() # adds admin back into database

    # Get first and second question for unlocking purposes
    # First question
    print(MultipleChoice.query.get(101).get_randomized_data())
    # Second question
    print(MultipleChoice.query.get(102).get_randomized_data())


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

