import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';
import { Pie } from 'react-chartjs-2';

function DataDistribution({ data }) {
    const chartData = {
        labels: ['Hot Tier', 'Warm Tier', 'Cold Tier'],
        datasets: [{
            data: [data?.hot || 0, data?.warm || 0, data?.cold || 0],
            backgroundColor: ['#ff6384', '#36a2eb', '#4bc0c0'],
            borderWidth: 2
        }]
    };
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {position: 'bottom'},
            title: {display: false}
        }
    };
    return (
        <Card sx={{height: '100%'}}>
            <CardContent>
                <Typography variant="h6" gutterBottom>Data Distribution</Typography>
                <Box sx={{height: 250}}>
                    <Pie data={chartData} options={options} />
                </Box>
                <Box mt={2}>
                    <Typography variant="body2">Total Storage: {data?.total_gb || 0} GB</Typography>
                    <Typography variant="body2">Total Objects: {data?.total_objects || 0}</Typography>
                    <Typography variant="body2" color="primary">
                        On-Premise: {data?.on_premise || 0} | AWS: {data?.aws || 0} | Azure: {data?.azure || 0} | GCP: {data?.gcp || 0}
                    </Typography>
                </Box>
            </CardContent>
        </Card>
    );
}
export default DataDistribution;
