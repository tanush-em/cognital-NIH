import React from 'react';
import { Box, Typography, Avatar } from '@mui/material';
import { Person, SmartToy, SupportAgent } from '@mui/icons-material';

const MessageBubble = ({ message, sender, timestamp, isTyping = false }) => {
  const isUser = sender === 'user';
  const isAgent = sender === 'agent';
  const isAI = sender === 'ai';

  const getAvatar = () => {
    if (isUser) return <Person />;
    if (isAgent) return <SupportAgent />;
    if (isAI) return <SmartToy />;
    return <Person />;
  };

  const getSenderName = () => {
    if (isUser) return 'You';
    if (isAgent) return 'Support Agent';
    if (isAI) return 'AI Assistant';
    return 'Unknown';
  };

  const getBubbleStyle = () => {
    const baseStyle = {
      maxWidth: '70%',
      margin: '8px 0',
      padding: '12px 16px',
      borderRadius: '18px',
      wordWrap: 'break-word',
      position: 'relative'
    };

    if (isUser) {
      return {
        ...baseStyle,
        backgroundColor: '#007bff',
        color: 'white',
        marginLeft: 'auto',
        borderBottomRightRadius: '4px'
      };
    } else {
      return {
        ...baseStyle,
        backgroundColor: '#f1f3f4',
        color: '#333',
        marginRight: 'auto',
        borderBottomLeftRadius: '4px'
      };
    }
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: isUser ? 'row-reverse' : 'row',
        alignItems: 'flex-start',
        gap: 1,
        marginBottom: 1
      }}
    >
      {!isUser && (
        <Avatar
          sx={{
            width: 32,
            height: 32,
            backgroundColor: isAgent ? '#4caf50' : '#2196f3',
            fontSize: '16px'
          }}
        >
          {getAvatar()}
        </Avatar>
      )}
      
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: isUser ? 'flex-end' : 'flex-start' }}>
        {!isUser && (
          <Typography
            variant="caption"
            sx={{
              color: '#666',
              fontSize: '0.75rem',
              marginBottom: 0.5
            }}
          >
            {getSenderName()}
          </Typography>
        )}
        
        <Box sx={getBubbleStyle()}>
          {isTyping ? (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
                {message}
              </Typography>
              <Box
                sx={{
                  display: 'flex',
                  gap: 0.5,
                  '& > div': {
                    width: 4,
                    height: 4,
                    backgroundColor: '#666',
                    borderRadius: '50%',
                    animation: 'typing 1.4s infinite ease-in-out',
                    '&:nth-of-type(1)': { animationDelay: '0s' },
                    '&:nth-of-type(2)': { animationDelay: '0.2s' },
                    '&:nth-of-type(3)': { animationDelay: '0.4s' }
                  }
                }}
              >
                <div></div>
                <div></div>
                <div></div>
              </Box>
            </Box>
          ) : (
            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
              {message}
            </Typography>
          )}
        </Box>
        
        {timestamp && (
          <Typography
            variant="caption"
            sx={{
              color: '#999',
              fontSize: '0.7rem',
              marginTop: 0.5,
              marginLeft: isUser ? 0 : 1,
              marginRight: isUser ? 1 : 0
            }}
          >
            {formatTimestamp(timestamp)}
          </Typography>
        )}
      </Box>
      
      {isUser && (
        <Avatar
          sx={{
            width: 32,
            height: 32,
            backgroundColor: '#007bff',
            fontSize: '16px'
          }}
        >
          {getAvatar()}
        </Avatar>
      )}
    </Box>
  );
};

export default MessageBubble;
