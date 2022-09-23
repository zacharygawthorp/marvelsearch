from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length

class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Choose Password', validators=[Length(min=6)])
    header_image_url = StringField('(Optional) Header Image URL')
    image_url = StringField('(Optional) Image URL')

class LoginForm(FlaskForm):
    """Login Form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class UpdateUserProfileForm(FlaskForm):
    """Update user profile form."""

    username = StringField('Username')
    email = StringField('E-mail')
    password = PasswordField('Password', validators=[Length(min=6)])
    bio = StringField('Bio')
    header_image_url = StringField('(Optional) Header Image URL')
    image_url = StringField('(Optional) Image URL')
   