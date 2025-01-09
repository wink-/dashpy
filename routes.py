from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from models import db, UserSettings

# Create blueprint
bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    return render_template('index.html')

@bp.route('/api/settings', methods=['GET', 'POST'])
@login_required
def handle_settings():
    if request.method == 'POST':
        data = request.json
        settings = UserSettings.query.filter_by(user_id=current_user.id).first()
        if not settings:
            settings = UserSettings(user_id=current_user.id)
            db.session.add(settings)
        
        # Update settings
        if 'theme' in data:
            settings.theme = data['theme']
        if 'items_per_page' in data:
            settings.items_per_page = data['items_per_page']
        
        db.session.commit()
        return jsonify(settings.to_dict())
    
    # GET request
    settings = UserSettings.query.filter_by(user_id=current_user.id).first()
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.session.add(settings)
        db.session.commit()
    
    return jsonify(settings.to_dict())
