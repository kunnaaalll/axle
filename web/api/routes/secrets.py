from flask import Blueprint, jsonify, request
from web.api.auth import requires_auth
from axle.secrets.vault import Vault

bp = Blueprint("secrets", __name__, url_prefix="/secrets")

def _get_vault():
    # In a real dashboard, we might hold the password in session 
    # For now, if the API is running, we assume it's unlocked via environment 
    # or we use a generic placeholder pass for testing.
    pwd = "scrypt:32768:8:1$u72T7ZtE9q6E5yqF$ec0e4b8682cd11fe1eef7c2eb21516ab1440d16be994dc15f92ffccb0c7989d31bd1e1a539bc2f60d6910da562ae5ad334057864aa6a3a4c585c53c4d12c24c2"
    return Vault(pwd)

@bp.route("/", methods=["GET"])
@requires_auth
def list_secrets():
    """T-125: List secret keys (never values)."""
    try:
        vault = _get_vault()
        return jsonify({"success": True, "keys": vault.list_keys()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@bp.route("/", methods=["POST"])
@requires_auth
def add_secret():
    """T-125: Add or update a secret."""
    data = request.get_json()
    if not data or "key" not in data or "value" not in data:
        return jsonify({"success": False, "error": "Missing key or value"}), 400
        
    try:
        vault = _get_vault()
        vault.set(data["key"], data["value"])
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@bp.route("/<string:key>", methods=["DELETE"])
@requires_auth
def delete_secret(key):
    """T-125: Delete a secret."""
    try:
        vault = _get_vault()
        success = vault.delete(key)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
