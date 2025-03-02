from flask import Flask, render_template, make_response, request, redirect, url_for, Blueprint

example_blueprint = Blueprint('example', __name__)

@example_blueprint.route('/other')
def other():
    some_text = "Hello, World!"
    return render_template('other.html', some_text=some_text)

@example_blueprint.route('/redirect_endpoint')
def redirect_endpoint():
    return redirect(url_for('example.other')) # uses blueprint name and function name

@example_blueprint.app_template_filter('reverse_string')
def reverse_string(s):
    return s[::-1]

@example_blueprint.route('/hello', methods=['GET'])
def hello():
    response = make_response("Hello, World!")
    response.status_code = 200
    response.headers['Content-Type'] = 'text/plain'
    return response
    #2 return 'Hello, World!', 200 #  EX. 200's Everything worked fine, 300 re-direction, 400 user did something wrong, and 500 the server did something wrong (Ex. 404 Not Found)
#1    if request.method == 'GET':
#1        return "you made a GET request"
#1    elif request.method == 'POST':
#1        return "you made a POST request"

@example_blueprint.route('/greet/<name>')
def greet(name):
    return f"<h1> Hello {name} </h1>"

@example_blueprint.route('/add/<int:num1>/<int:num2>')
def add(num1, num2):
    return f"<h1> The sum is {num1 + num2} </h1>"

@example_blueprint.route('/handle_url_params') # /handle_url_params?name=Mike&greeting=Hello
def handle_url_params():
    if 'greeting' in request.args.keys() and 'name' in request.args.keys():
        greeting = request.args['greeting']
        name = request.args.get('name')
        return f"{greeting} {name}"
    else:
        return "Params are missing"
    
@example_blueprint.route('/Testing')
def Testing():
    return render_template('Testing.html', value="INPUT Hello, World!", result=30, list=[1,2,3,4,5,6,7,8,9,10])