import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

# Initialize extensions
socketio = SocketIO(cors_allowed_origins="*")
logger = logging.getLogger("axle.web")

def create_app(test_config=None):
    """Create and configure the Flask application. (T-121)"""
    app = Flask(__name__, instance_relative_config=True)
    
    # Configure CORS to allow dashboard frontend to connect
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", "dev-axle-secret"),
        # Other default configs might go here
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    # Health check route
    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "version": "0.1.0"})

    # Initialize extensions with app
    socketio.init_app(app)
    
    # Register Socket Events
    from .websocket import register_socket_events
    register_socket_events(socketio)

    # Register Blueprints
    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from .routes.deploy import bp as deploy_bp
    app.register_blueprint(deploy_bp)
    
    from .routes.secrets import bp as secrets_bp
    app.register_blueprint(secrets_bp)
    
    from .routes.projects import bp as projects_bp
    app.register_blueprint(projects_bp)
    
    from .routes.monitor import bp as monitor_bp
    app.register_blueprint(monitor_bp)
    
    from .routes.chatbot import bp as chatbot_bp
    app.register_blueprint(chatbot_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    socketio.run(app, host="0.0.0.0", port=4000, allow_unsafe_werkzeug=True)
