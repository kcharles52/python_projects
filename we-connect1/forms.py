from wtforms import Form, StringField, TextAreaField, PasswordField, validators, TextField
from wtforms.validators import DataRequired, Length, EqualTo

class RegisterForm(Form):
    name = StringField('Name', [validators.length(min=4,max=50)])
    username = StringField('UserName',[validators.length(min=4, max=25)])
    email = StringField('Email', [validators.length(min=6,max=50)])
    password = PasswordField('Password',[
        validators.DataRequired(),
        validators.EqualTo('confirm','Password didn\'t match')
    ])
    confirm = PasswordField('Confirm Password')

class LoginForm(Form):
    username = TextField('Username', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])

class BusinessForm(Form):
    title = TextField('Business Titile',[DataRequired()])
    textarea= TextAreaField('About the Business',[DataRequired()])