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
        
    def IsAdmin(self):
        return self.userType == 'ADMIN'
    
    def IsCustomer(self):
        return self.userType == 'CUSTOMER'

# Sets the session cookies to a user when logged in (Not using database currently just a test dummy)
@session_route.route('/set_session')
def set_session():
    # Ensure the session data is already set by the signin route
    if 'userType' in session and 'username' in session and 'ID' in session:
        print(f"Session initialized: userType={session['userType']}, username={session['username']}, ID={session['ID']}")
        return redirect(url_for('index'))
    else:
        print("Session data is missing. Redirecting to sign-in.")
        return redirect(url_for('signin'))

# removes session cookies when logged out 
@session_route.route('/del_session')
def del_session():
    g.user = None
    session.pop('userType', None)
    session.pop('username', None)
    session.pop('ID', None)
    return redirect(url_for('index'))