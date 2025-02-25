from flask import Flask

app = Flask(__name__)  # Create the Flask app instance

# Import routes after app is created to avoid circular imports
from . import routes