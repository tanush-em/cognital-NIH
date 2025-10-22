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


class ChatMessage(db.Model):
    """Individual chat message model"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # user, ai, agent, system
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    message_type = db.Column(db.String(20), default='text')  # text, system, escalation
    message_metadata = db.Column(db.JSON, nullable=True)  # Additional message metadata
    
    # Relationships
    session = db.relationship('ChatSession', backref='messages', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'message_type': self.message_type,
            'metadata': self.message_metadata
        }


class Escalation(db.Model):
    """Escalation tracking model"""
    __tablename__ = 'escalations'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    reason = db.Column(db.String(200), nullable=False)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    analysis_data = db.Column(db.JSON, nullable=True)  # Store escalation analysis
    assigned_agent_id = db.Column(db.String(100), nullable=True)  # Agent assignment tracking
    triggered_at = db.Column(db.DateTime, default=datetime.utcnow)
    handled_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, handled, resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'reason': self.reason,
            'priority': self.priority,
            'analysis_data': self.analysis_data,
            'assigned_agent_id': self.assigned_agent_id,
            'triggered_at': self.triggered_at.isoformat(),
            'handled_at': self.handled_at.isoformat() if self.handled_at else None,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
