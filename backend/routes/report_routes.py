from flask import Blueprint, jsonify
from flask_login import login_required

report_bp = Blueprint('report', __name__)

@report_bp.route('/api/all', methods=['GET'])
@login_required
def api_all_reports():
    from models.attendance_model import Report
    reports = Report.query.all()
    return jsonify([r.to_dict() for r in reports]), 200
