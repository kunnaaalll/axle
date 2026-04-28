import os
from flask import Blueprint, jsonify, request
from web.api.auth import requires_auth
from axle.secrets.vault import Vault

bp = Blueprint("secrets", __name__, url_prefix="/secrets")

# The vault password is sourced from an environment variable set during `axle setup`.
# On a real deployment, this is configured once and stored securely.
VAULT_PASSWORD = os.environ.get("AXLE_VAULT_PASSWORD", "axle-default-vault-pw")

def _get_vault():
    """Get a Vault instance using the server-side vault password."""
    return Vault(VAULT_PASSWORD)

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

    key = data["key"].strip()
    value = data["value"]

    if not key:
        return jsonify({"success": False, "error": "Key cannot be empty"}), 400

    try:
        vault = _get_vault()
        vault.set(key, value)
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
        if not success:
            return jsonify({"success": False, "error": f"Key '{key}' not found"}), 404
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
