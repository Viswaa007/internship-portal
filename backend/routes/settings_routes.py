from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from extensions import db

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():

    if request.method == 'POST':

        username = request.form.get('username')
        email = request.form.get('email')

        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        try:

            # update username/email
            current_user.username = username
            current_user.email = email

            # PASSWORD CHANGE
            if new_password and new_password.strip() != '':

                # check current password
                if not current_user.check_password(current_password):
                    flash('Current password is incorrect!', 'danger')
                    return redirect(url_for('settings.settings'))

                # check confirm password
                if new_password != confirm_password:
                    flash('New passwords do not match!', 'danger')
                    return redirect(url_for('settings.settings'))

                # update password
                current_user.set_password(new_password)

            db.session.commit()

            flash('Settings updated successfully!', 'success')
            return redirect(url_for('settings.settings'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    return render_template('settings.html')