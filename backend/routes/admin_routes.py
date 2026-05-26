# =============================================================
# File: backend/routes/admin_routes.py
# Purpose: Admin dashboard and management functionalities
# =============================================================

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from extensions import db
from models.user_model import User
from models.student_model import Student
from models.mentor_model import Mentor
from models.internship_model import Internship, Application
from models.attendance_model import Attendance, Task, Report, Certificate
from datetime import datetime, date
import uuid

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator to restrict access to admin users only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with analytics overview."""
    # Gather statistics
    stats = {
        'total_students': Student.query.count(),
        'total_mentors': Mentor.query.count(),
        'active_internships': Internship.query.filter_by(status='open').count(),
        'total_internships': Internship.query.count(),
        'pending_applications': Application.query.filter_by(status='pending').count(),
        'pending_reports': Report.query.filter_by(status='pending').count(),
        'total_certificates': Certificate.query.count(),
    }

    # Recent applications
    recent_applications = Application.query.order_by(
        Application.applied_at.desc()
    ).limit(10).all()

    # Internship data for charts
    internship_stats = []
    for internship in Internship.query.all():
        internship_stats.append({
            'title': internship.title,
            'approved': internship.applications.filter_by(status='approved').count(),
            'pending': internship.applications.filter_by(status='pending').count(),
        })

    return render_template('admin_dashboard.html',
        stats=stats,
        recent_applications=recent_applications,
        internship_stats=internship_stats
    )


# ------------------------------------------------------------------
# STUDENT MANAGEMENT
# ------------------------------------------------------------------

@admin_bp.route('/students')
@login_required
@admin_required
def students():
    """List all students."""
    students = Student.query.all()
    return render_template('admin_students.html', students=students)


@admin_bp.route('/students/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_student():
    """Add a new student."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password', 'Student@123')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        college = request.form.get('college')
        department = request.form.get('department')
        year_of_study = request.form.get('year_of_study')
        cgpa = request.form.get('cgpa')

        errors = []
        if not all([username, email, full_name]):
            errors.append('Username, email, and full name are required.')
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered.')
        if User.query.filter_by(username=username).first():
            errors.append('Username already taken.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('admin_add_student.html')

        try:
            new_user = User(username=username, email=email, role='student')
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.flush()

            student = Student(
                user_id=new_user.id, full_name=full_name, phone=phone,
                college=college, department=department,
                year_of_study=year_of_study,
                cgpa=float(cgpa) if cgpa else None
            )
            db.session.add(student)
            db.session.commit()
            flash(f'Student {full_name} added successfully!', 'success')
            return redirect(url_for('admin.students'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding student: {str(e)}', 'danger')

    return render_template('admin_add_student.html')


@admin_bp.route('/students/edit/<int:student_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_student(student_id):
    """Edit an existing student."""
    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
        try:
            student.full_name = request.form.get('full_name', student.full_name)
            student.phone = request.form.get('phone', student.phone)
            student.college = request.form.get('college', student.college)
            student.department = request.form.get('department', student.department)
            student.year_of_study = request.form.get('year_of_study', student.year_of_study)
            cgpa = request.form.get('cgpa')
            student.cgpa = float(cgpa) if cgpa else student.cgpa
            db.session.commit()
            flash('Student updated successfully!', 'success')
            return redirect(url_for('admin.students'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating student: {str(e)}', 'danger')

    return render_template('admin_edit_student.html', student=student)


@admin_bp.route('/students/delete/<int:student_id>', methods=['POST'])
@login_required
@admin_required
def delete_student(student_id):
    """Delete a student."""
    student = Student.query.get_or_404(student_id)
    try:
        user = User.query.get(student.user_id)
        db.session.delete(user)  # Cascades to student profile
        db.session.commit()
        flash('Student deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting student: {str(e)}', 'danger')
    return redirect(url_for('admin.students'))


# ------------------------------------------------------------------
# MENTOR MANAGEMENT
# ------------------------------------------------------------------

@admin_bp.route('/mentors')
@login_required
@admin_required
def mentors():
    """List all mentors."""
    mentors = Mentor.query.all()
    return render_template('admin_mentors.html', mentors=mentors)


@admin_bp.route('/mentors/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_mentor():
    """Add a new mentor."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password', 'Mentor@123')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        designation = request.form.get('designation')
        department = request.form.get('department')
        expertise = request.form.get('expertise')

        errors = []
        if not all([username, email, full_name]):
            errors.append('Username, email, and full name are required.')
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered.')
        if User.query.filter_by(username=username).first():
            errors.append('Username already taken.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('admin_add_mentor.html')

        try:
            new_user = User(username=username, email=email, role='mentor')
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.flush()

            mentor = Mentor(
                user_id=new_user.id, full_name=full_name, phone=phone,
                designation=designation, department=department, expertise=expertise
            )
            db.session.add(mentor)
            db.session.commit()
            flash(f'Mentor {full_name} added successfully!', 'success')
            return redirect(url_for('admin.mentors'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding mentor: {str(e)}', 'danger')

    return render_template('admin_add_mentor.html')


@admin_bp.route('/mentors/delete/<int:mentor_id>', methods=['POST'])
@login_required
@admin_required
def delete_mentor(mentor_id):
    """Delete a mentor."""
    mentor = Mentor.query.get_or_404(mentor_id)
    try:
        user = User.query.get(mentor.user_id)
        db.session.delete(user)
        db.session.commit()
        flash('Mentor deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting mentor: {str(e)}', 'danger')
    return redirect(url_for('admin.mentors'))


# ------------------------------------------------------------------
# INTERNSHIP MANAGEMENT
# ------------------------------------------------------------------

@admin_bp.route('/internships')
@login_required
@admin_required
def internships():
    """List all internships."""
    internships = Internship.query.all()
    return render_template('admin_internships.html', internships=internships)


@admin_bp.route('/internships/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_internship():
    """Create a new internship."""
    mentors = Mentor.query.all()

    if request.method == 'POST':
        try:
            internship = Internship(
                title=request.form.get('title'),
                description=request.form.get('description'),
                domain=request.form.get('domain'),
                required_skills=request.form.get('required_skills'),
                duration_weeks=int(request.form.get('duration_weeks', 0)),
                start_date=datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date(),
                end_date=datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date(),
                max_students=int(request.form.get('max_students', 10)),
                mentor_id=request.form.get('mentor_id') or None,
                status=request.form.get('status', 'open')
            )
            db.session.add(internship)
            db.session.commit()
            flash('Internship created successfully!', 'success')
            return redirect(url_for('admin.internships'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating internship: {str(e)}', 'danger')

    return render_template('admin_add_internship.html', mentors=mentors)


# ------------------------------------------------------------------
# APPLICATION MANAGEMENT
# ------------------------------------------------------------------

@admin_bp.route('/applications')
@login_required
@admin_required
def applications():
    """View all applications."""
    applications = Application.query.order_by(Application.applied_at.desc()).all()
    return render_template('admin_applications.html', applications=applications)


@admin_bp.route('/applications/approve/<int:app_id>', methods=['POST'])
@login_required
@admin_required
def approve_application(app_id):
    """Approve a student application."""
    application = Application.query.get_or_404(app_id)
    application.status = 'approved'
    application.admin_remarks = request.form.get('remarks', 'Approved by admin')
    db.session.commit()
    flash('Application approved!', 'success')
    return redirect(url_for('admin.applications'))


@admin_bp.route('/applications/reject/<int:app_id>', methods=['POST'])
@login_required
@admin_required
def reject_application(app_id):
    """Reject a student application."""
    application = Application.query.get_or_404(app_id)
    application.status = 'rejected'
    application.admin_remarks = request.form.get('remarks', 'Rejected by admin')
    db.session.commit()
    flash('Application rejected.', 'warning')
    return redirect(url_for('admin.applications'))


# ------------------------------------------------------------------
# CERTIFICATE GENERATION
# ------------------------------------------------------------------

@admin_bp.route('/certificates/generate/<int:student_id>/<int:internship_id>', methods=['POST'])
@login_required
@admin_required
def generate_certificate(student_id, internship_id):
    """Generate a certificate for a student."""
    student = Student.query.get_or_404(student_id)
    internship = Internship.query.get_or_404(internship_id)

    # Check if certificate already exists
    existing = Certificate.query.filter_by(
        student_id=student_id, internship_id=internship_id
    ).first()

    if existing:
        flash('Certificate already generated!', 'warning')
        return redirect(url_for('admin.dashboard'))

    # Get performance grade from AI predictor
    performance_grade = 'Good'  # Default; replace with AI module result

    cert_number = f'CERT-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}'

    certificate = Certificate(
        student_id=student_id,
        internship_id=internship_id,
        certificate_number=cert_number,
        issued_date=date.today(),
        performance_grade=performance_grade,
        issued_by=current_user.id
    )
    db.session.add(certificate)
    db.session.commit()
    flash(f'Certificate generated: {cert_number}', 'success')
    return redirect(url_for('admin.dashboard'))


# ------------------------------------------------------------------
# REST API ENDPOINTS
# ------------------------------------------------------------------

@admin_bp.route('/api/stats', methods=['GET'])
@login_required
@admin_required
def api_stats():
    """API endpoint for dashboard statistics."""
    stats = {
        'total_students': Student.query.count(),
        'total_mentors': Mentor.query.count(),
        'active_internships': Internship.query.filter_by(status='open').count(),
        'pending_applications': Application.query.filter_by(status='pending').count(),
    }
    return jsonify(stats), 200


@admin_bp.route('/api/students', methods=['GET'])
@login_required
@admin_required
def api_students():
    """GET all students as JSON."""
    students = Student.query.all()
    return jsonify([s.to_dict() for s in students]), 200


@admin_bp.route('/api/internships', methods=['GET'])
@login_required
@admin_required
def api_internships():
    """GET all internships as JSON."""
    internships = Internship.query.all()
    return jsonify([i.to_dict() for i in internships]), 200
