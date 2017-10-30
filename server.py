import datetime
import os
import json
import re
import psycopg2 as dbapi2

from flask import Flask
from flask import render_template
from flask import redirect
from flask.helpers import url_for


app = Flask(__name__)


def get_elephantsql_dsn(vcap_services):
    parsed = json.loads(vcap_services)
    uri = parsed["elephantsql"][0]["credentials"]["uri"]
    match = re.match('postgres://(.*?):(.*?)@(.*?)(:(\d+))?/(.*)', uri)
    user, password, host, _, port, dbname = match.groups()
    dsn = """user='{}' password='{}' host='{}' port={}
             dbname='{}'""".format(user, password, host, port, dbname)
    return dsn




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
                 PRIMARY KEY(ID)
                 )"""
        cursor.execute(query)

        connection.commit()
    return redirect(url_for('home_page'))


@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/store')
def store_page():
    return render_template('store.html')

@app.route('/library')
def library_page():
    return render_template('library.html')

@app.route('/blog')
def blog_page():
    return render_template('blog.html')

@app.route('/profile')
def profile_page():
    return render_template('profile.html')

@app.route('/login')
def login_page():
    return render_template('login.html')


if __name__ == '__main__':
    VCAP_APP_PORT = os.getenv('VCAP_APP_PORT')
    if VCAP_APP_PORT is not None:
        port, debug = int(VCAP_APP_PORT), False
    else:
        port, debug = 5000, True

    VCAP_SERVICES = os.getenv('VCAP_SERVICES')
    if VCAP_SERVICES is not None:
        app.config['dsn'] = get_elephantsql_dsn(VCAP_SERVICES)
    else:
        app.config['dsn'] = """user='postgres' password='Batuhan190393'
                               host='localhost' port=5432 dbname='postgres'"""
    app.run(host='0.0.0.0', port=port, debug=debug)
