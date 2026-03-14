from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from wtforms.validators import Email

class UserForm(FlaskForm):

    name = StringField(
        "Name",
        validators=[DataRequired(), Length(min=2, max=50)]
    )

    email = StringField(
        "Email",
        validators=[DataRequired(), Email()]
    )

    phone = StringField(
        "Phone",
        validators=[DataRequired(), Length(min=10, max=15)]
    )

    submit = SubmitField("Submit")