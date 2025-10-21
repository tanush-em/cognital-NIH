import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Divider,
  CircularProgress,
  Alert,
  Grid,
  Paper,
  LinearProgress
} from '@mui/material';
import {
  Summarize as SummaryIcon,
  Person as PersonIcon,
  Schedule as ScheduleIcon,
  Tag as TagIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  Speed as SpeedIcon,
  Warning as WarningIcon
} from '@mui/icons-material';

const ChatSummary = ({ summary, analytics, loading, error }) => {
  if (loading) {
    return (
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="center" py={2}>
            <CircularProgress size={24} sx={{ mr: 1 }} />
            <Typography variant="body2" color="text.secondary">
              Generating summary...
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Alert severity="error">
            <Typography variant="body2">
              Failed to load chat summary: {error}
            </Typography>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!summary && !analytics) {
    return (
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="body2" color="text.secondary" textAlign="center">
            No summary or analytics available
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return dateString;
    }
  };

  return (
    <Box sx={{ mb: 2 }}>
      {/* Analytics Dashboard */}
      {analytics && (
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Box display="flex" alignItems="center" mb={2}>
              <AssessmentIcon sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6" component="h2">
                Analytics Dashboard
              </Typography>
            </Box>
            
            <Divider sx={{ mb: 2 }} />
            
            <Grid container spacing={2}>
              {/* Automation Rate */}
              <Grid item xs={12} sm={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <SpeedIcon sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
                  <Typography variant="h4" color="success.main">
                    {analytics.session_stats?.automation_rate || 0}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Automation Rate
                  </Typography>
                </Paper>
              </Grid>
              
              {/* Total Sessions */}
              <Grid item xs={12} sm={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <TrendingUpIcon sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
                  <Typography variant="h4" color="info.main">
                    {analytics.session_stats?.total_sessions || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Sessions
                  </Typography>
                </Paper>
              </Grid>
              
              {/* Escalated Sessions */}
              <Grid item xs={12} sm={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <WarningIcon sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
                  <Typography variant="h4" color="warning.main">
                    {analytics.session_stats?.escalated_sessions || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Escalated
                  </Typography>
                </Paper>
              </Grid>
              
              {/* Escalation Rate */}
              <Grid item xs={12} sm={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4" color="error.main">
                    {analytics.escalation_analytics?.escalation_rate || 0}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Escalation Rate
                  </Typography>
                </Paper>
              </Grid>
            </Grid>
            
            {/* Escalation Categories */}
            {analytics.escalation_analytics?.category_breakdown && (
              <Box mt={3}>
                <Typography variant="subtitle1" gutterBottom>
                  Escalation Categories
                </Typography>
                <Grid container spacing={1}>
                  {Object.entries(analytics.escalation_analytics.category_breakdown).map(([category, count]) => (
                    <Grid item key={category}>
                      <Chip
                        label={`${category}: ${count}`}
                        variant="outlined"
                        color="primary"
                      />
                    </Grid>
                  ))}
                </Grid>
              </Box>
            )}
            
            {/* Priority Breakdown */}
            {analytics.escalation_analytics?.priority_breakdown && (
              <Box mt={2}>
                <Typography variant="subtitle1" gutterBottom>
                  Priority Breakdown
                </Typography>
                <Grid container spacing={1}>
                  {Object.entries(analytics.escalation_analytics.priority_breakdown).map(([priority, count]) => (
                    <Grid item key={priority}>
                      <Chip
                        label={`${priority}: ${count}`}
                        variant="filled"
                        color={
                          priority === 'critical' ? 'error' :
                          priority === 'high' ? 'warning' :
                          priority === 'medium' ? 'info' : 'default'
                        }
                      />
                    </Grid>
                  ))}
                </Grid>
              </Box>
            )}
          </CardContent>
        </Card>
      )}
      
      {/* Chat Summary */}
      {summary && (
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Box display="flex" alignItems="center" mb={2}>
              <SummaryIcon sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6" component="h2">
                Chat Summary
              </Typography>
            </Box>

        <Divider sx={{ mb: 2 }} />

        {/* User Information */}
        <Box mb={2}>
          <Box display="flex" alignItems="center" mb={1}>
            <PersonIcon sx={{ mr: 1, fontSize: 20, color: 'text.secondary' }} />
            <Typography variant="subtitle2" color="text.secondary">
              Customer Information
            </Typography>
          </Box>
          <Typography variant="body2" sx={{ ml: 3 }}>
            <strong>Name:</strong> {summary.user?.name || 'Unknown'}
          </Typography>
          <Typography variant="body2" sx={{ ml: 3 }}>
            <strong>Phone:</strong> {summary.user?.phone || 'Not provided'}
          </Typography>
          {summary.user?.email && (
            <Typography variant="body2" sx={{ ml: 3 }}>
              <strong>Email:</strong> {summary.user.email}
            </Typography>
          )}
        </Box>

        {/* Session Details */}
        <Box mb={2}>
          <Box display="flex" alignItems="center" mb={1}>
            <ScheduleIcon sx={{ mr: 1, fontSize: 20, color: 'text.secondary' }} />
            <Typography variant="subtitle2" color="text.secondary">
              Session Details
            </Typography>
          </Box>
          <Typography variant="body2" sx={{ ml: 3 }}>
            <strong>Started:</strong> {formatDate(summary.session?.startTime)}
          </Typography>
          <Typography variant="body2" sx={{ ml: 3 }}>
            <strong>Duration:</strong> {summary.session?.duration || 'Unknown'}
          </Typography>
          <Typography variant="body2" sx={{ ml: 3 }}>
            <strong>Messages:</strong> {summary.session?.messageCount || 0}
          </Typography>
        </Box>

        {/* Issue Categories */}
        {summary.issues && summary.issues.length > 0 && (
          <Box mb={2}>
            <Box display="flex" alignItems="center" mb={1}>
              <TagIcon sx={{ mr: 1, fontSize: 20, color: 'text.secondary' }} />
              <Typography variant="subtitle2" color="text.secondary">
                Issue Categories
              </Typography>
            </Box>
            <Box sx={{ ml: 3 }}>
              {summary.issues.map((issue, index) => (
                <Chip
                  key={index}
                  label={issue}
                  size="small"
                  variant="outlined"
                  sx={{ mr: 1, mb: 1 }}
                />
              ))}
            </Box>
          </Box>
        )}

        {/* AI Summary */}
        <Box mb={2}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            AI Summary
          </Typography>
          <Typography variant="body2" sx={{ 
            backgroundColor: 'grey.50', 
            p: 2, 
            borderRadius: 1,
            border: '1px solid',
            borderColor: 'grey.200'
          }}>
            {summary.summary || 'No summary generated yet.'}
          </Typography>
        </Box>

        {/* Key Points */}
        {summary.keyPoints && summary.keyPoints.length > 0 && (
          <Box>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Key Points
            </Typography>
            <Box component="ul" sx={{ pl: 2, m: 0 }}>
              {summary.keyPoints.map((point, index) => (
                <Typography
                  key={index}
                  component="li"
                  variant="body2"
                  sx={{ mb: 0.5 }}
                >
                  {point}
                </Typography>
              ))}
            </Box>
          </Box>
        )}

        {/* Sentiment */}
        {summary.sentiment && (
          <Box mt={2}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Customer Sentiment
            </Typography>
            <Chip
              label={summary.sentiment}
              size="small"
              color={
                summary.sentiment === 'positive' ? 'success' :
                summary.sentiment === 'negative' ? 'error' :
                summary.sentiment === 'neutral' ? 'default' : 'warning'
              }
              variant="filled"
            />
          </Box>
        )}

        {/* Escalation Reason */}
        {summary.escalationReason && (
          <Box mt={2}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Escalation Reason
            </Typography>
            <Alert severity="warning" variant="outlined">
              <Typography variant="body2">
                {summary.escalationReason}
              </Typography>
            </Alert>
          </Box>
        )}
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default ChatSummary;
