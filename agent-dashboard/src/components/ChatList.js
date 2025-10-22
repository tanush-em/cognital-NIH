import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Chip,
  IconButton,
  Divider,
  Alert,
  CircularProgress,
  Badge,
  Tooltip
} from '@mui/material';
import {
  Person as PersonIcon,
  Schedule as ScheduleIcon,
  Refresh as RefreshIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon
} from '@mui/icons-material';

const ChatList = ({ 
  escalations, 
  activeRoom, 
  onJoinRoom, 
  onRefresh, 
  loading, 
  error,
  isConnected 
}) => {
  const [selectedRoom, setSelectedRoom] = useState(null);

  useEffect(() => {
    if (activeRoom) {
      setSelectedRoom(activeRoom.roomId);
    } else {
      setSelectedRoom(null);
    }
  }, [activeRoom]);

  const handleJoinRoom = (room) => {
    setSelectedRoom(room.roomId);
    onJoinRoom(room.roomId);
  };

  const formatTimeAgo = (timestamp) => {
    if (!timestamp) return 'Unknown';
    try {
      const now = new Date();
      const time = new Date(timestamp);
      const diffInSeconds = Math.floor((now - time) / 1000);
      
      if (diffInSeconds < 60) return 'Just now';
      if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
      if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
      return `${Math.floor(diffInSeconds / 86400)}d ago`;
    } catch {
      return timestamp;
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'escalated':
        return 'warning';
      case 'waiting':
        return 'info';
      case 'active':
        return 'success';
      case 'closed':
        return 'default';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case 'escalated':
        return <WarningIcon />;
      case 'waiting':
        return <ScheduleIcon />;
      case 'active':
        return <CheckCircleIcon />;
      case 'closed':
        return <CancelIcon />;
      default:
        return <ScheduleIcon />;
    }
  };

  const sortEscalations = (escalations) => {
    if (!escalations) return [];
    
    return [...escalations].sort((a, b) => {
      // Priority sorting
      const priorityOrder = { high: 3, medium: 2, low: 1 };
      const aPriority = priorityOrder[a.priority?.toLowerCase()] || 0;
      const bPriority = priorityOrder[b.priority?.toLowerCase()] || 0;
      
      if (aPriority !== bPriority) {
        return bPriority - aPriority;
      }
      
      // Time sorting (newest first)
      const aTime = new Date(a.escalatedAt || a.createdAt || 0);
      const bTime = new Date(b.escalatedAt || b.createdAt || 0);
      return bTime - aTime;
    });
  };

  if (error) {
    return (
      <Paper sx={{ height: '100%', p: 2 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          <Typography variant="body2">
            Failed to load escalations: {error}
          </Typography>
        </Alert>
        <Box display="flex" justifyContent="center">
          <IconButton onClick={onRefresh} color="primary">
            <RefreshIcon />
          </IconButton>
        </Box>
      </Paper>
    );
  }

  return (
    <Paper sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ 
        p: 2, 
        borderBottom: 1, 
        borderColor: 'divider',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        backgroundColor: 'grey.50'
      }}>
        <Typography variant="h6">
          Pending Chats
        </Typography>
        <Box display="flex" alignItems="center" gap={1}>
          {!isConnected && (
            <Chip 
              label="Disconnected" 
              size="small" 
              color="error" 
              variant="outlined" 
            />
          )}
          <IconButton 
            onClick={onRefresh} 
            color="primary"
            disabled={loading}
            size="small"
          >
            <RefreshIcon />
          </IconButton>
        </Box>
      </Box>

      {/* Connection Status */}
      {!isConnected && (
        <Alert severity="warning" sx={{ m: 1, mb: 0 }}>
          Disconnected from server
        </Alert>
      )}

      {/* Loading State */}
      {loading && (
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          p: 3 
        }}>
          <CircularProgress size={24} sx={{ mr: 1 }} />
          <Typography variant="body2" color="text.secondary">
            Loading escalations...
          </Typography>
        </Box>
      )}

      {/* Escalations List */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        {escalations && escalations.length > 0 ? (
          <List sx={{ p: 0 }}>
            {sortEscalations(escalations).map((room, index) => (
              <React.Fragment key={room.uniqueKey || room.roomId}>
                <ListItem disablePadding>
                  <ListItemButton
                    selected={selectedRoom === room.roomId}
                    onClick={() => handleJoinRoom(room)}
                    disabled={!isConnected}
                    sx={{
                      py: 2,
                      px: 2,
                      '&.Mui-selected': {
                        backgroundColor: 'primary.light',
                        '&:hover': {
                          backgroundColor: 'primary.light',
                        }
                      }
                    }}
                  >
                    <ListItemAvatar>
                      <Badge
                        overlap="circular"
                        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                        badgeContent={
                          room.priority === 'high' ? (
                            <Chip
                              label="!"
                              size="small"
                              color="error"
                              sx={{ 
                                minWidth: 16, 
                                height: 16, 
                                fontSize: '0.75rem' 
                              }}
                            />
                          ) : null
                        }
                      >
                        <Avatar sx={{ bgcolor: 'primary.main' }}>
                          <PersonIcon />
                        </Avatar>
                      </Badge>
                    </ListItemAvatar>
                    
                    <ListItemText
                      primary={
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="subtitle1" noWrap component="span">
                            {room.userName || 'Customer'}
                          </Typography>
                          <Chip
                            icon={getStatusIcon(room.status)}
                            label={room.status || 'Unknown'}
                            size="small"
                            color={getStatusColor(room.status)}
                            variant="outlined"
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary" noWrap component="div">
                            Room: {room.roomId}
                          </Typography>
                          <Box display="flex" alignItems="center" gap={1} mt={0.5}>
                            <Typography variant="caption" color="text.secondary" component="span">
                              {formatTimeAgo(room.escalatedAt || room.createdAt)}
                            </Typography>
                            {room.priority && (
                              <Chip
                                label={room.priority}
                                size="small"
                                color={getPriorityColor(room.priority)}
                                variant="outlined"
                              />
                            )}
                          </Box>
                          {room.lastMessage && (
                            <Typography 
                              variant="caption" 
                              color="text.secondary"
                              component="div"
                              sx={{ 
                                display: 'block',
                                mt: 0.5,
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap'
                              }}
                            >
                              {room.lastMessage}
                            </Typography>
                          )}
                        </Box>
                      }
                    />
                  </ListItemButton>
                </ListItem>
                {index < escalations.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        ) : (
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center', 
            height: '100%',
            textAlign: 'center',
            p: 3
          }}>
            <Box>
              <Typography variant="body1" color="text.secondary" gutterBottom>
                No pending chats
              </Typography>
              <Typography variant="body2" color="text.secondary">
                All customers are being helped or no escalations are pending
              </Typography>
            </Box>
          </Box>
        )}
      </Box>

      {/* Footer Info */}
      <Box sx={{ 
        p: 2, 
        borderTop: 1, 
        borderColor: 'divider',
        backgroundColor: 'grey.50'
      }}>
        <Typography variant="caption" color="text.secondary" textAlign="center" display="block">
          {escalations ? `${escalations.length} pending chat${escalations.length !== 1 ? 's' : ''}` : '0 pending chats'}
        </Typography>
      </Box>
    </Paper>
  );
};

export default ChatList;
