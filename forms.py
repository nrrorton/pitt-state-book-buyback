from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange, Optional
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    display_name = StringField('Display Name', validators=[DataRequired(), Length(min=2, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, field):
        allowed_domains = {"gus.pittstate.edu", "pittstate.edu"}

        email = field.data.strip().lower()

        try:
            domain = email.split("@")[1]
        except IndexError:
            raise ValidationError("Invalid email format.")
        
        if domain not in allowed_domains:
            raise ValidationError("You must register with a valid Pitt State email address.")
        
        user = User.query.filter_by(email=email).first()
        if user:
            raise ValidationError('That email is already in use. Please choose a different one.')

    def validate_display_name(self, display_name):
        user = User.query.filter_by(display_name=display_name.data).first()
        if user:
            raise ValidationError('That display name is already taken. Please choose a different one.')

class ListingForm(FlaskForm):
    title = StringField('Book Title', validators=[DataRequired(), Length(max=200)])
    author = StringField('Author', validators=[DataRequired(), Length(max=200)])
    edition = StringField('Edition (Optional)', validators=[Length(max=50)])
    condition = SelectField('Condition', choices=[
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('very_good', 'Very Good'),
        ('good', 'Good'),
        ('acceptable', 'Acceptable')
    ], validators=[DataRequired()])
    price = DecimalField('Price ($)', validators=[DataRequired(), NumberRange(min=0)])
    course_code = StringField('Course Code (Optional)', validators=[Length(max=20)])
    professor = StringField('Professor (Optional)', validators=[Length(max=100)])
    description = TextAreaField('Description (Optional)')
    submit = SubmitField('Post Listing')
