# =============================================================
# File: backend/models/user_model.py
# Purpose: User database model - handles authentication for
#          all roles: admin, mentor, student
# =============================================================

from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(UserMixin, db.Model):
    """
    User model for authentication.
    UserMixin provides default implementations for Flask-Login:
    - is_authenticated, is_active, is_anonymous, get_id()
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # Role determines what the user can access
    role = db.Column(db.Enum('admin', 'mentor', 'student'), nullable=False, default='student')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student_profile = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')
    mentor_profile = db.relationship('Mentor', backref='user', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash the password using werkzeug's pbkdf2:sha256."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password against stored hash."""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Check if user has admin role."""
        return self.role == 'admin'

    def is_mentor(self):
        """Check if user has mentor role."""
        return self.role == 'mentor'

    def is_student(self):
        """Check if user has student role."""
        return self.role == 'student'

    def get_dashboard_url(self):
        """Return dashboard URL based on role."""
        from flask import url_for
        role_urls = {
            'admin': 'admin.dashboard',
            'mentor': 'mentor.dashboard',
            'student': 'student.dashboard'
        }
        return url_for(role_urls.get(self.role, 'auth.login'))

    def to_dict(self):
        """Convert user object to dictionary for API responses."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
