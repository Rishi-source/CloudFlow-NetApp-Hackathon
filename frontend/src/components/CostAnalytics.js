import React from 'react';
import { Card, CardContent, Typography, Grid, Box } from '@mui/material';
import { Bar } from 'react-chartjs-2';

function CostAnalytics({ data }) {
    const chartData = {
        labels: ['AWS', 'Azure', 'GCP', 'On-Premise'],
        datasets: [{
            label: 'Monthly Cost ($)',
            data: [data?.aws || 0, data?.azure || 0, data?.gcp || 0, data?.on_premise || 0],
            backgroundColor: ['#ff9800', '#00bcd4', '#4caf50', '#9c27b0'],
            borderWidth: 1
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
                <Typography variant="h6" gutterBottom>Cost Analytics</Typography>
                <Grid container spacing={2} sx={{mb: 2}}>
                    <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">Current Month</Typography>
                        <Typography variant="h6" color="primary">${data?.current_month || 0}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">Projected</Typography>
                        <Typography variant="h6" color="warning.main">${data?.projected || 0}</Typography>
                    </Grid>
                    <Grid item xs={12}>
                        <Typography variant="body2" color="text.secondary">Potential Savings</Typography>
                        <Typography variant="h6" color="success.main">${data?.savings || 0}</Typography>
                    </Grid>
                </Grid>
                <Box sx={{height: 180}}>
                    <Bar data={chartData} options={options} />
                </Box>
            </CardContent>
        </Card>
    );
}
export default CostAnalytics;
