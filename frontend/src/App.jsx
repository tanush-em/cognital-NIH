import { useState, useEffect } from 'react'
import {
  Container,
  Box,
  Typography,
  Paper,
  Grid,
  AppBar,
  Toolbar,
  Chip,
  Alert,
  Snackbar,
} from '@mui/material'
import { SmartToy as BotIcon } from '@mui/icons-material'
import ChatWindow from './components/ChatWindow'
import FileUploader from './components/FileUploader'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

function App() {
  const [messages, setMessages] = useState([])
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [documentCount, setDocumentCount] = useState(0)
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' })

  useEffect(() => {
    // Load documents on mount
    loadDocuments()
  }, [])

  const loadDocuments = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/documents`)
      setUploadedFiles(response.data.documents || [])
      setDocumentCount(response.data.total_chunks || 0)
    } catch (error) {
      console.error('Error loading documents:', error)
    }
  }

  const handleFileUpload = async (file) => {
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setSnackbar({
        open: true,
        message: `File "${file.name}" uploaded successfully! Added ${response.data.chunks_added} chunks.`,
        severity: 'success',
      })

      // Reload documents list
      await loadDocuments()

      return response.data
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Upload failed'
      setSnackbar({
        open: true,
        message: `Upload failed: ${errorMessage}`,
        severity: 'error',
      })
      throw error
    }
  }

  const handleSendMessage = async (query) => {
    // Add user message to chat
    const userMessage = {
      id: Date.now(),
      type: 'user',
      text: query,
      timestamp: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, userMessage])

    try {
      const response = await axios.post(`${API_BASE_URL}/query`, { query })

      // Add AI response to chat
      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        text: response.data.answer,
        sources: response.data.source_documents,
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, aiMessage])
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Query failed'
      
      const errorMessageObj = {
        id: Date.now() + 1,
        type: 'ai',
        text: `Sorry, I encountered an error: ${errorMessage}`,
        error: true,
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, errorMessageObj])

      setSnackbar({
        open: true,
        message: `Query failed: ${errorMessage}`,
        severity: 'error',
      })
    }
  }

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false })
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', bgcolor: '#f5f5f5' }}>
      {/* App Bar */}
      <AppBar position="static" elevation={2}>
        <Toolbar>
          <BotIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            AI-First Customer Support
          </Typography>
          <Chip
            label={`${documentCount} chunks`}
            color="secondary"
            size="small"
            sx={{ bgcolor: 'rgba(255,255,255,0.2)' }}
          />
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4, flexGrow: 1 }}>
        <Grid container spacing={3}>
          {/* File Uploader Section */}
          <Grid item xs={12} md={4}>
            <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                Upload Documents
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Upload PDF or image files to build the knowledge base
              </Typography>
              <FileUploader onFileUpload={handleFileUpload} />

              {/* Uploaded Files List */}
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Uploaded Files ({uploadedFiles.length})
                </Typography>
                <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
                  {uploadedFiles.length === 0 ? (
                    <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                      No files uploaded yet
                    </Typography>
                  ) : (
                    uploadedFiles.map((file, index) => (
                      <Paper
                        key={index}
                        elevation={1}
                        sx={{
                          p: 1.5,
                          mb: 1,
                          bgcolor: '#f9f9f9',
                        }}
                      >
                        <Typography variant="body2" fontWeight="medium">
                          {file.filename}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {file.chunks} chunks • {new Date(file.upload_date).toLocaleDateString()}
                        </Typography>
                      </Paper>
                    ))
                  )}
                </Box>
              </Box>
            </Paper>
          </Grid>

          {/* Chat Window Section */}
          <Grid item xs={12} md={8}>
            <Paper elevation={3} sx={{ height: '700px', display: 'flex', flexDirection: 'column' }}>
              <Box sx={{ p: 2, bgcolor: '#f9f9f9', borderBottom: '1px solid #e0e0e0' }}>
                <Typography variant="h6">Chat Assistant</Typography>
                <Typography variant="body2" color="text.secondary">
                  Ask questions about your uploaded documents
                </Typography>
              </Box>
              <ChatWindow
                messages={messages}
                onSendMessage={handleSendMessage}
              />
            </Paper>
          </Grid>
        </Grid>
      </Container>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  )
}

export default App

