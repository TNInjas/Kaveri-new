from flask import Blueprint, redirect, render_template, session, url_for, flash, request
from app import db
from app.models.User import User
from app.models.profile import Profile

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def intro():
    return render_template('intro.html')

@auth_bp.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        check_password = request.form.get('check_password')

        existing_username = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if not all([username, password, check_password, email]):
            flash('All fields are required', 'error')
            return render_template('signup.html')  
        
        if password != check_password:
            flash('Passwords do not match', 'error') 
            return render_template('signup.html')
        
        if existing_username:
            flash('Username already exists. Please choose a different one.', 'error')
            return render_template('signup.html')
        if existing_email:
            flash('Email already registered. Please use a different email or login.', 'error')
            return render_template('signup.html')
        
        user = User(username=username, email=email)
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
            flash('Account created successfully! Please login to continue.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Error occurred while creating account. Please try again.', 'error')
            print(f"Signup error: {e}")
            return render_template('signup.html')
    
    return render_template('signup.html')

@auth_bp.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template('login.html')

        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            user.increment_login_count()
            db.session.commit()
            
            session['user_id'] = user.id
            session['username'] = user.username
            
            existing_profile = Profile.query.filter_by(user_id=user.id).first()
            
            if user.needs_reassessment():
                flash('Welcome back! Time to update your learning profile for better personalization.', 'info')
                return redirect(url_for('ass.assignment'))
            elif existing_profile:
                flash(f'Welcome back, {username}! Ready to continue learning?', 'success')
                return redirect(url_for('dash.dashboard'))
            else:
                flash('Welcome! Let\'s personalize your learning experience with a quick assessment.', 'success')
                return redirect(url_for('ass.assignment'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    try:
        username = session.get('username', 'User')
        session.clear()
        flash(f'Goodbye, {username}! You have been logged out successfully.', 'success')
        return render_template('intro.html')
    except Exception as e:
        flash('Error occurred while logging out.', 'error')
        print(f'Logout error: {e}')
        return redirect(url_for('auth.login'))