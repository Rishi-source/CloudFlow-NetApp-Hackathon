import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, Grid, Box, LinearProgress, Tooltip } from '@mui/material';
import { Speed, TrendingUp, CheckCircle, Timer } from '@mui/icons-material';

const PerformanceMetrics = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 60000);
    return () => clearInterval(interval);
  }, []);

  const fetchMetrics = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/metrics/performance?time_range=60', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setMetrics(data);
      }
    } catch (error) {
      console.error('Error fetching metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LinearProgress />;
  if (!metrics) return null;

  return (
    <Box sx={{ mt: 3 }}>
      <Typography variant="h6" gutterBottom>Performance Metrics (Last 60 min)</Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Tooltip title="Average response time for migration operations (lower is better)" placement="top" arrow>
            <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', color: 'white' }}>
                  <Timer sx={{ fontSize: 40, mr: 2 }} />
                  <Box>
                    <Typography variant="body2" sx={{ opacity: 0.9 }}>Avg Latency</Typography>
                    <Typography variant="h4">{metrics.average_latency_ms}ms</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Tooltip>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Tooltip title="Data transfer speed during migrations in megabytes per second" placement="top" arrow>
            <Card sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', color: 'white' }}>
                  <Speed sx={{ fontSize: 40, mr: 2 }} />
                  <Box>
                    <Typography variant="body2" sx={{ opacity: 0.9 }}>Throughput</Typography>
                    <Typography variant="h4">{metrics.throughput.average} MB/s</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Tooltip>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Tooltip title="Percentage of successful migration operations" placement="top" arrow>
            <Card sx={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', color: 'white' }}>
                  <CheckCircle sx={{ fontSize: 40, mr: 2 }} />
                  <Box>
                    <Typography variant="body2" sx={{ opacity: 0.9 }}>Success Rate</Typography>
                    <Typography variant="h4">{metrics.success_rate}%</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Tooltip>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Tooltip title="Total amount of data migrated in the last 60 minutes" placement="top" arrow>
            <Card sx={{ background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', color: 'white' }}>
                  <TrendingUp sx={{ fontSize: 40, mr: 2 }} />
                  <Box>
                    <Typography variant="body2" sx={{ opacity: 0.9 }}>Data Processed</Typography>
                    <Typography variant="h4">{metrics.throughput.total_data_gb} GB</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Tooltip>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Tooltip title="Latency distribution - shows how fast operations complete at different percentiles"><Typography variant="subtitle2" gutterBottom>Latency Percentiles</Typography></Tooltip>
              <Box sx={{ mt: 2 }}>
                <Tooltip title="50% of operations complete faster than this time" placement="left">
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">P50 (Median)</Typography>
                    <Typography variant="body2" fontWeight="bold">{metrics.latency_percentiles.p50}ms</Typography>
                  </Box>
                </Tooltip>
                <Tooltip title="90% of operations complete faster than this time" placement="left">
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">P90</Typography>
                    <Typography variant="body2" fontWeight="bold">{metrics.latency_percentiles.p90}ms</Typography>
                  </Box>
                </Tooltip>
                <Tooltip title="95% of operations complete faster than this time" placement="left">
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">P95</Typography>
                    <Typography variant="body2" fontWeight="bold">{metrics.latency_percentiles.p95}ms</Typography>
                  </Box>
                </Tooltip>
                <Tooltip title="99% of operations complete faster than this time (worst-case performance)" placement="left">
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">P99</Typography>
                    <Typography variant="body2" fontWeight="bold">{metrics.latency_percentiles.p99}ms</Typography>
                  </Box>
                </Tooltip>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Tooltip title="Detailed breakdown of data transfer speeds across all migrations"><Typography variant="subtitle2" gutterBottom>Throughput Details</Typography></Tooltip>
              <Box sx={{ mt: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Average</Typography>
                  <Typography variant="body2" fontWeight="bold">{metrics.throughput.average} MB/s</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Maximum</Typography>
                  <Typography variant="body2" fontWeight="bold">{metrics.throughput.max} MB/s</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Minimum</Typography>
                  <Typography variant="body2" fontWeight="bold">{metrics.throughput.min} MB/s</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Total Data</Typography>
                  <Typography variant="body2" fontWeight="bold">{metrics.throughput.total_data_gb} GB</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default PerformanceMetrics;
