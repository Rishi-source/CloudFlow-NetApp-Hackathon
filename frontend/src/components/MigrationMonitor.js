import React from 'react';
import { Card, CardContent, Typography, List, ListItem, ListItemText, LinearProgress, Box, Chip } from '@mui/material';

function MigrationMonitor({ jobs }) {
    const getStatusColor = (status) => {
        const colors = {completed: 'success', in_progress: 'primary', failed: 'error', pending: 'warning'};
        return colors[status] || 'default';
    };
    return (
        <Card sx={{height: '100%'}}>
            <CardContent>
                <Typography variant="h6" gutterBottom>Active Migrations</Typography>
                <List sx={{maxHeight: 350, overflow: 'auto'}}>
                    {jobs?.length > 0 ? jobs.map(job => (
                        <ListItem key={job.job_id} sx={{flexDirection: 'column', alignItems: 'flex-start', borderBottom: 1, borderColor: 'divider'}}>
                            <Box sx={{width: '100%', display: 'flex', justifyContent: 'space-between', mb: 1}}>
                                <ListItemText primary={job.data_object_name || job.data_object_id} secondary={`${job.source} → ${job.target}`} />
                                <Chip label={job.status} color={getStatusColor(job.status)} size="small" />
                            </Box>
                            <Box sx={{width: '100%', display: 'flex', alignItems: 'center', gap: 1}}>
                                <LinearProgress variant="determinate" value={job.progress || 0} sx={{flexGrow: 1, height: 8, borderRadius: 4}} />
                                <Typography variant="body2">{Math.round(job.progress || 0)}%</Typography>
                            </Box>
                        </ListItem>
                    )) : (
                        <Typography variant="body2" color="text.secondary" sx={{p: 2}}>No active migrations</Typography>
                    )}
                </List>
            </CardContent>
        </Card>
    );
}
export default MigrationMonitor;
