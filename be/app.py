"""
Main Flask application for AI-powered telecom support chatbot
"""
import os
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database and models
from utils.db import db, init_db, get_db_uri
from models import *

# Import routes
from routes import chat_bp, admin_bp

# Import services
from services.websocket_service import WebSocketService

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = get_db_uri()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, origins="*")
    
    # Initialize Socket.IO
    socketio = SocketIO(
        app, 
        cors_allowed_origins="*",
        logger=True,
        engineio_logger=True
    )
    
    # Initialize WebSocket service
    websocket_service = WebSocketService(socketio)
    
    # Register blueprints
    app.register_blueprint(chat_bp)
    app.register_blueprint(admin_bp)
    
    # Initialize database
    with app.app_context():
        db.create_all()
        print("Database tables created successfully")
    
    # Routes
    @app.route('/')
    def index():
        return {
            'message': 'AI-powered Telecom Support Chatbot API',
            'version': '1.0.0',
            'endpoints': {
                'chat': '/api/ask, /api/escalate, /api/sessions',
                'admin': '/api/ingest, /api/users, /api/agents',
                'websocket': 'Connect to /socket.io/ for real-time chat'
            }
        }
    
    @app.route('/api/status')
    def status():
        return {
            'status': 'operational',
            'services': {
                'database': 'connected',
                'rag': 'ready',
                'llm': 'ready',
                'escalation': 'ready'
            }
        }
    
    return app, socketio

def main():
    """Main entry point"""
    app, socketio = create_app()
    
    # Run the application
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    
    print(f"Starting AI-powered Telecom Support Chatbot...")
    print(f"Debug mode: {debug}")
    print(f"Port: {port}")
    
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=debug,
        allow_unsafe_werkzeug=True
    )

if __name__ == '__main__':
    main()
