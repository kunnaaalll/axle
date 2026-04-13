import psutil
from flask import Blueprint, jsonify
from web.api.auth import requires_auth
from axle.core.models import HealthMetrics

bp = Blueprint("monitor", __name__, url_prefix="/monitor")

@bp.route("/metrics", methods=["GET"])
@requires_auth
def get_metrics():
    """T-126: Return system health metrics."""
    try:
        metrics = HealthMetrics(
            cpu_percent=psutil.cpu_percent(interval=None),
            ram_used_mb=psutil.virtual_memory().used / (1024 * 1024),
            ram_total_mb=psutil.virtual_memory().total / (1024 * 1024),
            disk_used_gb=psutil.disk_usage('/').used / (1024**3),
            disk_total_gb=psutil.disk_usage('/').total / (1024**3),
        )
        return jsonify({"success": True, "metrics": metrics.model_dump()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
