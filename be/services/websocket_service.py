"""
WebSocket service for real-time chat functionality
"""
from flask_socketio import emit, join_room, leave_room
from models.chat_models import ChatSession
from services.rag_service import rag_service
from services.llm_service import llm_service
from services.escalation_service import escalation_service
from utils.db import db
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketService:
    def __init__(self, socketio):
        self.socketio = socketio
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup Socket.IO event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            logger.info('Client connected')
            emit('connected', {'message': 'Connected to chat server'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            logger.info('Client disconnected')
        
        @self.socketio.on('join_room')
        def handle_join_room(data):
            """Handle user joining a chat room"""
            try:
                room_id = data.get('room_id')
                user_type = data.get('user_type', 'user')  # user or agent
                user_id = data.get('user_id')
                
                if not room_id:
                    emit('error', {'message': 'Room ID is required'})
                    return
                
                # Join the room
                join_room(room_id)
                
                # Get or create session
                session = self._get_or_create_session(room_id, user_id, user_type)
                
                if session:
                    emit('joined_room', {
                        'room_id': room_id,
                        'session_id': session.id,
                        'status': session.status
                    })
                    
                else:
                    emit('error', {'message': 'Failed to create session'})
                    
            except Exception as e:
                logger.error(f"Error joining room: {str(e)}")
                emit('error', {'message': 'Failed to join room'})
        
        @self.socketio.on('leave_room')
        def handle_leave_room(data):
            """Handle user leaving a chat room"""
            try:
                room_id = data.get('room_id')
                if room_id:
                    leave_room(room_id)
                    emit('left_room', {'room_id': room_id})
            except Exception as e:
                logger.error(f"Error leaving room: {str(e)}")
        
        @self.socketio.on('close_session')
        def handle_close_session(data):
            """Handle closing a chat session"""
            try:
                room_id = data.get('roomId')
                agent_id = data.get('agentId')
                reason = data.get('reason', 'Session closed by agent')
                
                if room_id:
                    # Update session status
                    session = ChatSession.query.filter_by(room_id=room_id).first()
                    if session:
                        session.status = 'closed'
                        db.session.commit()
                    
                    # Emit session_closed event
                    self.socketio.emit('session_closed', {
                        'room_id': room_id,
                        'agent_id': agent_id,
                        'reason': reason,
                        'timestamp': datetime.utcnow().isoformat()
                    }, room=room_id)
                    
            except Exception as e:
                logger.error(f"Error closing session: {str(e)}")
                emit('error', {'message': 'Failed to close session'})
        
        @self.socketio.on('send_message')
        def handle_send_message(data):
            """Handle incoming messages"""
            try:
                room_id = data.get('room_id')
                message = data.get('message')
                user_type = data.get('user_type', 'user')
                user_id = data.get('user_id')
                
                if not all([room_id, message, user_id]):
                    emit('error', {'message': 'Missing required fields'})
                    return
                
                # Get session
                session = ChatSession.query.filter_by(room_id=room_id).first()
                if not session:
                    emit('error', {'message': 'Session not found'})
                    return
                
                
                # Broadcast user message to room
                self.socketio.emit('new_message', {
                    'role': user_type,
                    'content': message,
                    'timestamp': datetime.utcnow().isoformat(),
                    'session_id': session.id
                }, room=room_id)
                
                # Also emit chat_message for agent dashboard compatibility
                if user_type == 'user':
                    self.socketio.emit('chat_message', {
                        'role': user_type,
                        'content': message,
                        'timestamp': datetime.utcnow().isoformat(),
                        'session_id': session.id
                    }, room=room_id)
                
                # Handle AI response or escalation
                if user_type == 'user' and session.status == 'active':
                    self._handle_user_message(session, message, room_id)
                elif user_type == 'agent':
                    self._handle_agent_message(session, message, room_id)
                
            except Exception as e:
                logger.error(f"Error handling message: {str(e)}")
                emit('error', {'message': 'Failed to process message'})
        
        @self.socketio.on('join_session')
        def handle_join_session(data):
            """Handle joining a session"""
            try:
                session_id = data.get('sessionId')
                if not session_id:
                    emit('error', {'message': 'Session ID required'})
                    return
                
                # Get or create session
                session = ChatSession.query.filter_by(session_id=session_id).first()
                if not session:
                    # Create new session
                    session = ChatSession(
                        session_id=session_id,
                        user_id='user_' + session_id.split('_')[-1],  # Extract user ID from session
                        room_id=f'room_{session_id}',
                        status='active'
                    )
                    db.session.add(session)
                    db.session.commit()
                    logger.info(f"Created new session: {session_id}")
                
                # Join the room
                join_room(session.room_id)
                
                emit('joined_session', {
                    'session_id': session.session_id,
                    'room_id': session.room_id,
                    'status': session.status
                })
                
            except Exception as e:
                logger.error(f"Error joining session: {str(e)}")
                emit('error', {'message': 'Failed to join session'})
        
        @self.socketio.on('user_message')
        def handle_user_message(data):
            """Handle user messages directly"""
            try:
                session_id = data.get('sessionId')
                message = data.get('message')
                message_type = data.get('messageType', 'user')
                timestamp = data.get('timestamp')
                
                if not all([session_id, message]):
                    emit('error', {'message': 'Missing required fields'})
                    return
                
                # Get session by session_id (string) not id (integer)
                session = ChatSession.query.filter_by(session_id=session_id).first()
                if not session:
                    emit('error', {'message': 'Session not found'})
                    return
                
                # Broadcast user message to room
                self.socketio.emit('new_message', {
                    'role': 'user',
                    'content': message,
                    'timestamp': datetime.utcnow().isoformat(),
                    'session_id': session.id
                }, room=session.room_id)
                
                # Handle user message
                self._handle_user_message(session, message, session.room_id)
                    
            except Exception as e:
                logger.error(f"Error handling user message: {str(e)}")
                emit('error', {'message': 'Failed to process message'})
    
    def _get_or_create_session(self, room_id, user_id, user_type):
        """Get existing session or create new one"""
        try:
            session = ChatSession.query.filter_by(room_id=room_id).first()
            
            if not session:
                # Create new session
                session = ChatSession(
                    session_id=room_id,
                    user_id=user_id,
                    room_id=room_id,
                    status='active'
                )
                db.session.add(session)
                db.session.commit()
            elif user_type == 'agent':
                # Agent joining existing session
                session.agent_id = user_id
                session.status = 'escalated'
                db.session.commit()
            
            return session
            
        except Exception as e:
            logger.error(f"Error getting/creating session: {str(e)}")
            db.session.rollback()
            return None
    
    
    def _handle_user_message(self, session, message, room_id):
        """Handle user message - either respond with AI or escalate"""
        try:
            # Enable escalation service with proper error handling
            try:
                escalation_check = escalation_service.should_escalate(
                    session.id, 
                    message, 
                    confidence=0.8,  # Default confidence
                    message_count=1,  # This would need to be calculated from session history
                    session_duration=0  # This would need to be calculated from session start time
                )
            except Exception as e:
                logger.error(f"Error in escalation check: {str(e)}")
                # Fallback to no escalation if service fails
                escalation_check = {'should_escalate': False, 'reasons': []}
            
            if escalation_check['should_escalate']:
                # Create escalation with priority and analysis
                escalation = escalation_service.create_escalation(
                    session.id, 
                    '; '.join(escalation_check.get('reasons', ['Multiple triggers detected'])),
                    priority=escalation_check.get('priority', 'medium'),
                    escalation_analysis=escalation_check.get('analysis', {})
                )
                
                # Notify agents
                self._notify_agents_escalation(session, escalation_check)
                
                # Send escalation message to user
                escalation_msg = "I understand you need additional help. I'm connecting you with a human agent who will be with you shortly."
                
                self.socketio.emit('new_message', {
                    'role': 'ai',
                    'content': escalation_msg,
                    'timestamp': datetime.utcnow().isoformat(),
                    'session_id': session.id
                }, room=room_id)
                
                # Emit escalation events for both user chatbot and agent dashboard
                self.socketio.emit('escalation_triggered', {
                    'session_id': session.id,
                    'reasons': escalation_check['reasons']
                }, room=room_id)
                
                self.socketio.emit('escalation', {
                    'session_id': session.id,
                    'reasons': escalation_check['reasons']
                }, room=room_id)
                
                # Emit escalation_pending for agent dashboard
                self.socketio.emit('escalation_pending', {
                    'session_id': session.id,
                    'reasons': escalation_check['reasons']
                }, room='agents')
                
            else:
                # Generate AI response
                self._generate_ai_response(session, message, room_id)
                
        except Exception as e:
            logger.error(f"Error handling user message: {str(e)}")
            # Send error message to user
            self.socketio.emit('new_message', {
                'role': 'ai',
                'content': "I apologize, but I'm having trouble processing your request. Please try again.",
                'timestamp': datetime.utcnow().isoformat(),
                'session_id': session.id
            }, room=room_id)
    
    def _handle_agent_message(self, session, message, room_id):
        """Handle agent message"""
        try:
            # Agent messages are already saved in the main handler
            # Just broadcast to room
            pass
        except Exception as e:
            logger.error(f"Error handling agent message: {str(e)}")
    
    def _generate_ai_response(self, session, user_message, room_id):
        """Generate AI response using RAG and LLM"""
        try:
            # Emit typing indicator
            self.socketio.emit('ai_typing', {'typing': True}, room=room_id)
            
            # Get relevant context
            context = rag_service.get_context_for_query(user_message)
            
            
            # Generate response
            response = llm_service.generate_response(
                user_message=user_message,
                context=context
            )
            
            # Calculate confidence
            confidence = rag_service.calculate_confidence(user_message, response['response'])
            
            
            # Broadcast AI response
            logger.info(f"Emitting AI response to room {room_id}: {response['response'][:100]}...")
            self.socketio.emit('new_message', {
                'role': 'ai',
                'content': response['response'],
                'timestamp': datetime.utcnow().isoformat(),
                'session_id': session.id,
                'confidence': confidence
            }, room=room_id)
            
            # Emit typing complete
            self.socketio.emit('ai_typing', {'typing': False}, room=room_id)
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            # Send error message
            error_msg = "I apologize, but I'm having trouble processing your request. Please try again."
            self.socketio.emit('new_message', {
                'role': 'ai',
                'content': error_msg,
                'timestamp': datetime.utcnow().isoformat(),
                'session_id': session.id
            }, room=room_id)
    
    def _notify_agents_escalation(self, session, escalation_info):
        """Notify available agents about escalation"""
        try:
            # Get escalation summary
            summary = escalation_service.get_escalation_summary(session.id)
            
            # Emit escalation_alert for backward compatibility
            self.socketio.emit('escalation_alert', {
                'session_id': session.id,
                'room_id': session.room_id,
                'summary': summary,
                'reasons': escalation_info['reasons']
            }, room='agents')
            
            # Emit escalation_pending for agent dashboard
            self.socketio.emit('escalation_pending', {
                'session_id': session.id,
                'room_id': session.room_id,
                'summary': summary,
                'reasons': escalation_info['reasons']
            }, room='agents')
            
        except Exception as e:
            logger.error(f"Error notifying agents: {str(e)}")
    
    def join_agents_room(self, agent_id):
        """Agent joins the agents room to receive escalation alerts"""
        try:
            join_room('agents')
            return True
        except Exception as e:
            logger.error(f"Error joining agents room: {str(e)}")
            return False
