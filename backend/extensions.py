# =============================================================
# File: backend/extensions.py
# =============================================================

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail

# Create extension instances
db = SQLAlchemy()

login_manager = LoginManager()

csrf = CSRFProtect()

mail = Mail()