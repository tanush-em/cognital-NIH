# AI-Powered Telecom Support Chatbot Backend

A comprehensive Flask-based backend system for an AI-powered telecom support chatbot with real-time WebSocket communication, RAG (Retrieval-Augmented Generation), and intelligent escalation.

## 🚀 Features

- **Real-time Chat**: WebSocket-based communication for instant messaging
- **AI-Powered Responses**: Groq LLM integration with RAG for contextual answers
- **Intelligent Escalation**: Rule-based escalation to human agents
- **Knowledge Base**: ChromaDB vector database for document retrieval
- **Multi-client Support**: Separate handling for users and agents
- **REST API**: Complete REST endpoints for all operations
- **Real-time Communication**: WebSocket-based messaging

## 🛠 Tech Stack

- **Backend**: Flask, Flask-SocketIO
- **Database**: SQLite (for sessions and escalations only)
- **Vector DB**: ChromaDB for RAG
- **LLM**: Groq API (Llama3-8b-8192)
- **Real-time**: WebSocket communication
- **Embeddings**: Sentence Transformers

## 📁 Project Structure

```
be/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                  # Environment configuration
├── models/               # Database models
│   ├── __init__.py
│   ├── chat_models.py    # Chat, Escalation models
│   └── user_models.py    # User, Agent models
├── services/             # Business logic services
│   ├── rag_service.py    # RAG with ChromaDB
│   ├── llm_service.py    # Groq LLM integration
│   ├── escalation_service.py  # Escalation logic
│   └── websocket_service.py   # WebSocket handlers
├── routes/               # API routes
│   ├── __init__.py
│   ├── chat_routes.py    # Chat endpoints
│   └── admin_routes.py   # Admin endpoints
├── utils/                # Utilities
│   └── db.py            # Database configuration
└── static/              # Static files and logs
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
cd be
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Edit `.env` file with your configuration:

```env
# Required: Get your API key from https://console.groq.com/
GROQ_API_KEY=your-groq-api-key-here

# Optional: Database configuration
DATABASE_URL=sqlite:///chatbot.db

# Optional: Flask configuration
FLASK_DEBUG=True
PORT=5000
```

### 3. Run the Application

```bash
python app.py
```

The server will start on `http://localhost:5000`

## 📡 API Endpoints

### Chat Endpoints

- `POST /api/ask` - Manual AI query (testing)
- `POST /api/escalate` - Force escalation (testing)
- `POST /api/sessions` - Create new chat session
- `GET /api/agents/available` - Get available agents

### Admin Endpoints

- `POST /api/ingest` - Upload documents to knowledge base
- `POST /api/users` - Create user
- `POST /api/agents` - Create agent
- `PUT /api/agents/<id>/availability` - Update agent availability
- `GET /api/health` - Health check

### WebSocket Events

- `connect` - Client connection
- `join_room` - Join chat room
- `leave_room` - Leave chat room
- `send_message` - Send message
- `escalation_alert` - Escalation notification (agents)

## 🔧 Configuration

### Escalation Rules

The system automatically escalates conversations based on:

1. **Low Confidence** (< 0.6)
2. **Long Conversations** (> 10 message exchanges)
3. **Frustration Keywords**: "refund", "cancel", "angry", "not working", etc.
4. **Sensitive Topics**: "billing dispute", "service outage", etc.

### RAG Configuration

- **Embedding Model**: all-MiniLM-L6-v2
- **Vector Database**: ChromaDB with DuckDB backend
- **Context Length**: 2000 characters max

## 📊 Usage Examples

### 1. Create a Chat Session

```bash
curl -X POST http://localhost:5000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123"}'
```

### 2. Ingest Knowledge Documents

```bash
curl -X POST http://localhost:5000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "content": "To reset your password, go to the account settings...",
        "title": "Password Reset Guide",
        "category": "account_management"
      }
    ]
  }'
```

### 3. Test AI Response

```bash
curl -X POST http://localhost:5000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I reset my password?"}'
```

### 4. WebSocket Connection (JavaScript)

```javascript
const socket = io('http://localhost:5000');

// Join room
socket.emit('join_room', {
  room_id: 'room123',
  user_type: 'user',
  user_id: 'user123'
});

// Send message
socket.emit('send_message', {
  room_id: 'room123',
  message: 'Hello, I need help with my account',
  user_type: 'user',
  user_id: 'user123'
});

// Listen for messages
socket.on('new_message', (data) => {
  console.log('New message:', data);
});
```

## 🔄 Escalation Flow

1. **User sends message** → System checks escalation rules
2. **If escalation triggered** → Create escalation record, notify agents
3. **Agent joins room** → Takes over conversation
4. **Human conversation** → Agent responds directly

## 🗄 Database Schema

### Chat Sessions
- `id`, `session_id`, `user_id`, `agent_id`, `room_id`, `status`, `created_at`, `updated_at`

### Escalations
- `id`, `session_id`, `reason`, `triggered_at`, `handled_at`, `status`

### Users/Agents
- `id`, `user_id`/`agent_id`, `name`, `email`, `phone`, `is_available`

## 🚨 Error Handling

- Comprehensive error logging
- Graceful degradation for service failures
- User-friendly error messages
- Automatic retry mechanisms

## 🔒 Security Considerations

- Input validation and sanitization
- SQL injection prevention
- CORS configuration
- Environment variable protection

## 📈 Monitoring

- Health check endpoint: `/api/health`
- Logging to `./static/logs/chatbot.log`
- WebSocket connection monitoring
- Performance metrics

## 🧪 Testing

Test the system with the provided endpoints:

1. **Health Check**: `GET /api/health`
2. **AI Query**: `POST /api/ask`
3. **Document Ingestion**: `POST /api/ingest`
4. **Force Escalation**: `POST /api/escalate`

## 🚀 Production Deployment

1. Set `FLASK_DEBUG=False`
2. Configure production database (if needed)
3. Configure proper CORS origins
4. Set up SSL/TLS
5. Use environment variables for secrets
6. Set up monitoring and logging

## 📝 License

MIT License - See LICENSE file for details
