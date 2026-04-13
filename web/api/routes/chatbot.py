from flask import Blueprint, jsonify, request
from web.api.auth import requires_auth
from axle.ai.engine import AIEngine
from axle.config.settings import settings

bp = Blueprint("chatbot", __name__, url_prefix="/chat")

@bp.route("/", methods=["POST"])
@requires_auth
def chat():
    """T-127: AI chatbot query endpoint."""
    data = request.get_json()
    if not data or "query" not in data:
        return jsonify({"success": False, "error": "Missing query content"}), 400
        
    query = data["query"]
    # Provide system context along with user query
    context = (
        "You are AXLE OS Chatbot. You assist users with infrastructure, "
        "deployment, and server management inside AXLE OS.\n\n"
        f"User Query: {query}"
    )

    try:
        engine = AIEngine(
            gemini_api_key=settings.gemini_api_key,
            openai_api_key=settings.openai_api_key,
            openrouter_api_key=settings.openrouter_api_key,
        )
        response = engine.generate(context)
        return jsonify({"success": True, "reply": response})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
