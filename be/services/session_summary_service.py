from typing import Dict, Any, List, Optional
from models.chat_models import ChatSession, ChatMessage, Escalation
from models.user_models import User
from services.llm_service import llm_service
from utils.db import db
import logging
from datetime import datetime, timedelta
import re
from collections import Counter

logger = logging.getLogger(__name__)

class SessionSummaryService:
    def __init__(self):
        self.issue_keywords = {
            'billing': ['bill', 'charge', 'payment', 'cost', 'price', 'fee', 'invoice', 'billing'],
            'technical': ['internet', 'wifi', 'connection', 'speed', 'router', 'modem', 'signal', 'network'],
            'phone': ['phone', 'calling', 'text', 'sms', 'voicemail', 'number', 'dial'],
            'service': ['service', 'outage', 'down', 'not working', 'broken', 'issue', 'problem'],
            'account': ['account', 'login', 'password', 'username', 'profile', 'settings'],
            'plan': ['plan', 'package', 'upgrade', 'downgrade', 'change', 'switch'],
            'support': ['help', 'support', 'assistance', 'customer service', 'agent']
        }
        
        self.sentiment_keywords = {
            'positive': ['good', 'great', 'excellent', 'happy', 'satisfied', 'working', 'fixed', 'resolved'],
            'negative': ['bad', 'terrible', 'awful', 'angry', 'frustrated', 'annoyed', 'upset', 'mad'],
            'neutral': ['okay', 'fine', 'normal', 'average', 'standard']
        }

    def generate_session_summary(self, session_id: int) -> Dict[str, Any]:
        try:
            session = ChatSession.query.get(session_id)
            if not session:
                return {'error': 'Session not found'}
            messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.timestamp.asc()).all()
            escalation = Escalation.query.filter_by(session_id=session_id, status='pending').first()
            user = User.query.filter_by(user_id=session.user_id).first()
            
            summary_data = {
                'session_id': session_id,
                'room_id': session.room_id,
                'user': self._extract_user_info(user, session),
                'session': self._extract_session_info(session, messages),
                'issues': self._identify_issues(messages),
                'sentiment': self._analyze_sentiment(messages),
                'escalationReason': escalation.reason if escalation else None,
                'summary': self._generate_ai_summary(messages, escalation),
                'keyPoints': self._extract_key_points(messages),
                'conversationFlow': self._analyze_conversation_flow(messages),
                'recommendedActions': self._suggest_actions(messages, escalation)
            }
            
            logger.info(f"Generated session summary for session {session_id}")
            return summary_data
            
        except Exception as e:
            logger.error(f"Error generating session summary: {str(e)}")
            return {'error': str(e)}

    def _extract_user_info(self, user: Optional[User], session: ChatSession) -> Dict[str, Any]:
        if user:
            return {
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'user_id': user.user_id
            }
        else:
            return {
                'name': 'Unknown Customer',
                'email': 'Not provided',
                'phone': 'Not provided',
                'user_id': session.user_id
            }

    def _extract_session_info(self, session: ChatSession, messages: List[ChatMessage]) -> Dict[str, Any]:
        if not messages:
            return {
                'startTime': session.created_at.isoformat(),
                'duration': '0 minutes',
                'messageCount': 0
            }
        
        start_time = messages[0].timestamp
        end_time = messages[-1].timestamp
        duration = end_time - start_time
        
        return {
            'startTime': start_time.isoformat(),
            'duration': f"{duration.total_seconds() // 60:.0f} minutes",
            'messageCount': len(messages),
            'lastActivity': end_time.isoformat()
        }

    def _identify_issues(self, messages: List[ChatMessage]) -> List[str]:
        issue_counts = Counter()
        all_text = ' '.join([msg.content.lower() for msg in messages if msg.role == 'user'])
        
        for category, keywords in self.issue_keywords.items():
            for keyword in keywords:
                if keyword in all_text:
                    issue_counts[category] += all_text.count(keyword)
        
        return [issue for issue, count in issue_counts.most_common(3)]

    def _analyze_sentiment(self, messages: List[ChatMessage]) -> str:
        """Analyze customer sentiment"""
        user_messages = [msg.content.lower() for msg in messages if msg.role == 'user']
        all_text = ' '.join(user_messages)
        
        sentiment_scores = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for sentiment, keywords in self.sentiment_keywords.items():
            for keyword in keywords:
                sentiment_scores[sentiment] += all_text.count(keyword)
        
        if sentiment_scores['negative'] > sentiment_scores['positive']:
            return 'negative'
        elif sentiment_scores['positive'] > sentiment_scores['negative']:
            return 'positive'
        else:
            return 'neutral'

    def _generate_ai_summary(self, messages: List[ChatMessage], escalation: Optional[Escalation]) -> Dict[str, str]:
        """Generate AI-powered conversation summary with structured parsing"""
        try:
            conversation_text = ""
            for msg in messages[-10:]:  # Last 10 messages for context
                role = "Customer" if msg.role == 'user' else "AI Assistant"
                conversation_text += f"{role}: {msg.content}\n"
            
            prompt = f"""
            Analyze this customer support conversation and provide a structured summary for a human agent.
            
            Conversation:
            {conversation_text}
            
            Escalation Reason: {escalation.reason if escalation else 'No escalation'}
            
            Please provide a structured response with these exact sections:
            
            **Main Issue:** [Brief description of the customer's primary concern]
            **What's Been Tried:** [List of solutions or steps already attempted]
            **Current Status:** [Current state of the conversation and issue]
            **What Customer Needs Help With:** [Specific assistance the customer requires]
            **Actionable Recommendation:** [Clear next steps for the human agent]
            
            Keep each section concise and actionable. Do not use emojis or special formatting.
            """
            
            response = llm_service.generate_response(
                user_message=prompt,
                context="You are an AI assistant helping human agents understand customer conversations. Provide structured, professional summaries."
            )
            
            structured_summary = self._parse_structured_summary(response['response'])
            return structured_summary
            
        except Exception as e:
            logger.error(f"Error generating AI summary: {str(e)}")
            return {
                'mainIssue': 'Unable to generate AI summary at this time.',
                'triedSolutions': 'Summary generation failed',
                'currentStatus': 'Unknown',
                'customerNeeds': 'Manual review required',
                'recommendation': 'Review conversation history manually'
            }

    def _parse_structured_summary(self, summary_text: str) -> Dict[str, str]:
        """Parse structured AI summary into components"""
        try:
            structured = {
                'mainIssue': '',
                'triedSolutions': '',
                'currentStatus': '',
                'customerNeeds': '',
                'recommendation': ''
            }
            
            sections = summary_text.split('**')
            
            for i, section in enumerate(sections):
                section = section.strip()
                
                if section.startswith('Main Issue:'):
                    structured['mainIssue'] = section.replace('Main Issue:', '').strip()
                elif section.startswith("What's Been Tried:"):
                    structured['triedSolutions'] = section.replace("What's Been Tried:", '').strip()
                elif section.startswith('Current Status:'):
                    structured['currentStatus'] = section.replace('Current Status:', '').strip()
                elif section.startswith('What Customer Needs Help With:'):
                    structured['customerNeeds'] = section.replace('What Customer Needs Help With:', '').strip()
                elif section.startswith('Actionable Recommendation:'):
                    structured['recommendation'] = section.replace('Actionable Recommendation:', '').strip()
            
            if not any(structured.values()):
                import re
                patterns = {
                    'mainIssue': r'1\.\s*\*\*Main Issue:\*\*\s*(.*?)(?=2\.|\*\*|$)',
                    'triedSolutions': r'2\.\s*\*\*What\'s Been Tried:\*\*\s*(.*?)(?=3\.|\*\*|$)',
                    'currentStatus': r'3\.\s*\*\*Current Status:\*\*\s*(.*?)(?=4\.|\*\*|$)',
                    'customerNeeds': r'4\.\s*\*\*What Customer Needs Help With:\*\*\s*(.*?)(?=\*\*|$)',
                    'recommendation': r'\*\*Actionable Recommendation:\*\*\s*(.*?)$'
                }
                
                for key, pattern in patterns.items():
                    match = re.search(pattern, summary_text, re.DOTALL | re.IGNORECASE)
                    if match:
                        structured[key] = match.group(1).strip()
            
            if not any(structured.values()):
                lines = summary_text.split('\n')
                current_section = None
                content_lines = []
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    if 'main issue' in line.lower():
                        if current_section and content_lines:
                            structured[current_section] = ' '.join(content_lines)
                        current_section = 'mainIssue'
                        content_lines = [line.replace('**Main Issue:**', '').strip()]
                    elif 'tried' in line.lower() and 'been' in line.lower():
                        if current_section and content_lines:
                            structured[current_section] = ' '.join(content_lines)
                        current_section = 'triedSolutions'
                        content_lines = [line.replace('**What\'s Been Tried:**', '').strip()]
                    elif 'current status' in line.lower():
                        if current_section and content_lines:
                            structured[current_section] = ' '.join(content_lines)
                        current_section = 'currentStatus'
                        content_lines = [line.replace('**Current Status:**', '').strip()]
                    elif 'needs help' in line.lower():
                        if current_section and content_lines:
                            structured[current_section] = ' '.join(content_lines)
                        current_section = 'customerNeeds'
                        content_lines = [line.replace('**What Customer Needs Help With:**', '').strip()]
                    elif 'recommendation' in line.lower():
                        if current_section and content_lines:
                            structured[current_section] = ' '.join(content_lines)
                        current_section = 'recommendation'
                        content_lines = [line.replace('**Actionable Recommendation:**', '').strip()]
                    else:
                        content_lines.append(line)
                
                if current_section and content_lines:
                    structured[current_section] = ' '.join(content_lines)
            
            if not any(structured.values()):
                structured = self._fallback_parsing(summary_text)
            
            return structured
            
        except Exception as e:
            logger.error(f"Error parsing structured summary: {str(e)}")
            return {
                'mainIssue': summary_text[:200] + '...' if len(summary_text) > 200 else summary_text,
                'triedSolutions': 'Unable to parse',
                'currentStatus': 'Unable to parse',
                'customerNeeds': 'Unable to parse',
                'recommendation': 'Manual review required'
            }

    def _fallback_parsing(self, text: str) -> Dict[str, str]:
        """Fallback parsing method for unstructured text"""
        lines = text.split('\n')
        structured = {
            'mainIssue': '',
            'triedSolutions': '',
            'currentStatus': '',
            'customerNeeds': '',
            'recommendation': ''
        }
        
        current_section = None
        content_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if 'main issue' in line.lower() or 'primary concern' in line.lower():
                if current_section and content_lines:
                    structured[current_section] = ' '.join(content_lines)
                current_section = 'mainIssue'
                content_lines = [line]
            elif 'tried' in line.lower() or 'attempted' in line.lower():
                if current_section and content_lines:
                    structured[current_section] = ' '.join(content_lines)
                current_section = 'triedSolutions'
                content_lines = [line]
            elif 'current status' in line.lower() or 'status' in line.lower():
                if current_section and content_lines:
                    structured[current_section] = ' '.join(content_lines)
                current_section = 'currentStatus'
                content_lines = [line]
            elif 'needs help' in line.lower() or 'requires' in line.lower():
                if current_section and content_lines:
                    structured[current_section] = ' '.join(content_lines)
                current_section = 'customerNeeds'
                content_lines = [line]
            elif 'recommendation' in line.lower() or 'action' in line.lower():
                if current_section and content_lines:
                    structured[current_section] = ' '.join(content_lines)
                current_section = 'recommendation'
                content_lines = [line]
            else:
                content_lines.append(line)
        
        if current_section and content_lines:
            structured[current_section] = ' '.join(content_lines)
        
        if not any(structured.values()):
            structured['mainIssue'] = text[:300] + '...' if len(text) > 300 else text
        
        return structured

    def _extract_key_points(self, messages: List[ChatMessage]) -> List[str]:
        """Extract key points from the conversation"""
        key_points = []
        user_messages = [msg.content for msg in messages if msg.role == 'user']
        
        for msg in user_messages:
            msg_lower = msg.lower()
            
            if any(word in msg_lower for word in ['billing', 'bill', 'charge', 'payment']):
                key_points.append("Customer has billing-related concerns")
            
            if any(word in msg_lower for word in ['internet', 'wifi', 'connection', 'speed']):
                key_points.append("Technical connectivity issues mentioned")
            
            if any(word in msg_lower for word in ['phone', 'calling', 'text']):
                key_points.append("Phone service issues reported")
            
            if any(word in msg_lower for word in ['frustrated', 'angry', 'upset', 'annoyed']):
                key_points.append("Customer expressing frustration")
            
            if any(word in msg_lower for word in ['manager', 'supervisor', 'human', 'agent']):
                key_points.append("Customer requested human assistance")
        
        return list(set(key_points))[:5]

    def _analyze_conversation_flow(self, messages: List[ChatMessage]) -> Dict[str, Any]:
        """Analyze conversation flow and patterns"""
        if not messages:
            return {'pattern': 'No conversation', 'escalation_triggers': []}
        
        escalation_triggers = []
        user_message_count = len([msg for msg in messages if msg.role == 'user'])
        
        for msg in messages:
            if msg.role == 'user':
                msg_lower = msg.content.lower()
                if any(word in msg_lower for word in ['frustrated', 'angry', 'upset']):
                    escalation_triggers.append('Customer frustration detected')
                if any(word in msg_lower for word in ['manager', 'supervisor', 'human']):
                    escalation_triggers.append('Human assistance requested')
                if len(msg.content) > 100:  # Long messages might indicate complexity
                    escalation_triggers.append('Complex issue requiring detailed explanation')
        
        if user_message_count > 10:
            pattern = 'Extended conversation - multiple exchanges'
        elif user_message_count > 5:
            pattern = 'Moderate conversation - several exchanges'
        else:
            pattern = 'Brief conversation - few exchanges'
        
        return {
            'pattern': pattern,
            'escalation_triggers': list(set(escalation_triggers)),
            'total_exchanges': user_message_count
        }

    def _suggest_actions(self, messages: List[ChatMessage], escalation: Optional[Escalation]) -> List[str]:
        """Suggest recommended actions for the agent"""
        actions = []
        
        # Base actions
        actions.append("Review the conversation history above")
        actions.append("Acknowledge the customer's concerns")
        
        user_messages = ' '.join([msg.content.lower() for msg in messages if msg.role == 'user'])
        
        if any(word in user_messages for word in ['billing', 'bill', 'charge', 'payment']):
            actions.append("Check customer's billing history and recent charges")
            actions.append("Explain any billing discrepancies clearly")
        
        if any(word in user_messages for word in ['internet', 'wifi', 'connection', 'speed']):
            actions.append("Run diagnostic tests on customer's connection")
            actions.append("Check for known service outages in their area")
        
        if any(word in user_messages for word in ['phone', 'calling', 'text']):
            actions.append("Verify phone service settings and configuration")
            actions.append("Test calling functionality if possible")
        
        if escalation and 'frustration' in escalation.reason.lower():
            actions.append("Use empathetic communication approach")
            actions.append("Focus on resolving the core issue quickly")
        
        if escalation:
            actions.append(f"Address the escalation reason: {escalation.reason}")
            actions.append("Provide personalized solution")
        
        return actions[:6]  # Limit to 6 actions

    def get_session_summary_cached(self, session_id: int) -> Dict[str, Any]:
        """Get session summary with caching (for future optimization)"""
        return self.generate_session_summary(session_id)

session_summary_service = SessionSummaryService()
