# Admin Portal Requirements

## System Requirements
- Node.js 18+
- npm 9+

## Dependencies
- react 18.x, react-dom 18.x
- @mui/material 5.x, @mui/icons-material 5.x
- @emotion/react, @emotion/styled
- @reduxjs/toolkit 2.x, react-redux 9.x
- react-router-dom 6.x
- axios 1.x
- react-hook-form 7.x, @hookform/resolvers 3.x, zod 3.x
- recharts 2.x

## Dev Dependencies
- vite 5.x, @vitejs/plugin-react 4.x

## Browser Support
- Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- Responsive: 320px to 2560px width

## Backend Dependency
- Requires backend API running at VITE_API_URL
- Authentication via httpOnly cookies (withCredentials: true)
- Multi-tenant: school_code stored in localStorage for X-School-Code header
