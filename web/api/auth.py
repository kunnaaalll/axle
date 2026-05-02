import os
import functools
import secrets
from flask import Blueprint, request, jsonify, g

bp = Blueprint("auth", __name__, url_prefix="/auth")

# In-memory session store (for single-node setup)
ACTIVE_SESSIONS = set()

# Simplified Admin Password for now (Will be derived from vault or hashed on real deploy)
ADMIN_PASSWORD_HASH = os.environ.get(
    "AXLE_ADMIN_PASSWORD_HASH",
    # Default is 'admin' hashed using werkzeug pbkdf2:sha256 (cross-platform)
    "pbkdf2:sha256:1000000$3GfveWSNc3Cd2kBu$61640fe619599849b8520a01a9d9f1a73e376f3ef35236830d0d9d7ef1603ce9"
)

from werkzeug.security import check_password_hash

@bp.route("/login", methods=["POST"])
def login():
    """T-122: Password login yielding a session token."""
    data = request.get_json()
    if not data or "password" not in data:
        return jsonify({"success": False, "error": "Missing password"}), 400

    password = data["password"]
    
    if check_password_hash(ADMIN_PASSWORD_HASH, password):
        token = secrets.token_hex(32)
        ACTIVE_SESSIONS.add(token)
        return jsonify({"success": True, "token": token})
    else:
        return jsonify({"success": False, "error": "Invalid password"}), 401

@bp.route("/logout", methods=["POST"])
def logout():
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        ACTIVE_SESSIONS.discard(token)
    return jsonify({"success": True})

def requires_auth(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "error": "Unauthorized"}), 401
        
        token = auth_header.split(" ")[1]
        if token not in ACTIVE_SESSIONS:
            return jsonify({"success": False, "error": "Invalid or expired token"}), 401
            
        return f(*args, **kwargs)
    return decorated
