"""SQLAlchemy models for Marvel Search."""

from flask_bcrypt import Bcrypt 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Constraint, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

bcrypt = Bcrypt()
db = SQLAlchemy()

class Favorite(db.Model):

    __tablename__ = 'favorites'


    character_id = db.Column(
        db.Integer,
        primary_key=True,
        
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="CASCADE"),
        primary_key=True
    )

    character_name = db.Column(
        db.Text
    )

    
class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text, 
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    header_image_url = db.Column(
        db.Text,
        default="/static/images/default-header.jpg"
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-profile.png",
    )
    
    bio = db.Column(
        db.Text,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    favorites = db.relationship("Favorite", backref="users", cascade="all, delete-orphan")


    @classmethod
    def signup(cls, username, email, password, header_image_url, image_url):
        """Sign up user.

        Hashes password and adds user to the system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            header_image_url=header_image_url,
            image_url=image_url,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with 'username and 'password'.

        Method searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If it can't find a matching user (or the password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


def connect_db(app):
    """Connect this database to marvel-search DB."""

    db.app = app
    db.init_app(app)