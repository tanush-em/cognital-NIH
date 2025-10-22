import { io } from 'socket.io-client';

class SocketManager {
  constructor() {
    this.socket = null;
    this.connected = false;
    this.listeners = new Map();
  }

  connect(serverUrl = 'http://localhost:5000') {
    if (this.socket && this.connected) {
      return this.socket;
    }

    this.socket = io(serverUrl, {
      transports: ['polling', 'websocket'],
      autoConnect: true,
      upgrade: true,
      rememberUpgrade: true,
      reconnection: true,
      reconnectionAttempts: 10,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      timeout: 20000,
      forceNew: false,
      multiplex: false,
      pingTimeout: 60000,
      pingInterval: 25000
    });

    // Connection event handlers
    this.socket.on('connect', () => {
      console.log('Connected to server:', this.socket.id);
      this.connected = true;
      this.emit('connection_status', { connected: true });
      
      // Join agents room to receive escalation notifications
      this.socket.emit('join_room', {
        room_id: 'agents',
        user_type: 'agent',
        user_id: 'agent_001'
      });
    });

    this.socket.on('disconnect', (reason) => {
      console.log('Disconnected from server:', reason);
      this.connected = false;
      this.emit('connection_status', { connected: false, reason });
    });

    this.socket.on('connect_error', (error) => {
      console.error('Connection error:', error);
      this.connected = false;
      this.emit('connection_error', error);
    });

    this.socket.on('reconnect', (attemptNumber) => {
      console.log('Reconnected after', attemptNumber, 'attempts');
      this.connected = true;
      this.emit('connection_status', { connected: true });
    });

    this.socket.on('reconnect_error', (error) => {
      console.error('Reconnection error:', error);
      this.emit('connection_error', error);
    });

    this.socket.on('reconnect_failed', () => {
      console.error('Failed to reconnect after maximum attempts');
      this.connected = false;
      this.emit('connection_error', { message: 'Failed to reconnect to server' });
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

    // Double-check connection status
    if (!this.socket.connected) {
      console.error('Socket connection lost, attempting to reconnect...');
      this.connect();
      return;
    }

    try {
      // Add a small delay to ensure connection is stable
      setTimeout(() => {
        if (this.socket && this.socket.connected) {
          this.socket.emit('agent_join_room', {
            roomId,
            agentId,
            timestamp: new Date().toISOString()
          });
          
          console.log(`Agent ${agentId} joining room ${roomId}`);
        } else {
          console.error('Socket disconnected during join attempt');
        }
      }, 100);
    } catch (error) {
      console.error('Error joining room:', error);
    }
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

    try {
      const messageData = {
        roomId,
        message,
        agentId,
        timestamp: new Date().toISOString(),
        type: 'agent_message'
      };

      this.socket.emit('agent_message', messageData);
    } catch (error) {
      console.error('Error sending message:', error);
    }
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
