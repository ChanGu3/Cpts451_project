import os
from dotenv import load_dotenv
from dbmsInstance import GetDatabase
from flask import Flask, render_template, make_response, request, redirect, url_for, blueprints, session, g, abort, send_file
from routes.ErrorRoute import error_route
from routes.SessionRoute import session_route, User
from routes.ProfileRoute import profile_route
from routes.AdminProfileRoutes import adminPI_route

#App Config
app = Flask(__name__, static_folder='static', template_folder='templates')

# Load environment variables
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY') # Secret key for session

# Register Blueprints (Note Each blueprint has its own request and context_processor or other ones like that, that only apply to that blueprint and not the whole app so global versions of these needs to be done in this file to be done for every template rendering)
app.register_blueprint(error_route, url_prefix='/error')
app.register_blueprint(session_route, url_prefix='')
app.register_blueprint(profile_route, url_prefix='/Profile')
app.register_blueprint(adminPI_route, url_prefix='/Admin')

# Loads the user from the session if it exists globally
@app.before_request
def before_request():
    if session.get('userType') is not None and session.get('ID') is not None:
        g.user = User(session['userType'], session['ID'])

# Injects the user into the context of every template gloablly
@app.context_processor
def inject_user():
    user = None
    if g.get('user') is not None:
        user = g.user
    return dict(user=user)

# All Images that are retrieved here we can then use the link to get the images from here using the productName and imageName we get from the database
# plus it allows us to go to the images directly if we want to by just looking it up 
# Example: <img src="{{ url_for('get_image', productName='Product1', imageName='Image1') }}" alt="Image1">
@app.route('/Images/<string:productName>/<string:imageName>')
def get_image(productName, imageName):
    #database. Get image through database converting it into a byte stream using productName and imageName.
    #return send_file(image_stream, mimetype='image/png')
    #redirect to a folder with a error image if image is not found
    return redirect(url_for('index')) # here for now until database is implemented propelrly with this

@app.route('/')
def domain():
    return redirect(url_for('index'))

@app.route('/Home')
def index():
    return render_template('index.html')

@app.route('/SignIn', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        return redirect(url_for('session_route.set_session'))
    return render_template('SignIn.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) # debug false when delpoying
