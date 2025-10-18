"""
Admin API routes for document ingestion and management
"""
from flask import Blueprint, request, jsonify
from services.rag_service import rag_service
from models.user_models import User, Agent
from utils.db import db
import logging

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__, url_prefix='/api')

@admin_bp.route('/ingest', methods=['POST'])
def ingest_documents():
    """Upload documents to ChromaDB knowledge base"""
    try:
        data = request.get_json()
        if not data or 'documents' not in data:
            return jsonify({'error': 'Documents are required'}), 400
        
        documents = data['documents']
        
        # Validate document format
        for doc in documents:
            if 'content' not in doc:
                return jsonify({'error': 'Each document must have content'}), 400
        
        # Add documents to RAG service
        success = rag_service.add_documents(documents)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Successfully ingested {len(documents)} documents',
                'count': len(documents)
            })
        else:
            return jsonify({'error': 'Failed to ingest documents'}), 500
            
    except Exception as e:
        logger.error(f"Error ingesting documents: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/users', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()
        required_fields = ['user_id', 'name']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(user_id=data['user_id']).first()
        if existing_user:
            return jsonify({'error': 'User already exists'}), 400
        
        user = User(
            user_id=data['user_id'],
            name=data['name'],
            email=data.get('email'),
            phone=data.get('phone')
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/agents', methods=['POST'])
def create_agent():
    """Create a new agent"""
    try:
        data = request.get_json()
        required_fields = ['agent_id', 'name']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if agent already exists
        existing_agent = Agent.query.filter_by(agent_id=data['agent_id']).first()
        if existing_agent:
            return jsonify({'error': 'Agent already exists'}), 400
        
        agent = Agent(
            agent_id=data['agent_id'],
            name=data['name'],
            email=data.get('email'),
            is_available=data.get('is_available', True)
        )
        
        db.session.add(agent)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'agent': agent.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/agents/<agent_id>/availability', methods=['PUT'])
def update_agent_availability(agent_id):
    """Update agent availability"""
    try:
        data = request.get_json()
        if 'is_available' not in data:
            return jsonify({'error': 'is_available is required'}), 400
        
        agent = Agent.query.filter_by(agent_id=agent_id).first()
        if not agent:
            return jsonify({'error': 'Agent not found'}), 404
        
        agent.is_available = data['is_available']
        db.session.commit()
        
        return jsonify({
            'success': True,
            'agent': agent.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error updating agent availability: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'services': {
                'rag': 'operational',
                'llm': 'operational',
                'database': 'operational'
            }
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500
