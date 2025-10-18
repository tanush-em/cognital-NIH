import { io } from 'socket.io-client';

class SocketManager {
  constructor() {
    this.socket = null;
    this.sessionId = null;
    this.isConnected = false;
  }

  connect(serverUrl = 'http://localhost:5000') {
    if (this.socket) {
      return this.socket;
    }

    this.socket = io(serverUrl, {
      transports: ['websocket', 'polling'],
      autoConnect: true
    });

    this.socket.on('connect', () => {
      console.log('Connected to server');
      this.isConnected = true;
      this.createOrJoinSession();
    });

    // Handle server connection confirmation
    this.socket.on('connected', (data) => {
      console.log('Server response:', data);
    });

    // Handle session join confirmation
    this.socket.on('joined_session', (data) => {
      console.log('Joined session:', data);
    });

    this.socket.on('disconnect', () => {
      console.log('Disconnected from server');
      this.isConnected = false;
    });

    this.socket.on('connect_error', (error) => {
      console.error('Connection error:', error);
    });

    return this.socket;
  }

  createOrJoinSession() {
    if (this.socket && this.isConnected) {
      // Generate a unique session ID or get from localStorage
      this.sessionId = localStorage.getItem('chatSessionId') || this.generateSessionId();
      localStorage.setItem('chatSessionId', this.sessionId);
      
      this.socket.emit('join_session', { sessionId: this.sessionId });
      console.log('Joined session:', this.sessionId);
    }
  }

  generateSessionId() {
    return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
  }

  sendMessage(message, messageType = 'user') {
    if (this.socket && this.isConnected) {
      this.socket.emit('user_message', {
        sessionId: this.sessionId,
        message: message,
        messageType: messageType,
        timestamp: new Date().toISOString()
      });
    }
  }

  onMessage(callback) {
    if (this.socket) {
      // Remove existing listeners to prevent duplicates
      this.socket.off('new_message');
      this.socket.off('ai_response');
      this.socket.off('agent_response');
      this.socket.off('escalation');
      
      // Handle new message events from the updated WebSocket service
      this.socket.on('new_message', (data) => {
        console.log('New message received:', data);
        callback({
          type: data.role === 'ai' ? 'ai' : data.role === 'agent' ? 'agent' : 'user',
          message: data.content,
          sender: data.role,
          timestamp: data.timestamp,
          confidence: data.confidence
        });
      });
      
      // Legacy event handlers for backward compatibility
      this.socket.on('ai_response', callback);
      this.socket.on('agent_response', callback);
      this.socket.on('escalation', callback);
    }
  }

  onTypingIndicator(callback) {
    if (this.socket) {
      // Remove existing listeners to prevent duplicates
      this.socket.off('ai_typing');
      this.socket.off('typing');
      
      // Handle AI typing events from the updated WebSocket service
      this.socket.on('ai_typing', (data) => {
        console.log('AI typing event:', data);
        callback({
          isTyping: data.typing,
          sender: 'ai'
        });
      });
      
      // Legacy typing indicator
      this.socket.on('typing', callback);
    }
  }

  onEscalation(callback) {
    if (this.socket) {
      this.socket.on('escalation', callback);
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
    }
  }

  removeAllListeners() {
    if (this.socket) {
      this.socket.off('new_message');
      this.socket.off('ai_response');
      this.socket.off('agent_response');
      this.socket.off('escalation');
      this.socket.off('ai_typing');
      this.socket.off('typing');
      this.socket.off('connected');
      this.socket.off('joined_session');
    }
  }

  getSocket() {
    return this.socket;
  }

  isSocketConnected() {
    return this.isConnected;
  }
}

// Create a singleton instance
const socketManager = new SocketManager();

export default socketManager;
