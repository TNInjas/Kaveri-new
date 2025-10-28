from flask import Blueprint, render_template, session, redirect, url_for, flash
from app.models.User import User
from app.models.profile import Profile
from app.models.Understanding import Understanding

dash_bp = Blueprint('dash', __name__)

@dash_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access dashboard', 'error')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    try:
        user = User.query.get(user_id)
        profile = Profile.query.filter_by(user_id=user_id).first()
        understanding = Understanding.query.filter_by(user_id=user_id).first()
        
        if not profile:
            flash('Please complete the assessment first', 'info')
            return redirect(url_for('ass.assignment'))
        
        login_count = user.login_count or 0
        logins_until_reassessment = 10 - (login_count % 10)
        
        dashboard_data = {
            'username': user.username,
            'login_count': login_count,
            'logins_until_reassessment': logins_until_reassessment,
            'needs_reassessment': user.needs_reassessment() if user.login_count else False,
            'last_assessment': user.last_assessment,
            'understanding': understanding
        }
        
        return render_template('dashboard.html', **dashboard_data)
        
    except Exception as e:
        print(f"Dashboard error: {e}")
        flash('Error loading dashboard', 'error')
        return redirect(url_for('auth.login'))