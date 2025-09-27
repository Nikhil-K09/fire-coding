import os
from flask import Flask
from flask_pymongo import PyMongo
from dotenv import load_dotenv

load_dotenv()

mongo = PyMongo()


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['MONGO_URI'] = os.getenv('MONGO_URI')
    app.secret_key = os.getenv('SECRET_KEY', 'dev-secret')

    mongo.init_app(app)

    # register blueprints
    from .routes import main as main_bp
    app.register_blueprint(main_bp)

    return app
