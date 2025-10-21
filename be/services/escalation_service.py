"""
Enhanced escalation service for AI-first telecom customer support
Implements rule-based escalation with 4 categories: AI Performance, User Behavior, Topic Sensitivity, and Sentiment Signals
"""
from typing import Dict, Any, List, Optional
from models.chat_models import ChatSession, Escalation
from utils.db import db
import logging
import re
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

class EscalationService:
    def __init__(self):
        """Initialize enhanced escalation service for telecom support"""
        self.escalation_rules = {
            # AI Performance Category
            'confidence_threshold': 0.6,
            'repeated_fallback_threshold': 3,
            'low_retrieval_confidence': 0.4,
            
            # User Behavior Category  
            'message_count_threshold': 10,
            'repeated_query_threshold': 3,
            'session_duration_threshold': 1800,  # 30 minutes
            
            # Topic Sensitivity Category (Telecom-specific)
            'critical_telecom_topics': [
                'billing dispute', 'service outage', 'data breach', 'privacy concern',
                'contract termination', 'plan cancellation', 'refund request',
                'legal action', 'regulatory complaint', 'fraud report',
                'account suspension', 'credit dispute', 'payment failure'
            ],
            
            # Sentiment Signals Category
            'frustration_keywords': [
                'angry', 'frustrated', 'annoyed', 'upset', 'mad', 'terrible', 
                'awful', 'horrible', 'useless', 'waste', 'disappointed',
                'furious', 'livid', 'irritated', 'bothered', 'fed up'
            ],
            'escalation_phrases': [
                'speak to manager', 'speak to supervisor', 'human agent',
                'real person', 'customer service', 'complaint department',
                'cancel my plan', 'switch provider', 'file complaint'
            ],
            'negative_intensity_words': [
                'extremely', 'completely', 'totally', 'absolutely', 'never',
                'always', 'worst', 'best', 'perfect', 'disaster'
            ]
        }
        
        # Telecom-specific escalation priorities
        self.escalation_priorities = {
            'critical': ['billing dispute', 'data breach', 'fraud report', 'legal action'],
            'high': ['service outage', 'plan cancellation', 'account suspension'],
            'medium': ['refund request', 'payment failure', 'contract termination'],
            'low': ['general complaint', 'technical issue', 'billing question']
        }
    
    def should_escalate(self, session_id: int, user_message: str, confidence: float, 
                      message_count: int = 0, session_duration: int = 0) -> Dict[str, Any]:
        """Enhanced escalation check using 4 categories from the image"""
        try:
            # Get session
            session = ChatSession.query.get(session_id)
            if not session:
                return {'should_escalate': False, 'reason': 'Session not found'}
            
            escalation_analysis = {
                'ai_performance': self._check_ai_performance(confidence, session_id),
                'user_behavior': self._check_user_behavior(user_message, message_count, session_duration, session_id),
                'topic_sensitivity': self._check_topic_sensitivity(user_message),
                'sentiment_signals': self._check_sentiment_signals(user_message)
            }
            
            # Determine if escalation is needed
            should_escalate = any(category['should_escalate'] for category in escalation_analysis.values())
            
            # Calculate priority based on escalation reasons
            priority = self._calculate_escalation_priority(escalation_analysis)
            
            return {
                'should_escalate': should_escalate,
                'priority': priority,
                'analysis': escalation_analysis,
                'confidence': confidence,
                'message_count': message_count,
                'session_duration': session_duration
            }
            
        except Exception as e:
            logger.error(f"Error checking escalation: {str(e)}")
            return {'should_escalate': False, 'error': str(e)}
    
    def _check_ai_performance(self, confidence: float, session_id: int) -> Dict[str, Any]:
        """Category 1: AI Performance - Low confidence and repeated fallbacks"""
        reasons = []
        should_escalate = False
        
        # Low retrieval confidence
        if confidence < self.escalation_rules['confidence_threshold']:
            reasons.append(f"Low confidence ({confidence:.2f} < {self.escalation_rules['confidence_threshold']})")
            should_escalate = True
        
        # Very low confidence (critical)
        if confidence < self.escalation_rules['low_retrieval_confidence']:
            reasons.append(f"Critical low confidence ({confidence:.2f} < {self.escalation_rules['low_retrieval_confidence']})")
            should_escalate = True
        
        # Check for repeated fallback responses (would need message history)
        # This is a placeholder for when message storage is implemented
        fallback_count = self._get_fallback_count(session_id)
        if fallback_count >= self.escalation_rules['repeated_fallback_threshold']:
            reasons.append(f"Repeated fallback responses ({fallback_count} times)")
            should_escalate = True
        
        return {
            'should_escalate': should_escalate,
            'reasons': reasons,
            'confidence': confidence,
            'fallback_count': fallback_count
        }
    
    def _check_user_behavior(self, user_message: str, message_count: int, 
                           session_duration: int, session_id: int) -> Dict[str, Any]:
        """Category 2: User Behavior - Repeated queries, long threads, frustration patterns"""
        reasons = []
        should_escalate = False
        
        # Long conversation thread
        if message_count >= self.escalation_rules['message_count_threshold']:
            reasons.append(f"Long conversation ({message_count} messages)")
            should_escalate = True
        
        # Long session duration
        if session_duration >= self.escalation_rules['session_duration_threshold']:
            reasons.append(f"Extended session duration ({session_duration//60} minutes)")
            should_escalate = True
        
        # Repeated query patterns
        repeated_queries = self._detect_repeated_queries(user_message, session_id)
        if repeated_queries:
            reasons.append(f"Repeated query pattern detected")
            should_escalate = True
        
        # User explicitly asking for human help
        if any(phrase in user_message.lower() for phrase in self.escalation_rules['escalation_phrases']):
            reasons.append("User explicitly requested human assistance")
            should_escalate = True
        
        return {
            'should_escalate': should_escalate,
            'reasons': reasons,
            'message_count': message_count,
            'session_duration': session_duration,
            'repeated_queries': repeated_queries
        }
    
    def _check_topic_sensitivity(self, user_message: str) -> Dict[str, Any]:
        """Category 3: Topic Sensitivity - Critical telecom topics requiring human intervention"""
        reasons = []
        should_escalate = False
        priority = 'low'
        
        message_lower = user_message.lower()
        found_topics = []
        
        # Check for critical telecom topics
        for topic in self.escalation_rules['critical_telecom_topics']:
            if topic in message_lower:
                found_topics.append(topic)
                should_escalate = True
                
                # Determine priority
                if topic in self.escalation_priorities['critical']:
                    priority = 'critical'
                elif topic in self.escalation_priorities['high']:
                    priority = 'high'
                elif topic in self.escalation_priorities['medium']:
                    priority = 'medium'
        
        if found_topics:
            reasons.append(f"Critical telecom topic: {', '.join(found_topics)}")
        
        return {
            'should_escalate': should_escalate,
            'reasons': reasons,
            'found_topics': found_topics,
            'priority': priority
        }
    
    def _check_sentiment_signals(self, user_message: str) -> Dict[str, Any]:
        """Category 4: Sentiment Signals - Negative tone and emotional distress detection"""
        reasons = []
        should_escalate = False
        sentiment_score = 0
        
        message_lower = user_message.lower()
        
        # Check for frustration keywords
        frustration_found = [kw for kw in self.escalation_rules['frustration_keywords'] 
                           if kw in message_lower]
        if frustration_found:
            reasons.append(f"Frustration detected: {', '.join(frustration_found)}")
            should_escalate = True
            sentiment_score += len(frustration_found) * 2
        
        # Check for escalation phrases
        escalation_phrases_found = [phrase for phrase in self.escalation_rules['escalation_phrases'] 
                                  if phrase in message_lower]
        if escalation_phrases_found:
            reasons.append(f"Escalation request: {', '.join(escalation_phrases_found)}")
            should_escalate = True
            sentiment_score += len(escalation_phrases_found) * 3
        
        # Check for negative intensity words
        intensity_words_found = [word for word in self.escalation_rules['negative_intensity_words'] 
                               if word in message_lower]
        if intensity_words_found:
            reasons.append(f"High emotional intensity: {', '.join(intensity_words_found)}")
            sentiment_score += len(intensity_words_found)
        
        # Check for repeated negative words (basic pattern)
        negative_word_count = sum(1 for word in self.escalation_rules['frustration_keywords'] 
                                if message_lower.count(word) > 1)
        if negative_word_count > 0:
            reasons.append(f"Repeated negative language ({negative_word_count} instances)")
            should_escalate = True
        
        return {
            'should_escalate': should_escalate,
            'reasons': reasons,
            'sentiment_score': sentiment_score,
            'frustration_keywords': frustration_found,
            'escalation_phrases': escalation_phrases_found,
            'intensity_words': intensity_words_found
        }
    
    def create_escalation(self, session_id: int, reason: str, priority: str = 'medium', 
                         escalation_analysis: Dict[str, Any] = None) -> Escalation:
        """Create escalation record with priority and analysis"""
        try:
            escalation = Escalation(
                session_id=session_id,
                reason=reason,
                status='pending',
                priority=priority
            )
            
            # Add escalation analysis if provided
            if escalation_analysis:
                escalation.analysis_data = escalation_analysis
            
            db.session.add(escalation)
            db.session.commit()
            
            # Update session status
            session = ChatSession.query.get(session_id)
            if session:
                session.status = 'escalated'
                db.session.commit()
            
            logger.info(f"Created {priority} priority escalation for session {session_id}: {reason}")
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
    
    def _calculate_escalation_priority(self, escalation_analysis: Dict[str, Any]) -> str:
        """Calculate escalation priority based on analysis results"""
        # Critical priority triggers
        if escalation_analysis['topic_sensitivity']['should_escalate']:
            return escalation_analysis['topic_sensitivity']['priority']
        
        # High priority for multiple triggers
        trigger_count = sum(1 for category in escalation_analysis.values() 
                          if category['should_escalate'])
        
        if trigger_count >= 3:
            return 'high'
        elif trigger_count >= 2:
            return 'medium'
        elif trigger_count >= 1:
            return 'low'
        
        return 'low'
    
    def _get_fallback_count(self, session_id: int) -> int:
        """Get count of fallback responses for session (placeholder)"""
        # This would need message history storage to implement properly
        # For now, return 0 as placeholder
        return 0
    
    def _detect_repeated_queries(self, user_message: str, session_id: int) -> bool:
        """Detect if user is repeating similar queries (placeholder)"""
        # This would need message history to detect patterns
        # For now, check for obvious repetition in current message
        words = user_message.lower().split()
        if len(words) > 5:  # Only check longer messages
            word_freq = defaultdict(int)
            for word in words:
                if len(word) > 3:  # Only count meaningful words
                    word_freq[word] += 1
            
            # Check for repeated words
            repeated_words = [word for word, count in word_freq.items() if count > 2]
            return len(repeated_words) > 0
        
        return False
    
    def get_escalation_summary(self, session_id: int) -> Dict[str, Any]:
        """Enhanced escalation summary for telecom support"""
        try:
            session = ChatSession.query.get(session_id)
            if not session:
                return {}
            
            # Get user info
            from models.user_models import User
            user = User.query.filter_by(user_id=session.user_id).first()
            
            # Get escalation details
            escalation = Escalation.query.filter_by(session_id=session_id).first()
            
            return {
                'session_id': session_id,
                'room_id': session.room_id,
                'user_info': user.to_dict() if user else {},
                'escalation_reason': escalation.reason if escalation else 'Multiple triggers detected',
                'priority': getattr(escalation, 'priority', 'medium') if escalation else 'medium',
                'created_at': escalation.created_at if escalation else datetime.now(),
                'status': escalation.status if escalation else 'pending'
            }
            
        except Exception as e:
            logger.error(f"Error getting escalation summary: {str(e)}")
            return {}
    
    def get_escalation_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get escalation analytics for optimization"""
        try:
            from datetime import datetime, timedelta
            
            start_date = datetime.now() - timedelta(days=days)
            escalations = Escalation.query.filter(Escalation.created_at >= start_date).all()
            
            # Analytics by category
            category_stats = defaultdict(int)
            priority_stats = defaultdict(int)
            topic_stats = defaultdict(int)
            
            for escalation in escalations:
                # Parse escalation reason for categorization
                reason = escalation.reason.lower()
                
                # Categorize by trigger type
                if 'confidence' in reason:
                    category_stats['ai_performance'] += 1
                elif 'conversation' in reason or 'session' in reason:
                    category_stats['user_behavior'] += 1
                elif 'topic' in reason or 'billing' in reason or 'service' in reason:
                    category_stats['topic_sensitivity'] += 1
                elif 'frustration' in reason or 'angry' in reason:
                    category_stats['sentiment_signals'] += 1
                
                # Priority distribution
                priority = getattr(escalation, 'priority', 'medium')
                priority_stats[priority] += 1
                
                # Topic analysis
                for topic in self.escalation_rules['critical_telecom_topics']:
                    if topic in reason:
                        topic_stats[topic] += 1
            
            return {
                'total_escalations': len(escalations),
                'category_breakdown': dict(category_stats),
                'priority_breakdown': dict(priority_stats),
                'top_topics': dict(sorted(topic_stats.items(), key=lambda x: x[1], reverse=True)[:10]),
                'escalation_rate': len(escalations) / max(1, len(escalations)) * 100,  # Placeholder calculation
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"Error getting escalation analytics: {str(e)}")
            return {}
    
    def get_automation_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """Get suggestions for optimizing the 90% automation goal"""
        try:
            analytics = self.get_escalation_analytics(30)  # Last 30 days
            
            suggestions = []
            
            # AI Performance optimization
            ai_performance_escalations = analytics.get('category_breakdown', {}).get('ai_performance', 0)
            if ai_performance_escalations > 0:
                suggestions.append({
                    'category': 'AI Performance',
                    'issue': f'{ai_performance_escalations} escalations due to low confidence',
                    'suggestion': 'Improve RAG system confidence scoring and add more training data',
                    'impact': 'High - Directly affects automation rate'
                })
            
            # Topic Sensitivity optimization
            topic_escalations = analytics.get('category_breakdown', {}).get('topic_sensitivity', 0)
            if topic_escalations > 0:
                suggestions.append({
                    'category': 'Topic Sensitivity',
                    'issue': f'{topic_escalations} escalations for sensitive topics',
                    'suggestion': 'Create specialized AI workflows for common sensitive topics',
                    'impact': 'Medium - Some topics may always need human intervention'
                })
            
            # Sentiment optimization
            sentiment_escalations = analytics.get('category_breakdown', {}).get('sentiment_signals', 0)
            if sentiment_escalations > 0:
                suggestions.append({
                    'category': 'Sentiment Signals',
                    'issue': f'{sentiment_escalations} escalations due to negative sentiment',
                    'suggestion': 'Implement empathy training for AI responses and proactive de-escalation',
                    'impact': 'High - Can prevent many escalations'
                })
            
            # User Behavior optimization
            behavior_escalations = analytics.get('category_breakdown', {}).get('user_behavior', 0)
            if behavior_escalations > 0:
                suggestions.append({
                    'category': 'User Behavior',
                    'issue': f'{behavior_escalations} escalations due to user behavior patterns',
                    'suggestion': 'Improve conversation flow and add better context understanding',
                    'impact': 'Medium - Focus on reducing repeated queries'
                })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting optimization suggestions: {str(e)}")
            return []

# Global escalation service instance
escalation_service = EscalationService()
