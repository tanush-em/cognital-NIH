import React, { useState } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  LinearProgress,
  Alert,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction
} from '@mui/material';
import {
  CloudUpload,
  Close,
  Description,
  CheckCircle,
  Error
} from '@mui/icons-material';

const PDFUpload = ({ open, onClose }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [error, setError] = useState('');

  const handleFileUpload = async (event) => {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    setUploading(true);
    setError('');
    setUploadStatus('Uploading PDF files...');
    setUploadProgress(0);

    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        
        // Validate file type
        if (file.type !== 'application/pdf') {
          throw new Error(`${file.name} is not a PDF file`);
        }

        // Validate file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
          throw new Error(`${file.name} is too large. Maximum size is 10MB`);
        }

        const formData = new FormData();
        formData.append('file', file);

        setUploadStatus(`Uploading ${file.name}...`);
        setUploadProgress((i / files.length) * 100);

        const response = await fetch('http://localhost:5000/api/upload-pdf', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.message || 'Upload failed');
        }

        const result = await response.json();
        setUploadedFiles(prev => [...prev, {
          name: file.name,
          size: file.size,
          status: 'success',
          message: result.message
        }]);
      }

      setUploadProgress(100);
      setUploadStatus('All files uploaded successfully!');
      
      // Reload PDFs to update the knowledge base
      await reloadPDFs();
      
    } catch (err) {
      setError(err.message);
      setUploadStatus('Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const reloadPDFs = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/reload-pdfs', {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to reload PDFs');
      }

      const result = await response.json();
      console.log('PDFs reloaded:', result);
    } catch (err) {
      console.error('Error reloading PDFs:', err);
    }
  };

  const getPDFList = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/pdfs');
      if (response.ok) {
        const data = await response.json();
        return data.pdfs || [];
      }
    } catch (err) {
      console.error('Error fetching PDF list:', err);
    }
    return [];
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleClose = () => {
    setUploading(false);
    setUploadProgress(0);
    setUploadStatus('');
    setUploadedFiles([]);
    setError('');
    onClose();
  };

  return (
    <Dialog 
      open={open} 
      onClose={handleClose}
      maxWidth="md"
      fullWidth
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Description sx={{ marginRight: 1, color: '#1976d2' }} />
            <Typography variant="h6">Upload PDF Documents</Typography>
          </Box>
          <IconButton onClick={handleClose}>
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ marginBottom: 3 }}>
          <Typography variant="body2" color="text.secondary" sx={{ marginBottom: 2 }}>
            Upload PDF documents to enhance the AI's knowledge base. The system will automatically 
            extract text using OCR for scanned documents.
          </Typography>
          
          <input
            accept=".pdf"
            style={{ display: 'none' }}
            id="pdf-upload-input"
            multiple
            type="file"
            onChange={handleFileUpload}
            disabled={uploading}
          />
          
          <label htmlFor="pdf-upload-input">
            <Button
              variant="contained"
              component="span"
              startIcon={<CloudUpload />}
              disabled={uploading}
              sx={{
                backgroundColor: '#1976d2',
                '&:hover': {
                  backgroundColor: '#1565c0'
                }
              }}
            >
              {uploading ? 'Uploading...' : 'Select PDF Files'}
            </Button>
          </label>
        </Box>

        {uploading && (
          <Box sx={{ marginBottom: 2 }}>
            <Typography variant="body2" sx={{ marginBottom: 1 }}>
              {uploadStatus}
            </Typography>
            <LinearProgress 
              variant="determinate" 
              value={uploadProgress}
              sx={{ height: 8, borderRadius: 4 }}
            />
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ marginBottom: 2 }}>
            {error}
          </Alert>
        )}

        {uploadedFiles.length > 0 && (
          <Box>
            <Typography variant="subtitle1" sx={{ marginBottom: 1 }}>
              Uploaded Files:
            </Typography>
            <List dense>
              {uploadedFiles.map((file, index) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={file.name}
                    secondary={`${formatFileSize(file.size)} - ${file.status}`}
                  />
                  <ListItemSecondaryAction>
                    {file.status === 'success' ? (
                      <CheckCircle color="success" />
                    ) : (
                      <Error color="error" />
                    )}
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </Box>
        )}
      </DialogContent>
      
      <DialogActions>
        <Button onClick={handleClose} disabled={uploading}>
          {uploading ? 'Uploading...' : 'Close'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default PDFUpload;
