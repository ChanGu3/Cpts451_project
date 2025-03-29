from flask import Blueprint, render_template, url_for, g, session, request
from dbmsInstance import GetDatabase

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


@adminPI_route.route('<displayName>/Analytics')
def profile_analytics(displayName):
    database = GetDatabase()
    paproducts = database.retrieve_Top_10_product_details()
    
    del database
    return render_template('Profile/Admin/Analytics.html', displayName=displayName, paproducts=paproducts)