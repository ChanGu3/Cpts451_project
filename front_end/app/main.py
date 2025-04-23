import os
import io
import magic
from dotenv import load_dotenv
from dbmsInstance import GetDatabase
from backend.dbms import UserType
from flask import Flask, render_template, make_response, request, redirect, url_for, blueprints, session, g, abort, send_file, flash, get_flashed_messages
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
    if 'userType' in session and 'username' in session and 'ID' in session:
        g.user = User(session['userType'], session['username'], session['ID'])
        print(f"g.user initialized: {g.user.userType}, {g.user.username}, {g.user.ID}")
    else:
        g.user = None
        print("g.user is None")

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
def get_thumbnail(productName, imageName='placeholder.jpg'):
    if imageName == 'placeholder.jpg':
        return send_file(STATIC_IMAGE_PATH_TO_NOT_FOUND, mimetype='image/png')

    image_tuple = GetDatabase().get_specific_product_thumbnail(productName, imageName)
    if image_tuple is not None:
        image_data = image_tuple[0]
        mime = magic.Magic(mime=True)
        image_type = mime.from_buffer(image_data)
        image_stream = io.BytesIO(image_data)
        return send_file(image_stream, mimetype=f'{image_type}')
    else:
        return send_file(STATIC_IMAGE_PATH_TO_NOT_FOUND, mimetype='image/png')

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
        
        isCustomer = False
        isAbleReview = False
        is_Product_In_Wishlist = False
        customer_product_review = None
        average_rating = database.get_product_review_average(productID)
        
        if g.get('user') is not None:
            if g.user.IsCustomer(): 
                isCustomer = True
                is_Product_In_Wishlist = database._does_Wishlist_Product_exist(customer_id=g.user.ID, product_id=productID)
                isProductPurchased = database._does_Product_Exist_In_Customer_Orders(customer_id=g.user.ID, product_id=productID)
                if isProductPurchased is True:
                    isProductReviewed = database._does_Review_Of_Product_exist(customer_id=g.user.ID, product_id=productID)
                    if isProductReviewed is False:
                        isAbleReview = True   
                customer_product_review = database.get_Specific_Customer_Review(customer_id=g.user.ID, product_id=productID)
                product_Reviews = database.get_all_reviews_of_product_except_customer(g.user.ID, productID)
            else:
                product_Reviews = database.get_all_reviews_of_product_except_customer(-1, productID)
        else:
            product_Reviews = database.get_all_reviews_of_product_except_customer(-1, productID)
            del(database)
        
        return render_template('Product.html', 
                               product_details=product_details,
                               average_rating=average_rating, 
                               product_Reviews=product_Reviews,
                               customer_product_review=customer_product_review,
                               product_thumbnail_name=product_thumbnail_name, 
                               isProductInWishlist=is_Product_In_Wishlist, 
                               isCustomer=isCustomer, 
                               isAbleReview=isAbleReview)
    else:
        return abort(404)

@app.route('/Product/AddReview', methods=['POST'])
def add_product_review():
    if g.user is not None:
        if g.user.IsCustomer() == False:
            return abort(500)
    else:
        return abort(500)
    
    product_id = request.form.get('product_id')
    rating = request.form.get('rating')
    review = request.form.get('review')
    
    database = GetDatabase()
    database.add_review_to_product(customer_id=g.user.ID, product_id=product_id, rating=rating, review=review)
    del(database)
    
    return redirect(url_for('product_page', productID=product_id))

@app.route('/<string:username>/Cart')
def cart_page(username, methods=['GET', 'POST']): 
    if g.user is not None:
        if g.user.IsCustomer() == False or username != g.user.username:
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
        if g.user.IsCustomer() == False:
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
        if g.user.IsCustomer() == False:
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

@app.route('/Wishlist/AddItem', methods=['POST'])
def add_wishlist_item():
    if g.user is not None:
        if g.user.IsCustomer() == False:
            return abort(500)
    else:
        return abort(500)
    
    product_id = request.form.get('product_id')
    database = GetDatabase()
    database.add_product_to_wishlist(customer_id=g.user.ID, product_id=product_id)
    del(database)
    
    if request.form.get('pageSent') == "Product":
        return redirect(url_for('product_page', productID=product_id))

