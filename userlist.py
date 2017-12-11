import psycopg2 as dbapi2
from user import User
from flask import current_app as app

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



