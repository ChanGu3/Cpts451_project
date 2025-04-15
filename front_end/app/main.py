import os
import io
import magic
from dotenv import load_dotenv
from dbmsInstance import GetDatabase
from flask import Flask, render_template, make_response, request, redirect, url_for, blueprints, session, g, abort, send_file
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
            product_details = dict(product_details)  
            product_details['CategoryName'] = (product_category['CategoryName'],)
        product_thumbnail = database.retrieve_specific_product_thumbnail_details(productID)
        if product_thumbnail is not None:
            product_thumbnail_name = product_thumbnail[1]
        return render_template('Product.html', product_details=product_details, product_thumbnail_name=product_thumbnail_name)
    else:
        return abort(404)

@app.route('/<string:username>/Cart')
def cart_page(username, methods=['GET', 'POST']): 
    if g.user is not None:
        if g.user.userType != "Customer" or username != g.user.username:
            return abort(404)
    else:
        return abort(404)
    
    database = GetDatabase()
    
    cart_items = database.get_all_products_in_cart(g.user.ID)
    subTotal = 0
    item_count = 0
    for item in cart_items:
        subTotal += item['Price'] * item['Quantity']
        item_count += item['Quantity']
    return render_template('Cart.html', cart_items=cart_items, subTotal=subTotal, item_count=item_count)

@app.route('/Cart/AddItem', methods=['POST'])
def add_cart_item():
    if g.user is not None:
        if g.user.userType != "Customer":
            return abort(500)
    else:
        return abort(500)
    
    quantity = request.form.get('quantity')
    if quantity is None:
        quantity = 1
    else:
        quantity = int(quantity)   
    
    product_id = request.form.get('product_id')
    
    
    
    database = GetDatabase()
    database.add_product_to_cart(customer_id=g.user.ID, product_id=product_id, quantity=quantity)
    del(database)
    return redirect(url_for('cart_page', username=g.user.username))

@app.route('/Cart/RemoveItem', methods=['POST'])
def remove_cart_item():
    if g.user is not None:
        if g.user.userType != "Customer":
            return abort(500)
    else:
        return abort(500)
    
    quantity = request.form.get('quantity')
    if quantity is None:
        quantity = 1
    else:
        quantity = int(quantity)
    
    product_id = request.form.get('product_id')
    database = GetDatabase()
    database.remove_product_from_cart(customer_id=g.user.ID, product_id=product_id, quantity=quantity)
    #is_Product_In_Cart = database._does_Cart_Product_exist(customer_id=g.user.ID, product_id=product_id)
    del(database)
    return redirect(url_for('cart_page', username=g.user.username))
    #if is_Product_In_Cart is False:
    #    return redirect(url_for('cart_page', username=g.user.username))

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
