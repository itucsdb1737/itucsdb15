import os
import json
import re
import psycopg2 as dbapi2


from flask import json
from userlist import UserList
from activity import Activity
from activitylist import ActivityList
from flask import current_app as app
from functools import wraps
from wtforms import Form, StringField, PasswordField, SubmitField, validators, BooleanField
from flask import Flask, Blueprint
from user import User
from flask import render_template
from flask import redirect
from flask.helpers import url_for
from flask import flash, request, session
from activitylist import formatDate
import time
import datetime

site = Blueprint('site', __name__)

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first.")
            return redirect(url_for('site.login'))
    return wrap

@site.route('/')
def home_page():
    activities = app.activitylist.get_all_activities()
    return render_template('home.html', activities=activities)

class SignupForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=20)])
    password = PasswordField('Password', [validators.DataRequired(),
                                          validators.EqualTo('confirm', message="Passwords must match.")])
    email = StringField('E-mail', [validators.Length(min=4, max=20)])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the Terms of Service and the Privacy Notice.', [validators.DataRequired()])
    submit = SubmitField('Sign Up')


@site.route('/login', methods=['GET','POST'])
def login():
    message = None
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        attempted_username = request.form['username']
        attempted_password = request.form['password']
        user = app.userlist.get_user(attempted_username)
        if user is None:
            message = 'Invalid credentials!'
            return render_template('login.html', message=message)
        else:
            password = app.userlist.get_password(attempted_username)
            if password == attempted_password:
                session['logged_in'] = True
                session['username'] = attempted_username
                flash('You were just logged in as ' + attempted_username + ".")
                next_page = request.args.get('next', url_for('site.home_page'))
                return redirect(next_page)
            else:
                message = 'Invalid credentials !'
                return render_template('login.html', message=message)
    else:
        message = 'Invalid credentials !'
        return render_template('login.html', message=message)


@site.route('/signup', methods=['GET','POST'])
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
                app.userlist.add_user(new_user.username,new_user.password,new_user.email)
                app.activitylist.add_activity(new_user.username,"New user has been joined", formatDate())
                flash("Thanks for joining our site.")
                return redirect(url_for('site.login'))
        else:
            return render_template('signup.html', form=form)

    except Exception as e:
        return (str(e))


@site.route("/logout")
@login_required
def logout():
    session.clear()
    flash('You were just logged out.')
    return redirect(url_for('site.home_page'))

@site.route('/store')
def store_page():
    return render_template('store.html')


@site.route('/library')
@login_required
def library_page():
    return render_template('library.html', username=session['username'])

@site.route('/blog')
def blog_page():
    return render_template('blog.html')


@site.route('/profile')
@login_required
def profile_page():
    return render_template('profile.html', username=session['username'])
