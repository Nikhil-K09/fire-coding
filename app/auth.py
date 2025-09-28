from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import mongo, login_manager
from bson.objectid import ObjectId

auth_bp = Blueprint('auth', __name__)

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_dict):
        self.id = str(user_dict['_id'])
        self.username = user_dict['username']
        self.email = user_dict.get('email')

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    try:
        user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(user_data)
    except Exception as e:
        print("Error loading user:", e)
    return None

# Routes
# Routes
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        identifier = request.form.get('username')  # can be username or email
        password = request.form.get('password')

        # Try to find by username first, then by email
        user_data = mongo.db.users.find_one({
            "$or": [
                {"username": identifier},
                {"email": identifier}
            ]
        })

        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user)
            return redirect(url_for('main.index'))

        flash("Invalid username/email or password", "danger")

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Ensure unique username and email
        if mongo.db.users.find_one({"username": username}):
            flash("Username already exists", "danger")
            return redirect(url_for('auth.register'))

        if mongo.db.users.find_one({"email": email}):
            flash("Email already registered", "danger")
            return redirect(url_for('auth.register'))

        hashed_pw = generate_password_hash(password)
        user_id = mongo.db.users.insert_one({
            "username": username,
            "email": email,
            "password": hashed_pw
        }).inserted_id

        user = User({"_id": user_id, "username": username, "email": email})
        login_user(user)
        return redirect(url_for('main.index'))

    return render_template('register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
