# 🤖 AI-First Customer Support System

> Transforming telecom customer support with intelligent automation and seamless human handoff

## 🎯 Overview

An **AI-first customer support system** that combines the efficiency of an intelligent chatbot with the empathy and expertise of human agents. Built for telecom companies, this solution handles 80-90% of customer queries automatically while intelligently detecting when human intervention is needed.

### The Problem We Solve

Traditional customer support systems force users to wait in queues or navigate complex menus. Even simple queries take time, and complex issues often get mishandled. Our solution eliminates these pain points by:

- **Instantly answering** most queries using AI-powered knowledge retrieval
- **Automatically detecting** when issues need human attention
- **Seamlessly transitioning** from AI to human agents without disruption
- **Providing agents** with full context and AI-generated summaries

---

## ✨ Key Features

### 🧠 AI-Powered Chatbot
- **RAG-Based Intelligence**: Retrieval-Augmented Generation system that answers queries using your company's internal knowledge base and policy documents
- **Telecom-Specific**: Pre-trained on telecom industry documentation, FAQs, and policy documents
- **Instant Responses**: Answers most queries in seconds, 24/7

### 🚨 Intelligent Escalation Engine
- **Smart Detection**: Automatically identifies when issues need human attention based on:
  - Low AI confidence scores
  - Frustration keywords and sentiment analysis
  - Conversation length and repetition patterns
  - Sensitive topics (billing disputes, service outages, privacy concerns)
- **Proactive Handoff**: Escalates without requiring users to explicitly ask for help

### 🔄 Seamless Human Handoff
- **Zero Disruption**: Users stay in the same chat interface; no re-queuing or context loss
- **Instant Transition**: Human agents join the conversation immediately
- **Full Context**: Agents see the entire conversation history plus an AI-generated summary
- **Natural Continuation**: Conversations flow smoothly from AI to human

### 👥 Human Agent Dashboard
- **Real-Time Chat Management**: View and manage multiple chat sessions
- **AI-Generated Summaries**: Quick understanding of conversation context
- **Conversation History**: Full access to all messages and context
- **Performance Insights**: Track resolution times and customer satisfaction

### 📊 Unified Analytics
- **Complete Chat History**: All AI and human interactions stored in one place
- **Performance Metrics**: Track resolution rates, escalation patterns, and customer satisfaction
- **Continuous Learning**: System learns from human resolutions to improve AI responses
---

### Technology Stack

**Backend:**
- Flask (Python web framework)
- Flask-SocketIO (Real-time WebSocket communication)
- ChromaDB (Vector database for RAG)
- Sentence Transformers (Embeddings)
- Groq (LLM inference)
- PostgreSQL (Relational database)

**Frontend:**
- React (User interfaces)
- Material-UI (Design system)
- Socket.IO Client (Real-time communication)

**AI/ML:**
- Retrieval-Augmented Generation (RAG)
- Sentence Transformers for embeddings
- Rule-based escalation engine with sentiment analysis

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ 
- Node.js 16+ and npm
- Groq API key (for LLM inference)

### Installation

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd NIH
```

#### 2. Backend Setup

```bash
cd be

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env  # Create .env file with:
# GROQ_API_KEY=your_groq_api_key
# SECRET_KEY=your_secret_key
# FLASK_DEBUG=True
# PORT=5000


# Run the backend server
python app.py
```

The backend will start on `http://localhost:5000`

#### 3. User Chatbot Setup

```bash
cd ../user-chatbot

# Install dependencies
npm install

# Start development server
npm start
```

The user chatbot will start on `http://localhost:3000`

#### 4. Agent Dashboard Setup

```bash
cd ../agent-dashboard

# Install dependencies
npm install

# Update API endpoint in src/api.js if needed (default: http://localhost:5000)

# Start development server
npm start
```

The agent dashboard will start on `http://localhost:3001`

---

## 📖 Usage

### For End Users

1. Open the **User Chatbot** interface
2. Start chatting with the AI assistant
3. The system will automatically detect if you need human help and escalate seamlessly
4. Continue chatting - you won't notice the transition!

### For Support Agents

1. Open the **Agent Dashboard**
2. View active chat sessions that have been escalated
3. Review the AI-generated summary for quick context
4. Join the conversation and help the customer
5. Mark conversations as resolved when done

