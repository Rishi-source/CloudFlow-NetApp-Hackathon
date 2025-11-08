import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { AppBar, Toolbar, Typography, Button, Box, Chip } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import Register from './components/Register';
import CloudCredentials from './components/CloudCredentials';
import FileUpload from './components/FileUpload';
import AuthService from './services/auth';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#0070f3',
    },
    secondary: {
      main: '#7928ca',
    },
    background: {
      default: '#0a0a0a',
      paper: '#1a1a1a',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function ProtectedRoute({ children }) {
  return AuthService.isAuthenticated() ? children : <Navigate to="/login" />;
}

function NavBar() {
  const [isAuthenticated, setIsAuthenticated] = useState(AuthService.isAuthenticated());
  const [user, setUser] = useState(AuthService.getCurrentUser());
  const location = useLocation();
  useEffect(() => {
    setIsAuthenticated(AuthService.isAuthenticated());
    setUser(AuthService.getCurrentUser());
  }, [location]);
  const handleLogout = () => {
    AuthService.logout();
    window.location.href = '/login';
  };
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          CloudFlow Intelligence Platform
        </Typography>
        {isAuthenticated && (
          <>
            <Button color="inherit" href="/dashboard">Dashboard</Button>
            <Button color="inherit" href="/upload">Upload</Button>
            <Button color="inherit" href="/credentials">Credentials</Button>
            <Chip label={user?.email} color="primary" size="small" sx={{mx: 1}} />
            <Button color="inherit" onClick={handleLogout}>Logout</Button>
          </>
        )}
      </Toolbar>
    </AppBar>
  );
}

function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Router>
        <NavBar />
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/upload" element={<ProtectedRoute><FileUpload /></ProtectedRoute>} />
          <Route path="/credentials" element={<ProtectedRoute><CloudCredentials /></ProtectedRoute>} />
          <Route path="/" element={<Navigate to={AuthService.isAuthenticated() ? "/dashboard" : "/login"} />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
