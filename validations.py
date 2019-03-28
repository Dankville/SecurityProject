from models import User
from wtforms import validators, ValidationError
from database import DB_Session
import re
from passlib.hash import pbkdf2_sha256

def validate_name(form, field):
    if field.data is not None:
        if len(field.data) > 50:
            raise ValidationError("name must be less en 50 characters")
        if not re.match("^[A-Za-z0-9_-]*$", field.data):
            raise ValidationError("Name can only contain numbers, letters, '-' and '_'")
        db_session = DB_Session()
        usernameCheck = db_session.query(User).filter_by(username = field.data).first()
        db_session.close()
        if usernameCheck is not None:
            if usernameCheck.username != field.data:
                raise ValidationError("Username is already taken")

def validate_password(form, field):
    if field.data is not None:
        pwd = field.data
        if not (any(x.isupper() for x in pwd) and any(x.islower() for x in pwd) and any(x.isdigit() for x in pwd)):
            raise ValidationError("Password must contain at least 1 capital, 1 lower case letter and at least 1 number")
        if len(pwd) <= 7:
            raise ValidationError("Must be at least 8 characters long")

def validate_2FactorAuthKey(form, field):
    key = field.data
    if key != "" or key is not None:
        if len(key) < 16:
            raise ValidationError("Key must be longer than 16 character")
        elif len(key) > 32:
            raise ValidationError("Key must be less than 32 characters")
