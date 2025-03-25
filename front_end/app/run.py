import os
from dotenv import load_dotenv
from flask import Flask, render_template, make_response, request, redirect, url_for, blueprints, session, g, abort
from routes.ErrorRoute import error_route
from routes.SessionRoute import session_route

#App Config
app = Flask(__name__, static_folder='static', template_folder='templates')

# Load environment variables
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY') # Secret key for session

# Register Blueprints
app.register_blueprint(error_route, url_prefix='/error')
app.register_blueprint(session_route)

@app.route('/')
def address():
    return redirect(url_for('index'))

@app.route('/Home')
def index():
    return render_template('index.html')

@app.route('/SignIn', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        return redirect(url_for('session_route.set_session'))
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) # debug false when delpoying
