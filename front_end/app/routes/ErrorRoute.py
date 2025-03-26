from flask import Blueprint, render_template, redirect, url_for

error_route = Blueprint('error_route', __name__)

@error_route.app_errorhandler(404)
def page_not_found(e):
    return redirect(url_for('error_route.page_404'))

@error_route.route('/404')
def page_404():
    return render_template('404.html'), 404