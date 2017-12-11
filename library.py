from flask import current_app as app
import psycopg2 as dbapi2
from game import Game


class Library:
    def add_game(self, title, producer, publish_date, content, category, price):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """INSERT INTO LIBRARY (TITLE, PRODUCER, PUBLISH_DATE, CONTENT, CATEGORY, LIKE_COUNT, PRICE)
                                          VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (title, producer, publish_date, content, category, 0, price,))
            connection.commit()
            cursor.close()

    def get_all_games(self):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT ID, TITLE, PRODUCER, PUBLISH_DATE, CONTENT, CATEGORY, PRICE FROM LIBRARY
                       ORDER BY ID DESC"""
            cursor.execute(query)
            all_games = [(id, Game(title, producer, publish_date, content, category, price))
                        for id, title, producer, publish_date, content, category, price in cursor]

            connection.commit()
            cursor.close()
        return all_games