import os
from flask import Flask, render_template, make_response, request, redirect, url_for, blueprints, session, g
from dotenv import load_dotenv
from routes.example_route import example_blueprint


app = Flask(__name__, static_folder='static', template_folder='templates')

load_dotenv()
app.secret_key = os.getenv('SECRET_KEY') # Secret key for session

# User class for session
class User:
    def __init__(self, userType, username, ID):
        self.userType = userType
        self.username = username
        self.ID = ID
    
# Note Cookies:
# When using session this encrypts the cookies
# otherwise using cookies directly will store them as plain text

# Sets the session cookies to a user when logged in (Not using database currently just a test dummy)
@app.route('/set_session')
def set_session():
    # logging in is hardcoded when we have page for login we will use the form data to set the session cookies
    
    # if Admin
    session['userType'] = 'Admin'
    session['username'] = 'JohnDoe'
    session['ID'] = 1
    # if Customer
        # session['userType'] = 'Customer'
        # session['username'] = 'JohnDoe'
        # session['ID'] = '1'

    return redirect(url_for('index'))

# removes session cookies when logged out 
@app.route('/del_session')
def del_session():
    g.user = None
    session.pop('userType', None)
    session.pop('username', None)
    session.pop('ID', None)
    return redirect(url_for('index'))

# Loads the user from the session if it exists
@app.before_request
def before_request():
    g.user = None
    if 'userType' in session and 'username' in session and 'ID' in session:
        g.user = User(session['userType'], session['username'], session['ID'])

# Injects the user into the context of every template
@app.context_processor
def inject_user():
    return dict(user=g.user)

@app.route('/Home')
def index():
    return render_template('index.html')

@app.route('/Profile/Base')
def profile_base():
    return render_template('Profile/Base.html')

@app.route('/Profile/<username>')
def user_profile(username):
    if g.user is None:
        return redirect(url_for('page_not_found'))
    else:
        return redirect(url_for('user_profile_page', username=username))

@app.route('/Profile/<username>/PersonalInformation')
def user_profile_page(username, page="PersonalInformation"):
    if g.user.userType == 'Admin':
        return render_template(f'Profile/Admin/{page}.html')
    elif g.user.userType == 'Customer':
        return render_template(f'Profile/Customer/{page}.html')

@app.route('/404')
def page_not_found():
    return render_template('404.html')

app.register_blueprint(example_blueprint) # Register the blueprint from example for routing

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) # debug false when delpoying
