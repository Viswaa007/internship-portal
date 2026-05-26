# =============================================================
# File: backend/routes/mentor_routes.py
# Purpose: Mentor dashboard, student management, feedback
# =============================================================

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from extensions import db
from models.mentor_model import Mentor
from models.student_model import Student
from models.internship_model import Internship, Application
from models.attendance_model import Attendance, Task, Report, Feedback

mentor_bp = Blueprint('mentor', __name__)


def mentor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_mentor():
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_mentor():
    return Mentor.query.filter_by(user_id=current_user.id).first()


@mentor_bp.route('/dashboard')
@login_required
@mentor_required
def dashboard():
    mentor = get_current_mentor()
    if not mentor:
        flash('Mentor profile not found.', 'danger')
        return redirect(url_for('auth.login'))

    # Get all internships for this mentor
    my_internships = Internship.query.filter_by(mentor_id=mentor.id).all()
    internship_ids = [i.id for i in my_internships]

    # Get assigned students
    assigned_students = []
    for iid in internship_ids:
        apps = Application.query.filter_by(internship_id=iid, status='approved').all()
        for app in apps:
            assigned_students.append({'student': app.student, 'internship': app.internship})

    # Stats
    pending_reports = Report.query.filter(
        Report.internship_id.in_(internship_ids), Report.status == 'pending'
    ).count()
    pending_tasks = Task.query.filter(
        Task.mentor_id == mentor.id, Task.status == 'pending'
    ).count()

    return render_template('mentor_dashboard.html',
        mentor=mentor,
        my_internships=my_internships,
        assigned_students=assigned_students,
        pending_reports=pending_reports,
        pending_tasks=pending_tasks
    )


@mentor_bp.route('/students')
@login_required
@mentor_required
def students():
    mentor = get_current_mentor()
    internship_ids = [i.id for i in Internship.query.filter_by(mentor_id=mentor.id).all()]
    students_data = []
    for iid in internship_ids:
        apps = Application.query.filter_by(internship_id=iid, status='approved').all()
        for app in apps:
            s = app.student
            students_data.append({
                'student': s,
                'internship': app.internship,
                'attendance_pct': s.get_attendance_percentage(iid),
                'task_completion': s.get_task_completion_rate(iid)
            })
    return render_template('mentor_students.html', students_data=students_data)


@mentor_bp.route('/tasks/assign', methods=['GET', 'POST'])
@login_required
@mentor_required
def assign_task():
    mentor = get_current_mentor()
    internship_ids = [i.id for i in Internship.query.filter_by(mentor_id=mentor.id).all()]
    students_in_internships = []
    for iid in internship_ids:
        apps = Application.query.filter_by(internship_id=iid, status='approved').all()
        for app in apps:
            students_in_internships.append({'student': app.student, 'internship_id': iid})

    if request.method == 'POST':
        try:
            from datetime import datetime
            task = Task(
                internship_id=int(request.form.get('internship_id')),
                student_id=int(request.form.get('student_id')),
                mentor_id=mentor.id,
                title=request.form.get('title'),
                description=request.form.get('description'),
                assigned_date=datetime.today().date(),
                deadline=datetime.strptime(request.form.get('deadline'), '%Y-%m-%d').date(),
                priority=request.form.get('priority', 'medium')
            )
            db.session.add(task)
            db.session.commit()
            flash('Task assigned successfully!', 'success')
            return redirect(url_for('mentor.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    my_internships = Internship.query.filter_by(mentor_id=mentor.id).all()
    return render_template('mentor_assign_task.html',
        students=students_in_internships, internships=my_internships)


@mentor_bp.route('/tasks')
@login_required
@mentor_required
def tasks():
    mentor = get_current_mentor()
    all_tasks = Task.query.filter_by(mentor_id=mentor.id).order_by(Task.deadline).all()
    return render_template('tasks.html', tasks=all_tasks, role='mentor')


@mentor_bp.route('/tasks/rate/<int:task_id>', methods=['POST'])
@login_required
@mentor_required
def rate_task(task_id):
    task = Task.query.get_or_404(task_id)
    rating = request.form.get('rating')
    status = request.form.get('status', task.status)
    if rating:
        task.mentor_rating = int(rating)
    task.status = status
    db.session.commit()
    flash('Task updated!', 'success')
    return redirect(url_for('mentor.tasks'))


@mentor_bp.route('/reports')
@login_required
@mentor_required
def reports():
    mentor = get_current_mentor()
    internship_ids = [i.id for i in Internship.query.filter_by(mentor_id=mentor.id).all()]
    reports = Report.query.filter(Report.internship_id.in_(internship_ids)).order_by(Report.submitted_at.desc()).all()
    return render_template('reports.html', reports=reports, role='mentor')


@mentor_bp.route('/reports/review/<int:report_id>', methods=['POST'])
@login_required
@mentor_required
def review_report(report_id):
    report = Report.query.get_or_404(report_id)
    report.mentor_feedback = request.form.get('feedback')
    report.status = request.form.get('status', 'reviewed')
    db.session.commit()
    flash('Report reviewed!', 'success')
    return redirect(url_for('mentor.reports'))


@mentor_bp.route('/feedback/add/<int:student_id>/<int:internship_id>', methods=['GET', 'POST'])
@login_required
@mentor_required
def add_feedback(student_id, internship_id):
    mentor = get_current_mentor()
    student = Student.query.get_or_404(student_id)
    if request.method == 'POST':
        feedback = Feedback(
            mentor_id=mentor.id,
            student_id=student_id,
            internship_id=internship_id,
            feedback_text=request.form.get('feedback_text'),
            rating=int(request.form.get('rating', 3))
        )
        db.session.add(feedback)
        db.session.commit()
        flash('Feedback submitted!', 'success')
        return redirect(url_for('mentor.students'))
    return render_template('mentor_feedback.html', student=student, internship_id=internship_id)

