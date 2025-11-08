import React from 'react';
import { Card, CardContent, Typography, Box, Chip } from '@mui/material';

function StreamingViewer({ events }) {
    const getEventColor = (type) => {
        const colors = {access: 'info', migration: 'primary', alert: 'error', metric: 'success'};
        return colors[type] || 'default';
    };
    return (
        <Card sx={{height: '100%'}}>
            <CardContent>
                <Typography variant="h6" gutterBottom>Real-Time Events</Typography>
                <Box sx={{maxHeight: 350, overflow: 'auto'}}>
                    {events?.length > 0 ? events.map(event => (
                        <Box key={event.event_id} sx={{mb: 1.5, p: 1.5, border: 1, borderColor: 'divider', borderRadius: 1}}>
                            <Box sx={{display: 'flex', justifyContent: 'space-between', mb: 0.5}}>
                                <Chip label={event.event_type} color={getEventColor(event.event_type)} size="small" />
                                <Typography variant="caption" color="text.secondary">{new Date(event.timestamp).toLocaleTimeString()}</Typography>
                            </Box>
                            <Typography variant="body2">{event.message || event.data?.message || 'Event occurred'}</Typography>
                        </Box>
                    )) : (
                        <Typography variant="body2" color="text.secondary" sx={{p: 2}}>No recent events</Typography>
                    )}
                </Box>
            </CardContent>
        </Card>
    );
}
export default StreamingViewer;
