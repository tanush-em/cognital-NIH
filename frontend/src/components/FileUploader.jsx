import { useState } from 'react'
import {
  Box,
  Button,
  Typography,
  LinearProgress,
  Alert,
} from '@mui/material'
import {
  CloudUpload as UploadIcon,
  Description as FileIcon,
} from '@mui/icons-material'

function FileUploader({ onFileUpload }) {
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)

  const handleFileSelect = (event) => {
    const file = event.target.files[0]
    if (file) {
      // Validate file type
      const validTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff']
      if (!validTypes.includes(file.type) && !file.name.match(/\.(pdf|jpg|jpeg|png|bmp|tiff)$/i)) {
        setError('Please select a valid PDF or image file (PDF, JPG, PNG, BMP, TIFF)')
        return
      }

      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB')
        return
      }

      setSelectedFile(file)
      setError(null)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    setUploading(true)
    setError(null)

    try {
      await onFileUpload(selectedFile)
      setSelectedFile(null)
      // Reset the file input
      document.getElementById('file-input').value = ''
    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  return (
    <Box>
      {/* File Input (Hidden) */}
      <input
        id="file-input"
        type="file"
        accept=".pdf,.jpg,.jpeg,.png,.bmp,.tiff"
        onChange={handleFileSelect}
        style={{ display: 'none' }}
      />

      {/* Upload Button */}
      <Button
        variant="contained"
        component="label"
        htmlFor="file-input"
        fullWidth
        startIcon={<UploadIcon />}
        disabled={uploading}
        sx={{ mb: 2 }}
      >
        Choose File
      </Button>

      {/* Selected File Display */}
      {selectedFile && (
        <Box
          sx={{
            p: 2,
            mb: 2,
            border: '2px dashed',
            borderColor: 'primary.main',
            borderRadius: 1,
            bgcolor: 'primary.lighter',
            display: 'flex',
            alignItems: 'center',
            gap: 1,
          }}
        >
          <FileIcon color="primary" />
          <Box sx={{ flexGrow: 1, minWidth: 0 }}>
            <Typography variant="body2" fontWeight="medium" noWrap>
              {selectedFile.name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {(selectedFile.size / 1024).toFixed(2)} KB
            </Typography>
          </Box>
        </Box>
      )}

      {/* Upload Progress */}
      {uploading && (
        <Box sx={{ mb: 2 }}>
          <LinearProgress />
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
            Processing file...
          </Typography>
        </Box>
      )}

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Upload Action Button */}
      {selectedFile && !uploading && (
        <Button
          variant="contained"
          color="success"
          fullWidth
          onClick={handleUpload}
          startIcon={<UploadIcon />}
        >
          Upload and Process
        </Button>
      )}

      {/* Help Text */}
      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2 }}>
        Supported formats: PDF, JPG, PNG, BMP, TIFF (Max 10MB)
      </Typography>
    </Box>
  )
}

export default FileUploader

