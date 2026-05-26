# =============================================================
# File: backend/app.py
# Purpose: Flask application factory (FIXED VERSION)
# =============================================================

import os
from flask import Flask, redirect, render_template
from flask_login import current_user, login_required

from dotenv import load_dotenv

load_dotenv()  # ✅ LOAD .env FIRST

os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def create_app(config_name='default'):

    app = Flask(__name__)

    # =========================================================
    # LOAD CONFIG
    # =========================================================
    from config import config
    app.config.from_object(config[config_name])

    # =========================================================
    # EXTENSIONS
    # =========================================================
    from extensions import db, login_manager, csrf, mail

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please login first.'
    login_manager.login_message_category = 'warning'

    # =========================================================
    # USER LOADER
    # =========================================================
    from models.user_model import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # =========================================================
    # BLUEPRINTS
    # =========================================================
    from routes.auth_routes import auth_bp, google_bp
    from routes.admin_routes import admin_bp
    from routes.student_routes import student_bp
    from routes.mentor_routes import mentor_bp
    from routes.attendance_routes import attendance_bp
    from routes.task_routes import task_bp
    from routes.report_routes import report_bp
    from routes.ai_routes import ai_bp
    from routes.settings_routes import settings_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(google_bp, url_prefix="/login")  # ✅ IMPORTANT FIX
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(mentor_bp, url_prefix='/mentor')
    app.register_blueprint(attendance_bp, url_prefix='/attendance')
    app.register_blueprint(task_bp, url_prefix='/tasks')
    app.register_blueprint(report_bp, url_prefix='/reports')
    app.register_blueprint(ai_bp, url_prefix='/ai')
    app.register_blueprint(settings_bp)

    # =========================================================
    # BASE URL
    # =========================================================
    app.config['BASE_URL'] = "http://localhost:5000"

    # =========================================================
    # HOME
    # =========================================================
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(current_user.get_dashboard_url())
        return render_template('index.html')

    # =========================================================
    # PROFILE
    # =========================================================
    @app.route('/profile')
    @login_required
    def profile():
        return render_template('profile.html')

    # =========================================================
    # NOTIFICATIONS
    # =========================================================
    @app.route('/notifications')
    @login_required
    def notifications():
        return render_template('notifications.html')

    # =========================================================
    # DB INIT
    # =========================================================
    with app.app_context():

        import models.user_model
        import models.student_model
        import models.mentor_model
        import models.internship_model
        import models.attendance_model

        db.create_all()

        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['CERTIFICATE_FOLDER'], exist_ok=True)

    return app


# =============================================================
# RUN APP
# =============================================================
if __name__ == '__main__':

    app = create_app('development')

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )