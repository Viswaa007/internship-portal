from flask import Blueprint, render_template
from flask_login import login_required, current_user

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@profile_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@profile_bp.route('/notifications')
@login_required
def notifications():
    return render_template('notifications.html')