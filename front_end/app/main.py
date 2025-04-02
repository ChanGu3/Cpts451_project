import os
import io
import magic
from dotenv import load_dotenv
from dbmsInstance import GetDatabase
from flask import Flask, render_template, make_response, request, redirect, url_for, blueprints, session, g, abort, send_file, flash
from routes.ErrorRoute import error_route
from routes.SessionRoute import session_route, User
from routes.ProfileRoute import profile_route
from routes.AdminProfileRoutes import adminPI_route

STATIC_IMAGE_PATH_TO_NOT_FOUND = 'static/images/no_image_found.png'

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
        g.user = User(session['userType'], session['username'], session['ID'])

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
@app.route('/Product/Images/<string:productName>/<string:imageName>')
def get_image(productName, imageName):
    image_tuple = GetDatabase().get_specific_product_image(productName, imageName)
    
    if image_tuple is not None:
        image_data = image_tuple[0]
        mime = magic.Magic(mime=True)
        image_type = mime.from_buffer(image_data)
        image_stream = io.BytesIO(image_data)
        return send_file(image_stream, mimetype=f'{image_type}')
    else:
         return send_file(STATIC_IMAGE_PATH_TO_NOT_FOUND, mimetype=f'image/png')

# All Images that are retrieved here we can then use the link to get the images from here using the productName and imageName we get from the database
# plus it allows us to go to the images directly if we want to by just looking it up 
# Example: <img src="{{ url_for('get_thumbnail', productName='Product1', imageName='Image1') }}" alt="Image1">
@app.route('/Product/Thumbnail/<string:productName>/<string:imageName>')
def get_thumbnail(productName, imageName):
    image_tuple = GetDatabase().get_specific_product_thumbnail(productName, imageName)
    
    if image_tuple is not None:
        image_data = image_tuple[0]
        mime = magic.Magic(mime=True)
        image_type = mime.from_buffer(image_data)
        image_stream = io.BytesIO(image_data)
        
        return send_file(image_stream, mimetype=f'{image_type}')
    else:
        return send_file(STATIC_IMAGE_PATH_TO_NOT_FOUND, mimetype=f'image/jpeg')

# Sends user to products Page
@app.route('/Product/<int:productID>')
def product_page(productID):
    database = GetDatabase()
    
    product_details = database.retrieve_specific_product_details(productID)
    if product_details is not None:
        product_category = database.get_product_category(productID)
        if product_category is not None:
            product_details = product_details + (product_category[0],)
        product_thumbnail = database.retrieve_specific_product_thumbnail_details(productID)
        if product_thumbnail is not None:
            product_thumbnail_name = product_thumbnail[1]
        print(product_details)
        return render_template('Product.html', product_details=product_details, product_thumbnail_name=product_thumbnail_name)
    else:
        return abort(404)
    
@app.route('/')
def domain():
    return redirect(url_for('index'))

@app.route('/Home')
def index():
    return render_template('index.html')

@app.route('/SignIn', methods=['GET', 'POST'])
def signin():
    database = GetDatabase()

    if request.method == 'POST':
        # Get form data
        username = request.form.get('Username')
        password = request.form.get('Password')

        # Validate input
        if not username or not password:
            return redirect(url_for('signin'))

        try:
            user = database.sign_in(username, password)

            if user:
                user_id, email = user
                session['username'] = username
                session['ID'] = user_id
                return redirect(url_for('index')) 
            else:
                return redirect(url_for('signin'))

        except Exception as e:
            print("Error occurred:", e)
            return redirect(url_for('signin'))

    return render_template('SignIn.html')

@app.route('/CreateAccount', methods=['GET', 'POST'])
def createaccount():
    database = GetDatabase()

    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone_number')
        is_admin = request.form.get('is_admin')  # Will be 'on' if checked, None otherwise

        print(f"Name: {name}, Email: {email}, Password: {password}, Phone: {phone}, Is Admin: {is_admin}") # Debug check

        try:
            if is_admin:  # Checkbox is checked, this can be expanded upon in the future
                # Insert into AdminUser table
                database.admin_account_creation(name, email, password)
            else:
                # Insert into CustomerUser table
                database.customer_account_creation(name, email, password, phone)
                database.customer_account_creation(name, password, email, phone)
            return redirect(url_for('signin')) 

        except Exception as e:
            print("Error occurred:", e)
            return redirect(url_for('createaccount'))
            
    return render_template('CreateAccount.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) # debug false when delpoying
