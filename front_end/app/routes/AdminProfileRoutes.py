from flask import Blueprint, render_template, url_for, g, session, request, redirect
from dbmsInstance import GetDatabase
from math import ceil
adminPI_route = Blueprint('adminPI_route', __name__)


@adminPI_route.route('<displayName>/PersonalInformation', methods=['GET', 'POST'])
def profile_pi(displayName):
    actionMessage = None
    isError = None
    
    database = GetDatabase()
    adminInfo = database.get_admin_info(g.user.ID)
    email = adminInfo['Email']
    
    if request.method == 'POST':
        if request.form['newpassword1'] != request.form['newpassword2']:
            actionMessage = 'New Passwords Do Not Match'
            isError = True
        elif request.form['currentpassword'] == request.form['newpassword1']:
            actionMessage = 'New Password Cannot Be The Same As The Current Password'
            isError = True
        elif database.update_admin_password(g.user.username, request.form['currentpassword'], request.form['newpassword1']) is False:
            actionMessage = 'Current Password Is Incorrect'
            isError = True
        else:
            actionMessage = 'Password Changed Successfully!'
            isError = False
                   
    del database
    return render_template('Profile/Admin/PersonalInformation.html', displayName=displayName, email=email, actionMessage=actionMessage, isError=isError)

PRODUCTS_A_PER_PAGE = 10 # Number of products to display per page in the analytics view

@adminPI_route.route('<displayName>/Analytics', methods=['GET', 'POST'])
def profile_analytics(displayName):
    pageLeftURL = False
    pageRightURL = False
    currentSearch = None # Initialize current search to None
    
    page = int(request.args.get('page', 1)) # Get the current page from the request, default to 1 if not provided
    
    database = GetDatabase()
    paproducts = database.retrieve_Top_10_product_details()
    
    if request.method == 'POST':
        searchBarInput = request.form.get('productsearch', None)
        
        if searchBarInput == '' or searchBarInput is None:
            currentSearch = None  # If the search bar is empty, set current search to None
            searchedProducts = database.retrieve_all_product_details_With_Thumbnail_With_Analytics()
        else:
            currentSearch = searchBarInput  # Update current search to the input from the search bar
            searchedProducts = database.search_products_by_name_With_Thumbnail_With_Analytics(searchBarInput)
    else:
        currentSearch = request.args.get('currentSearch', None)
        print(f'CS: {currentSearch}')
        if currentSearch is not None:
            searchedProducts = database.search_products_by_name_With_Thumbnail_With_Analytics(currentSearch)
        else:
            searchedProducts = database.retrieve_all_product_details_With_Thumbnail_With_Analytics()
    
    displayedProducts = searchedProducts[(page-1)*PRODUCTS_A_PER_PAGE:page*PRODUCTS_A_PER_PAGE] # Get the products for the current page, 10 per page   
    
    if (page != 1):
        pageLeftURL = True
    if (ceil(len(searchedProducts)/PRODUCTS_A_PER_PAGE) != page and len(searchedProducts) > PRODUCTS_A_PER_PAGE):
        pageRightURL = True
    
    del database
    return render_template('Profile/Admin/Analytics.html', displayName=displayName, paproducts=paproducts, displayedProducts=displayedProducts, page=page, pageLeftURL=pageLeftURL, pageRightURL=pageRightURL, currentSearch=currentSearch)

PRODUCTS_P_PER_PAGE = 10 # Number of products to display per page in the analytics view

