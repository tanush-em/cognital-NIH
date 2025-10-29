"""
Admin API routes for document ingestion and management
"""
from flask import Blueprint, request, jsonify
from services.rag_service import rag_service
from services.pdf_processor import pdf_processor
from models.user_models import User, Agent
from models.chat_models import ChatSession, Escalation
from services.escalation_service import escalation_service
from utils.db import db
import logging
import os
from werkzeug.utils import secure_filename

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

@admin_bp.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    """Upload PDF file to resources folder and process it"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Secure filename and save to resources folder
        filename = secure_filename(file.filename)
        file_path = os.path.join('resources', filename)
        
        # Ensure resources directory exists
        os.makedirs('resources', exist_ok=True)
        
        # Save file
        file.save(file_path)
        
        # Process the PDF
        result = pdf_processor.add_pdf_file(file_path)
        
        if result['success']:
            # Add to RAG service
            rag_document = {
                'content': result['content'],
                'title': result['filename'],
                'source': 'pdf_upload',
                'file_path': result['file_path'],
                'extraction_method': result['extraction_method']
            }
            
            rag_success = rag_service.add_documents([rag_document])
            
            if rag_success:
                return jsonify({
                    'success': True,
                    'message': f'Successfully uploaded and processed PDF: {filename}',
                    'filename': filename,
                    'extraction_method': result['extraction_method'],
                    'content_length': len(result['content'])
                })
            else:
                return jsonify({'error': 'Failed to add PDF to knowledge base'}), 500
        else:
            return jsonify({
                'error': f'Failed to process PDF: {result.get("error", "Unknown error")}'
            }), 500
            
    except Exception as e:
        logger.error(f"Error uploading PDF: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/reload-pdfs', methods=['POST'])
def reload_pdfs():
    """Reload all PDFs from resources folder"""
    try:
        success = rag_service.reload_pdfs()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Successfully reloaded all PDFs from resources folder'
            })
        else:
            return jsonify({'error': 'Failed to reload PDFs'}), 500
            
    except Exception as e:
        logger.error(f"Error reloading PDFs: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/pdfs', methods=['GET'])
def list_pdfs():
    """List all PDF files in resources folder"""
    try:
        pdf_files = pdf_processor.get_pdf_files()
        pdf_info = []
        
        for pdf_path in pdf_files:
            filename = os.path.basename(pdf_path)
            file_size = os.path.getsize(pdf_path)
            pdf_info.append({
                'filename': filename,
                'file_path': pdf_path,
                'size_bytes': file_size,
                'size_mb': round(file_size / (1024 * 1024), 2)
            })
        
        return jsonify({
            'success': True,
            'pdf_files': pdf_info,
            'count': len(pdf_info)
        })
        
    except Exception as e:
        logger.error(f"Error listing PDFs: {str(e)}")
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

@admin_bp.route('/escalations', methods=['GET'])
def get_escalations():
    """Get all escalations for agent dashboard"""
    try:
        status = request.args.get('status', 'pending')
        limit = request.args.get('limit', 50, type=int)
        
        query = Escalation.query
        if status != 'all':
            query = query.filter_by(status=status)
        
        escalations = query.order_by(Escalation.created_at.desc()).limit(limit).all()
        
        escalation_data = []
        for escalation in escalations:
            session = ChatSession.query.get(escalation.session_id)
            escalation_info = escalation.to_dict()
            escalation_info['session'] = session.to_dict() if session else None
            escalation_data.append(escalation_info)
        
        return jsonify({
            'success': True,
            'escalations': escalation_data,
            'count': len(escalation_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting escalations: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/escalations/<int:escalation_id>/assign', methods=['POST'])
def assign_escalation(escalation_id):
    """Assign escalation to an agent"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        
        if not agent_id:
            return jsonify({'error': 'agent_id is required'}), 400
        
        escalation = Escalation.query.get(escalation_id)
        if not escalation:
            return jsonify({'error': 'Escalation not found'}), 404
        
        # Update escalation
        escalation.assigned_agent_id = agent_id
        escalation.status = 'handled'
        db.session.commit()
        
        # Update session
        session = ChatSession.query.get(escalation.session_id)
        if session:
            session.agent_id = agent_id
            session.status = 'escalated'
            db.session.commit()
        
        return jsonify({
            'success': True,
            'escalation': escalation.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error assigning escalation: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/escalations/assign-by-session', methods=['POST'])
def assign_escalation_by_session():
    """Assign escalation by session ID"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        agent_id = data.get('agent_id')
        
        if not session_id or not agent_id:
            return jsonify({'error': 'session_id and agent_id are required'}), 400
        
        # Use escalation service to assign agent
        success = escalation_service.assign_agent(session_id, agent_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Agent {agent_id} assigned to session {session_id}'
            })
        else:
            return jsonify({'error': 'Failed to assign agent'}), 500
        
    except Exception as e:
        logger.error(f"Error assigning escalation by session: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/sessions/<int:session_id>/summary', methods=['GET'])
def get_session_summary(session_id):
    """Get comprehensive session summary for agent dashboard"""
    try:
        from services.session_summary_service import session_summary_service
        
        summary = session_summary_service.generate_session_summary(session_id)
        
        if 'error' in summary:
            return jsonify({'error': summary['error']}), 404
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        logger.error(f"Error getting session summary: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/sessions', methods=['GET'])
def get_sessions():
    """Get all chat sessions for agent dashboard"""
    try:
        status = request.args.get('status', 'all')
        limit = request.args.get('limit', 50, type=int)
        
        query = ChatSession.query
        if status != 'all':
            query = query.filter_by(status=status)
        
        sessions = query.order_by(ChatSession.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'sessions': [session.to_dict() for session in sessions],
            'count': len(sessions)
        })
        
    except Exception as e:
        logger.error(f"Error getting sessions: {str(e)}")
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
