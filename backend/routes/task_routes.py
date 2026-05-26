from flask import Blueprint, jsonify
from flask_login import login_required

task_bp = Blueprint('task', __name__)

@task_bp.route('/api/all', methods=['GET'])
@login_required
def api_all_tasks():
    from models.attendance_model import Task
    tasks = Task.query.all()
    return jsonify([t.to_dict() for t in tasks]), 200
