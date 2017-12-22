Parts Implemented by Batuhan Islek
================================

HANDLERS
########

Sign Up User
***********

Sign up operation is done in the handlers.py. It is written to add new users to the platform. WTForms package is used to maintain signup form.


* SIGN UP FORM

It has username, password, email, confirm password, accept terms fields and submit button. All fields has validators to check whether the conditions are followed.
It checks the length of the input and checks if there is an input or not.

.. code-block:: python

    class SignupForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=20)])
    password = PasswordField('Password', [validators.DataRequired(),
                                          validators.EqualTo('confirm', message="Passwords must match.")])
    email = StringField('E-mail', [validators.Length(min=4, max=20)])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the Terms of Service and the Privacy Notice.', [validators.DataRequired()])
    submit = SubmitField('Sign Up')



* /SIGN UP

Sign up functions takes the input parameters from the SignupForm and checks if there is a user with the taken information. If there is, it flashes a message as "Invalid credentials",
if not it adds the user to the userlist and updates the activity feed with "New user has been joined".

.. code-block:: python

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




Login User
***********

* /LOGIN

In the login operation, a form is used the take username and password parameters. If there is not a user with taken parameters it gives a message as **'Invalid credentials!'**.
If the login is successful, we start a session for this user with **session['logged_in']**. A message is sent to the home page as **'You were just logged in as ' + attempted_username**

.. code-block:: python

    @site.route('/login', methods=['GET','POST'])
    def login():
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


* LOGIN DECORATOR

Decator is used to prevent some places to open without login in. So it returns a flash message if a place is visited wtihout login as **"You need to login first."** and
returns the user to the login page. If it is successful, it allows user to enter the place.

.. code-block:: python

    def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first.")
            return redirect(url_for('site.login'))
    return wrap


* /LOG OUT

Log out the user with a flash message and redirects it to the home page. Flash message is given as **'You were just logged out.'**


.. code-block:: python

    @site.route("/logout")
    @login_required
    def logout():
        session.clear()
        flash('You were just logged out.')
        return redirect(url_for('site.home_page'))


Store Page
***********

* /STORE

Store page shows all the games in a card format with the game informations. So it returns all games to the store.html

.. code-block:: python

    @site.route('/store')
    def store_page():
        all_games = app.store.get_all_games()
        return render_template('store.html', games = all_games)




* /STORE/ADD

It adds a game to the store with filling the add game form with game informations and submit. It returns an error message if all the areas are not filled as **'Fill all the areas !'**.
It renders to the store page if the game is added and adds activity to the activity list as **"New game has been added : "**.

.. code-block:: python

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




Library Page
***********

* LIBRARY

It shows the current users purchase history. It gets the session username and gets all the games where the buyer of the game is the current user. It returns all selected games to the library page.
When the user buys a game, it sends the game_id to he /library. Then the title and the price of the game is get with parsing the returning value. Then game is added to the library automatically.


.. code-block:: python

    @site.route('/library', methods=['GET', 'POST'])
    @login_required
    def library_page():
        if request.method == 'GET':
            buyer = session['username']
            library_games_all = app.library.get_all_games(buyer)
            return render_template('library.html', username=session['username'], games=library_games_all)

        if request.method == 'POST':
            tag = request.form['buy_now']
            tag = tag.split(":")
            title = tag[1]
            price = tag[3]
            username = session['username']
            content = app.store.get_game_content(title)
            app.library.add_game(title,"",formatDate(),content,"",price, username)
            return redirect(url_for('site.store_page'))



Profile Page
***********

* PROFILE

Profile page gets the current user's informations with getter functions with giving username paramater. Then it sends all the results which are username, email, name_surname, date, gender,
address, phone_number and join_date to the profile.html page.

.. code-block:: python

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

* EDIT PROFILE

The edit profile button leads to this function. It shows the edit_profile.html page, It gets name, gender, address and phone number informations from the form and updates the
user properties accordingly after saving the changes.

.. code-block:: python

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

* DELETE PROFILE (ACCOUNT)

When user deletes profile, it deletes it from the user list, closes and clears the session. Then sends message to the home page as **'You deleted your account.'**.

.. code-block:: python

    @site.route('/profile/delete_profile')
    def delete_profile():
        username = session['username']
        app.userlist.delete_user(username)
        session['logged_in']=False
        session.clear()
        flash('You deleted your account.')
        return redirect(url_for('site.home_page'))





Blog Page
***********

* /BLOG

Blog page show all the post that has been added. It directs the edit, delete and +1 buttons for edit, delete and like operations.

.. code-block:: python

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



* /BLOG/ADD POST

It adds the post to the blog with the title and content informations.Then it updates the activity feed. User should fill all the areas to add a post.

