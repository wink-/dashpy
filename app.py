from flask import Flask
from flask_login import LoginManager
import os
from dotenv import load_dotenv
from models import db, migrate, User
from routes import bp as main_bp
from auth import bp as auth_bp
from routes.calsys import bp as calsys_bp

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Set secret key for session management
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

    # Database configurations
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Main database (SQLite)
    app.config['SQLALCHEMY_BINDS'] = {
        'calsys': f"mysql+mysqlconnector://{os.getenv('CALSYS_USER')}:{os.getenv('CALSYS_PASSWORD')}@{os.getenv('CALSYS_HOST')}/{os.getenv('CALSYS_DATABASE')}"
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(calsys_bp)
    
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
