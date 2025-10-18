"""
Database utilities and configuration
"""
import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

db = SQLAlchemy()

def init_db(app: Flask):
    """Initialize database with Flask app"""
    db.init_app(app)
    
    with app.app_context():
        db.create_all()

def get_db_uri():
    """Get database URI from environment or use SQLite default"""
    if os.getenv('DATABASE_URL'):
        return os.getenv('DATABASE_URL')
    else:
        return 'sqlite:///chatbot.db'
