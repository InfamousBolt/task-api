import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from app.models import User
from app.database import db


def generate_token(user_id):
    """Generate JWT access token for user"""
    try:
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(seconds=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(
            payload,
            current_app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
        return token
    except Exception as e:
        return None


def decode_token(token):
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """Decorator to protect routes with JWT authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401

        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401

        # Decode and verify token
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401

        # Get user from database
        user = db.session.get(User, payload['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 401

        # Pass current user to the route
        return f(current_user=user, *args, **kwargs)

    return decorated


def validate_user_credentials(username, password):
    """Validate user credentials and return user if valid"""
    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return None

    return user


def register_user(username, email, password):
    """Register a new user"""
    # Check if user already exists
    if User.query.filter_by(username=username).first():
        return None, 'Username already exists'

    if User.query.filter_by(email=email).first():
        return None, 'Email already exists'

    # Create new user
    try:
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)
