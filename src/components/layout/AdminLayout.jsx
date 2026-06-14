import { useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { useIsFetching } from '@tanstack/react-query';
import { useSelector, useDispatch } from 'react-redux';
import {
  LayoutDashboard, Users, GraduationCap, UserCog, Calendar, ClipboardList,
  BookOpen, DollarSign, Bus, Bell, Briefcase, FileText, Settings, BarChart2, UserCheck, KeyRound, ClipboardCheck, UserPlus,
} from 'lucide-react';
import { Sidebar, Topbar, useLocalStorage, SessionTimeout, ChangePasswordModal, useToast, ErrorBoundary } from 'school-erp-ui-shared';
import { logout } from '../../store/authSlice';
import SubscriptionBanner from '../SubscriptionBanner';
import CommandPalette from '../CommandPalette';
import DarkModeToggle from '../DarkModeToggle';
import api from '../../services/api';
import { useSchoolProfile } from '../../services/settingsService';

const NAV_ITEMS = [
  { path: '/admin/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/admin/students', label: 'Students', icon: Users },
  { path: '/admin/admissions', label: 'Admissions', icon: UserPlus },
  { path: '/admin/teachers', label: 'Staff', icon: GraduationCap },
  { path: '/admin/staff', label: 'Staff & Payroll', icon: Briefcase },
  { path: '/admin/timetable', label: 'Timetable', icon: Calendar },
  { path: '/admin/attendance', label: 'Attendance', icon: ClipboardCheck },
  { path: '/admin/examinations', label: 'Examinations', icon: ClipboardList },
  { path: '/admin/fees', label: 'Fee Management', icon: DollarSign },
  { path: '/admin/transport', label: 'Transport', icon: Bus },
  { path: '/admin/leaves', label: 'Leave Management', icon: FileText },
  { path: '/admin/mentoring', label: 'Mentoring', icon: UserCheck },
  { path: '/admin/notifications', label: 'Notifications', icon: Bell },
  { path: '/admin/analytics', label: 'Analytics', icon: BarChart2 },
  { path: '/admin/credentials', label: 'Credentials', icon: KeyRound },
  { path: '/admin/settings', label: 'Settings', icon: Settings },
];

export default function AdminLayout() {
  const isFetching = useIsFetching();
  const [collapsed, setCollapsed] = useLocalStorage('admin-sidebar-collapsed', false);
  const [showChangePw, setShowChangePw] = useState(false);
  const [changePwLoading, setChangePwLoading] = useState(false);
  const [changePwError, setChangePwError] = useState('');
  const { user } = useSelector(s => s.auth);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const toast = useToast();
  const { data: schoolProfile } = useSchoolProfile();

  const handleChangePassword = async (data) => {
    setChangePwError('');
    setChangePwLoading(true);
    try {
      await api.post('/auth/change-password', data);
      toast.success('Password changed successfully');
      setShowChangePw(false);
    } catch (err) {
      setChangePwError(err.response?.data?.error || err.response?.data?.detail || 'Failed to change password');
    } finally {
      setChangePwLoading(false);
    }
  };

  // Session timeout: use token_expires_at if available, otherwise default to 30 minutes from now
  const tokenExpiresAt = user?.token_expires_at || user?.exp || (Date.now() + 30 * 60 * 1000);

  return (
    <>
      <style>{`@keyframes loading { 0% { transform: translateX(-100%); } 50% { transform: translateX(200%); } 100% { transform: translateX(-100%); } }`}</style>
      {isFetching > 0 && (
        <div className="fixed top-0 left-0 right-0 z-[9999] h-0.5 bg-primary-100">
          <div className="h-full bg-primary-500 animate-[loading_1.5s_ease-in-out_infinite]" style={{ width: '30%' }} />
        </div>
      )}
    <div className="flex h-screen overflow-hidden bg-slate-50">
      <Sidebar
        items={NAV_ITEMS}
        brand="ERP Portal"
        user={user ? { name: user.full_name, email: user.email, role: user.role } : null}
        collapsed={collapsed}
        onToggle={() => setCollapsed(!collapsed)}
        onLogout={() => dispatch(logout())}
        onSettings={() => navigate('/admin/settings')}
      />
      <div className={`flex-1 flex flex-col overflow-hidden transition-[margin] duration-200 ${collapsed ? 'md:ml-[68px]' : 'md:ml-60'}`}>
        <Topbar
          school={{ name: schoolProfile?.school_name || '', logo: schoolProfile?.logo_url?.startsWith('http') ? schoolProfile.logo_url : schoolProfile?.logo_url ? `${import.meta.env.VITE_API_BASE_URL?.replace(/\/api\/v1\/?$/, '')}${schoolProfile.logo_url}` : null }}
          user={user ? { name: user.full_name, role: user.role } : null}
          notificationCount={3}
          onNotificationClick={() => navigate('/admin/notifications')}
          onLogout={() => dispatch(logout())}
          onSettings={() => navigate('/admin/settings')}
          onChangePassword={() => setShowChangePw(true)}
          extraActions={<DarkModeToggle />}
          navItems={NAV_ITEMS}
        />
        <main className="flex-1 overflow-y-auto p-4 md:p-6 pb-20 md:pb-6">
          <SubscriptionBanner />
          <ErrorBoundary>
            <div className="animate-fade-in" style={{ animationDuration: '0.2s' }}>
              <Outlet />
            </div>
          </ErrorBoundary>
        </main>
      </div>
      <SessionTimeout tokenExpiresAt={tokenExpiresAt} onLogout={() => dispatch(logout())} onRefresh={async () => { await api.post('/auth/refresh-token'); window.location.reload(); }} />
      <ChangePasswordModal open={showChangePw} onClose={() => setShowChangePw(false)} onSubmit={handleChangePassword} loading={changePwLoading} error={changePwError} />
      <CommandPalette />
    </div>
    </>
  );
}
