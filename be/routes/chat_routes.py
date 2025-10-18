"""
Chat-related API routes
"""
from flask import Blueprint, request, jsonify
from flask_socketio import emit
from models.chat_models import ChatSession, Escalation
from models.user_models import User, Agent
from services.rag_service import rag_service
from services.llm_service import llm_service
from services.escalation_service import escalation_service
from utils.db import db
import uuid
import logging

logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__, url_prefix='/api')

@chat_bp.route('/ask', methods=['POST'])
def ask_ai():
    """Manually query the AI (for testing)"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message']
        
        # Get relevant context
        context = rag_service.get_context_for_query(user_message)
        
        # Generate response
        response = llm_service.generate_response(
            user_message=user_message,
            context=context
        )
        
        return jsonify({
            'response': response['response'],
            'confidence': response['confidence'],
            'context_used': bool(context)
        })
        
    except Exception as e:
        logger.error(f"Error in ask endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@chat_bp.route('/escalate', methods=['POST'])
def force_escalate():
    """Force escalation (manual test)"""
    try:
        data = request.get_json()
        if not data or 'session_id' not in data:
            return jsonify({'error': 'Session ID is required'}), 400
        
        session_id = data['session_id']
        reason = data.get('reason', 'Manual escalation')
        
        # Create escalation
        escalation = escalation_service.create_escalation(session_id, reason)
        
        # Get escalation summary
        summary = escalation_service.get_escalation_summary(session_id)
        
        return jsonify({
            'success': True,
            'escalation_id': escalation.id,
            'summary': summary
        })
        
    except Exception as e:
        logger.error(f"Error in escalate endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@chat_bp.route('/sessions/<int:session_id>', methods=['GET'])
def get_session(session_id):
    """Get session details"""
    try:
        session = ChatSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        return jsonify(session.to_dict())
        
    except Exception as e:
        logger.error(f"Error getting session: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@chat_bp.route('/sessions', methods=['POST'])
def create_session():
    """Create a new chat session"""
    try:
        data = request.get_json()
        if not data or 'user_id' not in data:
            return jsonify({'error': 'User ID is required'}), 400
        
        user_id = data['user_id']
        
        # Create session
        session_id = str(uuid.uuid4())
        room_id = str(uuid.uuid4())
        
        session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            room_id=room_id,
            status='active'
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'session_id': session.id,
            'session_uuid': session_id,
            'room_id': room_id,
            'status': 'active'
        })
        
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@chat_bp.route('/agents/available', methods=['GET'])
def get_available_agents():
    """Get list of available agents"""
    try:
        agents = escalation_service.get_available_agents()
        return jsonify({'agents': agents})
        
    except Exception as e:
        logger.error(f"Error getting available agents: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@chat_bp.route('/sessions/<int:session_id>/assign', methods=['POST'])
def assign_agent():
    """Assign agent to session"""
    try:
        data = request.get_json()
        if not data or 'agent_id' not in data:
            return jsonify({'error': 'Agent ID is required'}), 400
        
        session_id = request.view_args['session_id']
        agent_id = data['agent_id']
        
        success = escalation_service.assign_agent(session_id, agent_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Agent assigned successfully'})
        else:
            return jsonify({'error': 'Failed to assign agent'}), 400
            
    except Exception as e:
        logger.error(f"Error assigning agent: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
