import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  IconButton,
  List,
  ListItem,
  ListItemText,
  Avatar,
  Divider,
  Button,
  Chip,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  Send as SendIcon,
  Close as CloseIcon,
  Person as PersonIcon,
  SmartToy as BotIcon,
  Support as AgentIcon
} from '@mui/icons-material';

const ChatWindow = ({ 
  activeRoom, 
  onSendMessage,
  onCloseSession, 
  onJoinRoom,
  isConnected,
  loading 
}) => {
  const [message, setMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };


  useEffect(() => {
    if (activeRoom && inputRef.current) {
      inputRef.current.focus();
    }
  }, [activeRoom]);

  const handleSendMessage = () => {
    if (message.trim() && activeRoom && isConnected) {
      onSendMessage(activeRoom.roomId, message.trim());
      setMessage('');
      setIsTyping(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const handleInputChange = (event) => {
    setMessage(event.target.value);
    if (event.target.value.trim()) {
      setIsTyping(true);
    } else {
      setIsTyping(false);
    }
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    try {
      return new Date(timestamp).toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    } catch {
      return timestamp;
    }
  };

  const getMessageIcon = (messageType) => {
    switch (messageType) {
      case 'user':
        return <PersonIcon />;
      case 'agent':
        return <AgentIcon />;
      case 'bot':
      default:
        return <BotIcon />;
    }
  };

  const getMessageColor = (messageType) => {
    switch (messageType) {
      case 'user':
        return 'primary.main';
      case 'agent':
        return 'secondary.main';
      case 'bot':
      default:
        return 'grey.600';
    }
  };

  const getMessageAlignment = (messageType) => {
    switch (messageType) {
      case 'user':
        return 'flex-end';
      case 'agent':
        return 'flex-start';
      case 'bot':
      default:
        return 'flex-start';
    }
  };

  if (!activeRoom) {
    return (
      <Paper sx={{ 
        height: '100%', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        p: 3
      }}>
        <Box textAlign="center">
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No Active Chat
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Select a chat from the list to start helping a customer
          </Typography>
        </Box>
      </Paper>
    );
  }

  if (loading) {
    return (
      <Paper sx={{ 
        height: '100%', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center' 
      }}>
        <Box textAlign="center">
          <CircularProgress sx={{ mb: 2 }} />
          <Typography variant="body2" color="text.secondary">
            Loading...
          </Typography>
        </Box>
      </Paper>
    );
  }

  return (
    <Paper sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Chat Header */}
      <Box sx={{ 
        p: 2, 
        borderBottom: 1, 
        borderColor: 'divider',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        backgroundColor: 'grey.50'
      }}>
        <Box>
          <Typography variant="h6" gutterBottom>
            {activeRoom.userName || 'Customer'}
          </Typography>
          <Box display="flex" alignItems="center" gap={1}>
            <Chip 
              label={`Room: ${activeRoom.roomId}`} 
              size="small" 
              variant="outlined" 
            />
            <Chip 
              label={activeRoom.status || 'Active'} 
              size="small" 
              color={
                activeRoom.status === 'escalated' ? 'warning' :
                activeRoom.status === 'active' ? 'success' : 'default'
              }
            />
          </Box>
        </Box>
        <Button
          variant="outlined"
          color="error"
          startIcon={<CloseIcon />}
          onClick={() => onCloseSession(activeRoom.roomId)}
          disabled={!isConnected}
        >
          Close Session
        </Button>
      </Box>

      {/* Connection Status */}
      {!isConnected && (
        <Alert severity="warning" sx={{ m: 1 }}>
          Disconnected from server. Messages cannot be sent.
        </Alert>
      )}

      {/* Messages Area */}
      <Box sx={{ 
        flex: 1, 
        overflow: 'auto', 
        p: 1,
        backgroundColor: 'background.default'
      }}>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          height: '100%',
          textAlign: 'center',
          p: 2
        }}>
          <Box>
            <Typography variant="body1" color="text.secondary" gutterBottom>
              {activeRoom ? 'You are now connected to the customer' : 'Select a chat to begin'}
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {activeRoom ? 'Start the conversation by sending a message below' : 'No active chat session'}
            </Typography>
            {activeRoom && (
              <Box sx={{ mt: 2, p: 2, bgcolor: 'primary.light', borderRadius: 1 }}>
                <Typography variant="caption" color="primary.contrastText">
                  Customer: {activeRoom.userName || 'Unknown'}
                </Typography>
                <br />
                <Typography variant="caption" color="primary.contrastText">
                  Room: {activeRoom.roomId}
                </Typography>
                {activeRoom.reason && (
                  <>
                    <br />
                    <Typography variant="caption" color="primary.contrastText">
                      Reason: {activeRoom.reason}
                    </Typography>
                  </>
                )}
              </Box>
            )}
          </Box>
        </Box>
        <div ref={messagesEndRef} />
      </Box>

      {/* Message Input */}
      <Box sx={{ 
        p: 2, 
        borderTop: 1, 
        borderColor: 'divider',
        backgroundColor: 'background.paper'
      }}>
        <Box display="flex" gap={1} alignItems="flex-end">
          <TextField
            ref={inputRef}
            fullWidth
            multiline
            maxRows={4}
            placeholder="Type your message..."
            value={message}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            disabled={!isConnected}
            variant="outlined"
            size="small"
          />
          <IconButton
            color="primary"
            onClick={handleSendMessage}
            disabled={!message.trim() || !isConnected}
            sx={{ alignSelf: 'flex-end' }}
          >
            <SendIcon />
          </IconButton>
        </Box>
        {isTyping && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            Typing...
          </Typography>
        )}
      </Box>
    </Paper>
  );
};

export default ChatWindow;
