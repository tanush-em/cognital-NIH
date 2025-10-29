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
import apiService from './api';
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
  const [chatSummary, setChatSummary] = useState(null);
  const [messages, setMessages] = useState([]);
  const [pendingChatHistory, setPendingChatHistory] = useState([]);

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
        console.log('Current escalations before update:', escalations);
        
        setEscalations(prev => {
          console.log('Previous escalations state:', prev);
          const existing = prev.find(e => e.roomId === data.roomId);
          if (existing) {
            console.log('Updating existing escalation');
            return prev.map(e => e.roomId === data.roomId ? { ...e, ...data } : e);
          }
          // Ensure unique key for new escalations
          const escalationWithKey = {
            ...data,
            uniqueKey: data.uniqueKey || `escalation_${data.escalationId || Date.now()}`
          };
          console.log('Adding new escalation:', escalationWithKey);
          return [...prev, escalationWithKey];
        });
        showNotification(`New escalation from ${data.userName || 'Customer'}`, 'info');
      });

      socketManager.on('chat_message', (data) => {
        console.log('New message:', data);

        // Update escalations list with last message
        setEscalations(prev => 
          prev.map(esc => 
            esc.roomId === data.roomId 
              ? { ...esc, lastMessage: data.message }
              : esc
          )
        );
      });

      socketManager.on('new_message', (data) => {
        console.log('New message received:', data);
        console.log('Active room:', activeRoom);
        console.log('Data session_id:', data.session_id);
        console.log('Data role:', data.role);
        
        // Add message to messages array if it's for the active room
        if (activeRoom && data.session_id) {
          console.log('Adding new message to messages array');
          setMessages(prev => {
            // Check if this message already exists to avoid duplicates
            const exists = prev.some(msg => 
              msg.content === data.content && 
              msg.timestamp === data.timestamp && 
              msg.role === data.role
            );
            
            if (exists) {
              console.log('Message already exists, skipping');
              return prev;
            }
            
            console.log('Adding new message to array');
            return [...prev, {
              role: data.role,
              content: data.content,
              timestamp: data.timestamp,
              session_id: data.session_id
            }];
          });
        } else {
          console.log('Not adding new message - activeRoom:', !!activeRoom, 'session_id:', data.session_id);
          // If we have an active room but no session_id, still try to add the message
          if (activeRoom && !data.session_id) {
            console.log('Adding message without session_id for active room');
            setMessages(prev => [...prev, {
              role: data.role,
              content: data.content,
              timestamp: data.timestamp,
              session_id: data.session_id
            }]);
          }
        }
      });

      socketManager.on('chat_history', (data) => {
        console.log('Chat history received:', data);
        console.log('Active room:', activeRoom);
        console.log('Data session_id:', data.session_id);
        
        // If activeRoom is not set yet, store the chat history temporarily
        if (!activeRoom && data.session_id) {
          console.log('Storing chat history temporarily - activeRoom not set yet');
          setPendingChatHistory(prev => [...prev, {
            role: data.role,
            content: data.content,
            timestamp: data.timestamp,
            session_id: data.session_id,
            message_type: data.message_type,
            metadata: data.metadata
          }]);
          return;
        }
        
        // Add chat history messages to messages array if it's for the active room
        if (activeRoom && data.session_id) {
          console.log('Adding chat history message to messages array');
          setMessages(prev => {
            // Check if this message already exists to avoid duplicates
            const exists = prev.some(msg => 
              msg.content === data.content && 
              msg.timestamp === data.timestamp && 
              msg.role === data.role
            );
            
            if (exists) {
              console.log('Message already exists, skipping');
              return prev;
            }
            
            console.log('Adding new message to array');
            return [...prev, {
              role: data.role,
              content: data.content,
              timestamp: data.timestamp,
              session_id: data.session_id,
              message_type: data.message_type,
              metadata: data.metadata
            }];
          });
        } else {
          console.log('Not adding chat history - activeRoom:', !!activeRoom, 'session_id:', data.session_id);
        }
      });

      socketManager.on('session_closed', (data) => {
        console.log('Session closed:', data);
        
        // Remove from escalations if it was there
        setEscalations(prev => prev.filter(esc => esc.roomId !== data.roomId));
        
        // Clear active room if it was the one that closed
        if (activeRoom && data.roomId === activeRoom.roomId) {
          setActiveRoom(null);
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
      setTimeout(async () => {
        await requestEscalations();
      }, 1000);
    };

    initializeSocket();

    // Cleanup on unmount
    return () => {
      socketManager.disconnect();
    };
  }, []);

  // Process pending chat history when activeRoom is set
  useEffect(() => {
    if (activeRoom && pendingChatHistory.length > 0) {
      console.log('Processing pending chat history:', pendingChatHistory.length, 'messages');
      setMessages(prev => {
        const newMessages = [...prev];
        
        // Add pending messages that don't already exist
        pendingChatHistory.forEach(pendingMsg => {
          const exists = newMessages.some(msg => 
            msg.content === pendingMsg.content && 
            msg.timestamp === pendingMsg.timestamp && 
            msg.role === pendingMsg.role
          );
          
          if (!exists) {
            newMessages.push(pendingMsg);
          }
        });
        
        return newMessages;
      });
      
      // Clear pending chat history
      setPendingChatHistory([]);
    }
  }, [activeRoom, pendingChatHistory]);

  const showNotification = useCallback((message, severity = 'info') => {
    setNotification({ open: true, message, severity });
  }, []);

  const handleCloseNotification = () => {
    setNotification(prev => ({ ...prev, open: false }));
  };

  const requestEscalations = useCallback(async () => {
    try {
      setLoading(true);
      const response = await apiService.getEscalations('pending', 50);
      if (response.success) {
        // Transform API data to match expected format
        const transformedEscalations = response.escalations.map(escalation => ({
          roomId: escalation.session?.room_id || `room_${escalation.session_id}`,
          sessionId: escalation.session_id,
          userName: escalation.session?.user_id || 'Customer',
          status: escalation.status,
          priority: escalation.priority,
          reason: escalation.reason,
          createdAt: escalation.created_at,
          escalationId: escalation.id,
          // Use escalation ID as unique key to prevent React duplicate key warnings
          uniqueKey: `escalation_${escalation.id}`
        }));
        setEscalations(transformedEscalations);
      }
    } catch (error) {
      console.error('Error fetching escalations:', error);
      setError('Failed to fetch escalations');
    } finally {
      setLoading(false);
    }
  }, []);


  const handleJoinRoom = useCallback(async (roomId) => {
    console.log('Joining room:', roomId);
    if (!socketManager.isConnected()) {
      showNotification('Not connected to server', 'error');
      return;
    }

    setLoading(true);
    setError(null);

    // Find the escalation data
    const escalation = escalations.find(esc => esc.roomId === roomId);
    console.log('Found escalation:', escalation);
    
    // Set as active room first
    const newActiveRoom = {
      roomId,
      userName: escalation?.userName || 'Customer',
      status: 'escalated', // Set to escalated when agent joins
      priority: escalation?.priority,
      reason: escalation?.reason,
      createdAt: escalation?.createdAt,
      escalationId: escalation?.escalationId,
      sessionId: escalation?.sessionId,
      ...escalation
    };
    console.log('Setting active room:', newActiveRoom);
    setActiveRoom(newActiveRoom);

    // Clear messages for new room AFTER setting active room
    console.log('Clearing messages array');
    setMessages([]);
    
    // Clear pending chat history for new room
    setPendingChatHistory([]);
    
    // Fetch session summary
    if (escalation?.sessionId) {
      try {
        console.log('Fetching session summary for session:', escalation.sessionId);
        const summaryResponse = await apiService.getSessionSummary(escalation.sessionId);
        if (summaryResponse.success) {
          console.log('Session summary loaded:', summaryResponse.summary);
          setChatSummary(summaryResponse.summary);
        } else {
          console.warn('Failed to load session summary:', summaryResponse.error);
          setChatSummary(null);
        }
      } catch (error) {
        console.error('Error fetching session summary:', error);
        setChatSummary(null);
      }
    } else {
      setChatSummary(null);
    }
    
    // Join the room
    console.log('Joining room via socket manager');
    socketManager.joinRoom(roomId);
    
    // Remove from escalations list
    setEscalations(prev => prev.filter(esc => esc.roomId !== roomId));

    setLoading(false);
    showNotification(`Joined room ${roomId}`, 'success');
  }, [escalations, showNotification]);

  const handleSendMessage = useCallback((roomId, message) => {
    if (!socketManager.isConnected()) {
      showNotification('Not connected to server', 'error');
      return;
    }

    // Add agent message to messages array immediately
    setMessages(prev => [...prev, {
      role: 'agent',
      content: message,
      timestamp: new Date().toISOString(),
      session_id: activeRoom?.sessionId
    }]);
    
    // Send to server
    socketManager.sendMessage(roomId, message);
  }, [showNotification, activeRoom]);

  const handleCloseSession = useCallback((roomId) => {
    if (!socketManager.isConnected()) {
      showNotification('Not connected to server', 'error');
      return;
    }

    if (window.confirm('Are you sure you want to close this session?')) {
      socketManager.closeSession(roomId, 'agent_001', 'Agent closed session');
      
      // Clear local state
      setActiveRoom(null);
      setChatSummary(null);
    }
  }, [showNotification]);

  const handleRefresh = useCallback(async () => {
    await requestEscalations();
  }, [requestEscalations]);

  const handleAssignEscalation = useCallback(async (escalationId, agentId = 'agent_001') => {
    try {
      const response = await apiService.assignEscalation(escalationId, agentId);
      if (response.success) {
        showNotification('Escalation assigned successfully', 'success');
        await requestEscalations(); // Refresh the list
      }
    } catch (error) {
      console.error('Error assigning escalation:', error);
      showNotification('Failed to assign escalation', 'error');
    }
  }, [requestEscalations, showNotification]);

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
            Human Agent Dashboard
          </Typography>
          
          {/* Connection Status */}
          <Box display="flex" alignItems="center" gap={2}>
            <Chip
              icon={isConnected ? <WifiIcon /> : <WifiOffIcon />}
              label={isConnected ? 'Connected' : 'Disconnected'}
              color={isConnected ? 'success' : 'error'}
              variant="filled"
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
                  loading={loading}
                  error={error}
                />
              </Grid>

              {/* Chat Window */}
              <Grid item xs={12} sx={{ flex: 1 }}>
                <ChatWindow
                  activeRoom={activeRoom}
                  messages={messages}
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
