"""
Authentication Blueprint for Loan Approval Prediction System.
Handles user registration, login, logout, and account management.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import logging

# Import the database and User model
from extensions import db
from models import User

# Set up logging
logger = logging.getLogger(__name__)

# Create auth blueprint
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        
        # Check if user exists and password is correct
        if not user or not check_password_hash(user.password_hash, password):
            flash('Please check your login details and try again.', 'danger')
            logger.warning(f'Failed login attempt for email: {email}')
            return redirect(url_for('auth.login'))
        
        # Log the user in
        login_user(user, remember=remember)
        logger.info(f'User {user.email} logged in successfully')
        
        # Redirect to appropriate page based on user role
        if user.role == 'admin':
            return redirect(url_for('admin_panel'))
        return redirect(url_for('index'))
    
    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        
        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        
        if user:
            flash('Email address already exists', 'warning')
            return redirect(url_for('auth.signup'))
        
        # Create new user
        new_user = User(
            email=email,
            name=name,
            password_hash=generate_password_hash(password, method='sha256'),
            role='applicant'  # Default role
        )
        
        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        
        logger.info(f'New user registered: {email}')
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('signup.html')

@auth.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@auth.route('/profile')
@login_required
def profile():
    """Display user profile."""
    return render_template('profile.html', user=current_user)

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Handle password change."""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Verify current password
        if not check_password_hash(current_user.password_hash, current_password):
            flash('Current password is incorrect', 'danger')
            return redirect(url_for('auth.change_password'))
        
        # Check if new passwords match
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return redirect(url_for('auth.change_password'))
        
        # Update password
        current_user.password_hash = generate_password_hash(new_password, method='sha256')
        db.session.commit()
        
        flash('Password updated successfully!', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('change_password.html')

# Error handlers
@auth.errorhandler(401)
def unauthorized(error):
    flash('Please log in to access this page.', 'warning')
    return redirect(url_for('auth.login', next=request.path))