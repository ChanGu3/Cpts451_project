from flask import Blueprint, render_template, url_for, g, session, request
from dbmsInstance import GetDatabase
from math import ceil
adminPI_route = Blueprint('adminPI_route', __name__)


@adminPI_route.route('<displayName>/PersonalInformation', methods=['GET', 'POST'])
def profile_pi(displayName):
    actionMessage = None
    isError = None
    
    database = GetDatabase()
    adminInfo = database.get_admin_info(g.user.ID)
    email = adminInfo[3]
    
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

PRODUCTS_PER_PAGE = 10 # Number of products to display per page in the analytics view

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
        
        if searchBarInput == '':
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
    
    displayedProducts = searchedProducts[(page-1)*PRODUCTS_PER_PAGE:page*PRODUCTS_PER_PAGE] # Get the products for the current page, 10 per page   
    
    if (page != 1):
        pageLeftURL = True
    if (ceil(len(searchedProducts)/PRODUCTS_PER_PAGE) != page and len(searchedProducts) > PRODUCTS_PER_PAGE):
        pageRightURL = True
    
    del database
    return render_template('Profile/Admin/Analytics.html', displayName=displayName, paproducts=paproducts, displayedProducts=displayedProducts, page=page, pageLeftURL=pageLeftURL, pageRightURL=pageRightURL, currentSearch=currentSearch)