.. code-block:: python

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


* /BLOG/EDIT POST

After clicking the edit button, it returns a form to edit the fields of the post. Then returns all posts to the blog.html page.

.. code-block:: python

    @site.route('/blog/edit_post', methods=['GET', 'POST'])
    def edit_page():
         if request.method == 'GET':
           return render_template('edit_post.html')

         if request.method == 'POST':
           index = int(request.form['tag'])
           new_title = request.form['post_title']
           old_title = app.blog.get_post_title(index)
           new_content = request.form['post_content']
           app.blog.update_post(new_title, new_content, index)
           all_posts = app.blog.get_all_posts()
           app.activitylist.add_activity(session['username'], "Post has been edited : "+ old_title , formatDate())
           return render_template('blog.html', posts = all_posts)




USERS
########
Users Table Initialization
***********

|  All of the tables are dropped if exists and then created.
|  The Users table is initialized in the server.py as follow:

.. code-block:: python

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
                 JOIN_DATE VARCHAR DEFAULT '',
                 BIRTH_DATE VARCHAR DEFAULT '',
                 NAME VARCHAR DEFAULT '',
                 GENDER VARCHAR DEFAULT '',
                 ADDRESS VARCHAR DEFAULT '',
                 PHONE VARCHAR DEFAULT '',
                 PRIMARY KEY(ID)
                 )"""
    cursor.execute(query)

Users entity has 10 attributes.
    - **ID :** ID is a serial value that increments when new users are added. It is also the primary key of the users.
    - **USERNAME :** Username is VARCHAR type attribute that is limited with 30 characters. It is used as login parameter.
    - **PASSWORD :** Password is VARCHAR type attribute that is limited with 30 characters. It is used as login parameter.
    - **EMAIL :** Email is VARCHAR type with limit of 30 characters.
    - **JOIN_DATE :** Join date is VARCHAR type and given empty string as DEFAULT.
    - **BIRTH_DATE :** Birth date is VARCHAR type and given empty string as DEFAULT.
    - **NAME :** Name is VARCHAR type and given empty string as DEFAULT. It holds the name and surname of the user.
    - **GENDER :** Gender is VARCHAR type and given empty string as DEFAULT.
    - **ADDRESS :** Address is VARCHAR type and given empty string as DEFAULT. It holds the address of the user.
    - **PHONE :** Phone is VARCHAR type and given empty string as DEFAULT. It holds the phone number of the user.


User Class Definition
***********
The user class is defined in user.py as follows:

.. code-block:: python

    class User():
        def __init__(self, username, password, email):
            self.username = username
            self.password = password
            self.email = email

User class has username, password and emial attributes that has been initalized with init function. This class used when new user is added as a model.It sets the attributes of the user.

User List Definition
***********

UserList class has all the database activities for the user. It is written in the userlist.py. Main purpose of this class is to make CRUD operations.
ADDING, DELETING, UPDATING and GETTING user informations is handled in this class.

.. code-block:: python

    class UserList:
        def __init__(self):
                self.last_mod_id = None

        def add_user(self, username, password, email):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """INSERT INTO USERS (USERNAME,PASSWORD, EMAIL) VALUES (%s, %s, %s)"""
                cursor.execute(query, (username, password, email,))
                connection.commit()
                cursor.close()

        def update_join_date(self, username, join_date):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """UPDATE USERS
                           SET JOIN_DATE = (%s)
                           WHERE (USERNAME = %s)"""
                cursor.execute(query, (join_date, username,))
                connection.commit()
                cursor.close()
        def get_join_date(self, username):
                with dbapi2.connect(app.config['dsn']) as connection:
                    cursor = connection.cursor()
                    query = "SELECT JOIN_DATE FROM USERS WHERE (USERNAME = %s)"
                    cursor.execute(query, (username,))
                    join_date = cursor.fetchone() [0]
                    return join_date

        def get_user(self, username):
                with dbapi2.connect(app.config['dsn']) as connection:
                    cursor = connection.cursor()
                    query = "SELECT ID FROM USERS WHERE (USERNAME = %s)"
                    cursor.execute(query, (username,))
                    user = cursor.fetchone()
                    return user

        def get_email(self, username):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = "SELECT EMAIL FROM USERS WHERE (USERNAME = %s)"
                cursor.execute(query, (username,))
                email = cursor.fetchone()[0]
                return email

        def get_password(self, username):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """SELECT PASSWORD FROM USERS WHERE (USERNAME=%s)"""
                cursor.execute(query, (username,))
                password = cursor.fetchone()[0]
                connection.commit()
                return password

        def get_name(self, username):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """SELECT NAME FROM USERS WHERE (USERNAME=%s)"""
                cursor.execute(query, (username,))
                name = cursor.fetchone()[0]
                connection.commit()
                return name

        def get_birth_date(self, username):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """SELECT BIRTH_DATE FROM USERS WHERE (USERNAME=%s)"""
                cursor.execute(query, (username,))
                date = cursor.fetchone()[0]
                connection.commit()
                return date

        def update_birth_date(self, username, date):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """UPDATE USERS
                           SET BIRTH_DATE = (%s)
                           WHERE (USERNAME = %s)"""
                cursor.execute(query, (date, username,))
                connection.commit()
                cursor.close()

        def update_name(self, username, name):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """UPDATE USERS
                           SET NAME = (%s)
                           WHERE (USERNAME = %s)"""
                cursor.execute(query, (name, username,))
                connection.commit()
                cursor.close()

        def get_gender(self, username):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """SELECT GENDER FROM USERS WHERE (USERNAME=%s)"""
                cursor.execute(query, (username,))
                date = cursor.fetchone()[0]
                connection.commit()
                return date

        def update_gender(self, username, gender):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """UPDATE USERS
                           SET GENDER = (%s)
                           WHERE (USERNAME = %s)"""
                cursor.execute(query, (gender, username,))
                connection.commit()
                cursor.close()

        def get_address(self, username):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """SELECT ADDRESS FROM USERS WHERE (USERNAME=%s)"""
                cursor.execute(query, (username,))
                address = cursor.fetchone()[0]
                connection.commit()
                return address

        def update_address(self, username, address):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """UPDATE USERS
                           SET ADDRESS = (%s)
                           WHERE (USERNAME = %s)"""
                cursor.execute(query, (address, username,))
                connection.commit()
                cursor.close()

        def get_phone(self, username):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """SELECT PHONE FROM USERS WHERE (USERNAME=%s)"""
                cursor.execute(query, (username,))
                phone = cursor.fetchone()[0]
                connection.commit()
                return phone

        def update_phone(self, username, phone_number):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """UPDATE USERS
                           SET PHONE = (%s)
                           WHERE (USERNAME = %s)"""
                cursor.execute(query, (phone_number, username,))
                connection.commit()
                cursor.close()

        def delete_user(self, username):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """DELETE FROM USERS WHERE (USERNAME=%s)"""
                cursor.execute(query, (username,))
                connection.commit()
                cursor.close()




STORE
########
Store Table Initialization
***********

The Store table is initialized in the server.py as follow:

.. code-block:: python

    query = """CREATE TABLE STORE(
                 ID SERIAL NOT NULL,
                 TITLE VARCHAR(200),
                 PRODUCER VARCHAR(200),
                 PUBLISH_DATE VARCHAR(150),
                 CONTENT VARCHAR,
                 CATEGORY VARCHAR(150),
                 LIKE_COUNT INTEGER,
                 PRICE INTEGER,
                 PRIMARY KEY(ID)
                 )"""
    cursor.execute(query)



Store entity has 8 attributes.
    - **ID :** ID is a serial value that increments when new users are added. It is also the primary key of the games.
    - **TITLE :** Title is VARCHAR type attribute that is limited with 200 characters.
    - **PRODUCER :** Producer is VARCHAR type attribute that is limited with 200 characters.
    - **PUBLISH_DATE :** Publish date is VARCHAR type with limit of 150 characters.
    - **CONTENT :** Content is VARCHAR type.
    - **CATEGORY :** Category is VARCHAR type.
    - **LIKE_COUNT :** Like count is INTEGER type. It holds the name and surname of the user.
    - **PRICE :** Price is INTEGER type and given empty string as DEFAULT.



Game Class Definition
***********
The game class is defined in user.py as follows:

.. code-block:: python

    class Game:
    def __init__(self, title, producer, publish_date, content, category, price):
        self.title = title
        self.producer = producer
        self.publish_date = publish_date
        self.content = content
        self.like_count = 0
        self.category = category
        self.price = price

* Game class has title, producer, publish_date, content, category and price attributes. Only the like count does not taken as parameter to initalize the game.It is given as 0 at start. This is used to modal games to add them into the store.



Store Class Definition
***********

The store class is defined in store.py as follows:

.. code-block:: python

    class Store:
        def add_game(self, title, producer, publish_date, content, category, price):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """INSERT INTO STORE (TITLE, PRODUCER, PUBLISH_DATE, CONTENT, CATEGORY, LIKE_COUNT, PRICE)
                                              VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(query, (title, producer, publish_date, content, category, 0, price,))
                connection.commit()
                cursor.close()

        def get_game_content(self, game_title):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """SELECT CONTENT FROM STORE WHERE (TITLE = %s)"""
                cursor.execute(query, (game_title,))
                game_content = cursor.fetchone()
                return game_content

        def get_all_games(self):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """SELECT ID, TITLE, PRODUCER, PUBLISH_DATE, CONTENT, CATEGORY, PRICE FROM STORE
                           ORDER BY ID DESC"""
                cursor.execute(query)
                all_games = [(id, Game(title, producer, publish_date, content, category, price))
                            for id, title, producer, publish_date, content, category, price in cursor]

                connection.commit()
                cursor.close()
            return all_games

