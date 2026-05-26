# =============================================================
# File: backend/routes/ai_routes.py
# Purpose: REST API endpoints for AI/ML features
#          - Resume Screening
#          - Performance Prediction
# =============================================================

from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import sys

# Add ai directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai'))

ai_bp = Blueprint('ai', __name__)


@ai_bp.route('/resume-analyze', methods=['GET', 'POST'])
@login_required
def resume_analyze():
    """
    Upload a resume and analyze it against internship requirements.
    Returns a match score and extracted skills.
    """
    from models.internship_model import Internship
    internships = Internship.query.filter_by(status='open').all()

    if request.method == 'POST':
        # Check if file was uploaded
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file uploaded'}), 400

        file = request.files['resume']
        internship_id = request.form.get('internship_id')

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Save file temporarily
        filename = secure_filename(f"temp_resume_{current_user.id}_{file.filename}")
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            from resume_analyzer import ResumeAnalyzer
            analyzer = ResumeAnalyzer()

            # Get internship requirements if specified
            required_skills_str = ''
            if internship_id:
                internship = Internship.query.get(internship_id)
                if internship:
                    required_skills_str = internship.required_skills or ''

            # Analyze the resume
            result = analyzer.analyze(filepath, required_skills_str)
            print("\n========== AI RESULT ==========")
            print(result)
            print("================================\n")

            # Update resume score in application if student has applied
            if current_user.is_student() and internship_id:
                from models.student_model import Student
                from models.internship_model import Application
                student = Student.query.filter_by(user_id=current_user.id).first()
                if student:
                    app = Application.query.filter_by(
                        student_id=student.id, internship_id=internship_id
                    ).first()
                    if app:
                        app.resume_score = result.get('match_score', 0)
                        from extensions import db
                        db.session.commit()

            return jsonify({
                'success': True,
                'result': result
            }), 200

        except Exception as e:
            return jsonify({'error': f'Analysis failed: {str(e)}'}), 500
        finally:
            # Clean up temp file
            if os.path.exists(filepath):
                os.remove(filepath)

    return render_template('ai_resume.html', internships=internships)


@ai_bp.route('/performance-predict', methods=['GET', 'POST'])
@login_required
def performance_predict():
    """
    Predict student performance based on metrics.
    Input: attendance%, task completion%, report submissions
    Output: Excellent / Good / Average / Needs Improvement
    """
    if request.method == 'POST':
        try:
            # Get metrics from request
            data = request.get_json() or {}

            attendance_pct = float(data.get('attendance_pct', 0))
            task_completion = float(data.get('task_completion', 0))
            report_submissions = int(data.get('report_submissions', 0))
            mentor_rating = float(data.get('mentor_rating', 3.0))

            from performance_predictor import PerformancePredictor
            predictor = PerformancePredictor()
            prediction = predictor.predict(
                attendance_pct=attendance_pct,
                task_completion=task_completion,
                report_submissions=report_submissions,
                mentor_rating=mentor_rating
            )

            return jsonify({
                'success': True,
                'prediction': prediction
            }), 200

        except Exception as e:
            return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

    # GET request - show prediction form
    if current_user.is_student():
        from models.student_model import Student
        from models.internship_model import Application
        student = Student.query.filter_by(user_id=current_user.id).first()
        approved_app = Application.query.filter_by(
            student_id=student.id, status='approved'
        ).first() if student else None

        metrics = {}
        if student and approved_app:
            internship_id = approved_app.internship_id
            metrics = {
                'attendance_pct': student.get_attendance_percentage(internship_id),
                'task_completion': student.get_task_completion_rate(internship_id),
                'report_submissions': student.reports.filter_by(status='approved').count(),
            }

        return render_template('ai_performance.html', metrics=metrics)

    return render_template('ai_performance.html', metrics={})


@ai_bp.route('/api/batch-predict', methods=['POST'])
@login_required
def api_batch_predict():
    """
    Batch performance prediction for admin/mentor use.
    Predict performance for multiple students at once.
    """
    if not (current_user.is_admin() or current_user.is_mentor()):
        return jsonify({'error': 'Unauthorized'}), 403

    from models.student_model import Student
    from models.internship_model import Application
    from performance_predictor import PerformancePredictor

    data = request.get_json() or {}
    internship_id = data.get('internship_id')

    if not internship_id:
        return jsonify({'error': 'internship_id required'}), 400

    predictor = PerformancePredictor()
    results = []

    apps = Application.query.filter_by(internship_id=internship_id, status='approved').all()
    for app in apps:
        student = app.student
        try:
            prediction = predictor.predict(
                attendance_pct=student.get_attendance_percentage(internship_id),
                task_completion=student.get_task_completion_rate(internship_id),
                report_submissions=student.reports.filter_by(status='approved').count(),
                mentor_rating=3.0  # Default; update with actual rating if available
            )
            results.append({
                'student_id': student.id,
                'student_name': student.full_name,
                'prediction': prediction
            })
        except Exception as e:
            results.append({
                'student_id': student.id,
                'student_name': student.full_name,
                'error': str(e)
            })

    return jsonify({'success': True, 'results': results}), 200
