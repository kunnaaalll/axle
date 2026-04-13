import asyncio
import threading
from flask import Blueprint, request, jsonify
from web.api.auth import requires_auth
from axle.core.scanner import clone_and_scan, scan_repository
from axle.ai.engine import AIEngine
from axle.core.planner import Planner
from axle.core.runner import TaskRunner
from axle.config.settings import settings

bp = Blueprint("deploy", __name__, url_prefix="/deploy")

# In-memory storage for active deployment (T-123)
active_deployment = {
    "status": "idle",
    "plan": None,
    "error": None,
    "logs": []
}

@bp.route("/", methods=["POST"])
@requires_auth
def start_deployment():
    """T-123: Start a new deployment."""
    global active_deployment
    
    if active_deployment["status"] in ["planning", "running"]:
        return jsonify({"success": False, "error": "A deployment is already in progress"}), 400

    data = request.get_json()
    repo_url = data.get("url")
    provider = data.get("provider", None)

    if not repo_url:
        return jsonify({"success": False, "error": "Repository URL is required"}), 400

    # Reset state
    active_deployment = {
        "status": "planning",
        "plan": None,
        "error": None,
        "logs": []
    }

    # Run deployment in background thread
    thread = threading.Thread(target=_run_deployment_background, args=(repo_url, provider))
    thread.start()

    return jsonify({"success": True, "message": "Deployment started"}), 202

@bp.route("/status", methods=["GET"])
@requires_auth
def get_status():
    """T-123: Get current deployment status."""
    plan_dict = None
    if active_deployment["plan"]:
        # Convert plan model to dict using pydantic
        plan_dict = active_deployment["plan"].model_dump()
        
    return jsonify({
        "success": True,
        "status": active_deployment["status"],
        "plan": plan_dict,
        "error": active_deployment["error"]
    })

def _run_deployment_background(repo_url: str, provider: str):
    """Background task to run the deployment engine."""
    global active_deployment
    try:
        # 1. Scan
        if repo_url.startswith("http") or repo_url.startswith("git@"):
            profile = clone_and_scan(repo_url)
        else:
            profile = scan_repository(repo_url)

        # 2. Plan
        engine = AIEngine(
            gemini_api_key=settings.gemini_api_key,
            openai_api_key=settings.openai_api_key,
            openrouter_api_key=settings.openrouter_api_key,
            preferred_provider=provider,
        )
        
        if not engine.list_available_providers():
            raise ValueError("No AI provider configured.")

        planner = Planner(engine)
        plan = planner.generate_plan(profile)
        
        active_deployment["plan"] = plan
        active_deployment["status"] = "running"
        
        # 3. Execute
        runner = TaskRunner()
        context = {"app_name": profile.name, "port": profile.port, "stack": profile.stack.value}
        
        # Capture runner logs explicitly later through WebSocket
        final_plan = asyncio.run(runner.execute_plan(plan, context))
        active_deployment["plan"] = final_plan

        if any(step.status == "failed" for step in final_plan.steps):
            active_deployment["status"] = "failed"
            active_deployment["error"] = "One or more deployment steps failed."
        else:
            active_deployment["status"] = "completed"

    except Exception as e:
        active_deployment["status"] = "failed"
        active_deployment["error"] = str(e)
