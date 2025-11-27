"""
Application factory for Loan Approval Prediction System.
"""

from flask import Flask
from extensions import db, login_manager
import os

def create_app(config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Default configuration
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev-key-please-change-in-production'),
        SQLALCHEMY_DATABASE_URI='sqlite:///loan_app.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        PROPAGATE_EXCEPTIONS=True
    )
    
    # Override with any provided config
    if config:
        app.config.update(config)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Register blueprints
    with app.app_context():
        from auth import auth as auth_blueprint
        app.register_blueprint(auth_blueprint, url_prefix='/auth')
        
        # Import and register other blueprints here
        # from main import main as main_blueprint
        # app.register_blueprint(main_blueprint)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
