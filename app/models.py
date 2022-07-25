# Database models
# TODO - follow Stackoverflow guide.
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db
from datetime import datetime

class User(UserMixin, db.Model):
    # Basic fields
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(10),index=True,unique=True)
    password_hash = db.Column(db.String(128),index=False,unique=False)
    joined_at = db.Column(db.Date(),index=True,default=datetime.utcnow())

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

    def __repr__(self):
        return f'ID: {self.id}; user name: {self.username}; date registered: {self.joined_at}'

class Calibration(db.Model):
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

#class Progress():
    #id = db.Column(db.Integer(),primary_key=True)
    #game_number = db.Column(db.Integer(),index=True)
    #num_stars = db.Column(db.Integer(),)


if __name__ == '__main__':
    # When models.py is run by itself, the database gets established.
    # 3. Database checks
    # Check that database exists and contains the admin entry
    # If not, initialize database & add admin entry

    db.create_all()
    # Add default user "admin"
    admin_user = User(username='admin')
    admin_user.set_password('123456')
    db.session.add(admin_user)
    try:
        db.session.commit()
    except:
        db.session.rollback()