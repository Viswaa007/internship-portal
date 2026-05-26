# =============================================================
# File: backend/routes/auth_routes.py
# =============================================================

import os
from dotenv import load_dotenv
from flask import session

load_dotenv()
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    current_app
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

from flask_dance.contrib.google import (
    make_google_blueprint,
    google
)

from extensions import db, mail
from models.user_model import User
from models.student_model import Student
from models.mentor_model import Mentor

# =============================================================
# DEBUG CHECK
# =============================================================
print("CLIENT ID:", os.getenv("GOOGLE_CLIENT_ID"))
print("CLIENT SECRET:", os.getenv("GOOGLE_CLIENT_SECRET"))

# =============================================================
# BLUEPRINT
# =============================================================
auth_bp = Blueprint('auth', __name__)


# =============================================================
# GOOGLE BLUEPRINT (FIXED)
# =============================================================
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ],
    redirect_to="auth.google_login",
)


# =============================================================
# SERIALIZER
# =============================================================
def get_serializer():
    return URLSafeTimedSerializer(
        current_app.config['SECRET_KEY']
    )


# =============================================================
# LOGIN
# =============================================================
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(current_user.get_dashboard_url())

    if request.method == 'POST':

        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Welcome {user.username}!', 'success')
            return redirect(user.get_dashboard_url())

        flash('Invalid email or password.', 'danger')

    return render_template('login.html')


# =============================================================
# REGISTER STUDENT
# =============================================================
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        college = request.form.get('college', '').strip()
        department = request.form.get('department', '').strip()
        year_of_study = request.form.get('year_of_study', '').strip()

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('auth.register'))

        try:
            user = User(username=username, email=email, role='student')
            user.set_password(password)

            db.session.add(user)
            db.session.flush()

            student = Student(
                user_id=user.id,
                full_name=full_name,
                phone=phone,
                college=college,
                department=department,
                year_of_study=year_of_study
            )

            db.session.add(student)
            db.session.commit()

            flash('Registration successful!', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            flash('Error: ' + str(e), 'danger')

    return render_template('register.html')


# =============================================================
# REGISTER MENTOR
# =============================================================
@auth_bp.route('/register/mentor', methods=['GET', 'POST'])
def register_mentor():

    if request.method == 'POST':

        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        designation = request.form.get('designation', '').strip()
        department = request.form.get('department', '').strip()
        expertise = request.form.get('expertise', '').strip()

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('auth.register_mentor'))

        try:
            user = User(username=username, email=email, role='mentor')
            user.set_password(password)

            db.session.add(user)
            db.session.flush()

            mentor = Mentor(
                user_id=user.id,
                full_name=full_name,
                phone=phone,
                designation=designation,
                department=department,
                expertise=expertise
            )

            db.session.add(mentor)
            db.session.commit()

            flash('Mentor registration successful!', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            flash('Error: ' + str(e), 'danger')

    return render_template('register_mentor.html')


# =============================================================
# LOGOUT
# =============================================================
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('auth.login'))


# =============================================================
# FORGOT PASSWORD
# =============================================================
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():

    if request.method == 'POST':

        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()

        if user:
            try:
                serializer = get_serializer()

                token = serializer.dumps(email, salt='password-reset-salt')

                reset_link = url_for(
                    'auth.reset_password',
                    token=token,
                    _external=True
                )

                msg = Message(
                    subject='Password Reset Request',
                    recipients=[email]
                )

                msg.body = f"""Hello {user.username},

Click below link to reset password:

{reset_link}

If not requested, ignore this email.
"""

                mail.send(msg)
                flash('Password reset link sent!', 'success')

            except Exception as e:
                flash('Mail Error: ' + str(e), 'danger')

        else:
            flash('Email not found!', 'danger')

    return render_template('forgot_password.html')


# =============================================================
# RESET PASSWORD
# =============================================================
@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):

    serializer = get_serializer()

    try:
        email = serializer.loads(
            token,
            salt='password-reset-salt',
            max_age=3600
        )

    except Exception:
        flash('Reset link expired or invalid!', 'danger')
        return redirect(url_for('auth.forgot_password'))

    user = User.query.filter_by(email=email).first()

    if not user:
        flash('User not found!', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':

        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(request.url)

        user.set_password(password)
        db.session.commit()

        flash('Password reset successful!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', token=token)


# =============================================================
# GOOGLE LOGIN (FIXED)
# =============================================================
@auth_bp.route('/google-login')
def google_login():

    if not google.authorized:
        return redirect(url_for("google.login"))

    try:
        resp = google.get("/oauth2/v2/userinfo")

        if not resp.ok:
            flash("Google login failed", "danger")
            return redirect(url_for('auth.login'))

        info = resp.json()

        email = info["email"]
        username = info.get("name", email.split("@")[0])

        user = User.query.filter_by(email=email).first()

        if not user:
            user = User(
                username=username,
                email=email,
                role="student"
            )
            user.set_password(os.urandom(16).hex())

            db.session.add(user)
            db.session.commit()
        if user.role == "student":
            student = Student.query.filter_by(user_id=user.id).first()
            if not student:
                student = Student(
                    user_id=user.id,
                    full_name=username,
                    phone="",
                    college="",
                    department="",
                    year_of_study=""
                )
                db.session.add(student)
                db.session.commit()
        login_user(user)

        flash("Google Login Successful!", "success")
        return redirect(user.get_dashboard_url())

    except Exception as e:
        flash(f"Google login error: {str(e)}", "danger")
        return redirect(url_for('auth.login'))


# =============================================================
# API LOGIN
# =============================================================
@auth_bp.route('/api/login', methods=['POST'])
def api_login():

    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'error': 'No data'})

    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        login_user(user)
        return jsonify({
            'success': True,
            'redirect': user.get_dashboard_url()
        })

    return jsonify({
        'success': False,
        'error': 'Invalid credentials'
    })