import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Alert,
  Snackbar,
  Chip,
  IconButton,
  Menu,
  MenuItem
} from '@mui/material';
import {
  Support as SupportIcon,
  Wifi as WifiIcon,
  WifiOff as WifiOffIcon,
  AccountCircle as AccountCircleIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';

import socketManager from './socket';
import ChatList from './components/ChatList';
import ChatWindow from './components/ChatWindow';
import ChatSummary from './components/ChatSummary';

const App = () => {
  // Connection state
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState(null);

  // Chat state
  const [escalations, setEscalations] = useState([]);
  const [activeRoom, setActiveRoom] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [chatSummary, setChatSummary] = useState(null);

  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' });
  const [anchorEl, setAnchorEl] = useState(null);

  // Initialize socket connection and event listeners
  useEffect(() => {
    const initializeSocket = () => {
      // Connect to socket
      socketManager.connect();

      // Connection status listeners
      socketManager.on('connection_status', (data) => {
        setIsConnected(data.connected);
        if (!data.connected) {
          setActiveRoom(null);
          setChatHistory([]);
          setChatSummary(null);
        }
      });

      socketManager.on('connection_error', (error) => {
        setConnectionError(error.message || 'Connection failed');
        showNotification('Failed to connect to server', 'error');
      });

      // Chat event listeners
      socketManager.on('escalation_pending', (data) => {
        console.log('New escalation:', data);
        setEscalations(prev => {
          const existing = prev.find(e => e.roomId === data.roomId);
          if (existing) {
            return prev.map(e => e.roomId === data.roomId ? { ...e, ...data } : e);
          }
          return [...prev, data];
        });
        showNotification(`New escalation from ${data.userName || 'Customer'}`, 'info');
      });

      socketManager.on('chat_message', (data) => {
        console.log('New message:', data);
        
        // Update chat history if this is for the active room
        if (activeRoom && data.roomId === activeRoom.roomId) {
          setChatHistory(prev => [...prev, data]);
        }

        // Update escalations list with last message
        setEscalations(prev => 
          prev.map(esc => 
            esc.roomId === data.roomId 
              ? { ...esc, lastMessage: data.message }
              : esc
          )
        );
      });

      socketManager.on('session_closed', (data) => {
        console.log('Session closed:', data);
        
        // Remove from escalations if it was there
        setEscalations(prev => prev.filter(esc => esc.roomId !== data.roomId));
        
        // Clear active room if it was the one that closed
        if (activeRoom && data.roomId === activeRoom.roomId) {
          setActiveRoom(null);
          setChatHistory([]);
          setChatSummary(null);
        }

        showNotification(`Session closed: ${data.reason || 'Unknown reason'}`, 'info');
      });

      socketManager.on('agent_joined', (data) => {
        console.log('Agent joined:', data);
        showNotification(`Joined room ${data.roomId}`, 'success');
      });

      socketManager.on('agent_left', (data) => {
        console.log('Agent left:', data);
        showNotification(`Left room ${data.roomId}`, 'info');
      });

      // Request initial data
      setTimeout(() => {
        if (socketManager.isConnected()) {
          requestEscalations();
        }
      }, 1000);
    };

    initializeSocket();

    // Cleanup on unmount
    return () => {
      socketManager.disconnect();
    };
  }, [activeRoom]);

  const showNotification = useCallback((message, severity = 'info') => {
    setNotification({ open: true, message, severity });
  }, []);

  const handleCloseNotification = () => {
    setNotification(prev => ({ ...prev, open: false }));
  };

  const requestEscalations = useCallback(() => {
    if (socketManager.isConnected()) {
      socketManager.requestEscalations();
    }
  }, []);

  const handleJoinRoom = useCallback((roomId) => {
    if (!socketManager.isConnected()) {
      showNotification('Not connected to server', 'error');
      return;
    }

    setLoading(true);
    setError(null);

    // Find the escalation data
    const escalation = escalations.find(esc => esc.roomId === roomId);
    
    // Join the room
    socketManager.joinRoom(roomId);
    
    // Set as active room
    setActiveRoom({
      roomId,
      userName: escalation?.userName || 'Customer',
      status: escalation?.status || 'active',
      ...escalation
    });

    // Request chat history
    socketManager.requestChatHistory(roomId);

    // Remove from escalations list
    setEscalations(prev => prev.filter(esc => esc.roomId !== roomId));

    setLoading(false);
  }, [escalations, showNotification]);

  const handleSendMessage = useCallback((roomId, message) => {
    if (!socketManager.isConnected()) {
      showNotification('Not connected to server', 'error');
      return;
    }

    // Add message to local history immediately for better UX
    const newMessage = {
      message,
      type: 'agent',
      timestamp: new Date().toISOString(),
      roomId
    };

    setChatHistory(prev => [...prev, newMessage]);
    
    // Send to server
    socketManager.sendMessage(roomId, message);
  }, [showNotification]);

  const handleCloseSession = useCallback((roomId) => {
    if (!socketManager.isConnected()) {
      showNotification('Not connected to server', 'error');
      return;
    }

    if (window.confirm('Are you sure you want to close this session?')) {
      socketManager.closeSession(roomId, 'agent_001', 'Agent closed session');
      
      // Clear local state
      setActiveRoom(null);
      setChatHistory([]);
      setChatSummary(null);
    }
  }, [showNotification]);

  const handleRefresh = useCallback(() => {
    requestEscalations();
  }, [requestEscalations]);

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleSettings = () => {
    handleMenuClose();
    // TODO: Implement settings dialog
    showNotification('Settings feature coming soon', 'info');
  };

  const handleLogout = () => {
    handleMenuClose();
    // TODO: Implement logout
    showNotification('Logout feature coming soon', 'info');
  };

  return (
    <Box sx={{ flexGrow: 1, height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* App Bar */}
      <AppBar position="static">
        <Toolbar>
          <SupportIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Agent Dashboard
          </Typography>
          
          {/* Connection Status */}
          <Box display="flex" alignItems="center" gap={2}>
            <Chip
              icon={isConnected ? <WifiIcon /> : <WifiOffIcon />}
              label={isConnected ? 'Connected' : 'Disconnected'}
              color={isConnected ? 'success' : 'error'}
              variant="outlined"
              size="small"
            />
            
            {/* User Menu */}
            <IconButton
              color="inherit"
              onClick={handleMenuOpen}
            >
              <AccountCircleIcon />
            </IconButton>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleMenuClose}
            >
              <MenuItem onClick={handleSettings}>
                <SettingsIcon sx={{ mr: 1 }} />
                Settings
              </MenuItem>
              <MenuItem onClick={handleLogout}>
                Logout
              </MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Connection Error Alert */}
      {connectionError && (
        <Alert 
          severity="error" 
          onClose={() => setConnectionError(null)}
          sx={{ borderRadius: 0 }}
        >
          Connection Error: {connectionError}
        </Alert>
      )}

      {/* Main Content */}
      <Container maxWidth={false} sx={{ flex: 1, py: 2 }}>
        <Grid container spacing={2} sx={{ height: '100%' }}>
          {/* Left Panel - Chat List */}
          <Grid item xs={12} md={4} lg={3}>
            <ChatList
              escalations={escalations}
              activeRoom={activeRoom}
              onJoinRoom={handleJoinRoom}
              onRefresh={handleRefresh}
              loading={loading}
              error={error}
              isConnected={isConnected}
            />
          </Grid>

          {/* Right Panel - Chat Interface */}
          <Grid item xs={12} md={8} lg={9}>
            <Grid container spacing={2} sx={{ height: '100%' }}>
              {/* Chat Summary */}
              <Grid item xs={12}>
                <ChatSummary
                  summary={chatSummary}
                  loading={false}
                  error={null}
                />
              </Grid>

              {/* Chat Window */}
              <Grid item xs={12} sx={{ flex: 1 }}>
                <ChatWindow
                  activeRoom={activeRoom}
                  chatHistory={chatHistory}
                  onSendMessage={handleSendMessage}
                  onCloseSession={handleCloseSession}
                  onJoinRoom={handleJoinRoom}
                  isConnected={isConnected}
                  loading={loading}
                />
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      </Container>

      {/* Notification Snackbar */}
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={handleCloseNotification}
          severity={notification.severity}
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default App;
