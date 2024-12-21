from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()

# Configure login manager
login_manager.login_view = 'main.login' 