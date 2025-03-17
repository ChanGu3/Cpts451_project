import os
from flask import Flask, render_template, make_response, request, redirect, url_for, blueprints, session, g, abort
from dotenv import load_dotenv


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
    session['userType'] = 'Customer'
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

@app.route('/')
def address():
    return redirect(url_for('index'))

@app.route('/Home')
def index():
    return render_template('index.html')

@app.route('/SignIn', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        return redirect(url_for('set_session'))
    return render_template('SignIn.html')

@app.route('/Profile/<username>')
def user_profile_menu(username):
    # if user is not logged or username is typed directly in redirect page not found
    if g.user is None:
        return abort(404)
        
    if g.user.userType == 'Admin':
        return render_template(f'Profile/Admin/Menu.html');
    elif g.user.userType == 'Customer':
        return render_template(f'Profile/Customer/Menu.html');

    return abort(404)
    # if username is typed incorrectly still log them in with their own username
    #if username != g.user.username:
    #    return redirect(url_for('user_profile_page', username=g.user.username, page='PersonalInformation'))
    
    #return redirect(url_for('user_profile_page', username=username, page='PersonalInformation'))

@app.route('/Profile/<username>/<page>')
def user_profile_page(username, page):
    # if user is not logged  in redirect page not found
    if g.user is None:
        abort(404)
    
    # if username is typed incorrectly still log them in with their own username
    if username != g.user.username:
        redirect(url_for('user_profile_page', username=g.user.username, page=page))
    
    try:        
        if g.user.userType == 'Admin':
            if page == 'PersonalInformation':
                pageData = {'username': g.user.username}
            elif page == 'Products':
                pageData = {}
            elif page == 'Analytics':
                pageData = {}
            
        elif g.user.userType == 'Customer':    
            if page == 'PersonalInformation':
                pageData = {'email': g.user.username, 'PhoneNumber': '555-555-5555'}
            elif page == 'Orders':
                pageData = {}
            elif page == 'Wishlist':
                pageData = {}
                
        return render_template(f'Profile/{g.user.userType}/{page}.html', pageData=pageData)
    except:
        abort(404)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) # debug false when delpoying
