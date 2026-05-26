# =============================================================
# File: backend/routes/student_routes.py
# Purpose: Student dashboard, profile, applications, tasks
# =============================================================

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from functools import wraps
from werkzeug.utils import secure_filename
from extensions import db
from models.student_model import Student
from models.internship_model import Internship, Application
from models.attendance_model import Attendance, Task, Report, Certificate, Feedback
import os

student_bp = Blueprint('student', __name__)


def student_required(f):
    """Decorator to restrict access to student users only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_student():
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_student():
    """Helper to get the current logged-in student's profile."""
    return Student.query.filter_by(user_id=current_user.id).first()


@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    """Student dashboard with overview."""
    student = get_current_student()
    if not student:
        flash('Student profile not found. Contact admin.', 'danger')
        return redirect(url_for('auth.login'))

    # Get approved internship
    approved_app = Application.query.filter_by(
        student_id=student.id, status='approved'
    ).first()

    internship = None
    attendance_pct = 0
    task_completion = 0
    pending_tasks = []
    recent_feedback = []

    if approved_app:
        internship = approved_app.internship
        attendance_pct = student.get_attendance_percentage(internship.id)
        task_completion = student.get_task_completion_rate(internship.id)
        pending_tasks = Task.query.filter_by(
            student_id=student.id, status='pending'
        ).limit(5).all()
        recent_feedback = Feedback.query.filter_by(
            student_id=student.id
        ).order_by(Feedback.feedback_date.desc()).limit(3).all()

    recent_attendance = Attendance.query.filter_by(
        student_id=student.id
    ).order_by(Attendance.date.desc()).limit(10).all()

    return render_template('student_dashboard.html',
        student=student,
        internship=internship,
        attendance_pct=attendance_pct,
        task_completion=task_completion,
        pending_tasks=pending_tasks,
        recent_feedback=recent_feedback,
        recent_attendance=recent_attendance
    )


@student_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@student_required
def profile():
    """View and edit student profile."""
    student = get_current_student()

    if request.method == 'POST':
        try:
            student.full_name = request.form.get('full_name', student.full_name)
            student.phone = request.form.get('phone', student.phone)
            student.college = request.form.get('college', student.college)
            student.department = request.form.get('department', student.department)
            student.year_of_study = request.form.get('year_of_study', student.year_of_study)
            student.skills = request.form.get('skills', student.skills)

            # Handle profile picture upload
            if 'profile_pic' in request.files:
                file = request.files['profile_pic']
                if file and file.filename:
                    filename = secure_filename(f"profile_{student.id}_{file.filename}")
                    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                    os.makedirs(upload_folder, exist_ok=True)
                    file_path = os.path.join(upload_folder, filename)
                    file.save(file_path)
                    student.profile_pic = filename

            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')

    return render_template('student_profile.html', student=student)


@student_bp.route('/internships')
@login_required
@student_required
def internships():
    """View available internships and application status."""
    student = get_current_student()
    open_internships = Internship.query.filter_by(status='open').all()

    # Get student's applications
    my_applications = Application.query.filter_by(student_id=student.id).all()
    applied_internship_ids = [app.internship_id for app in my_applications]

    return render_template('student_internships.html',
        internships=open_internships,
        my_applications=my_applications,
        applied_internship_ids=applied_internship_ids
    )


@student_bp.route('/apply/<int:internship_id>', methods=['POST'])
@login_required
@student_required
def apply_internship(internship_id):
    """Apply for an internship."""
    student = get_current_student()
    internship = Internship.query.get_or_404(internship_id)

    # Check if already applied
    existing = Application.query.filter_by(
        student_id=student.id, internship_id=internship_id
    ).first()

    if existing:
        flash('You have already applied for this internship.', 'warning')
        return redirect(url_for('student.internships'))

    try:
        application = Application(
            student_id=student.id,
            internship_id=internship_id,
            status='pending'
        )
        db.session.add(application)
        db.session.commit()
        flash(f'Successfully applied for {internship.title}!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error applying: {str(e)}', 'danger')

    return redirect(url_for('student.internships'))


@student_bp.route('/resume-upload', methods=['GET', 'POST'])
@login_required
@student_required
def resume_upload():
    """Upload resume for AI screening."""
    student = get_current_student()

    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No file selected.', 'danger')
            return redirect(request.url)

        file = request.files['resume']
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(request.url)

        allowed = {'pdf', 'doc', 'docx'}
        if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed:
            flash('Invalid file type. Upload PDF or DOCX only.', 'danger')
            return redirect(request.url)

        try:
            filename = secure_filename(f"resume_{student.id}_{file.filename}")
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            student.resume_path = filename
            db.session.commit()
            flash('Resume uploaded successfully!', 'success')
            return redirect(url_for('student.dashboard'))
        except Exception as e:
            flash(f'Upload failed: {str(e)}', 'danger')

    return render_template('student_resume.html', student=student)


