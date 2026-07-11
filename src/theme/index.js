import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: { main: '#1a237e' },      // Dark navy sidebar
    secondary: { main: '#4fc3f7' },    // Light blue accent
    background: { default: '#f5f7fa', paper: '#ffffff' },
    success: { main: '#4caf50' },
    warning: { main: '#ff9800' },
    error: { main: '#f44336' },
  },
  typography: {
    fontFamily: 'Roboto, sans-serif',
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: { textTransform: 'none', borderRadius: 8 },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: { borderRadius: 12, boxShadow: 'none', overflow: 'visible' },
      },
    },
  },
});

export default theme;
