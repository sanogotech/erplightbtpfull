from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
from dotenv import load_dotenv
from config import config

# Load environment variables
load_dotenv()

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
jwt = JWTManager()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load the config
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=app.config.get('CORS_SUPPORTS_CREDENTIALS', False))
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)
    
    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from .routes import auth, clients, projects, exports
    app.register_blueprint(auth.bp)
    app.register_blueprint(clients.bp)
    app.register_blueprint(projects.bp)
    app.register_blueprint(exports.bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)