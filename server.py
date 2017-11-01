import datetime
import os
import json
import re
import psycopg2 as dbapi2

import sqlalchemy
from wtforms import Form
from flask import json
from functools import wraps
from wtforms import StringField, PasswordField, SubmitField, validators, BooleanField
from wtforms.validators import DataRequired
from flask import Flask
from flask import render_template
from flask import redirect
from flask.helpers import url_for
from flask import flash, request, session, abort
from flask_login import LoginManager, UserMixin,login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt


app = Flask(__name__)
app.secret_key = "secretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Batuhan190393@localhost/postgres'
db = SQLAlchemy(app)

def get_elephantsql_dsn(vcap_services):
    parsed = json.loads(vcap_services)
    uri = parsed["elephantsql"][0]["credentials"]["uri"]
    match = re.match('postgres://(.*?):(.*?)@(.*?)(:(\d+))?/(.*)', uri)
    user, password, host, _, port, dbname = match.groups()
    dsn = """user='{}' password='{}' host='{}' port={}
             dbname='{}'""".format(user, password, host, port, dbname)
    return dsn


class SignupForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=20), validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired(),
                                          validators.EqualTo('confirm', message="Passwords must match.")])
    email = StringField('E-mail', [validators.Length(min=6, max=20), validators.DataRequired()])
    confirm = PasswordField('Repeat Password', [validators.DataRequired()] )
    accept_tos = BooleanField('I accept the Terms of Service and the Privacy Notice.', [validators.DataRequired()])
    submit = SubmitField('Sign Up')



class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column('username',db.String(30), unique=True, nullable=False)
    email = db.Column('email', db.String(30), nullable=False)
    password = db.Column('password', db.String(100), nullable=False)

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User %r>' % self.user


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        return user
    return None


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login'))
    return wrap

@app.route('/initdb_1737')
def initialize_database():
    db.drop_all()
    db.create_all()
    return redirect(url_for('home_page'))


@app.route('/')
def home_page():
    return render_template('home.html')



@app.route('/login', methods=['GET','POST'])
def login():
    message = None
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user:
            if user.password == request.form['password']:
                login_user(user)
                session['logged_in'] = True
                session['username'] = user.username
                flash('You were just logged in as ' + user.username)
                next_page = request.args.get('next', url_for('home_page'))
                return redirect(next_page)
            else:
                message='Wrong password !'
                return render_template('login.html', message=message)
        else:
            message = 'Wrong username !'
            return render_template('login.html', message=message)
    else:
        message = 'Invalid credentials !'
        return render_template('login.html', message=message)


@app.route('/signup', methods=['GET','POST'])
def register():
    try:
        form = SignupForm(request.form)
        if request.method == 'POST' and form.validate():
            username = form.username.data
            email = form.email.data
            password = str(form.password.data)
            if User.query.filter_by(username=username).all():
                flash('The username is already taken, please choose another')
                return render_template('signup.html', form=form)
            else:
                new_user = User(str(form.username.data), str(form.password.data), str(form.email.data))
                db.session.add(new_user)
                db.session.commit()
                flash("Thanks for joining our site")
                return redirect(url_for('login'))
        else:
            return render_template('signup.html', form=form)
    except Exception as e:
        return (str(e))



@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash('You were just logged out')
    return redirect(url_for('home_page'))

@app.route('/store')
def store_page():
    return render_template('store.html')


@app.route('/library')
def library_page():
    return render_template('library.html')

@app.route('/blog')
def blog_page():
    return render_template('blog.html')


@app.route('/profile')
def profile_page():
    return render_template('profile.html')




if __name__ == '__main__':

    VCAP_APP_PORT = os.getenv('VCAP_APP_PORT')
    if VCAP_APP_PORT is not None:
        port, debug = int(VCAP_APP_PORT), False
    else:
        port, debug = 5000, True

    VCAP_SERVICES = os.getenv('VCAP_SERVICES')
    if VCAP_SERVICES is not None:
        app.config['dsn'] = get_elephantsql_dsn(VCAP_SERVICES)
    else:
        app.config['dsn'] = """user='postgres' password='Batuhan190393'
                               host='localhost' port=5432 dbname='postgres'"""
    app.run(host='0.0.0.0', port=port, debug=debug)
