# =============================================================
# File: backend/models/student_model.py
# Purpose: Student profile model
# =============================================================

from extensions import db
from datetime import datetime


class Student(db.Model):
    """Student extended profile linked to User."""
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    college = db.Column(db.String(200))
    department = db.Column(db.String(100))
    year_of_study = db.Column(db.String(20))
    cgpa = db.Column(db.Numeric(4, 2))
    skills = db.Column(db.Text)
    resume_path = db.Column(db.String(300))
    profile_pic = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    attendance_records = db.relationship('Attendance', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    applications = db.relationship('Application', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    feedbacks = db.relationship('Feedback', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    certificates = db.relationship('Certificate', backref='student', lazy='dynamic', cascade='all, delete-orphan')

    def get_attendance_percentage(self, internship_id=None):
        """Calculate attendance percentage for a given internship."""
        query = self.attendance_records
        if internship_id:
            query = query.filter_by(internship_id=internship_id)
        total = query.count()
        if total == 0:
            return 0.0
        present = query.filter_by(status='present').count()
        return round((present / total) * 100, 2)

    def get_task_completion_rate(self, internship_id=None):
        """Calculate task completion percentage."""
        query = self.tasks
        if internship_id:
            query = query.filter_by(internship_id=internship_id)
        total = query.count()
        if total == 0:
            return 0.0
        completed = query.filter_by(status='completed').count()
        return round((completed / total) * 100, 2)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'phone': self.phone,
            'college': self.college,
            'department': self.department,
            'year_of_study': self.year_of_study,
            'cgpa': float(self.cgpa) if self.cgpa else None,
            'skills': self.skills,
            'email': self.user.email if self.user else None
        }

    def __repr__(self):
        return f'<Student {self.full_name}>'
