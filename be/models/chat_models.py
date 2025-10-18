"""
Chat-related database models
"""
from datetime import datetime
from utils.db import db

class ChatSession(db.Model):
    """Chat session model"""
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.String(100), nullable=False)
    agent_id = db.Column(db.String(100), nullable=True)
    room_id = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, escalated, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    escalations = db.relationship('Escalation', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'agent_id': self.agent_id,
            'room_id': self.room_id,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Escalation(db.Model):
    """Escalation tracking model"""
    __tablename__ = 'escalations'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    reason = db.Column(db.String(200), nullable=False)
    triggered_at = db.Column(db.DateTime, default=datetime.utcnow)
    handled_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, handled, resolved
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'reason': self.reason,
            'triggered_at': self.triggered_at.isoformat(),
            'handled_at': self.handled_at.isoformat() if self.handled_at else None,
            'status': self.status
        }
