import { io } from 'socket.io-client';

class SocketManager {
  constructor() {
    this.socket = null;
    this.connected = false;
    this.listeners = new Map();
  }

  connect(serverUrl = 'http://localhost:3001') {
    if (this.socket && this.connected) {
      return this.socket;
    }

    this.socket = io(serverUrl, {
      transports: ['websocket'],
      autoConnect: true,
    });

    // Connection event handlers
    this.socket.on('connect', () => {
      console.log('Connected to server:', this.socket.id);
      this.connected = true;
      this.emit('connection_status', { connected: true });
    });

    this.socket.on('disconnect', () => {
      console.log('Disconnected from server');
      this.connected = false;
      this.emit('connection_status', { connected: false });
    });

    this.socket.on('connect_error', (error) => {
      console.error('Connection error:', error);
      this.emit('connection_error', error);
    });

    // Chat-specific event handlers
    this.socket.on('escalation_pending', (data) => {
      console.log('New escalation pending:', data);
      this.emit('escalation_pending', data);
    });

    this.socket.on('chat_message', (data) => {
      console.log('New chat message:', data);
      this.emit('chat_message', data);
    });

    this.socket.on('session_closed', (data) => {
      console.log('Session closed:', data);
      this.emit('session_closed', data);
    });

    this.socket.on('agent_joined', (data) => {
      console.log('Agent joined room:', data);
      this.emit('agent_joined', data);
    });

    this.socket.on('agent_left', (data) => {
      console.log('Agent left room:', data);
      this.emit('agent_left', data);
    });

    return this.socket;
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.connected = false;
    }
  }

  // Join a chat room as an agent
  joinRoom(roomId, agentId = 'agent_001') {
    if (!this.socket || !this.connected) {
      console.error('Socket not connected');
      return;
    }

    this.socket.emit('agent_join_room', {
      roomId,
      agentId,
      timestamp: new Date().toISOString()
    });
  }

  // Leave a chat room
  leaveRoom(roomId, agentId = 'agent_001') {
    if (!this.socket || !this.connected) {
      console.error('Socket not connected');
      return;
    }

    this.socket.emit('agent_leave_room', {
      roomId,
      agentId,
      timestamp: new Date().toISOString()
    });
  }

  // Send a message to the user
  sendMessage(roomId, message, agentId = 'agent_001') {
    if (!this.socket || !this.connected) {
      console.error('Socket not connected');
      return;
    }

    const messageData = {
      roomId,
      message,
      agentId,
      timestamp: new Date().toISOString(),
      type: 'agent_message'
    };

    this.socket.emit('agent_message', messageData);
  }

  // Close a chat session
  closeSession(roomId, agentId = 'agent_001', reason = 'Agent closed session') {
    if (!this.socket || !this.connected) {
      console.error('Socket not connected');
      return;
    }

    this.socket.emit('close_session', {
      roomId,
      agentId,
      reason,
      timestamp: new Date().toISOString()
    });
  }


  // Request escalation list
  requestEscalations() {
    if (!this.socket || !this.connected) {
      console.error('Socket not connected');
      return;
    }

    this.socket.emit('get_escalations');
  }

  // Event listener management
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in event listener for ${event}:`, error);
        }
      });
    }
  }

  // Get connection status
  isConnected() {
    return this.connected && this.socket && this.socket.connected;
  }

  // Get socket instance
  getSocket() {
    return this.socket;
  }
}

// Create and export a singleton instance
const socketManager = new SocketManager();
export default socketManager;
