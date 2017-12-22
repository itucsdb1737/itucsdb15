Parts Implemented by Batuhan Islek
================================

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
