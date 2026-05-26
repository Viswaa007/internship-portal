# =============================================================
# File: backend/models/mentor_model.py
# Purpose: Mentor profile model
# =============================================================

from extensions import db
from datetime import datetime


class Mentor(db.Model):
    """Mentor extended profile linked to User."""
    __tablename__ = 'mentors'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    designation = db.Column(db.String(150))
    department = db.Column(db.String(100))
    expertise = db.Column(db.String(300))
    profile_pic = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    internships = db.relationship('Internship', backref='mentor', lazy='dynamic')
    tasks_assigned = db.relationship('Task', backref='mentor', lazy='dynamic')
    feedbacks_given = db.relationship('Feedback', backref='mentor', lazy='dynamic')

    def get_assigned_students(self):
        """Get all students assigned to this mentor via internships."""
        from models.internship_model import Internship, Application
        internship_ids = [i.id for i in self.internships.all()]
        students = []
        for iid in internship_ids:
            apps = Application.query.filter_by(internship_id=iid, status='approved').all()
            for app in apps:
                students.append(app.student)
        return students

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'phone': self.phone,
            'designation': self.designation,
            'department': self.department,
            'expertise': self.expertise,
            'email': self.user.email if self.user else None
        }

    def __repr__(self):
        return f'<Mentor {self.full_name}>'
