import { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  AppBar, Toolbar, Typography, IconButton, Badge, Avatar,
  Menu, MenuItem, InputBase, Box, Divider,
} from '@mui/material';
import { Search, Notifications, Person, Settings, Logout, Lock } from '@mui/icons-material';
import { logout } from '../../store/authSlice';

export default function Header() {
  const user = useSelector((s) => s.auth.user);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  return (
    <AppBar position="sticky" elevation={0} sx={{ bgcolor: '#ffffff', color: '#1e293b', borderBottom: '1px solid #e2e8f0' }}>
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        <Box>
          <Typography sx={{ fontSize: '1rem', fontWeight: 600, color: '#1e293b' }}>Welcome, {user?.full_name?.split(' ')[0]}</Typography>
          <Typography sx={{ fontSize: '0.75rem', color: '#94a3b8' }}>Have a great day!</Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', bgcolor: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 2, px: 1.5, py: 0.5 }}>
            <Search sx={{ color: '#94a3b8', mr: 1 }} fontSize="small" />
            <InputBase placeholder="Search..." sx={{ fontSize: 14, color: '#475569' }} />
          </Box>

          <IconButton sx={{ color: '#64748b' }}>
            <Badge badgeContent={3} color="error"><Notifications /></Badge>
          </IconButton>

          <Box
            sx={{ display: 'flex', alignItems: 'center', gap: 1, cursor: 'pointer' }}
            onClick={(e) => setAnchorEl(e.currentTarget)}
          >
            <Avatar sx={{ background: 'linear-gradient(135deg, #6366f1, #4338ca)', width: 36, height: 36 }}>
              {user?.full_name?.charAt(0)}
            </Avatar>
            <Box>
              <Typography sx={{ fontSize: '0.875rem', fontWeight: 600, color: '#1e293b' }}>{user?.full_name}</Typography>
              <Typography sx={{ fontSize: '0.75rem', color: '#94a3b8' }}>Admin</Typography>
            </Box>
          </Box>

          <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={() => setAnchorEl(null)}>
            <Box sx={{ px: 2, py: 1 }}>
              <Typography sx={{ fontWeight: 600, color: '#1e293b' }}>{user?.full_name}</Typography>
              <Typography sx={{ fontSize: '0.75rem', color: '#64748b' }}>{user?.email}</Typography>
            </Box>
            <Divider sx={{ borderColor: '#e2e8f0' }} />
            <MenuItem onClick={() => { setAnchorEl(null); }} sx={{ color: '#475569' }}><Person sx={{ mr: 1, color: '#64748b' }} fontSize="small" />My Profile</MenuItem>
            <MenuItem onClick={() => { setAnchorEl(null); }} sx={{ color: '#475569' }}><Settings sx={{ mr: 1, color: '#64748b' }} fontSize="small" />Settings</MenuItem>
            <MenuItem onClick={() => { setAnchorEl(null); navigate('/admin/change-password'); }} sx={{ color: '#475569' }}><Lock sx={{ mr: 1, color: '#64748b' }} fontSize="small" />Change Password</MenuItem>
            <MenuItem onClick={handleLogout} sx={{ color: '#ef4444' }}><Logout sx={{ mr: 1 }} fontSize="small" />Logout</MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
}
