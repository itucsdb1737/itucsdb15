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