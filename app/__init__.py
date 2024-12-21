from flask import Flask
from flask_login import LoginManager
import os
import logging
from pathlib import Path
import openai
from .config import OPENAI_API_KEY, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, SECRET_KEY

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask-Login
login_manager = LoginManager()

# Initialize OpenAI with API key from config
openai.api_key = OPENAI_API_KEY
logger.debug(f"Using OpenAI API key: {OPENAI_API_KEY[:10]}...")

def create_app():
    # Get the absolute path to the app directory
    base_dir = Path(__file__).resolve().parent.parent
    template_dir = os.path.join(base_dir, 'app', 'templates')
    static_dir = os.path.join(base_dir, 'app', 'static')
    
    logger.debug(f"Template directory: {template_dir}")
    logger.debug(f"Static directory: {static_dir}")
    
    app = Flask(__name__,
                template_folder=template_dir,
                static_folder=static_dir)
    
    # Configure the app using values from config
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
    
    # Initialize extensions
    from app.extensions import db
    db.init_app(app)
    
    # Initialize and configure Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.main import main_bp
    app.register_blueprint(main_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create necessary directories
        os.makedirs(os.path.join(static_dir, 'test_videos'), exist_ok=True)
        os.makedirs(template_dir, exist_ok=True)
    
    return app