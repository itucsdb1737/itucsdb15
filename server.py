import datetime
import os

from flask import Flask
from flask import render_template


app = Flask(__name__)


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
    app.run(host='0.0.0.0', port=port, debug=debug)