@student_bp.route('/tasks')
@login_required
@student_required
def tasks():
    """View all assigned tasks."""
    student = get_current_student()
    all_tasks = Task.query.filter_by(student_id=student.id).order_by(Task.deadline).all()
    return render_template('tasks.html', tasks=all_tasks, role='student')


@student_bp.route('/tasks/update/<int:task_id>', methods=['POST'])
@login_required
@student_required
def update_task_status(task_id):
    """Update task status (student marks as in_progress or completed)."""
    task = Task.query.get_or_404(task_id)
    student = get_current_student()

    if task.student_id != student.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('student.tasks'))

    new_status = request.form.get('status')
    if new_status in ['in_progress', 'completed']:
        task.status = new_status
        if new_status == 'completed':
            from datetime import date
            task.completion_date = date.today()
        db.session.commit()
        flash('Task status updated!', 'success')

    return redirect(url_for('student.tasks'))


@student_bp.route('/attendance')
@login_required
@student_required
def attendance():
    """View attendance history."""
    student = get_current_student()

    # all attendance records
    records = Attendance.query.filter_by(
        student_id=student.id
    ).order_by(Attendance.date.desc()).all()

    # total internship days
    total_days = 30

    # count present
    present_count = Attendance.query.filter_by(
        student_id=student.id,
        status='present'
    ).count()

    # calculate absent
    absent_count = total_days - present_count

    # percentage
    attendance_pct = round((present_count / total_days) * 100, 2)

    return render_template(
        'attendance.html',
        records=records,
        attendance_pct=attendance_pct,
        present_count=present_count,
        absent_count=absent_count,
        total_days=total_days,
        role='student'
    )


@student_bp.route('/mark-attendance', methods=['POST'])
@login_required
@student_required
def mark_attendance():
    """Student marks their own attendance."""
    from datetime import date, datetime as dt
    student = get_current_student()

    # Get approved internship
    approved_app = Application.query.filter_by(student_id=student.id, status='approved').first()
    if not approved_app:
        flash('You must be enrolled in an internship to mark attendance.', 'warning')
        return redirect(url_for('student.attendance'))

    today = date.today()
    existing = Attendance.query.filter_by(
        student_id=student.id, internship_id=approved_app.internship_id, date=today
    ).first()

    if existing:
        flash('Attendance already marked for today.', 'warning')
        return redirect(url_for('student.attendance'))

    try:
        status = request.form.get('status', 'present')
        attendance = Attendance(
            student_id=student.id,
            internship_id=approved_app.internship_id,
            date=today,
            check_in_time=dt.now().time() if status == 'present' else None,
            status=status
        )
        db.session.add(attendance)
        db.session.commit()
        flash('Attendance marked successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('student.attendance'))


@student_bp.route('/reports')
@login_required
@student_required
def reports():
    """View submitted reports."""
    student = get_current_student()
    all_reports = Report.query.filter_by(student_id=student.id).order_by(Report.submitted_at.desc()).all()
    return render_template('reports.html', reports=all_reports, role='student')


@student_bp.route('/reports/submit', methods=['GET', 'POST'])
@login_required
@student_required
def submit_report():
    """Submit a new report."""
    student = get_current_student()
    approved_app = Application.query.filter_by(student_id=student.id, status='approved').first()

    if not approved_app:
        flash('You must be enrolled in an internship to submit reports.', 'warning')
        return redirect(url_for('student.reports'))

    if request.method == 'POST':
        title = request.form.get('title')
        report_type = request.form.get('report_type', 'weekly')
        file = request.files.get('report_file')

        file_path = None
        if file and file.filename:
            filename = secure_filename(f"report_{student.id}_{file.filename}")
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            file_path = filename

        try:
            report = Report(
                student_id=student.id,
                internship_id=approved_app.internship_id,
                title=title,
                report_type=report_type,
                file_path=file_path
            )
            db.session.add(report)
            db.session.commit()
            flash('Report submitted successfully!', 'success')
            return redirect(url_for('student.reports'))
        except Exception as e:
            db.session.rollback()
            flash(f'Submission failed: {str(e)}', 'danger')

    return render_template('student_submit_report.html', student=student)


@student_bp.route('/certificates')
@login_required
@student_required
def certificates():
    """View earned certificates."""
    student = get_current_student()
    certs = Certificate.query.filter_by(student_id=student.id).all()
    return render_template('certificates.html', certificates=certs, role='student')


@student_bp.route('/feedback')
@login_required
@student_required
def feedback():
    """View feedback from mentors."""
    student = get_current_student()
    feedbacks = Feedback.query.filter_by(student_id=student.id).order_by(Feedback.feedback_date.desc()).all()
    return render_template('student_feedback.html', feedbacks=feedbacks)


# ------------------------------------------------------------------
# REST API
# ------------------------------------------------------------------

@student_bp.route('/api/profile', methods=['GET'])
@login_required
@student_required
def api_profile():
    """GET student profile as JSON."""
    student = get_current_student()
    return jsonify(student.to_dict()), 200
