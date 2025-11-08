import React, { useState, useEffect } from 'react';
import { Container, Box, Typography, Button, Paper, LinearProgress, Alert, Select, MenuItem, FormControl, InputLabel, List, ListItem, ListItemText } from '@mui/material';
import { CloudUpload } from '@mui/icons-material';
import axios from 'axios';
import AuthService from '../services/auth';

const API_URL = process.env.NODE_ENV === 'production' 
  ? '/api/v1'
  : 'http://localhost:8000/api/v1';

export default function FileUpload() {
  const [file, setFile] = useState(null);
  const [credentials, setCredentials] = useState([]);
  const [selectedCredential, setSelectedCredential] = useState('');
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [dragActive, setDragActive] = useState(false);

  useEffect(() => {
    loadCredentials();
  }, []);

  const loadCredentials = async () => {
    try {
      const response = await axios.get(`${API_URL}/credentials/`, { headers: AuthService.getAuthHeader() });
      setCredentials(response.data);
    } catch (err) {
      console.error('Failed to load credentials');
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }
    setError('');
    setSuccess('');
    setUploading(true);
    setProgress(0);
    const formData = new FormData();
    formData.append('file', file);
    const url = selectedCredential 
      ? `${API_URL}/upload/file?credential_id=${selectedCredential}`
      : `${API_URL}/upload/file`;
    try {
      const response = await axios.post(url, formData, {
        headers: { ...AuthService.getAuthHeader(), 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setProgress(percentCompleted);
        }
      });
      setSuccess(`File uploaded successfully to ${response.data.data.location}${response.data.is_real ? ' (Real Cloud)' : ' (Simulation)'}`);
      setFile(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
      setProgress(0);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>Upload File</Typography>
      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>{success}</Alert>}
      <Paper
        elevation={3}
        sx={{ p: 4, textAlign: 'center', border: dragActive ? '2px dashed #1976d2' : '2px dashed #ccc', backgroundColor: dragActive ? '#f0f8ff' : 'white' }}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <CloudUpload sx={{ fontSize: 60, color: '#1976d2', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          Drag and drop file here
        </Typography>
        <Typography color="textSecondary" sx={{ mb: 2 }}>or</Typography>
        <input accept="*/*" style={{ display: 'none' }} id="file-input" type="file" onChange={handleFileChange} />
        <label htmlFor="file-input">
          <Button variant="contained" component="span">
            Choose File
          </Button>
        </label>
        {file && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="body1">Selected: {file.name}</Typography>
            <Typography variant="body2" color="textSecondary">Size: {(file.size / 1024 / 1024).toFixed(2)} MB</Typography>
          </Box>
        )}
      </Paper>
      <FormControl fullWidth sx={{ mt: 3 }}>
        <InputLabel>Cloud Destination (Optional)</InputLabel>
        <Select value={selectedCredential} onChange={(e) => setSelectedCredential(e.target.value)} label="Cloud Destination (Optional)">
          <MenuItem value="">Simulation Mode</MenuItem>
          {credentials.map(cred => (
            <MenuItem key={cred.id} value={cred.id}>
              {cred.display_name} ({cred.provider.toUpperCase()})
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <Button fullWidth variant="contained" size="large" sx={{ mt: 3 }} onClick={handleUpload} disabled={!file || uploading}>
        {uploading ? 'Uploading...' : 'Upload File'}
      </Button>
      {uploading && <LinearProgress variant="determinate" value={progress} sx={{ mt: 2 }} />}
    </Container>
  );
}
