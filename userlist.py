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

    def get_user(self, username):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = "SELECT ID FROM USERS WHERE (USERNAME = %s)"
                cursor.execute(query, (username,))
                user = cursor.fetchone()
                return user

    def get_password(self, username):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT PASSWORD FROM USERS WHERE (USERNAME=%s)"""
            cursor.execute(query, (username,))
            password = cursor.fetchone()[0]
            connection.commit()
            return password