@app.route('/Wishlist/RemoveItem', methods=['POST'])
def remove_wishlist_item():
    if g.user is not None:
        if g.user.IsCustomer() == False:
            return abort(500)
    else:
        return abort(500)
    
    product_id = request.form.get('product_id')
    database = GetDatabase()
    database.remove_product_from_wishlist(customer_id=g.user.ID, product_id=product_id)
    del(database)
    
    if request.form.get('pageSent') == "Product":
        return redirect(url_for('product_page', productID=product_id))
    
@app.route('/')
def domain():
    return redirect(url_for('index'))

@app.route('/Home')
def index():
    database = GetDatabase()

    # Fetch featured products
    featured_products = database.retrieve_Top_10_product_details()
    featured_products = [dict(product) for product in featured_products]  # Convert rows to dictionaries

    # Fetch latest products
    latest_products = database.retrieve_all_product_details_With_Thumbnail_With_Analytics()
    latest_products = [dict(product) for product in latest_products]  # Convert rows to dictionaries

    print("Featured Products:", featured_products)
    print("Latest Products:", latest_products)

    del database

    return render_template(
        'index.html',
        featured_products=featured_products[:10],  # Limit to 10 products
        latest_products=latest_products[:10]       # Limit to 10 products
    )

@app.route('/SignIn', methods=['GET', 'POST'])
def signin():
    database = GetDatabase()

    if request.method == 'POST':
        # Get form data
        username = request.form.get('Username')
        password = request.form.get('Password')

        # Validate input
        if not username or not password:
            print(f"Invalid input. Username: {username}, Password: {password}")
            return redirect(url_for('signin'))

        try:
            print(f"Username: {username}, Password: {password}")  # Debug check
            user, user_type = database.sign_in(username, password)
            print(f"User: {user}, UserType: {user_type}")  # Debug check

            if user:
                # Convert the Row object to a dictionary
                user_dict = {key: user[key] for key in user.keys()}
                print(f"User Dictionary: {user_dict}")

                # Store user details in the session
                session['username'] = username
                session['email'] = user_dict['Email']
                session['ID'] = user_dict['Customer_ID'] if user_type == UserType.CUSTOMER else user_dict['Admin_ID']
                session['userType'] = 'CUSTOMER' if user_type == UserType.CUSTOMER else 'ADMIN'

                print(f"Session Data: {session['username']}, {session['email']}, {session['ID']}, {session['userType']}")  # Debug check    

                return redirect(url_for('session_route.set_session'))
            else:
                return redirect(url_for('signin'))

        except Exception as e:
            print("Error occurred:", e)
            return redirect(url_for('signin'))

    return render_template('SignIn.html')

@app.route('/CreateAccount', methods=['GET', 'POST'])
def createaccount():
    database = GetDatabase()
    actionMessage = None
    isError = False

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
                print("Creating admin account...")
                database.admin_account_creation(name, password, email)
                actionMessage = "Admin account created successfully!"
            else:
                # Insert into CustomerUser table
                # database.customer_account_creation(name, email, password, phone)
                print("Creating customer account...")
                database.customer_account_creation(name, password, email, phone)
                actionMessage = "Account created successfully!"
            return render_template('SignIn.html', actionMessage=actionMessage, isError=isError) 

        except Exception as e:
            print("Error occurred:", e)
            actionMessage = "An error occurred while creating the account. Please try again."
            isError = True
            return render_template('CreateAccount.html', actionMessage=actionMessage, isError=isError)
            
    return render_template('CreateAccount.html', actionMessage=actionMessage)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) # debug false when delpoying
    STATIC_IMAGE_PATH_TO_NOT_FOUND = os.path.join(os.path.abspath(__file__), url_for('static', filename='images/no_image_found.png'))