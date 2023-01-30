# SQL Database models

from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
#from vstabletop.app import db
from datetime import datetime
import numpy as np

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Player table for login and progress keeping

    Columns
    -------
    id : user entry primary key
    username : user name for login
    password_hash : hashed user password
    joined_at : date of registration

    Methods
    -------
    set_password(password)
        Change user's password and store hash
    check_password(password)
        Check if the input matches user's password
    __repr__()
        Return string representation for printing

    """
    __table_args__ = {'extend_existing': True}


    # Basic fields
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(10),index=True,unique=True)
    password_hash = db.Column(db.String(128),index=False,unique=False)
    joined_at = db.Column(db.Date(),index=True,default=datetime.utcnow())
    #progresses = db.relationship('Progress',backref='user',lazy='dynamic')

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

    def __repr__(self):
        return f'ID: {self.id}; user name: {self.username}; date registered: {self.joined_at}'

class Calibration(db.Model):
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer(),primary_key=True)
    f0 = db.Column(db.Float(6,False),index=True)
    shimx = db.Column(db.Float(6,False))
    shimy = db.Column(db.Float(6,False))
    shimz = db.Column(db.Float(6,False))
    tx_amp = db.Column(db.Float(6,False))
    stored_at = db.Column(db.Date(),index=True,default=datetime.utcnow())


    def get_config_dict(self):
        # Write calibration parameters to config.py provided by path
        params = {'f0': float(self.f0) * 1e6, 'tx_amp': float(self.tx_amp),
                  'shimx': float(self.shimx), 'shimy': float(self.shimy), 'shimz': float(self.shimz)}
        print(params)
        return params

    def __repr__(self):
        return f'f0={self.f0/1e6} MHz, shim = ({self.shimx},{self.shimy},{self.shimz}), Tx amp = {self.tx_amp}, \
               stored at {self.stored_at}.'

class Progress(db.Model):
    __table_args__ = {'extend_existing': True}


    id = db.Column(db.Integer(),primary_key=True)
    game_number = db.Column(db.Integer(),index=True)
    num_questions = db.Column(db.Integer(),index=True)
    num_correct = db.Column(db.Integer(),index=True)
    num_stars = db.Column(db.Integer(),index=True)
    num_steps_complete = db.Column(db.Integer(),index=True)
    num_steps_total = db.Column(db.Integer(),index=True)
    user_id = db.Column(db.Integer(),index=True)
    #user_id = db.Column(db.Integer(),db.ForeignKey('user.id')) # Which user it belongs to

    date_achieved = db.Column(db.Date(),index=True,default=datetime.utcnow())

    def update_stars(self):
        correct_rate = self.num_correct / self.num_questions
        complete_rate = self.num_steps_complete / self.num_steps_total
        self.num_stars = round(2*(correct_rate * 2 + complete_rate * 3))/2


    def __repr__(self):
        rep = f'Progress of User ID #{self.user_id} for Game {self.game_number}: \n'
        rep += f'Multiple choice questions: {self.num_correct}/{self.num_questions} correct \n'
        rep += f'Game steps: {self.num_steps_complete}/{self.num_steps_total} complete \n'
        rep += f'Number of stars earned: {self.num_stars}/5 \n'
        rep += f'Date: {self.date_achieved}'

        return rep

class MultipleChoice(db.Model):
    __table_args__ = {'extend_existing': True}
    # Multiple choice question to store in database
    id = db.Column(db.Integer(),primary_key=True)
    game_number = db.Column(db.Integer(),index=True)# 1 - 8
    main_image_path = db.Column(db.String(),default='')
    uses_images = db.Column(db.Boolean(),default=False, index=True)
    question_text = db.Column(db.Text(),index=True, unique=False)
    choiceA = db.Column(db.String(),default='First choice') # Choice text or path to image
    choiceB = db.Column(db.String(),default='Second choice')
    choiceC = db.Column(db.String(),default='Third choice')
    choiceD = db.Column(db.String(),default='Fourth choice')
    correct_choice = db.Column(db.Enum('A','B','C','D',name='four_choices')) # A, B, C, or D
    difficulty = db.Column(db.Enum('easy','medium','hard'),default='easy',index=True) # easy, medium, hard

    def check_answer(self,answer):
    # Check if answer is correct!
    #  answer is the TEXT of the choice, not the LETTER
    #                (this is required because of random answer order display)
        letters = ['A', 'B', 'C', 'D']
        choices = [self.choiceA, self.choiceB, self.choiceC, self.choiceD]
        try:
            answer_letter = letters[choices.index(answer)]
        except:
            return ValueError(f"Provided MC choice '{answer}' does not exist in this question")

        return answer_letter == self.correct_choice

    def get_randomized_data(self):
        # Returns: question text, list of shuffled choices, new correct choice letter
        # If a choice's text is an empty string, it doesn't exist.
        # Randomize options!
        perm = np.random.permutation(4)
        letters = ['A','B','C','D']
        choices_orig = [self.choiceA, self.choiceB, self.choiceC, self.choiceD]
        corrects_orig = [l==self.correct_choice for l in letters]
        choices = [choices_orig[ind] for ind in perm]
        corrects = [corrects_orig[ind] for ind in perm]
        correct = letters[np.where(corrects)[0][0]]

        return self.question_text, choices, correct

    def __repr__(self):
        question_string = f'{self.question_text} \n'
        question_string += f'  A. {self.choiceA} \n'
        question_string += f'  B. {self.choiceB} \n'
        question_string += f'  C. {self.choiceC} \n'
        question_string += f'  D. {self.choiceD} \n'
        question_string += f'Correct answer: {self.correct_choice}\n'

        return question_string

def initialize_users():
    # When models.py is run by itself, the database gets established.
    # 3. Database checks
    # Check that database exists and contains the admin entry
    # If not, initialize database
    db.create_all()
    # Add default user "admin"
    admin_user = User(username='admin')
    admin_user.set_password('123456')
    db.session.add(admin_user)
    try:
        db.session.commit()
    except:
        db.session.rollback()


if __name__ == '__main__':
    initialize_users()
    # Try initiating some MC questions!
    mc = MultipleChoice(
        game_number = 1,
        uses_images = False,
        question_text = "What is equal to 1 + 1 in binary? ",
        choiceA = '1',
        choiceB = '2',
        choiceC = '10',
        choiceD = '101',
        correct_choice = 'C',
        difficulty = 'easy'
    )

    print(mc)
    print(mc.check_answer('10'))
    a,b,c = mc.get_randomized_data()
    print(a)
    print(b)
    print(c)