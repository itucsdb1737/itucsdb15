import os
import json
import re
import psycopg2 as dbapi2



from userlist import UserList
from activity import Activity
from activitylist import ActivityList
from blog import Blog
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
                app.userlist.add_user(new_user.username, new_user.password,new_user.email)
                app.activitylist.add_activity(new_user.username,
                                              "New user has been joined",
                                              formatDate())
                flash("Thanks for joining our site.")
                app.userlist.update_join_date(new_user.username, formatDate())
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
    all_games = app.store.get_all_games()
    return render_template('store.html', games = all_games)

@site.route('/store/add', methods=['GET','POST'])
def add_game_page():
    if request.method == 'GET':
        return render_template('add_game.html')
    if request.method == 'POST':
        game_title = request.form['game_title']
        game_producer = request.form['game_producer']
        game_publish_date = request.form['game_publish_date']
        game_content = request.form['game_content']
        game_category = request.form['game_category']
        game_price = request.form['game_price']
        if game_title == "" or game_producer == "" or game_publish_date == "" or game_content == "" \
                            or game_category == "" or str(game_price) == "":
            message = 'Fill all the areas !'
            return render_template('add_game.html', message=message)
        else:
            app.store.add_game(game_title, game_producer, game_publish_date, game_content, game_category, game_price)
            app.activitylist.add_activity("GameHouse",
                                      "New game has been added : " + game_title,
                                      formatDate())
            return redirect(url_for('site.store_page'))

@site.route('/library', methods=['GET', 'POST'])
@login_required
def library_page():
    if request.method == 'GET':
        library_games_all = app.library.get_all_games()
        return render_template('library.html', username=session['username'], games=library_games_all)

    if request.method == 'POST':
        tag = request.form['buy_now']
        tag = tag.split(":")
        title = tag[1]
        price = tag[3]
        content = app.store.get_game_content(title)
        app.library.add_game(title,"",formatDate(),content,"",price)

        return redirect(url_for('site.store_page'))

@site.route('/profile')
@login_required
def profile_page():
    username = session['username']
    email = app.userlist.get_email(username)
    name_surname = app.userlist.get_name(username)
    date = app.userlist.get_birth_date(username)
    gender = app.userlist.get_gender(username)
    address = app.userlist.get_address(username)
    phone_number = app.userlist.get_phone(username)
    join_date = app.userlist.get_join_date(username)
    return render_template('profile.html', username=username, email=email, name=name_surname,
                           date=date, gender=gender, address=address, phone_number=phone_number, join_date=join_date)

@site.route('/profile/edit_profile', methods=['GET','POST'])
def edit_profile():
    username = session['username']
    if request.method == 'GET':
        return render_template('edit_profile.html')
    if request.method == 'POST':
        name = request.form['user_name']
        date = request.form['birth_date']
        gender = request.form['gender']
        address = request.form['address']
        phone_number = request.form['phone']
        if name:
            app.userlist.update_name(username, name)
        if date:
            app.userlist.update_birth_date(username, date)
        if gender:
            app.userlist.update_gender(username, gender)
        if address:
            app.userlist.update_address(username, address)
        if phone_number:
            app.userlist.update_phone(username, phone_number)
        else:
            return redirect(url_for('site.profile_page'))

        return redirect(url_for('site.profile_page'))

@site.route('/profile/delete_profile')
def delete_profile():
    username = session['username']
    app.userlist.delete_user(username)
    session['logged_in']=False
    session.clear()
    flash('You deleted your account.')
    return redirect(url_for('site.home_page'))



@site.route('/blog/add_post', methods=['GET','POST'])
def add_post():
    if request.method == 'GET':
        return render_template('add_post.html')
    if request.method == 'POST':
        post_title = request.form['post_title']
        post_content = request.form['post_content']
        if post_title == "" or post_content == "":
            message = 'Fill all the areas !'
            return render_template('add_post.html', message=message)
        else:
            app.blog.add_post(post_title, post_content, formatDate(), session['username'], 0)
            app.activitylist.add_activity(session['username'],
                                          "New post has been added to the Blog : " + post_title,
                                          formatDate())

            return redirect(url_for('site.blog_page'))



@site.route('/blog', methods=['GET', 'POST'])
def blog_page():
    if request.method == 'POST':
        tag = request.form['tag']

        if "clap" in tag:
             tag = tag.split(":")
             index = tag[1]
             app.blog.like_post(index)
             all_posts = app.blog.get_all_posts()
             return render_template('blog.html', posts=all_posts)

        if "edit"in tag:
            tag = tag.split(":")
            index = tag[1]
            content = app.blog.get_post_content(index)
            title = str(app.blog.get_post_title(index))
            writer = app.blog.get_writer(index)
            if writer == session['username']:
                title = title.partition("'")[-1].rpartition("'")[0]
                return render_template('edit_post.html', content=content, title=title, num=index)
            else:
                message = "Only author can edit the post !"
                all_posts = app.blog.get_all_posts()
                return render_template('blog.html',message=message, posts=all_posts)

        if "delete" in tag:
            tag = tag.split(":")
            index = tag[1]
            writer = app.blog.get_writer(index)
            post_title = str(app.blog.get_post_title(index))
            if writer == session['username']:
                app.blog.delete_post(index)
                all_posts = app.blog.get_all_posts()
                app.activitylist.add_activity(session['username'],
                                          "Post has been deleted : " + post_title,
                                          formatDate())
                return render_template('blog.html', posts=all_posts)
            else:
                message = "Only author can delete the post !"
                all_posts = app.blog.get_all_posts()
                return render_template('blog.html',message=message, posts=all_posts)


        else:
            all_posts = app.blog.get_all_posts()
            return render_template('blog.html', posts=all_posts)

    if request.method == 'GET':
        all_posts = app.blog.get_all_posts()
        return render_template('blog.html', posts=all_posts)


@site.route('/blog/edit_post', methods=['GET', 'POST'])
def edit_page():
     if request.method == 'GET':
       return render_template('edit_post.html')
     
     if request.method == 'POST':
       index = int(request.form['tag'])
       new_title = request.form['post_title']
       old_title = str(app.blog.get_post_title(index))
       old_title = old_title.partition("'")[-1].rpartition("'")[0]
       new_content = request.form['post_content']
       app.blog.update_post(new_title, new_content, index)
       all_posts = app.blog.get_all_posts()
       app.activitylist.add_activity(session['username'],
                                     "Post has been edited : "+ old_title , formatDate())
       return render_template('blog.html', posts = all_posts)





