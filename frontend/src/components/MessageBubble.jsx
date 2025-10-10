import { Box, Typography, Paper, Chip, Accordion, AccordionSummary, AccordionDetails } from '@mui/material'
import { Person as UserIcon, SmartToy as BotIcon, ExpandMore as ExpandMoreIcon } from '@mui/icons-material'

function MessageBubble({ message }) {
  const isUser = message.type === 'user'
  const isError = message.error === true

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        mb: 2,
      }}
    >
      <Box
        sx={{
          display: 'flex',
          flexDirection: isUser ? 'row-reverse' : 'row',
          alignItems: 'flex-start',
          maxWidth: '75%',
        }}
      >
        {/* Avatar */}
        <Box
          sx={{
            width: 40,
            height: 40,
            borderRadius: '50%',
            bgcolor: isUser ? 'primary.main' : isError ? 'error.main' : 'secondary.main',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            flexShrink: 0,
            mx: 1,
          }}
        >
          {isUser ? <UserIcon /> : <BotIcon />}
        </Box>

        {/* Message Content */}
        <Box sx={{ flexGrow: 1 }}>
          <Paper
            elevation={2}
            sx={{
              p: 2,
              bgcolor: isUser ? 'primary.light' : isError ? '#ffebee' : 'white',
              color: isUser ? 'primary.contrastText' : 'text.primary',
            }}
          >
            <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
              {message.text}
            </Typography>

            {/* Timestamp */}
            <Typography
              variant="caption"
              sx={{
                display: 'block',
                mt: 1,
                opacity: 0.7,
                textAlign: 'right',
              }}
            >
              {new Date(message.timestamp).toLocaleTimeString()}
            </Typography>
          </Paper>

          {/* Source Documents */}
          {message.sources && message.sources.length > 0 && (
            <Box sx={{ mt: 1 }}>
              <Accordion elevation={1}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="caption">
                    <Chip
                      label={`${message.sources.length} source(s)`}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  {message.sources.map((source, index) => (
                    <Paper
                      key={index}
                      elevation={0}
                      sx={{
                        p: 1.5,
                        mb: 1,
                        bgcolor: '#f5f5f5',
                        border: '1px solid #e0e0e0',
                      }}
                    >
                      <Typography variant="caption" color="text.secondary" fontWeight="bold">
                        Source {index + 1}
                        {source.metadata?.filename && ` - ${source.metadata.filename}`}
                      </Typography>
                      <Typography variant="body2" sx={{ mt: 0.5, fontSize: '0.85rem' }}>
                        {source.content.substring(0, 200)}
                        {source.content.length > 200 && '...'}
                      </Typography>
                    </Paper>
                  ))}
                </AccordionDetails>
              </Accordion>
            </Box>
          )}
        </Box>
      </Box>
    </Box>
  )
}

export default MessageBubble

