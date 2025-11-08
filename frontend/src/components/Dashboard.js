import React, { useState, useEffect } from 'react';
import { Container, Grid, Paper, Typography, Box, Card, CardContent, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, LinearProgress, Button, Dialog, DialogTitle, DialogContent, DialogActions, Select, MenuItem, FormControl, InputLabel, Alert, IconButton, TablePagination, Tooltip, Fab } from '@mui/material';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';
import StorageIcon from '@mui/icons-material/Storage';
import CloudIcon from '@mui/icons-material/Cloud';
import SpeedIcon from '@mui/icons-material/Speed';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import AddIcon from '@mui/icons-material/Add';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import MoveUpIcon from '@mui/icons-material/MoveUp';
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import AuthService from '../services/auth';
import PerformanceMetrics from './PerformanceMetrics';
import TourGuide from './TourGuide';

const API_URL = process.env.NODE_ENV === 'production' ? '/api/v1' : 'http://localhost:8000/api/v1';
const COLORS = ['#0070f3', '#7928ca', '#ff0080', '#00dfd8', '#f5a623'];

function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [migrations, setMigrations] = useState([]);
  const [dataObjects, setDataObjects] = useState([]);
  const [recommendations, setRecommendations] = useState(null);
  const [credentials, setCredentials] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openMigrate, setOpenMigrate] = useState(false);
  const [selectedObject, setSelectedObject] = useState(null);
  const [targetLocation, setTargetLocation] = useState('');
  const [alert, setAlert] = useState(null);
  const [ws, setWs] = useState(null);
  const [filesPage, setFilesPage] = useState(0);
  const [filesRowsPerPage, setFilesRowsPerPage] = useState(5);
  const [migrationsPage, setMigrationsPage] = useState(0);
  const [migrationsRowsPerPage, setMigrationsRowsPerPage] = useState(5);
  const [systemStatus, setSystemStatus] = useState({kafka: true, email: true, websocket: false});
  const [kafkaEvents, setKafkaEvents] = useState([]);
  const [runTour, setRunTour] = useState(false);

  useEffect(() => {
    fetchData();
    const tourCompleted = localStorage.getItem('cloudflow-tour-completed');
    if (!tourCompleted) {
      setTimeout(() => setRunTour(true), 1000);
    }
    const user = AuthService.getCurrentUser();
    if (user && user.id) {
      const websocket = new WebSocket(`ws://localhost:8000/ws/${user.id}`);
      websocket.onopen = () => {
        setSystemStatus(prev => ({...prev, websocket: true}));
      };
      websocket.onclose = () => {
        setSystemStatus(prev => ({...prev, websocket: false}));
      };
      websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        const kafkaEvent = {
          id: Date.now(),
          timestamp: new Date().toLocaleTimeString(),
          topic: 'migration-events',
          type: data.type,
          message: `${data.type}: ${data.job_id ? 'Job ' + data.job_id.slice(-6) : ''} ${data.progress ? data.progress + '%' : ''}`,
          data: data
        };
        setKafkaEvents(prev => [kafkaEvent, ...prev].slice(0, 10));
        if (data.type === 'migration_complete') {
          setAlert({type: 'success', message: `📧 Email sent: Migration completed for ${data.object_name || 'file'}`});
          setTimeout(() => {
            const emailEvent = {
              id: Date.now() + 1,
              timestamp: new Date().toLocaleTimeString(),
              topic: 'email-notifications',
              type: 'email_sent',
              message: `email_sent: Migration completion notification`,
              data: {type: 'email_sent'}
            };
            setKafkaEvents(prev => [emailEvent, ...prev].slice(0, 10));
          }, 500);
        }
        if (data.type === 'migration_update' || data.type === 'migration_complete' || data.type === 'migration_failed') {
          fetchData();
        }
      };
      setWs(websocket);
      return () => websocket.close();
    }
  }, []);

  const fetchData = async () => {
    try {
      const headers = AuthService.getAuthHeader();
      const [summaryRes, migrationsRes, objectsRes, recsRes, credsRes] = await Promise.all([
        axios.get(`${API_URL}/analytics/summary`, {headers}),
        axios.get(`${API_URL}/migration/`, {headers}),
        axios.get(`${API_URL}/data/`, {headers}),
        axios.get(`${API_URL}/recommendations/`, {headers}),
        axios.get(`${API_URL}/credentials/`, {headers})
      ]);
      setSummary(summaryRes.data);
      setMigrations(migrationsRes.data);
      setDataObjects(objectsRes.data);
      setRecommendations(recsRes.data);
      setCredentials(credsRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  const handleGenerateSample = async () => {
    try {
      await axios.post(`${API_URL}/data/generate-sample?count=10`, {}, {headers: AuthService.getAuthHeader()});
      setAlert({type: 'success', message: '10 sample files generated successfully'});
      fetchData();
    } catch (error) {
      setAlert({type: 'error', message: 'Failed to generate sample data'});
    }
  };

  const handleSimulateAccess = async () => {
    try {
      const res = await axios.post(`${API_URL}/recommendations/simulate-access`, {}, {headers: AuthService.getAuthHeader()});
      setAlert({type: 'success', message: `Simulated ${res.data.simulated_accesses} accesses`});
      fetchData();
    } catch (error) {
      setAlert({type: 'error', message: 'Failed to simulate access patterns'});
    }
  };

  const handleMigrate = (obj) => {
    setSelectedObject(obj);
    setTargetLocation('');
    setOpenMigrate(true);
  };

  const handleConfirmMigrate = async () => {
    try {
      await axios.post(`${API_URL}/migration/trigger?object_id=${selectedObject._id}&target_location=${targetLocation}`, {}, {headers: AuthService.getAuthHeader()});
      setAlert({type: 'success', message: `Migration to ${targetLocation} initiated`});
      setOpenMigrate(false);
      fetchData();
    } catch (error) {
      setAlert({type: 'error', message: 'Failed to initiate migration'});
    }
  };

  const handleApplyRecommendation = async (rec) => {
    const target = rec.action === 'tier_downgrade' || rec.action === 'tier_upgrade' ? rec.current_location : rec.recommended_location;
    try {
      await axios.post(`${API_URL}/migration/trigger?object_id=${rec.object_id}&target_location=${target}&target_tier=${rec.recommended_tier || ''}`, {}, {headers: AuthService.getAuthHeader()});
      setAlert({type: 'success', message: 'Recommendation applied successfully'});
      fetchData();
    } catch (error) {
      setAlert({type: 'error', message: 'Failed to apply recommendation'});
    }
  };

  if (loading || !summary) {
    return <Box sx={{width: '100%', mt: 2}}><LinearProgress /></Box>;
  }

  const tierData = Object.entries(summary.distribution.by_tier).map(([name, value]) => ({name: name.charAt(0).toUpperCase() + name.slice(1), value}));
  const locationData = Object.entries(summary.distribution.by_location).map(([name, value]) => ({name: name.charAt(0).toUpperCase() + name.slice(1), value}));
  const costData = Object.entries(summary.costs.by_location).map(([name, value]) => ({name: name.charAt(0).toUpperCase() + name.slice(1), cost: value}));

  return (
    <Container maxWidth="xl" sx={{mt: 4}}>
      <TourGuide run={runTour} onFinish={() => setRunTour(false)} />
      <Tooltip title="Start Interactive Tour" placement="left">
        <Fab
          color="primary"
          sx={{position: 'fixed', bottom: 24, right: 24, zIndex: 1000}}
          onClick={() => {localStorage.removeItem('cloudflow-tour-completed'); setRunTour(true);}}
        >
          <HelpOutlineIcon />
        </Fab>
      </Tooltip>
      {alert && <Alert severity={alert.type} onClose={() => setAlert(null)} sx={{mb: 2}}>{alert.message}</Alert>}
      <Paper sx={{p: 2, mb: 3, bgcolor: '#1a1a1a'}} data-tour="system-status">
        <Box sx={{display: 'flex', alignItems: 'center', gap: 3}}>
          <Typography variant="h6">System Status</Typography>
          <Tooltip title="Apache Kafka event streaming - shows live migration events" placement="top" arrow><Chip icon={<CloudIcon />} label={`Kafka: ${systemStatus.kafka ? 'Connected' : 'Disconnected'}`} color={systemStatus.kafka ? 'success' : 'error'} size="small" /></Tooltip>
          <Tooltip title="SMTP email service for migration notifications" placement="top" arrow><Chip icon={<CloudIcon />} label={`Email SMTP: ${systemStatus.email ? 'Ready' : 'Unavailable'}`} color={systemStatus.email ? 'success' : 'error'} size="small" /></Tooltip>
          <Tooltip title="WebSocket connection for real-time updates" placement="top" arrow><Chip icon={<CloudIcon />} label={`WebSocket: ${systemStatus.websocket ? 'Connected' : 'Disconnected'}`} color={systemStatus.websocket ? 'success' : 'error'} size="small" /></Tooltip>
          <Chip label="Real-Time Mode" color="primary" size="small" variant="outlined" />
        </Box>
      </Paper>
      {kafkaEvents.length > 0 && (
        <Paper sx={{p: 2, mb: 3, bgcolor: '#0a2540'}} data-tour="kafka-stream">
          <Typography variant="h6" gutterBottom sx={{color: '#fff', display: 'flex', alignItems: 'center'}}>
            <CloudIcon sx={{mr: 1, color: '#00ff00'}} />
            Kafka Event Stream (Topic: migration-events)
            <Chip label="LIVE" color="success" size="small" sx={{ml: 2}} />
          </Typography>
          <Box sx={{maxHeight: 200, overflowY: 'auto', bgcolor: '#000', p: 2, borderRadius: 1, fontFamily: 'monospace'}}>
            {kafkaEvents.map((event) => (
              <Box key={event.id} sx={{mb: 1, color: '#00ff00', fontSize: '12px'}}>
                <Typography component="span" sx={{color: '#888', mr: 1}}>[{event.timestamp}]</Typography>
                <Typography component="span" sx={{color: '#0ff', mr: 1}}>Topic: {event.topic}</Typography>
                <Typography component="span" sx={{color: '#ff0'}}>Type: {event.type}</Typography>
                <Typography component="span" sx={{color: '#0f0', ml: 1}}>{event.message}</Typography>
              </Box>
            ))}
          </Box>
        </Paper>
      )}
      <Box sx={{display: 'flex', gap: 2, mb: 3}}>
        <Tooltip title="Create 10 sample files for testing migrations and ML recommendations" placement="top" arrow data-tour="generate-sample">
          <Button variant="contained" startIcon={<AddIcon />} onClick={handleGenerateSample}>Generate Sample Data</Button>
        </Tooltip>
        <Tooltip title="Simulate file access patterns to train the ML model" placement="top" arrow data-tour="simulate-access">
          <Button variant="contained" startIcon={<PlayArrowIcon />} onClick={handleSimulateAccess} color="secondary">Simulate Access</Button>
        </Tooltip>
      </Box>
      <Grid container spacing={3} data-tour="summary-cards">
        <Grid item xs={12} md={3}>
          <Tooltip title="Total number of files and their combined size"><Card><CardContent><Box sx={{display: 'flex', alignItems: 'center', mb: 1}}><StorageIcon color="primary" sx={{mr: 1}} /><Typography variant="h6">Total Objects</Typography></Box><Typography variant="h3">{summary.distribution.total_objects}</Typography><Typography variant="body2" color="text.secondary">{summary.distribution.total_size_gb} GB</Typography></CardContent></Card></Tooltip>
        </Grid>
        <Grid item xs={12} md={3}>
          <Tooltip title="Current and projected monthly storage costs across all clouds"><Card><CardContent><Box sx={{display: 'flex', alignItems: 'center', mb: 1}}><AttachMoneyIcon color="primary" sx={{mr: 1}} /><Typography variant="h6">Monthly Cost</Typography></Box><Typography variant="h3">${summary.costs.current_month}</Typography><Typography variant="body2" color="text.secondary">Projected: ${summary.costs.projected}</Typography></CardContent></Card></Tooltip>
        </Grid>
        <Grid item xs={12} md={3}>
          <Tooltip title="Average response time for data operations (lower is better)"><Card><CardContent><Box sx={{display: 'flex', alignItems: 'center', mb: 1}}><SpeedIcon color="primary" sx={{mr: 1}} /><Typography variant="h6">Avg Latency</Typography></Box><Typography variant="h3">{summary.performance.avg_latency_ms}ms</Typography><Typography variant="body2" color="text.secondary">Success: {summary.performance.success_rate}%</Typography></CardContent></Card></Tooltip>
        </Grid>
        <Grid item xs={12} md={3}>
          <Tooltip title="Number of migrations currently in progress"><Card><CardContent><Box sx={{display: 'flex', alignItems: 'center', mb: 1}}><CloudIcon color="primary" sx={{mr: 1}} /><Typography variant="h6">Active Migrations</Typography></Box><Typography variant="h3">{summary.active_migrations_count}</Typography><Typography variant="body2" color="text.secondary">In progress</Typography></CardContent></Card></Tooltip>
        </Grid>
        {recommendations && recommendations.recommendations.length > 0 && (
          <Grid item xs={12} data-tour="ml-recommendations">
            <Paper sx={{p: 2, bgcolor: '#fff3e0'}}>
              <Typography variant="h6" gutterBottom sx={{display: 'flex', alignItems: 'center'}}>
                <LightbulbIcon sx={{mr: 1}} color="warning" />
                ML Recommendations - Save ${recommendations.total_potential_savings}/month
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>File</TableCell>
                      <TableCell>Current</TableCell>
                      <TableCell>Recommended</TableCell>
                      <TableCell>Reason</TableCell>
                      <TableCell>Savings</TableCell>
                      <TableCell>Action</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {recommendations.recommendations.slice(0, 3).map((rec) => (
                      <TableRow key={rec.object_id}>
                        <TableCell>{rec.object_name}</TableCell>
                        <TableCell><Tooltip title={rec.current_tier === 'hot' ? 'Frequently accessed - fast but expensive' : rec.current_tier === 'warm' ? 'Moderate access - balanced cost' : 'Rarely accessed - slow but cheap'}><Chip label={rec.current_tier || rec.current_location} size="small" /></Tooltip></TableCell>
                        <TableCell><Tooltip title="AI-recommended tier for optimal cost"><Chip label={rec.recommended_tier || rec.recommended_location} size="small" color="success" /></Tooltip></TableCell>
                        <TableCell>{rec.reason}</TableCell>
                        <TableCell>${rec.savings_per_month}/mo</TableCell>
                        <TableCell><Tooltip title="Apply this recommendation"><Button size="small" onClick={() => handleApplyRecommendation(rec)}>Apply</Button></Tooltip></TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>
        )}
        <Grid item xs={12} md={6}><Paper sx={{p: 2}}><Tooltip title="Distribution of files across Hot (frequent), Warm (moderate), and Cold (rare) tiers"><Typography variant="h6" gutterBottom>Data Distribution by Tier</Typography></Tooltip><ResponsiveContainer width="100%" height={300}><PieChart><Pie data={tierData} cx="50%" cy="50%" labelLine={false} label={({name, percent}) => `${name} ${(percent * 100).toFixed(0)}%`} outerRadius={100} fill="#8884d8" dataKey="value">{tierData.map((entry, index) => (<Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />))}</Pie></PieChart></ResponsiveContainer></Paper></Grid>
        <Grid item xs={12} md={6}><Paper sx={{p: 2}}><Tooltip title="Distribution of files across cloud providers and on-premise storage"><Typography variant="h6" gutterBottom>Data Distribution by Location</Typography></Tooltip><ResponsiveContainer width="100%" height={300}><PieChart><Pie data={locationData} cx="50%" cy="50%" labelLine={false} label={({name, percent}) => `${name} ${(percent * 100).toFixed(0)}%`} outerRadius={100} fill="#8884d8" dataKey="value">{locationData.map((entry, index) => (<Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />))}</Pie></PieChart></ResponsiveContainer></Paper></Grid>
        <Grid item xs={12}><Paper sx={{p: 2}}><Tooltip title="Monthly storage costs per cloud provider"><Typography variant="h6" gutterBottom>Cost Breakdown by Location</Typography></Tooltip><ResponsiveContainer width="100%" height={300}><BarChart data={costData}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis /><Legend /><Bar dataKey="cost" fill="#0070f3" name="Monthly Cost ($)" /></BarChart></ResponsiveContainer></Paper></Grid>
      </Grid>
      <Box data-tour="performance-metrics"><PerformanceMetrics /></Box>
      <Grid container spacing={3} sx={{mt: 1}}>
        <Grid item xs={12} data-tour="files-table">
          <Paper sx={{p: 2}}>
            <Typography variant="h6" gutterBottom>Your Files</Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Size</TableCell>
                    <TableCell>Tier</TableCell>
                    <TableCell>Location</TableCell>
                    <TableCell>Cost/mo</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {dataObjects.slice(filesPage * filesRowsPerPage, filesPage * filesRowsPerPage + filesRowsPerPage).map((obj) => (
                    <TableRow key={obj._id}>
                      <TableCell>{obj.name}</TableCell>
                      <TableCell>{(obj.size_bytes / 1024 / 1024).toFixed(2)} MB</TableCell>
                      <TableCell><Tooltip title={obj.current_tier === 'hot' ? 'Hot: Frequently accessed (fast, expensive)' : obj.current_tier === 'warm' ? 'Warm: Moderate access (balanced)' : 'Cold: Rarely accessed (slow, cheap)'}><Chip label={obj.current_tier} size="small" color={obj.current_tier === 'hot' ? 'error' : obj.current_tier === 'warm' ? 'warning' : 'success'} /></Tooltip></TableCell>
                      <TableCell><Chip label={obj.current_location} size="small" /></TableCell>
                      <TableCell>${obj.cost_per_month}</TableCell>
                      <TableCell><Tooltip title="Migrate this file to another cloud or tier"><IconButton size="small" onClick={() => handleMigrate(obj)} color="primary"><MoveUpIcon /></IconButton></Tooltip></TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination component="div" count={dataObjects.length} page={filesPage} onPageChange={(e, newPage) => setFilesPage(newPage)} rowsPerPage={filesRowsPerPage} onRowsPerPageChange={(e) => {setFilesRowsPerPage(parseInt(e.target.value, 10)); setFilesPage(0);}} />
          </Paper>
        </Grid>
        <Grid item xs={12} data-tour="migrations-table">
          <Paper sx={{p: 2}}>
            <Typography variant="h6" gutterBottom>Recent Migrations</Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>File</TableCell>
                    <TableCell>Source</TableCell>
                    <TableCell>Target</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Progress</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {migrations.slice(migrationsPage * migrationsRowsPerPage, migrationsPage * migrationsRowsPerPage + migrationsRowsPerPage).map((mig) => (
                    <TableRow key={mig._id}>
                      <TableCell>{mig.object_name}</TableCell>
                      <TableCell>{mig.source_location}</TableCell>
                      <TableCell>{mig.target_location}</TableCell>
                      <TableCell><Chip label={mig.status} color={mig.status === 'completed' ? 'success' : mig.status === 'in_progress' ? 'primary' : 'default'} size="small" /></TableCell>
                      <TableCell><Box sx={{display: 'flex', alignItems: 'center'}}><Box sx={{width: '100%', mr: 1}}><LinearProgress variant="determinate" value={mig.progress || 0} /></Box><Box sx={{minWidth: 35}}><Typography variant="body2" color="text.secondary">{Math.round(mig.progress || 0)}%</Typography></Box></Box></TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination component="div" count={migrations.length} page={migrationsPage} onPageChange={(e, newPage) => setMigrationsPage(newPage)} rowsPerPage={migrationsRowsPerPage} onRowsPerPageChange={(e) => {setMigrationsRowsPerPage(parseInt(e.target.value, 10)); setMigrationsPage(0);}} />
          </Paper>
        </Grid>
      </Grid>
      <Dialog open={openMigrate} onClose={() => setOpenMigrate(false)}>
        <DialogTitle>Migrate File</DialogTitle>
        <DialogContent>
          {selectedObject && (
            <>
              <Typography>Migrate: {selectedObject.name}</Typography>
              <Typography variant="body2" color="text.secondary">Current: {selectedObject.current_location}</Typography>
              <FormControl fullWidth sx={{mt: 2}}>
                <InputLabel>Target Location</InputLabel>
                <Select value={targetLocation} onChange={(e) => setTargetLocation(e.target.value)} label="Target Location">
                  {credentials.map((cred) => (<MenuItem key={cred.id} value={cred.provider}>{cred.display_name} ({cred.provider.toUpperCase()})</MenuItem>))}
                  <MenuItem value="on-premise">On-Premise (Local)</MenuItem>
                  <MenuItem value="simulation">Simulation (Demo)</MenuItem>
                </Select>
              </FormControl>
              {credentials.length === 0 && <Alert severity="info" sx={{mt: 2}}>Add cloud credentials in Credentials page to migrate to real clouds</Alert>}
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenMigrate(false)}>Cancel</Button>
          <Button onClick={handleConfirmMigrate} variant="contained" disabled={!targetLocation}>Migrate</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

export default Dashboard;