@adminPI_route.route('<displayName>/Products', methods=['GET', 'POST'])
def profile_products(displayName):
    pageLeftURL = False
    pageRightURL = False
    currentSearch = None # Initialize current search to None
    currentEditProductValues = None
    categories = None
    isError = None
    errorMessage = None
    
    if session.get('currentEditProductValues') is not None:
        currentEditProductValues = session['currentEditProductValues']
        session.pop('currentEditProductValues', None)
    
    # For Error Handling 
    if session.get('isError') is not None:
        isError = session['isError'] 
        session.pop('isError', None)
    if session.get('errorMessage') is not None:
        errorMessage = session['errorMessage']
        session.pop('errorMessage', None)
    
    
    page = int(request.args.get('page', 1)) # Get the current page from the request, default to 1 if not provided
    NonFormButtonTypeClicked = request.args.get('buttonClicked', None)
    
    database = GetDatabase()

    categories = database.get_all_product_categories()  
    
    if request.method == 'POST':
        # For Searching Products in the Products Page
        searchBarInput = request.form.get('productsearch', None)
        if searchBarInput == '' or searchBarInput is None:
            currentSearch = None  # If the search bar is empty, set current search to None
            searchedProducts = database.retrieve_all_product_details_With_Thumbnail_With_Analytics()
        else:
            currentSearch = searchBarInput  # Update current search to the input from the search bar
            searchedProducts = database.search_products_by_name_With_Thumbnail_With_Analytics(searchBarInput)
        
        submitButton = request.form.get('submitButton', None)
        
        # Add a Product
        if submitButton == 'add':
            newProductDetails = {"Title": request.form.get('product_name', None), 
                                 "Price": request.form.get('price', None),
                                 "Stock": request.form.get('stock', None),
                                 "Description": request.form.get('description', None),
                                 "DiscountPercentage": request.form.get('discount', 0),
                                 "WebsiteInfo": request.form.get('websiteURL', ""),}
            
            productID = database.insert_new_product_return_id(newProductDetails)
            file = request.files['thumbnail']
            file_bytes = file.read()  # Read the file bytes
            database.insert_new_product_thumbnail(productID, file.filename, file_bytes)
            
            if request.form.get('category', None) is not None and request.form.get('category', None) != 'None':
                database.set_product_category_OnlyOne(productID, request.form['category'])
            
            return redirect(url_for('adminPI_route.profile_products', displayName=displayName, page=page, currentSearch=currentSearch))
        elif submitButton == 'edit':
            newProductDetails = {"Title": request.form.get('product_name', None), 
                                 "Price": request.form.get('price', None),
                                 "Stock": request.form.get('stock', None),
                                 "Description": request.form.get('description', None),
                                 "DiscountPercentage": request.form.get('discount', None),
                                 "WebsiteInfo": request.form.get('websiteURL', None),}
            
            database.admin_update_product(request.form.get('product_id', None), new_product_details=newProductDetails)
            
            session['currentEditProductValues'] = Helper_GetCurrentEditProductValues(
                request.form.get('product_id', None),
                request.form.get('product_name', None), 
                request.form.get('price', None), 
                request.form.get('stock', None), 
                request.form.get('description', None), 
                request.form.get('discount', None), 
                request.form.get('websiteURL', None),
                request.form.get('category', None)
            )
            
            if request.files.get('thumbnail', None):
                file = request.files['thumbnail']
                file_bytes = file.read()  # Read the file bytes
                database.insert_new_product_thumbnail(request.form.get('product_id', None), file.filename, file_bytes)
            
            if request.form.get('category', None) is not None and request.form.get('category', None) != 'None':
                print(request.form['category'])
                database.set_product_category_OnlyOne(request.form.get('product_id', None), request.form['category'])
            
            del database
            return redirect(url_for('adminPI_route.profile_products', displayName=displayName, page=page, currentSearch=currentSearch) + '#EditProductModal')
    else:

        # Handle Edit Product Values if the button was clicked from the form
        if NonFormButtonTypeClicked == 'EditProduct':
            productID = request.args.get('productID', None)
            currentEditProductValues = database.retrieve_specific_product_details(productID)
            currentEditProductCategory = database.get_product_category(productID)
            if currentEditProductCategory is not None:
                currentEditProductValues = dict(currentEditProductValues)
                currentEditProductValues['CategoryName'] = currentEditProductCategory['CategoryName']
                
            del database
            session['currentEditProductValues'] = currentEditProductValues
            return redirect(url_for('adminPI_route.profile_products', displayName=displayName, page=page, currentSearch=currentSearch) + '#EditProductModal')
        elif NonFormButtonTypeClicked == 'DeleteProduct':
            print(database.admin_remove_product_WithOutAdmin(request.args.get('productID', None)))
        
        # For Searching Products in the Products Page
        currentSearch = request.args.get('currentSearch', None)
        if currentSearch is not None:
            searchedProducts = database.search_products_by_name_With_Thumbnail_With_Analytics(currentSearch)
        else:
            searchedProducts = database.retrieve_all_product_details_With_Thumbnail_With_Analytics()
            
    displayedProducts = searchedProducts[(page-1)*PRODUCTS_P_PER_PAGE:page*PRODUCTS_P_PER_PAGE] # Get the products for the current page, 10 per page   
    
    if (page != 1):
        pageLeftURL = True
    if (ceil(len(searchedProducts)/PRODUCTS_P_PER_PAGE) != page and len(searchedProducts) > PRODUCTS_P_PER_PAGE):
        pageRightURL = True
    
    del database
    return render_template('Profile/Admin/Products.html', displayName=displayName, displayedProducts=displayedProducts, isError=isError, errorMessage=errorMessage, page=page, pageLeftURL=pageLeftURL, pageRightURL=pageRightURL, currentSearch=currentSearch, categories=categories, currentEditProductValues=currentEditProductValues)

@adminPI_route.route('<displayName>/Orders', methods=['GET', 'POST'])
def profile_orders(displayName):
    return render_template('Profile/Admin/Orders.html', displayName=displayName)




def Helper_GetCurrentEditProductValues(productID, productName, price, stock, description, discount, websiteURL, currentCategory):
    return {"Product_ID":productID, 
            "Title": productName, 
            "Price": price, 
            "Stock": stock, 
            "Description": description, 
            "DiscountPercentage": discount, 
            "WebsiteInfo": websiteURL, 
            "CategoryName": currentCategory}