from flask_socketio import emit
import logging

logger = logging.getLogger("axle.web.socket")

def register_socket_events(socketio):
    """T-128: Register WebSocket events for real-time communication."""
    
    @socketio.on('connect')
    def handle_connect():
        # Ideally check auth token from headers or query string here 
        # before allowing the connection
        logger.info("Client connected to Socket.IO")
        emit('server_message', {'data': 'Connected to AXLE Web API'})

    @socketio.on('disconnect')
    def handle_disconnect():
        logger.info("Client disconnected from Socket.IO")

    # To be used by TaskRunner or external log streams
    # e.g., socketio.emit('log_stream', {'line': '...'})
