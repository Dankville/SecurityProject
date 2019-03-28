from flask_wtf import FlaskForm, Form
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Length, Email
from validations import *
from database import DB_Session
from models import User
from passlib.hash import pbkdf2_sha256
from validate_email import validate_email
import re

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators= [DataRequired(message="Enter a username"), validate_name])
    email = StringField("Email", validators = [DataRequired('Please enter your email address'), Email("Needs to be a valid email address")])
    password = PasswordField("Password", validators=[DataRequired(),
        EqualTo("confirm", message="Passwords must match"),
        validate_password
        ])
    confirm = PasswordField("Repeat password", validators=[DataRequired()])
    twoFactorAuthEnabled = BooleanField("Enable 2 factor authentication")
    twoFactorAuthKey = StringField("2 Factor Authentication key", validators=[validate_2FactorAuthKey])
        
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])

class TwoFactorAuthForm(FlaskForm):
    verify = StringField("Verify", validators=[DataRequired()])

class EditProfileForm(FlaskForm):
    username = StringField("Username")
    email = StringField("Email")
    password = PasswordField("Password")
    confirm = PasswordField("Confirm new Password")

    old_password = PasswordField("Current Password", validators = [DataRequired()])

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        # User in session
        self.loggedInUser = kwargs['user']

        print ('self.username.data: %s' % (self.username.data))
        print ('self.loggedInUser.username: %s' % (self.loggedInUser.username))

    def validate(self):
        validated = True

        if self.loggedInUser is None:
            validated = False

        # means the user has changed his password, so we have to add the usual validators manually here since this is a special case form
        if self.password.data is not None:
            if not pbkdf2_sha256.verify(self.password.data, self.loggedInUser.password):
                errorList = []
                pwd = self.password.data
                if not (any(x.isupper() for x in pwd) and any(x.islower() for x in pwd) and any(x.isdigit() for x in pwd)):
                    errorList.append("Password must contain at least 1 capital, 1 lower case letter and at least 1 number")
                if len(pwd) <= 7:
                    errorList.append("Must be at least 8 characters long")
                self.password.errors = tuple(errorList)
                validated = False

        ## to check if the user changed his username and if so, if the new username already exists in database
        dbsess = DB_Session()
        userCheck = dbsess.query(User).filter_by(username = self.username.data).first()
        dbsess.close()
        if self.username.data != self.loggedInUser.username:
            if self.username.data is not None:
                errorList = []
                if userCheck is not None:
                    errorList.append('username already taken')
                    validated = False

                if len(self.username.data) > 50:
                    errorList.append('username must be less than 50 characters long')
                    validated = False
                
                if not re.match("^[A-Za-z0-9_-]*$", self.username.data):
                    errorList.append("Name can only contain numbers, letters, '-' and '_'")
                    validated = False
                
                self.username.errors = tuple(errorList)

        if self.email.data != self.loggedInUser.email:
            if self.email.data is not None:
                errorList = []
                if not validate_email:
                    errorList.append('Should be a valid email')
                    self.email.errors = tuple(errorList)
                    validated = False               

        if not pbkdf2_sha256.verify(self.old_password.data, self.loggedInUser.password):
            errorList = []
            if self.old_password is None:
                errorList.append("Current password is required, when trying to change your profile.")
            else:
                errorList.append("Wrong current password.")
            self.old_password.errors = tuple(errorList)
            validated = False

        return validated

class ForgotPasswordForm(FlaskForm):
    email = StringField("email", validators = [DataRequired('we need your email to send you a code')])
    code = StringField("code")

class TestForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators = [DataRequired()])

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        print(args[0])

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            print('rv is none')
            return False

        if (self.username.data != 'test'):
            self.username.errors.append("username should be test")
            return False
        
        return True
    
