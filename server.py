import os
import json
import re
import psycopg2 as dbapi2

from flask_wtf import Form
from flask import json
from functools import wraps
from wtforms import StringField, PasswordField, SubmitField, validators, BooleanField
from flask import Flask
from flask import render_template
from flask import redirect
from flask.helpers import url_for
from flask import flash, request, session
from flask_login import LoginManager, UserMixin




app = Flask(__name__)
app.secret_key = "secretkey"


def get_elephantsql_dsn(vcap_services):
    parsed = json.loads(vcap_services)
    uri = parsed["elephantsql"][0]["credentials"]["uri"]
    match = re.match('postgres://(.*?):(.*?)@(.*?)(:(\d+))?/(.*)', uri)
    user, password, host, _, port, dbname = match.groups()
    dsn = """user='{}' password='{}' host='{}' port={}
             dbname='{}'""".format(user, password, host, port, dbname)
    return dsn


class SignupForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=20)])
    password = PasswordField('Password', [validators.DataRequired(),
                                          validators.EqualTo('confirm', message="Passwords must match.")])
    email = StringField('E-mail', [validators.Length(min=4, max=20)])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the Terms of Service and the Privacy Notice.', [validators.DataRequired()])
    submit = SubmitField('Sign Up')



class User(UserMixin):
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email  = email

    def get_id(self):
        def get_id(self):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = "SELECT ID FROM USERS WHERE (USERNAME = %s)"
                cursor.execute(query, (self.username,))
                user = cursor.fetchone()
                return user



login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    #user = User.query.filter_by(id=user_id).first()
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """SELECT * FROM USERS WHERE (ID= (%s))"""
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()[2]
        connection.commit()
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
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = """DROP TABLE IF EXISTS USERS"""
        cursor.execute(query)

        query = """CREATE TABLE USERS(
                 ID SERIAL NOT NULL,
                 USERNAME VARCHAR(30),
                 PASSWORD VARCHAR(30),
                 EMAIL VARCHAR(30),
                 PRIMARY KEY(ID)
                 )"""
        cursor.execute(query)

        connection.commit()
    return redirect(url_for('home_page'))


@app.route('/')
def home_page():
    return render_template('home.html')



@app.route('/login', methods=['GET','POST'])
def login():
    message = None
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        attempted_username = request.form['username']
        attempted_password = request.form['password']
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT ID FROM USERS WHERE (USERNAME = %s)"""
            cursor.execute(query, (attempted_username,))
            user = cursor.fetchone()
            if user is None:
                message = 'Invalid credentials!'
                return render_template('login.html', message=message)
            else:
                with dbapi2.connect(app.config['dsn']) as connection:
                    cursor = connection.cursor()
                    query = """SELECT PASSWORD FROM USERS WHERE (USERNAME=%s)"""
                    cursor.execute(query, (attempted_username,))
                    result = cursor.fetchone()[0]
                    connection.commit()
                    password = result
                if password == attempted_password:
                    session['logged_in'] = True
                    session['username'] = attempted_username
                    flash('You were just logged in as ' + attempted_username)
                    next_page = request.args.get('next', url_for('home_page'))
                    return redirect(next_page)
                else:
                    message = 'Invalid credentials !'
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
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """SELECT COUNT(*) FROM USERS WHERE (USERNAME=(%s))"""
                cursor.execute(query, (username,))
                num = cursor.fetchone()[0]
                connection.commit()
                num = int(num)
            if num > 0:
                message = 'The username is already taken, please choose another'
                return render_template('signup.html', form=form, message=message )
            else:
                new_user = User(str(form.username.data), str(form.password.data), str(form.email.data))
                with dbapi2.connect(app.config['dsn']) as connection:
                    cursor = connection.cursor()
                    query = """INSERT INTO USERS (USERNAME,PASSWORD, EMAIL) VALUES (%s, %s, %s)"""
                    cursor.execute(query, (new_user.username, new_user.password, new_user.email))
                    connection.commit()
                    cursor.close()
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
@login_required
def library_page():
    return render_template('library.html')

@app.route('/blog')
def blog_page():
    return render_template('blog.html')


@app.route('/profile')
@login_required
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
