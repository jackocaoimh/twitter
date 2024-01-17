from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class User(db.Model):
    
    __tablename__='users'

    # id = db.Column(db.Integer, 
    #                primary_key=True, 
    #                autoincrement=True)

    username = db.Column(db.String(20),
                         primary_key=True, 
                         nullable=False, 
                         unique=True)

    password = db.Column(db.Text, 
                         nullable=False)
    
    email = db.Column(db.String(50),
                      nullable=False)
    
    first_name = db.Column(db.String(30),
                           nullable=False,
                           unique=False)
    
    last_name = db.Column(db.String(30),
                           nullable=False,
                           unique=False)
    
    # Cascade all mean if the user is deleted all their feedback will be deleted too
    feedback = db.relationship("Feedback", backref="user", cascade="all,delete")
    
    # start_register
    @classmethod
    def register(cls, username, password, email, first_name, last_name):
        
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(password)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")
        # return instance of user w/username and hashed password
        user = cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)
        return user
    # end_register

    # start_authenticate
    @classmethod
    def authenticate(cls, username, password):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            # return user instance
            return user
        else:
            return False
    # end_authenticate    
    
class Feedback(db.Model):

    __tablename__ ='feedback'

    id = db.Column(db.Integer, 
                   primary_key=True, 
                   autoincrement=True)
    
    title = db.Column(db.String(100),
                      nullable=False,
                      )
    
    content = db.Column(db.Text,
                        nullable=False)
    
    username = db.Column(db.String(20),
                        db.ForeignKey('users.username'),
                        nullable=False)
    
    
    

