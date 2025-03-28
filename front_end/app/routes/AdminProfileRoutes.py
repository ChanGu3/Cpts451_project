from flask import Blueprint, render_template, url_for, g, session, flash


adminPI_route = Blueprint('adminPI_route', __name__)


@adminPI_route.route('<displayName>/PersonalInformation')
def profile_pi(displayName):
    actionMessage = None
    isError = None

    if session.get('actionMessage') is not None and session.get('isError') is not None:
        actionMessage = session['actionMessage'] 
        isError = session['isError']
        session.pop('actionMessage', None)
        session.pop('isError', None)
    
    return render_template('Profile/Admin/PersonalInformation.html', displayName=displayName, actionMessage=actionMessage, isError=isError)
