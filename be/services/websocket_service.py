"""
WebSocket service for real-time chat functionality
"""
from flask import request
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
        
        # Setup agent handlers
        self._setup_agent_handlers()
        
        @self.socketio.on('connect')
        def handle_connect():
            logger.info(f'Client connected: {request.sid}')
            emit('connected', {'message': 'Connected to chat server'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            logger.info(f'Client disconnected: {request.sid}')
        
        @self.socketio.on('error')
        def handle_error(error):
            logger.error(f'Socket error: {error}')
            emit('error', {'message': 'Server error occurred'})
        
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
                
                # Special handling for agents room
                if room_id == 'agents' and user_type == 'agent':
                    # Send existing pending escalations to the agent
                    self._send_existing_escalations()
                    return
                
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
                if user_type == 'user' and session.status == 'active' and not session.agent_id:
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
                    'reasons': escalation_check.get('reasons', ['Multiple triggers detected'])
                }, room=room_id)
                
                self.socketio.emit('escalation', {
                    'session_id': session.id,
                    'reasons': escalation_check.get('reasons', ['Multiple triggers detected'])
                }, room=room_id)
                
                # Emit escalation_pending for agent dashboard
                self.socketio.emit('escalation_pending', {
                    'roomId': session.room_id,
                    'sessionId': session.id,
                    'userName': session.user_id,
                    'status': 'pending',
                    'priority': escalation_check.get('priority', 'medium'),
                    'reason': '; '.join(escalation_check.get('reasons', ['Multiple triggers detected'])),
                    'createdAt': datetime.utcnow().isoformat(),
                    'escalationId': escalation.id,
                    'uniqueKey': f'escalation_{escalation.id}'
                }, room='agents')
                
                # Also emit to the specific room for user notification
                self.socketio.emit('escalation_triggered', {
                    'session_id': session.id,
                    'room_id': session.room_id,
                    'reasons': escalation_check.get('reasons', ['Multiple triggers detected']),
                    'priority': escalation_check.get('priority', 'medium')
                }, room=room_id)
                
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
            
            # Extract reasons from escalation analysis
            reasons = []
            if 'analysis' in escalation_info:
                analysis = escalation_info['analysis']
                for category, data in analysis.items():
                    if isinstance(data, dict) and 'reasons' in data:
                        reasons.extend(data['reasons'])
            
            # Fallback to basic reason if no detailed reasons found
            if not reasons and 'reason' in escalation_info:
                reasons = [escalation_info['reason']]
            
            # Emit escalation_alert for backward compatibility
            self.socketio.emit('escalation_alert', {
                'session_id': session.id,
                'room_id': session.room_id,
                'summary': summary,
                'reasons': reasons
            }, room='agents')
            
            # Emit escalation_pending for agent dashboard
            self.socketio.emit('escalation_pending', {
                'session_id': session.id,
                'room_id': session.room_id,
                'summary': summary,
                'reasons': reasons
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
    
    def _send_existing_escalations(self):
        """Send existing pending escalations to connected agents"""
        try:
            from models.chat_models import Escalation
            from routes.admin_routes import get_escalations
            
            # Get pending escalations
            escalations = Escalation.query.filter_by(status='pending').order_by(Escalation.created_at.desc()).limit(50).all()
            
            for escalation in escalations:
                session = ChatSession.query.get(escalation.session_id)
                if session:
                    emit('escalation_pending', {
                        'roomId': session.room_id,
                        'sessionId': session.id,
                        'userName': session.user_id,
                        'status': escalation.status,
                        'priority': escalation.priority,
                        'reason': escalation.reason,
                        'createdAt': escalation.created_at.isoformat(),
                        'escalationId': escalation.id,
                        'uniqueKey': f'escalation_{escalation.id}'
                    })
            
            logger.info(f"Sent {len(escalations)} existing escalations to agent")
            
        except Exception as e:
            logger.error(f"Error sending existing escalations: {str(e)}")
    
    def _setup_agent_handlers(self):
        """Setup agent-specific WebSocket handlers"""
        from flask_socketio import emit, join_room, leave_room
        from models.chat_models import ChatSession
        from utils.db import db
        from datetime import datetime
        import logging
        
        logger = logging.getLogger(__name__)
        
        @self.socketio.on('agent_join_room')
        def handle_agent_join_room(data):
            """Handle agent joining a chat room"""
            try:
                room_id = data.get('roomId')
                agent_id = data.get('agentId', 'agent_001')
                
                logger.info(f"Agent {agent_id} attempting to join room {room_id}")
                
                if not room_id:
                    emit('error', {'message': 'Missing room ID'})
                    return
                
                # Join the room
                join_room(room_id)
                logger.info(f"Agent {agent_id} successfully joined room {room_id}")
                
                # Update session with agent
                session = ChatSession.query.filter_by(room_id=room_id).first()
                if session:
                    try:
                        session.agent_id = agent_id
                        session.status = 'escalated'
                        db.session.commit()
                        
                        # Assign agent to escalation
                        escalation_service.assign_agent(session.id, agent_id)
                        logger.info(f"Successfully assigned agent {agent_id} to session {session.id}")
                    except Exception as e:
                        logger.error(f"Error updating session {session.id}: {str(e)}")
                        db.session.rollback()
                        # Don't return here, continue with notifications
                else:
                    logger.warning(f"No session found for room {room_id}")
                
                # Always send notifications, even if session update failed
                try:
                    # Notify user that agent joined
                    self.socketio.emit('agent_joined', {
                        'roomId': room_id,
                        'agentId': agent_id,
                        'timestamp': datetime.utcnow().isoformat()
                    }, room=room_id)
                    
                    # Send a message to the user that agent has joined
                    self.socketio.emit('new_message', {
                        'role': 'system',
                        'content': f'Agent {agent_id} has joined the conversation and will assist you shortly.',
                        'timestamp': datetime.utcnow().isoformat(),
                        'session_id': session.id if session else None
                    }, room=room_id)
                    
                    logger.info(f"Agent {agent_id} joined room {room_id}")
                except Exception as e:
                    logger.error(f"Error sending notifications: {str(e)}")
                
            except Exception as e:
                logger.error(f"Error handling agent join room: {str(e)}")
                emit('error', {'message': 'Error joining room'})
        
        @self.socketio.on('agent_leave_room')
        def handle_agent_leave_room(data):
            """Handle agent leaving a chat room"""
            try:
                room_id = data.get('roomId')
                agent_id = data.get('agentId', 'agent_001')
                
                if not room_id:
                    emit('error', {'message': 'Missing room ID'})
                    return
                
                # Leave the room
                leave_room(room_id)
                
                # Notify user that agent left
                emit('agent_left', {
                    'roomId': room_id,
                    'agentId': agent_id,
                    'timestamp': datetime.utcnow().isoformat()
                }, room=room_id)
                
                logger.info(f"Agent {agent_id} left room {room_id}")
                
            except Exception as e:
                logger.error(f"Error handling agent leave room: {str(e)}")
                emit('error', {'message': 'Error leaving room'})
        
        @self.socketio.on('agent_message')
        def handle_agent_message(data):
            """Handle agent messages"""
            try:
                room_id = data.get('roomId')
                message = data.get('message')
                agent_id = data.get('agentId', 'agent_001')
                
                if not room_id or not message:
                    emit('error', {'message': 'Missing room ID or message'})
                    return
                
                # Send message to user
                emit('new_message', {
                    'role': 'agent',
                    'content': message,
                    'timestamp': datetime.utcnow().isoformat(),
                    'agent_id': agent_id
                }, room=room_id)
                
                logger.info(f"Agent {agent_id} sent message in room {room_id}")
                
            except Exception as e:
                logger.error(f"Error handling agent message: {str(e)}")
                emit('error', {'message': 'Error sending message'})
        
        @self.socketio.on('get_escalations')
        def handle_get_escalations():
            """Handle request for escalations list"""
            try:
                # This will be handled by the API endpoint
                # Just acknowledge the request
                emit('escalations_requested', {'status': 'success'})
                
            except Exception as e:
                logger.error(f"Error handling get escalations: {str(e)}")
                emit('error', {'message': 'Error getting escalations'})
