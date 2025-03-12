import os
from flask import Flask, render_template, make_response, request, redirect, url_for, blueprints, session, g
from routes.example_route import example_blueprint


app = Flask(__name__, static_folder='static', template_folder='templates')

load_dotenv()
app.secret_key = os.getenv('SECRET_KEY') # Secret key for session

# User class for session
class User:
    def __init__(self, username):
        self.username = username

# Note Cookies:
# When using session this encrypts the cookies
# otherwise using cookies directly will store them as plain text

# Sets the session cookies to a user when logged in (Not using database currently just a test dummy)
@app.route('/set_session')
def set_session():
    session['username'] = 'JohnDoe'
    return redirect(url_for('index'))

# removes session cookies when logged out 
@app.route('/del_session')
def del_session():
    session.pop('username', None)
    return redirect(url_for('index'))

# Loads the user from the session if it exists
@app.before_request
def before_request():
    g.user = None
    if 'username' in session:
        g.user = User(session['username'])

# Injects the user into the context of every template
@app.context_processor
def inject_user():
    return dict(user=g.user)

@app.route('/')
def index():
    return render_template('index.html')


app.register_blueprint(example_blueprint) # Register the blueprint from example for routing

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) # debug false when delpoying
