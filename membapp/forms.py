from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,TextAreaField
from wtforms.validators import DataRequired,Email, Length,EqualTo
from flask_wtf.file import FileField, FileRequired,FileAllowed

class ContactForm(FlaskForm):
    screenshot = FileField("upload screenshot")
    
    email = StringField("Your Email: ", validators=[Email(message="Hello, your email should be valid"),DataRequired(message="We will need to have your email address in order to get back to you")])
    confirm_email = StringField("Confirm Email")
    message = TextAreaField("Message", validators=[DataRequired(),Length(min=10,message="This message is too small now")])
    submit = SubmitField("Send Message")    