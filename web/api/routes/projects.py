from flask import Blueprint, jsonify
from web.api.auth import requires_auth

bp = Blueprint("projects", __name__, url_prefix="/projects")

@bp.route("/", methods=["GET"])
@requires_auth
def get_projects():
    """T-124: Get list of deployed projects. Stub for now."""
    return jsonify({
        "success": True,
        "projects": []
    })

@bp.route("/<string:project_id>", methods=["GET"])
@requires_auth
def get_project(project_id):
    """T-124: Get specific project details."""
    return jsonify({
        "success": False,
        "error": "Project not found"
    }), 404
