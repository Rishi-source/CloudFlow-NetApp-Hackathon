import React from 'react';
import { Card, CardContent, Typography, Box, Chip } from '@mui/material';
import { Line } from 'react-chartjs-2';

function MLInsights({ predictions }) {
    const chartData = {
        labels: predictions?.dates || [],
        datasets: [{
            label: 'Predicted Access Count',
            data: predictions?.values || [],
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            tension: 0.4,
            fill: true
        }]
    };
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {legend: {display: false}},
        scales: {y: {beginAtZero: true}}
    };
    return (
        <Card sx={{height: '100%'}}>
            <CardContent>
                <Typography variant="h6" gutterBottom>ML Predictions</Typography>
                <Box sx={{height: 200, mb: 2}}>
                    <Line data={chartData} options={options} />
                </Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>Recommendations:</Typography>
                <Box sx={{display: 'flex', gap: 1, flexWrap: 'wrap'}}>
                    {predictions?.recommendations?.map((rec, idx) => (
                        <Chip key={idx} label={rec.action} color={rec.priority === 'high' ? 'error' : 'primary'} size="small" />
                    )) || <Chip label="No recommendations" size="small" />}
                </Box>
                {predictions?.confidence && (
                    <Typography variant="caption" color="primary" sx={{mt: 1, display: 'block'}}>
                        Confidence: {Math.round(predictions.confidence * 100)}%
                    </Typography>
                )}
            </CardContent>
        </Card>
    );
}
export default MLInsights;
