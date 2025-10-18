"""
API routes for the chatbot system
"""
from .chat_routes import chat_bp
from .admin_routes import admin_bp

__all__ = ['chat_bp', 'admin_bp']
