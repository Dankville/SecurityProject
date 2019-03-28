from flask import Flask, render_template, request, redirect, session, url_for
from Forms import RegistrationForm, LoginForm, TwoFactorAuthForm, EditProfileForm, ForgotPasswordForm
from database import DB_Session, init_db
from models import User, Role, ResetPwdCode
from wtforms.validators import ValidationError
from passlib.hash import pbkdf2_sha256
import os
import jsonpickle
import json
from TwoFactorAuth import TwoFactorAuth
from DBInitializer import RoleInitializer, UserInitializer
from validate_email import validate_email
import smtplib

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Geheim01!'
app.secret_key = os.urandom(24)
init_db()
RoleInitializer()
UserInitializer()
totp = TwoFactorAuth()

def getUser():
    db_session = DB_Session()
    user = db_session.query(User).filter_by(username = session['username']).first()
    db_session.close()
    return user

def editProfileFunc(loggedInUser, form):
    changedUsername = False
    if form.username.data is not None:
        if form.username.data != loggedInUser.username:
            dbsess = DB_Session()
            dbsess.query(User).filter(username = loggedInUser.username).update({'username' : form.username.data})
            dbsess.commit()
            dbsess.close()
            changedUsername = True

    if form.password.data is not None:
        if loggedInUser.username != pbkdf2_sha256.hash(form.password.data):
            dbsess = DB_Session()
            dbsess.query(User).filter(username = loggedInUser.username).update({'password' : pbkdf2_sha256.hash(form.password.data)})
            dbsess.commit()
            dbsess.close()
    
    if form.email.data is not None:
        if loggedInUser.email != form.email.data:
            dbsess = DB_Session()
            dbsess.query(User).filter(username = loggedInUser.username).update({'email' : form.email.data})
            dbsess.commit()
            dbsess.close()

    if changedUsername:
        dbsess = DB_Session()
        changedUser = dbsess.query(User).filter_by(username = form.username.data).first()
        dbsess.close()
        session['username'] = changedUser.username 

def SendAndSaveForgotPasswordCode(email):
    code = os.urandom(8)
    
    content = "Yo dog here's your code to reset your password: \n <b>%s</b>" % (code)

    print(email)
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login('mpfib0test@gmail.com', 'Geheimlol!1')
        server.sendmail('mpfib0test@gmail.com', email, content)
        server.close()
        
        dbsess = DB_Session()
        user = dbsess.query(User).filter_by(email = email).first()
        newCode = ResetPwdCode(owner = user.username, code = code)
        dbsess.add(newCode)
        dbsess.commit()
        dbsess.close()
    except:
        pass

@app.route('/')
def index():
    if 'username' in session:
        db_session = DB_Session()
        loginUser = db_session.query(User).filter_by(username = session['username']).first()
        db_session.close()
        if loginUser is not None:
            userJson = json.loads(jsonpickle.encode(loginUser))
            # app.logger.info('%s logged into existing session' % loginUser.username)
            return render_template('profile.html', user = userJson)
    
    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if form.validate_on_submit():
        db_session = DB_Session()
        loginUser = db_session.query(User).filter_by(username = form.username.data).first()
        db_session.close()

        if loginUser is not None:
            if pbkdf2_sha256.verify(form.password.data, loginUser.password):
                session['username'] = loginUser.username
                userJson = json.loads(jsonpickle.encode(loginUser))
                # app.logger.info('%s logged in and created session' % loginUser.username)
                # TODO Add logging
                if loginUser.twoFactorAuthEnabled:
                    totp.SetAuthenticator(loginUser.twoFactorAuthKey)
                    return redirect(url_for("twoFactorAuth"))

                return render_template("profile.html", user = userJson)
        return render_template("login.html", form = form, loginError = "Wrong username or password")

    return render_template('login.html', form = form)


@app.route('/twoFactorAuth', methods=['GET', 'POST'])
def twoFactorAuth():
    form = TwoFactorAuthForm(request.form)
    if form.validate_on_submit():
        if (totp.Verify(form.verify.data)):
            db_session = DB_Session()
            loginUser = db_session.query(User).filter_by(username = session['username']).first()
            db_session.close()
            userJson = json.loads(jsonpickle.encode(loginUser))
            return render_template("profile.html", user = userJson)
        else:
            return render_template("twoFactorAuth.html", form = form, error = "Wrong code")           

    return render_template('twoFactorAuth.html', form = form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if form.validate_on_submit():
        db_session = DB_Session()

        hashedPWD = pbkdf2_sha256.hash(form.password.data)

        newUser = User(form.username.data, hashedPWD, form.email.data, form.twoFactorAuthEnabled.data, form.twoFactorAuthKey.data)
        db_session.add(newUser)

        db_session.commit()
        db_session.close()
        # app.logger.info('Account created with username: %s' % form.username.data)
        
        return render_template('index.html')

    return render_template('register.html', form = form)


@app.route('/profile')
def profile():
    if 'username' in session:
        db_session = DB_Session()
        loginUser = db_session.query(User).filter_by(username = session['username']).first()
        db_session.close()
        if loginUser is not None:
            userJson = json.loads(jsonpickle.encode(loginUser))
            # app.logger.info('%s logged into existing session' % loginUser.username)
            return render_template('profile.html', user = userJson)
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


@app.route('/allUsers', methods = ['GET'])
def allUsers():
    db_session = DB_Session()
    allUsers = db_session.query(User).all()
    db_session.close()
    return render_template('allUsers.html', allUsers = allUsers)


@app.route('/logout', methods = ['POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/editProfile', methods = ['GET', 'POST'])
def editProfile():
    if 'username' in session:
        loggedInUser = getUser()
        form = EditProfileForm(request.form, user = loggedInUser)
        if form.validate_on_submit():
            editProfileFunc(loggedInUser, form)
            return render_template("profile.html")

        return render_template("editProfile.html", form = form)
    else:
        return render_template("login.html", form = LoginForm())

@app.route('/forgotPassword', methods = ['GET', 'POST'])
def forgotPassword():
    form = ForgotPasswordForm(request.form)

    if form.validate_on_submit():
        
        if form.code.data != "" and form.email.data != "":
            dbsess = DB_Session()
            user = dbsess.query(User).filter_by(email = form.email.data).first()
            dbsess.close()
            print(user.username)
            if user is not None:
                code = dbsess.query(ResetPwdCode).filter_by(owner = user.username).first()
                if code == form.code.data:
                    return "Succes"
                else:
                    return "Wrong code"
            else:
                render_template   
        
        if form.code.data == "" and validate_email(form.email.data):
            print("sending code to email: %s" % (form.email.data))
            SendAndSaveForgotPasswordCode(form.email.data)

    return render_template('forgotPassword.html', form = form)


if __name__ == "__main__":
    app.run(debug=True, port=5000)