### Adding Knowledge Base Documents

1. Place PDF documents in `be/resources/` folder
2. The system automatically processes them on startup
3. Documents are indexed and ready for querying within seconds

---

## 📈 Expected Impact

### Efficiency Gains
- **80-90% automation**: Handle most repetitive queries automatically
- **Reduced wait times**: Instant responses for common questions
- **Higher throughput**: Agents focus on complex issues only

### Customer Satisfaction
- **Faster resolutions**: No queue waiting for simple queries
- **Seamless experience**: No context loss during escalation
- **24/7 availability**: AI handles queries anytime

### Operational Benefits
- **Lower costs**: Reduced need for round-the-clock human agents
- **Scalable**: Handles growing customer volumes automatically
- **Continuous improvement**: System learns from every interaction

---

## 🔧 Configuration

### Escalation Rules

The system uses configurable rules for automatic escalation. Key parameters can be adjusted in `be/services/escalation_service.py`:

- Confidence thresholds
- Message count limits
- Frustration keyword detection
- Sensitive topic identification
- Session duration thresholds

### RAG Settings

- Embedding model: `all-MiniLM-L6-v2` (can be changed for better accuracy)
- Vector database: ChromaDB (persistent storage)
- Retrieval: Top-K similar chunks (configurable)

---

## 🎓 How It Works

### 1. User Query Processing
- User sends a message via the chatbot interface
- Query is embedded using sentence transformers
- Similar chunks are retrieved from the knowledge base

### 2. AI Response Generation
- Retrieved context + user query → LLM
- LLM generates contextual, accurate response
- Response confidence score is calculated

### 3. Escalation Decision
- Multiple signals are analyzed:
  - AI confidence score
  - Sentiment and frustration keywords
  - Conversation patterns
  - Topic sensitivity
- If thresholds are met → Automatic escalation

### 4. Human Handoff
- Chat session is flagged for agent attention
- AI generates a conversation summary
- Agent joins seamlessly via dashboard
- User experience remains uninterrupted

---

## 📁 Project Structure

```
NIH/
├── be/                          # Backend Flask application
│   ├── app.py                   # Main application entry point
│   ├── models/                  # Database models
│   │   ├── chat_models.py       # Chat session and message models
│   │   └── user_models.py       # User and agent models
│   ├── routes/                  # API routes
│   │   ├── chat_routes.py       # Chat endpoints
│   │   └── admin_routes.py      # Admin/agent endpoints
│   ├── services/                # Core business logic
│   │   ├── rag_service.py       # RAG implementation
│   │   ├── llm_service.py       # LLM integration
│   │   ├── escalation_service.py # Escalation logic
│   │   ├── websocket_service.py # Real-time communication
│   │   └── pdf_processor.py     # Document processing
│   ├── resources/               # Knowledge base PDFs
│   └── requirements.txt         # Python dependencies
│
├── user-chatbot/                # User-facing React app
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── ChatWindow.js    # Main chat interface
│   │   │   ├── MessageBubble.js # Message display
│   │   │   └── EscalationNotification.js
│   │   └── socket.js            # WebSocket client
│   └── package.json
│
└── agent-dashboard/             # Agent-facing React app
    ├── src/
    │   ├── components/          # React components
    │   │   ├── ChatList.js      # Active chat sessions
    │   │   ├── ChatWindow.js    # Chat interface for agents
    │   │   └── ChatSummary.js   # AI-generated summaries
    │   └── api.js               # API client
    └── package.json
```

---

## 🔒 Security Considerations

- API keys stored in environment variables
- CORS configured for frontend-backend communication
- Database credentials secured via environment variables
- WebSocket connections use secure protocols

---

## 🚧 Future Enhancements

- [ ] Multi-language support
- [ ] Voice input/output integration
- [ ] Advanced analytics dashboard
- [ ] Integration with CRM systems
- [ ] Custom LLM fine-tuning on company data
- [ ] Feedback loop for continuous AI improvement
- [ ] Support for additional document formats (Word, Excel)

---

## 👥 Team

Built for StrongHerAda Lovelace Hackathon by Team Ctrl+Alt+Elite

---
## 📞 Contact

For questions or feedback, please open an issue or contact the development team.

---