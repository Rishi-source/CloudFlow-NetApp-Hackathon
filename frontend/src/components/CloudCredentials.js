import React, { useState, useEffect } from 'react';
import { Container, Box, Typography, Button, TextField, Card, CardContent, CardActions, Grid, Alert, Dialog, DialogTitle, DialogContent, DialogActions, Chip } from '@mui/material';
import { CloudUpload, Delete, Check, Close } from '@mui/icons-material';
import axios from 'axios';
import AuthService from '../services/auth';

const API_URL = process.env.NODE_ENV === 'production' 
  ? '/api/v1'
  : 'http://localhost:8000/api/v1';

export default function CloudCredentials() {
  const [credentials, setCredentials] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [provider, setProvider] = useState('');
  const [formData, setFormData] = useState({});
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadCredentials();
  }, []);

  const loadCredentials = async () => {
    try {
      const response = await axios.get(`${API_URL}/credentials/`, { headers: AuthService.getAuthHeader() });
      setCredentials(response.data);
    } catch (err) {
      setError('Failed to load credentials');
    }
  };

  const handleAddCredential = async () => {
    setError('');
    setSuccess('');
    try {
      await axios.post(`${API_URL}/credentials/${provider}`, formData, { headers: AuthService.getAuthHeader() });
      setSuccess(`${provider.toUpperCase()} credentials added successfully`);
      setOpenDialog(false);
      setFormData({});
      loadCredentials();
    } catch (err) {
      const errorDetail = err.response?.data?.detail;
      if (Array.isArray(errorDetail)) {
        setError(errorDetail.map(e => e.msg).join(', '));
      } else if (typeof errorDetail === 'string') {
        setError(errorDetail);
      } else {
        setError('Failed to add credentials');
      }
    }
  };

  const handleTestCredential = async (id) => {
    try {
      const response = await axios.post(`${API_URL}/credentials/${id}/test`, {}, { headers: AuthService.getAuthHeader() });
      setSuccess(response.data.message);
      loadCredentials();
    } catch (err) {
      setError('Connection test failed');
    }
  };

  const handleDeleteCredential = async (id) => {
    try {
      await axios.delete(`${API_URL}/credentials/${id}`, { headers: AuthService.getAuthHeader() });
      setSuccess('Credential deleted');
      loadCredentials();
    } catch (err) {
      setError('Failed to delete credential');
    }
  };

  const openAddDialog = (prov) => {
    setProvider(prov);
    setFormData({});
    setOpenDialog(true);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>Cloud Credentials</Typography>
      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>{success}</Alert>}
      <Box sx={{ mb: 3 }}>
        <Button variant="contained" onClick={() => openAddDialog('aws')} sx={{ mr: 2 }}>Add AWS</Button>
        <Button variant="contained" onClick={() => openAddDialog('azure')} sx={{ mr: 2 }}>Add Azure</Button>
        <Button variant="contained" onClick={() => openAddDialog('gcp')}>Add GCP</Button>
      </Box>
      <Grid container spacing={3}>
        {credentials.map(cred => (
          <Grid item xs={12} md={6} key={cred.id}>
            <Card>
              <CardContent>
                <Typography variant="h6">{cred.display_name}</Typography>
                <Typography color="textSecondary">{cred.provider.toUpperCase()}</Typography>
                <Box sx={{ mt: 1 }}>
                  {cred.is_verified ? (
                    <Chip icon={<Check />} label="Verified" color="success" size="small" />
                  ) : (
                    <Chip icon={<Close />} label="Not Verified" color="warning" size="small" />
                  )}
                </Box>
              </CardContent>
              <CardActions>
                <Button size="small" onClick={() => handleTestCredential(cred.id)}>Test</Button>
                <Button size="small" color="error" onClick={() => handleDeleteCredential(cred.id)}>Delete</Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add {provider.toUpperCase()} Credentials</DialogTitle>
        <DialogContent>
          {provider === 'aws' && (
            <>
              <TextField fullWidth margin="normal" label="Display Name" onChange={(e) => setFormData({...formData, display_name: e.target.value})} />
              <TextField fullWidth margin="normal" label="Access Key ID" onChange={(e) => setFormData({...formData, access_key_id: e.target.value})} />
              <TextField fullWidth margin="normal" label="Secret Access Key" type="password" onChange={(e) => setFormData({...formData, secret_access_key: e.target.value})} />
              <TextField fullWidth margin="normal" label="Region" defaultValue="us-east-1" onChange={(e) => setFormData({...formData, region: e.target.value})} />
              <TextField fullWidth margin="normal" label="Bucket Name" onChange={(e) => setFormData({...formData, bucket_name: e.target.value})} />
            </>
          )}
          {provider === 'azure' && (
            <>
              <TextField fullWidth margin="normal" label="Display Name" onChange={(e) => setFormData({...formData, display_name: e.target.value})} />
              <TextField fullWidth margin="normal" label="Account Name" onChange={(e) => setFormData({...formData, account_name: e.target.value})} />
              <TextField fullWidth margin="normal" label="Account Key" type="password" onChange={(e) => setFormData({...formData, account_key: e.target.value})} />
              <TextField fullWidth margin="normal" label="Container Name" onChange={(e) => setFormData({...formData, container_name: e.target.value})} />
            </>
          )}
          {provider === 'gcp' && (
            <>
              <TextField fullWidth margin="normal" label="Display Name" onChange={(e) => setFormData({...formData, display_name: e.target.value})} />
              <TextField fullWidth margin="normal" label="Project ID" onChange={(e) => setFormData({...formData, project_id: e.target.value})} />
              <TextField fullWidth margin="normal" label="Bucket Name" onChange={(e) => setFormData({...formData, bucket_name: e.target.value})} />
              <TextField fullWidth margin="normal" label="Service Account JSON" multiline rows={4} placeholder='{"type":"service_account",...}' onChange={(e) => setFormData({...formData, service_account_json: e.target.value})} />
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleAddCredential} variant="contained">Add</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
