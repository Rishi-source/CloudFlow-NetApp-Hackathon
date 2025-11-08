import React from 'react';
import { Card, CardContent, Typography, List, ListItem, Alert, AlertTitle, Box, Chip } from '@mui/material';

function AlertPanel({ alerts }) {
    const getSeverityColor = (severity) => {
        const colors = {critical: 'error', warning: 'warning', info: 'info', success: 'success'};
        return colors[severity] || 'default';
    };
    return (
        <Card sx={{height: '100%'}}>
            <CardContent>
                <Typography variant="h6" gutterBottom>Active Alerts</Typography>
                <List sx={{maxHeight: 350, overflow: 'auto'}}>
                    {alerts?.length > 0 ? alerts.map(alert => (
                        <ListItem key={alert.alert_id} sx={{p: 0, mb: 1}}>
                            <Alert severity={getSeverityColor(alert.severity)} sx={{width: '100%'}}>
                                <AlertTitle sx={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                                    <span>{alert.type}</span>
                                    <Chip label={alert.severity} size="small" color={getSeverityColor(alert.severity)} />
                                </AlertTitle>
                                <Typography variant="body2">{alert.message}</Typography>
                                <Typography variant="caption" color="text.secondary" sx={{mt: 0.5, display: 'block'}}>
                                    {new Date(alert.timestamp).toLocaleString()}
                                </Typography>
                            </Alert>
                        </ListItem>
                    )) : (
                        <Box sx={{p: 2, textAlign: 'center'}}>
                            <Typography variant="body2" color="text.secondary">No active alerts</Typography>
                            <Chip label="All systems normal" color="success" size="small" sx={{mt: 1}} />
                        </Box>
                    )}
                </List>
            </CardContent>
        </Card>
    );
}
export default AlertPanel;