* Store class has 3 functions that is used for ADDING and SHOWING the game informations in the game store. So it has only adding and getting functions for the games.
The database operations of the games are done in this class.


BLOG
########
Blog Table Initialization
***********

Blog table is dropped and created in the server.py

.. code-block:: python

    query = """DROP TABLE IF EXISTS BLOG"""

    query = """CREATE TABLE BLOG(
                 ID SERIAL NOT NULL,
                 TITLE VARCHAR(300),
                 CONTENT VARCHAR,
                 PUBLISH_DATE VARCHAR(150),
                 WRITER VARCHAR(30),
                 LIKE_COUNT INTEGER,
                 PRIMARY KEY(ID)
                 )"""
    cursor.execute(query)


Post Class Definition
***********

In the post class, title, content, publish date, writer and like count is initialized. It is used as a model to add posts to the blog page.

.. code-block:: python

    class Post:
    def __init__(self, title, content, publish_date, writer, like_count):
        self.content = content
        self.title = title
        self.publish_date = publish_date
        self.writer = writer
        self.like_count = like_count

Blog Class Definition
***********

All create, delete, like and get oeprations of the posts are done in this class.

.. code-block:: python

    class Blog:
        def __init__(self):
            self.last_post_id = None

        def add_post(self, title, text, publish_date, writer, like_count):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """INSERT INTO BLOG (TITLE, CONTENT, PUBLISH_DATE, WRITER, LIKE_COUNT) VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(query, (title, text, publish_date, writer, like_count,))
                connection.commit()
                cursor.close()

        def get_post_id(self, title, writer):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """SELECT ID FROM BLOG WHERE (TITLE = %s AND WRITER = %s)"""
                cursor.execute(query, (title, writer,))
                post = cursor.fetchone()
                return post

        def like_post(self, post_id):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """UPDATE BLOG
                           SET LIKE_COUNT = LIKE_COUNT+1
                           WHERE (ID = %s)"""
                cursor.execute(query, (post_id,))
                connection.commit()
                cursor.close()

        def update_post(self, title, content, post_id):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """UPDATE BLOG
                           SET TITLE = (%s),
                           CONTENT = (%s)
                           WHERE (ID = %s)"""
                cursor.execute(query, (title, content, post_id,))
                connection.commit()
                cursor.close()

        def dislike_post(self, post_id):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """UPDATE BLOG
                           SET LIKE_COUNT = LIKE_COUNT-1
                           WHERE (ID = %s)"""
                cursor.execute(query, (post_id,))
                connection.commit()
                cursor.close()

        def get_like_count(self,post_id):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """SELECT LIKE_COUNT FROM BLOG WHERE (ID = %s)"""
                cursor.execute(query, (post_id,))
                post = cursor.fetchone()
                return post

        def get_publishers_post_id(self, writer):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """SELECT ID FROM BLOG WHERE (WRITER = %s)"""
                cursor.execute(query, (writer,))
                post_id = cursor.fetchone()
                return post_id

        def delete_post(self, post_id):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                statement = """DELETE FROM BLOG WHERE (ID = (%s))"""
                cursor.execute(statement, (post_id,))
                connection.commit()
                cursor.close()

        def get_post_title(self, post_id):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                statement = """SELECT TITLE FROM BLOG WHERE (ID = (%s))"""
                cursor.execute(statement, (post_id,))
                title = cursor.fetchone()[0]
                return title

        def get_writer(self, post_id):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                statement = """SELECT WRITER FROM BLOG WHERE (ID = (%s))"""
                cursor.execute(statement, (post_id,))
                writer = cursor.fetchone()[0]
                return writer



        def get_post_content(self, post_id):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                statement = """SELECT CONTENT FROM BLOG WHERE (ID = (%s))"""
                cursor.execute(statement, (post_id,))
                content = cursor.fetchone()
                return content


        def get_all_posts(self):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """SELECT ID, TITLE, CONTENT, PUBLISH_DATE, WRITER, LIKE_COUNT FROM BLOG
                           ORDER BY ID DESC"""
                cursor.execute(query)
                all_posts = [(id, Post(title, content, publish_date, writer, like_count))
                            for id, title, content, publish_date, writer, like_count in cursor]

                connection.commit()
                cursor.close()
            return all_posts


