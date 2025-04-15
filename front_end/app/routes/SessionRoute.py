from flask import Blueprint, redirect, url_for, g, session
# Note Cookies:
# When using session this encrypts the cookies
# otherwise using cookies directly will store them as plain text

session_route = Blueprint('session_route', __name__)

class User:
    def __init__(self, userType, username, ID):
        self.userType = userType
        self.username = username
        self.ID = ID

# Sets the session cookies to a user when logged in (Not using database currently just a test dummy)
@session_route.route('/set_session')
def set_session():
    # logging in is hardcoded when we have page for login we will use the form data to set the session cookies
    
    # if Admin
    session['userType'] = 'Customer'
    session['username'] = 'customer1'
    session['ID'] = 1
    # if Customer
        # session['userType'] = 'Customer'
        # session['username'] = 'JohnDoe'
        # session['ID'] = '1'

    return redirect(url_for('index'))

# removes session cookies when logged out 
@session_route.route('/del_session')
def del_session():
    g.user = None
    session.pop('userType', None)
    session.pop('username', None)
    session.pop('ID', None)
    return redirect(url_for('index'))