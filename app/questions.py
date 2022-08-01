# Generates multiple choice questions and stores them in database
# Gehua Tong, July 2022

from app import db
from models import MultipleChoice
import random

# Game 1 questions
# Try initiating some MC questions!
def initialize_game1_questions():
    mcs = [] # List of questions

    mcs.append(MultipleChoice(
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

    db.create_all()
    for mc in mcs:
        db.session.add(mc)
        try:
            db.session.commit()
        except:
            db.session.rollback()


if __name__ == "__main__":
    # Note: the questions are set so the question text must be unique
    #       if you try to add the same question (i.e. with the same unique questioning text) twice
    #           only the first time will count
    #           if you need to modify the question, delete the local file myDB.db first.
    #                     It gets regenerated when you call the function db.create_all().


    # Input questions into database
    initialize_game1_questions()
    # Example querying of database
    # All Game 1 questions

    # Get all game 1 questions
    print('All questions for game 1: ')
    q = MultipleChoice.query.filter_by(game_number=1).all()
    print(q)

    # Get the first game 1 question that is easy
    print('The first easy question for game 1: ')
    q2 = MultipleChoice.query.filter_by(game_number=1,difficulty='easy').first_or_404() # Only gets first!!
    print(q2)

    # Get one random question (game number not specified)
    print('Random question from any game: ')
    q3 = MultipleChoice.query.all()
    print(random.sample(q3,1))

    # Check answer
    my_question = q2
    # Check answer by text
    print(my_question.check_answer('Pixel amount and size have no effect on resolution'))

    # Shuffle A,B,C,D choices
    print(my_question.get_randomized_data())