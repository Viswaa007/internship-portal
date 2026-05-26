# =============================================================
# File: backend/models/attendance_model.py
# Purpose: Attendance tracking model
# =============================================================
from extensions import db
from datetime import datetime

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    internship_id = db.Column(db.Integer, db.ForeignKey('internships.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    check_in_time = db.Column(db.Time)
    status = db.Column(db.Enum('present', 'absent', 'late', 'half_day'), default='present')
    remarks = db.Column(db.String(300))
    __table_args__ = (db.UniqueConstraint('student_id', 'internship_id', 'date'),)

    def to_dict(self):
        return {
            'id': self.id, 'student_id': self.student_id,
            'internship_id': self.internship_id,
            'date': self.date.isoformat() if self.date else None,
            'check_in_time': str(self.check_in_time) if self.check_in_time else None,
            'status': self.status, 'remarks': self.remarks
        }

# =============================================================
# File: backend/models/task_model.py
# Purpose: Task assignment and tracking model
# =============================================================

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    internship_id = db.Column(db.Integer, db.ForeignKey('internships.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentors.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    assigned_date = db.Column(db.Date)
    deadline = db.Column(db.Date)
    priority = db.Column(db.Enum('low', 'medium', 'high'), default='medium')
    status = db.Column(db.Enum('pending', 'in_progress', 'completed', 'overdue'), default='pending')
    completion_date = db.Column(db.Date)
    mentor_rating = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'title': self.title, 'description': self.description,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'priority': self.priority, 'status': self.status,
            'student_name': self.student.full_name if self.student else None
        }

# =============================================================
# File: backend/models/report_model.py
# Purpose: Report submission and review model
# =============================================================

class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    internship_id = db.Column(db.Integer, db.ForeignKey('internships.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    report_type = db.Column(db.Enum('weekly', 'monthly', 'final'), default='weekly')
    file_path = db.Column(db.String(300))
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum('pending', 'reviewed', 'approved', 'rejected'), default='pending')
    mentor_feedback = db.Column(db.Text)
    admin_approval = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id, 'title': self.title, 'report_type': self.report_type,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'status': self.status, 'mentor_feedback': self.mentor_feedback,
            'student_name': self.student.full_name if self.student else None
        }

# =============================================================
# File: backend/models/feedback_model.py
# Purpose: Mentor feedback on student performance
# =============================================================

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentors.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    internship_id = db.Column(db.Integer, db.ForeignKey('internships.id'), nullable=False)
    feedback_text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer)
    feedback_date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'feedback_text': self.feedback_text,
            'rating': self.rating,
            'feedback_date': self.feedback_date.isoformat() if self.feedback_date else None,
            'mentor_name': self.mentor.full_name if self.mentor else None
        }

# =============================================================
# File: backend/models/certificate_model.py (included here)
# Purpose: Certificate generation tracking
# =============================================================

class Certificate(db.Model):
    __tablename__ = 'certificates'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    internship_id = db.Column(db.Integer, db.ForeignKey('internships.id'), nullable=False)
    certificate_number = db.Column(db.String(100), unique=True)
    issued_date = db.Column(db.Date)
    file_path = db.Column(db.String(300))
    performance_grade = db.Column(db.Enum('Excellent', 'Good', 'Average', 'Needs Improvement'))
    issued_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'certificate_number': self.certificate_number,
            'issued_date': self.issued_date.isoformat() if self.issued_date else None,
            'performance_grade': self.performance_grade,
            'student_name': self.student.full_name if self.student else None,
            'internship_title': self.internship.title if self.internship else None
        }
