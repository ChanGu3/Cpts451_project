from flask import Flask, render_template, make_response, request, redirect, url_for, blueprints
from routes.example_route import example_blueprint

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    mylist = [1, 2, 3, 4, 5]
    return render_template('index.html', list=mylist)

app.register_blueprint(example_blueprint) # Register the blueprint from example for routing

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) # debug false when delpoying
