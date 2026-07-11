import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import {
  Box, Drawer, List, ListItemButton, ListItemIcon, ListItemText,
  Typography, Avatar, IconButton, Divider,
} from '@mui/material';
import {
  Dashboard, People, PersonSearch, School, Shield,
  AccountBalance, CalendarMonth, Quiz, MenuBook,
  AttachMoney, DirectionsBus, Notifications, Logout,
  ChevronLeft, ChevronRight,
} from '@mui/icons-material';

const DRAWER_WIDTH = 240;
const COLLAPSED_WIDTH = 64;

const menuItems = [
  { text: 'Dashboard', icon: <Dashboard />, path: '/admin/dashboard' },
  { text: 'Students', icon: <People />, path: '/admin/students' },
  { text: 'Student Details', icon: <PersonSearch />, path: '/admin/student-details' },
  { text: 'Staff', icon: <School />, path: '/admin/staff' },
  { text: 'Teacher Privileges', icon: <Shield />, path: '/admin/teacher-privileges' },
  { text: 'Leave Management', icon: <CalendarMonth />, path: '/admin/leaves' },
  { text: 'Payroll', icon: <AccountBalance />, path: '/admin/payroll' },
  { text: 'Timetable', icon: <CalendarMonth />, path: '/admin/timetable' },
  { text: 'Examinations', icon: <Quiz />, path: '/admin/examinations' },
  { text: 'Library', icon: <MenuBook />, path: '/admin/library' },
  { text: 'Fee Management', icon: <AttachMoney />, path: '/admin/fees' },
  { text: 'Transport', icon: <DirectionsBus />, path: '/admin/transport' },
  { text: 'Notifications', icon: <Notifications />, path: '/admin/notifications' },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const user = useSelector((s) => s.auth.user);
  const width = collapsed ? COLLAPSED_WIDTH : DRAWER_WIDTH;

  return (
    <Drawer
      variant="permanent"
      sx={{
        width,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width,
          bgcolor: '#0f172a',
          color: '#e2e8f0',
          transition: 'width 0.2s',
          overflowX: 'hidden',
          borderRight: 'none',
        },
      }}
    >
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        {!collapsed && (
          <Typography sx={{ fontSize: '1.125rem', fontWeight: 700, color: '#f8fafc' }}>ERP Portal</Typography>
        )}
        <IconButton onClick={() => setCollapsed(!collapsed)} sx={{ color: '#94a3b8' }}>
          {collapsed ? <ChevronRight /> : <ChevronLeft />}
        </IconButton>
      </Box>

      {!collapsed && (
        <Typography sx={{ px: 2, fontSize: '0.6875rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: 1 }}>Admin</Typography>
      )}

      {!collapsed && user && (
        <Box sx={{ px: 2, py: 1.5, display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Avatar sx={{ background: 'linear-gradient(135deg, #6366f1, #4338ca)', width: 36, height: 36 }}>
            {user.full_name?.charAt(0)}
          </Avatar>
          <Box>
            <Typography sx={{ fontSize: '0.875rem', fontWeight: 600, color: '#f1f5f9' }}>{user.full_name}</Typography>
            <Typography sx={{ fontSize: '0.75rem', color: '#64748b' }}>{user.email}</Typography>
          </Box>
        </Box>
      )}

      <Divider sx={{ borderColor: '#1e293b', my: 1 }} />

      <List sx={{ flex: 1, px: 1 }}>
        {menuItems.map((item) => (
          <ListItemButton
            key={item.path}
            onClick={() => navigate(item.path)}
            selected={location.pathname === item.path}
            sx={{
              borderRadius: 2, mb: 0.5,
              '&.Mui-selected': { bgcolor: '#6366f1', '&:hover': { bgcolor: '#4f46e5' } },
              '&:hover': { bgcolor: 'rgba(99, 102, 241, 0.08)' },
            }}
          >
            <ListItemIcon sx={{ color: location.pathname === item.path ? '#fff' : '#94a3b8', minWidth: 40 }}>{item.icon}</ListItemIcon>
            {!collapsed && <ListItemText primary={item.text} primaryTypographyProps={{ sx: { fontSize: '0.8125rem', fontWeight: location.pathname === item.path ? 600 : 400, color: location.pathname === item.path ? '#fff' : '#cbd5e1' } }} />}
          </ListItemButton>
        ))}
      </List>

      <List sx={{ px: 1 }}>
        <ListItemButton
          onClick={() => { navigate('/login'); }}
          sx={{ borderRadius: 2, '&:hover': { bgcolor: 'rgba(239, 68, 68, 0.08)' } }}
        >
          <ListItemIcon sx={{ color: '#94a3b8', minWidth: 40 }}><Logout /></ListItemIcon>
          {!collapsed && <ListItemText primary="Logout" primaryTypographyProps={{ sx: { fontSize: '0.8125rem', color: '#cbd5e1' } }} />}
        </ListItemButton>
      </List>
    </Drawer>
  );
}
