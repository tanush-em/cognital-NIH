import React, { useState, useEffect } from 'react';
import {
  Alert,
  Box,
  Typography,
  LinearProgress,
  Button,
  Rating,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import { Person, AccessTime, ThumbUp } from '@mui/icons-material';

const EscalationNotification = ({ 
  isVisible, 
  escalationStatus, 
  onClose,
  estimatedWaitTime = 2 // minutes
}) => {
  const [waitTime, setWaitTime] = useState(estimatedWaitTime);
  const [showSurvey, setShowSurvey] = useState(false);
  const [rating, setRating] = useState(0);
  const [feedback, setFeedback] = useState('');

  useEffect(() => {
    if (escalationStatus === 'escalated') {
      // Start countdown
      const interval = setInterval(() => {
        setWaitTime(prev => {
          if (prev <= 0) {
            clearInterval(interval);
            return 0;
          }
          return prev - 0.1;
        });
      }, 100);

      return () => clearInterval(interval);
    }
  }, [escalationStatus]);

  const handleSurveySubmit = () => {
    // Here you would send the survey data to the backend
    console.log('Survey submitted:', { rating, feedback });
    setShowSurvey(false);
    setRating(0);
    setFeedback('');
  };

  const getAlertSeverity = () => {
    switch (escalationStatus) {
      case 'agent_joined':
        return 'success';
      case 'escalated':
        return 'info';
      default:
        return 'info';
    }
  };

  const getAlertMessage = () => {
    switch (escalationStatus) {
      case 'agent_joined':
        return 'A human agent has joined the conversation and will assist you shortly.';
      case 'escalated':
        return `Your request has been escalated to a human agent. Estimated wait time: ${Math.ceil(waitTime)} minutes.`;
      default:
        return 'Connecting you to a specialist...';
    }
  };

  if (!isVisible) return null;

  return (
    <>
      <Alert 
        severity={getAlertSeverity()}
        sx={{ margin: 1 }}
        action={
          escalationStatus === 'agent_joined' && (
            <Button
              color="inherit"
              size="small"
              onClick={() => setShowSurvey(true)}
              startIcon={<ThumbUp />}
            >
              Rate Experience
            </Button>
          )
        }
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Person />
          <Typography variant="body2">
            {getAlertMessage()}
          </Typography>
        </Box>
        
        {escalationStatus === 'escalated' && waitTime > 0 && (
          <Box sx={{ mt: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <AccessTime sx={{ fontSize: 16 }} />
              <Typography variant="caption">
                Estimated wait time: {Math.ceil(waitTime)} minutes
              </Typography>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={((estimatedWaitTime - waitTime) / estimatedWaitTime) * 100}
              sx={{ height: 4, borderRadius: 2 }}
            />
          </Box>
        )}
      </Alert>

      {/* Satisfaction Survey Dialog */}
      <Dialog open={showSurvey} onClose={() => setShowSurvey(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Rate Your Experience</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" gutterBottom>
              How would you rate your experience with our support?
            </Typography>
            <Rating
              value={rating}
              onChange={(event, newValue) => setRating(newValue)}
              size="large"
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Additional feedback (optional)"
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="Tell us how we can improve..."
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSurvey(false)}>Cancel</Button>
          <Button onClick={handleSurveySubmit} variant="contained">
            Submit
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default EscalationNotification;
