import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  Fade
} from '@mui/material';
import { Send, Phone } from '@mui/icons-material';
import MessageBubble from './MessageBubble';
import socketManager from '../socket';

const ChatWindow = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [escalationMessage, setEscalationMessage] = useState('');
  const [showEscalation, setShowEscalation] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Initialize socket connection
  useEffect(() => {
    const socket = socketManager.connect();
    
    // Check connection status
    const checkConnection = () => {
      setIsConnected(socketManager.isSocketConnected());
    };

    checkConnection();
    const interval = setInterval(checkConnection, 1000);

    // Listen for messages
    socketManager.onMessage((data) => {
      console.log('Received message:', data);
      
      if (data.type === 'escalation') {
        setEscalationMessage(data.message || 'Connecting you to a specialist...');
        setShowEscalation(true);
        setIsTyping(false);
        
        // Hide escalation message after 3 seconds
        setTimeout(() => {
          setShowEscalation(false);
        }, 3000);
      } else {
        const newMessage = {
          id: Date.now() + Math.random(),
          message: data.message || data.text,
          sender: data.sender || (data.type === 'agent' ? 'agent' : 'ai'),
          timestamp: data.timestamp || new Date().toISOString()
        };
        
        setMessages(prev => [...prev, newMessage]);
        setIsTyping(false);
      }
    });

    // Listen for typing indicators
    socketManager.onTypingIndicator((data) => {
      if (data.isTyping) {
        setIsTyping(true);
      } else {
        setIsTyping(false);
      }
    });

    // Add welcome message
    setMessages([{
      id: 1,
      message: "Hello! I'm your AI telecom support assistant. How can I help you today?",
      sender: 'ai',
      timestamp: new Date().toISOString()
    }]);

    return () => {
      clearInterval(interval);
    };
  }, []);

  const handleSendMessage = () => {
    if (!inputMessage.trim() || !isConnected) return;

    const userMessage = {
      id: Date.now(),
      message: inputMessage.trim(),
      sender: 'user',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    socketManager.sendMessage(inputMessage.trim());
    setInputMessage('');
    setIsTyping(true);

    // Focus back on input
    setTimeout(() => {
      inputRef.current?.focus();
    }, 100);
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const handleInputChange = (event) => {
    setInputMessage(event.target.value);
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        maxHeight: '100vh',
        backgroundColor: '#f5f5f5'
      }}
    >
      {/* Header */}
      <Paper
        elevation={2}
        sx={{
          padding: 2,
          backgroundColor: '#1976d2',
          color: 'white',
          borderRadius: 0
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6" component="h1">
            <Phone sx={{ marginRight: 1, verticalAlign: 'middle' }} />
            Telecom Support Assistant
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box
              sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                backgroundColor: isConnected ? '#4caf50' : '#f44336'
              }}
            />
            <Typography variant="caption">
              {isConnected ? 'Connected' : 'Disconnected'}
            </Typography>
          </Box>
        </Box>
      </Paper>

      {/* Escalation Alert */}
      <Fade in={showEscalation}>
        <Alert
          severity="info"
          sx={{
            margin: 1,
            backgroundColor: '#e3f2fd',
            color: '#1976d2'
          }}
        >
          {escalationMessage}
        </Alert>
      </Fade>

      {/* Messages Container */}
      <Box
        sx={{
          flex: 1,
          overflow: 'auto',
          padding: 2,
          display: 'flex',
          flexDirection: 'column',
          gap: 1
        }}
      >
        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            message={msg.message}
            sender={msg.sender}
            timestamp={msg.timestamp}
          />
        ))}
        
        {/* Typing Indicator */}
        {isTyping && (
          <MessageBubble
            message="AI is typing..."
            sender="ai"
            isTyping={true}
          />
        )}
        
        <div ref={messagesEndRef} />
      </Box>

      {/* Input Area */}
      <Paper
        elevation={3}
        sx={{
          padding: 2,
          backgroundColor: 'white',
          borderRadius: 0,
          borderTop: '1px solid #e0e0e0'
        }}
      >
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
          <TextField
            ref={inputRef}
            fullWidth
            multiline
            maxRows={4}
            placeholder="Type your message here..."
            value={inputMessage}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            disabled={!isConnected}
            variant="outlined"
            size="small"
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: '20px',
                backgroundColor: '#f5f5f5'
              }
            }}
          />
          <Button
            variant="contained"
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || !isConnected}
            sx={{
              minWidth: '48px',
              height: '48px',
              borderRadius: '50%',
              backgroundColor: '#1976d2',
              '&:hover': {
                backgroundColor: '#1565c0'
              }
            }}
          >
            <Send />
          </Button>
        </Box>
        
        {!isConnected && (
          <Typography
            variant="caption"
            color="error"
            sx={{ display: 'block', marginTop: 1, textAlign: 'center' }}
          >
            Unable to connect to server. Please check your connection.
          </Typography>
        )}
      </Paper>
    </Box>
  );
};

export default ChatWindow;
