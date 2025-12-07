
from flask import Blueprint, jsonify, redirect, render_template, request, url_for
import werkzeug.security
from flask_login import login_user, logout_user

from app.models import User
from app.app import db


bp = Blueprint("auth", __name__, url_prefix = "/auth")

@bp.route('/login', methods=['GET'])
def login():
    return render_template('auth/login.html', message=request.args.get('message', ''))

@bp.route('/signup', methods=['GET'])
def signup():
    return render_template('auth/signup.html')

@bp.route('/login', methods=['POST'])
def login_post():
    username = (request.json or {}).get('username')
    password = (request.json or {}).get('password')

    if not username or not password:
        return jsonify({"message": "Missing fields"}), 400
    
    user = User.query.filter_by(username = username).first() or User.query.filter_by(email = username).first()
    if not isinstance(user, User) or not user.authenticate(password):
        return jsonify({"message": "Invalid credentials"}), 401
    
    login_user(user)

    return redirect('/')

@bp.route('/signup', methods=['POST'])
def signup_post():
    username = request.form.get('username')
    email    = request.form.get('email')
    password = request.form.get('password')

    if not username or not email or not password:
        return jsonify({"message": "Missing fields"}), 400
    
    pwd_hash = werkzeug.security.generate_password_hash(password)
    
    user = User(username = username, email = email, password = pwd_hash)
    db.session.add(user)
    db.session.commit()

    return redirect('/auth/login?message=Account created, please log in.')

@bp.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect('/auth/login?message=Logged out successfully.')
