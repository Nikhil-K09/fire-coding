import os
from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from dotenv import load_dotenv

# Load .env
load_dotenv()

mongo = PyMongo()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # Secret key & Mongo URI from .env
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')
    app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/online_judge')

    # Initialize extensions
    mongo.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # redirect if not logged in

    # Register blueprints
    from .routes import main
    from .auth import auth_bp

    app.register_blueprint(main)
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app
