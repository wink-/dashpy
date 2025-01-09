from flask import Blueprint, render_template

# Create main blueprint
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

from . import calsys
