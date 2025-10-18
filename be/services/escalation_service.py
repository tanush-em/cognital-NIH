"""
Escalation service for rule-based escalation logic
"""
from typing import Dict, Any, List
from models.chat_models import ChatSession, Escalation
from utils.db import db
import logging

logger = logging.getLogger(__name__)

class EscalationService:
    def __init__(self):
        """Initialize escalation service"""
        self.escalation_rules = {
            'confidence_threshold': 0.6,
            'message_count_threshold': 10,
            'frustration_keywords': [
                'refund', 'cancel', 'angry', 'not working', 'frustrated',
                'annoyed', 'upset', 'mad', 'terrible', 'awful', 'horrible',
                'complaint', 'sue', 'legal', 'manager', 'supervisor'
            ],
            'sensitive_topics': [
                'billing dispute', 'service outage', 'data breach',
                'privacy concern', 'contract termination'
            ]
        }
    
    def should_escalate(self, session_id: int, user_message: str, confidence: float) -> Dict[str, Any]:
        """Check if conversation should be escalated"""
        try:
            # Get session
            session = ChatSession.query.get(session_id)
            if not session:
                return {'should_escalate': False, 'reason': 'Session not found'}
            
            # No message count tracking since we removed message storage
            message_count = 0
            
            # Check escalation rules
            escalation_reasons = []
            
            # Rule 1: Low confidence
            if confidence < self.escalation_rules['confidence_threshold']:
                escalation_reasons.append(f"Low confidence ({confidence:.2f} < {self.escalation_rules['confidence_threshold']})")
            
            # Rule 2: Message count disabled (no message storage)
            # if message_count >= self.escalation_rules['message_count_threshold']:
            #     escalation_reasons.append(f"Long conversation ({message_count} messages)")
            
            # Rule 3: Frustration keywords
            frustration_keywords_found = self._check_frustration_keywords(user_message)
            if frustration_keywords_found:
                escalation_reasons.append(f"Frustration detected: {', '.join(frustration_keywords_found)}")
            
            # Rule 4: Sensitive topics
            sensitive_topics_found = self._check_sensitive_topics(user_message)
            if sensitive_topics_found:
                escalation_reasons.append(f"Sensitive topic: {', '.join(sensitive_topics_found)}")
            
            should_escalate = len(escalation_reasons) > 0
            
            return {
                'should_escalate': should_escalate,
                'reasons': escalation_reasons,
                'message_count': message_count,
                'confidence': confidence
            }
            
        except Exception as e:
            logger.error(f"Error checking escalation: {str(e)}")
            return {'should_escalate': False, 'error': str(e)}
    
    def create_escalation(self, session_id: int, reason: str) -> Escalation:
        """Create escalation record"""
        try:
            escalation = Escalation(
                session_id=session_id,
                reason=reason,
                status='pending'
            )
            
            db.session.add(escalation)
            db.session.commit()
            
            # Update session status
            session = ChatSession.query.get(session_id)
            if session:
                session.status = 'escalated'
                db.session.commit()
            
            logger.info(f"Created escalation for session {session_id}: {reason}")
            return escalation
            
        except Exception as e:
            logger.error(f"Error creating escalation: {str(e)}")
            db.session.rollback()
            raise
    
    def get_available_agents(self) -> List[Dict[str, Any]]:
        """Get list of available agents"""
        try:
            from models.user_models import Agent
            agents = Agent.query.filter_by(is_available=True).all()
            return [agent.to_dict() for agent in agents]
        except Exception as e:
            logger.error(f"Error getting available agents: {str(e)}")
            return []
    
    def assign_agent(self, session_id: int, agent_id: str) -> bool:
        """Assign agent to escalated session"""
        try:
            session = ChatSession.query.get(session_id)
            if not session:
                return False
            
            session.agent_id = agent_id
            session.status = 'escalated'
            
            # Update escalation status
            escalation = Escalation.query.filter_by(session_id=session_id, status='pending').first()
            if escalation:
                escalation.status = 'handled'
                escalation.handled_at = db.func.now()
            
            db.session.commit()
            logger.info(f"Assigned agent {agent_id} to session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error assigning agent: {str(e)}")
            db.session.rollback()
            return False
    
    def _check_frustration_keywords(self, message: str) -> List[str]:
        """Check for frustration keywords in message"""
        message_lower = message.lower()
        found_keywords = [kw for kw in self.escalation_rules['frustration_keywords'] 
                         if kw in message_lower]
        return found_keywords
    
    def _check_sensitive_topics(self, message: str) -> List[str]:
        """Check for sensitive topics in message"""
        message_lower = message.lower()
        found_topics = [topic for topic in self.escalation_rules['sensitive_topics'] 
                       if topic in message_lower]
        return found_topics
    
    def get_escalation_summary(self, session_id: int) -> Dict[str, Any]:
        """Get summary for escalation notification"""
        try:
            session = ChatSession.query.get(session_id)
            if not session:
                return {}
            
            # No message history available (removed message storage)
            recent_messages = []
            
            # Get user info
            from models.user_models import User
            user = User.query.filter_by(user_id=session.user_id).first()
            
            return {
                'session_id': session_id,
                'room_id': session.room_id,
                'user_info': user.to_dict() if user else {},
                'recent_messages': [],
                'escalation_reason': 'Multiple escalation triggers detected'
            }
            
        except Exception as e:
            logger.error(f"Error getting escalation summary: {str(e)}")
            return {}

# Global escalation service instance
escalation_service = EscalationService()
