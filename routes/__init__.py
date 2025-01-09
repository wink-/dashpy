from flask import Blueprint

# Create main blueprint
bp = Blueprint('main', __name__)

# Import routes
from . import main
from . import calsys
