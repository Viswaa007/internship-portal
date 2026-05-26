# =============================================================
# File: backend/models/internship_model.py
# Purpose: Internship program and application models
# =============================================================

from extensions import db
from datetime import datetime


class Internship(db.Model):
    """Internship program created by admin."""
    __tablename__ = 'internships'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    domain = db.Column(db.String(100))
    required_skills = db.Column(db.Text)
    duration_weeks = db.Column(db.Integer)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    max_students = db.Column(db.Integer, default=10)
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentors.id'), nullable=True)
    status = db.Column(db.Enum('open', 'closed', 'completed'), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    applications = db.relationship('Application', backref='internship', lazy='dynamic', cascade='all, delete-orphan')
    attendance_records = db.relationship('Attendance', backref='internship', lazy='dynamic')
    tasks = db.relationship('Task', backref='internship', lazy='dynamic')
    reports = db.relationship('Report', backref='internship', lazy='dynamic')
    certificates = db.relationship('Certificate', backref='internship', lazy='dynamic')

    def get_approved_students_count(self):
        """Count of approved students."""
        return self.applications.filter_by(status='approved').count()

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'domain': self.domain,
            'required_skills': self.required_skills,
            'duration_weeks': self.duration_weeks,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'max_students': self.max_students,
            'mentor_id': self.mentor_id,
            'status': self.status,
            'approved_count': self.get_approved_students_count()
        }

    def __repr__(self):
        return f'<Internship {self.title}>'


class Application(db.Model):
    """Student application for an internship."""
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    internship_id = db.Column(db.Integer, db.ForeignKey('internships.id'), nullable=False)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum('pending', 'approved', 'rejected'), default='pending')
    resume_score = db.Column(db.Numeric(5, 2), default=0.0)
    admin_remarks = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'internship_id': self.internship_id,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'status': self.status,
            'resume_score': float(self.resume_score) if self.resume_score else 0.0,
            'student_name': self.student.full_name if self.student else None,
            'internship_title': self.internship.title if self.internship else None
        }

    def __repr__(self):
        return f'<Application Student:{self.student_id} Internship:{self.internship_id}>'
