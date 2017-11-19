import psycopg2 as dbapi2
from activity import Activity
from flask import current_app as app
import datetime


def formatDate():
    i = datetime.datetime.now()
    year = str(i.year)
    month = str(i.month)
    day = str(i.day - 1)
    currentDate = day + "-" + month + "-" + year
    return currentDate

class ActivityList:
    def __init__(self):
            self.last_mod_id = None

    def add_activity(self, activator, status, date):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """INSERT INTO ACTIVITIES (ACTIVATOR, STATUS, DATE) VALUES (%s, %s, %s)"""
            cursor.execute(query, (activator, status, date))
            connection.commit()
            cursor.close()

    def get_last_activity(self):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = "SELECT TOP 1 * FROM ACTIVITIES ORDER BY ID DESC"
                cursor.execute(query, ())
                activity = cursor.fetchone()
                return activity

    def get_all_activities(self):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT ID, ACTIVATOR, STATUS, DATE FROM ACTIVITIES
                       ORDER BY ID DESC"""
            cursor.execute(query)
            table = [(id, Activity(activator,status,date))
                        for id, activator, status, date in cursor]

            connection.commit()
            cursor.close()
        return table


