from flask import Blueprint, jsonify
from flask_login import login_required

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/api/all', methods=['GET'])
@login_required
def api_all_attendance():
    from models.attendance_model import Attendance
    records = Attendance.query.all()
    return jsonify([r.to_dict() for r in records]), 200
