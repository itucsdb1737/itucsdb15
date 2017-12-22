Parts Implemented by Batuhan Islek
================================

USERS
########
Users Table Initialization
***********

|  All of the tables are dropped if exists and then created.
|  The Users table is initialized in the server.py as follow:

.. code-block:: python
	:linenos:

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
