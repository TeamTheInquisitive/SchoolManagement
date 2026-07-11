import { useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { useIsFetching, useQueryClient } from '@tanstack/react-query';
import { useSelector, useDispatch } from 'react-redux';
import {
  LayoutDashboard, Users, GraduationCap, UserCog, Calendar, ClipboardList,
  BookOpen, DollarSign, Bus, Bell, Briefcase, FileText, Settings, BarChart2, UserCheck, KeyRound, ClipboardCheck, UserPlus, Stamp,
} from 'lucide-react';
import { Sidebar, Topbar, useLocalStorage, SessionTimeout, ChangePasswordModal, useToast, ErrorBoundary } from 'school-erp-ui-shared';
import { logout } from '../../store/authSlice';
import SubscriptionBanner from '../SubscriptionBanner';
import { CommandPalette } from 'school-erp-ui-shared';
import DarkModeToggle from '../DarkModeToggle';
import api from '../../services/api';
import { useSchoolProfile } from '../../services/settingsService';

const ALL_NAV_ITEMS = [
  { path: '/admin/dashboard', label: 'Dashboard', icon: LayoutDashboard, module: 'dashboard' },
  { path: '/admin/students', label: 'Students', icon: Users, module: 'students' },
  { path: '/admin/admissions', label: 'Admissions', icon: UserPlus, module: 'admissions' },
  { path: '/admin/staff', label: 'Staff', icon: GraduationCap, module: 'staff' },
  { path: '/admin/payroll', label: 'Payroll', icon: Briefcase, module: 'staff' },
  { path: '/admin/timetable', label: 'Timetable', icon: Calendar, module: 'timetable' },
  { path: '/admin/attendance', label: 'Attendance', icon: ClipboardCheck, module: 'attendance' },
  { path: '/admin/examinations', label: 'Examinations', icon: ClipboardList, module: 'examinations' },
  { path: '/admin/fees', label: 'Fee Management', icon: DollarSign, module: 'fees' },
  { path: '/admin/transport', label: 'Transport', icon: Bus, module: 'transport' },
  { path: '/admin/leaves', label: 'Leave Management', icon: FileText, module: 'leaves' },
  { path: '/admin/mentoring', label: 'Mentoring', icon: UserCheck, module: 'mentoring' },
  { path: '/admin/credentials', label: 'Credentials', icon: KeyRound, module: 'settings' },
  { path: '/admin/analytics', label: 'Analytics', icon: BarChart2, module: 'dashboard' },
  { path: '/admin/notifications', label: 'Notifications', icon: Bell, module: 'notifications' },
  { path: '/admin/generators', label: 'Generators', icon: Stamp, module: 'settings' },
  { path: '/admin/settings', label: 'Settings', icon: Settings, module: 'settings' },
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
  const queryClient = useQueryClient();

  const allowedModules = user?.allowed_modules;
  const NAV_ITEMS = allowedModules
    ? ALL_NAV_ITEMS.filter(item => allowedModules.includes(item.module))
    : ALL_NAV_ITEMS;

  const handleLogout = () => {
    queryClient.clear();
    dispatch(logout());
  };
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
        onLogout={handleLogout}
        onSettings={() => navigate('/admin/settings')}
      />
      <div className={`flex-1 flex flex-col overflow-hidden transition-[margin] duration-200 ${collapsed ? 'md:ml-[68px]' : 'md:ml-60'}`}>
        <Topbar
          school={{ name: schoolProfile?.school_name || '', logo: schoolProfile?.logo_url?.startsWith('http') ? schoolProfile.logo_url : schoolProfile?.logo_url ? `${import.meta.env.VITE_API_BASE_URL?.replace(/\/api\/v1\/?$/, '')}${schoolProfile.logo_url}` : null }}
          user={user ? { name: user.full_name, role: user.role } : null}
          notificationCount={3}
          onNotificationClick={() => navigate('/admin/notifications')}
          onLogout={handleLogout}
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
      <SessionTimeout tokenExpiresAt={tokenExpiresAt} onLogout={handleLogout} onRefresh={async () => { await api.post('/auth/refresh-token'); window.location.reload(); }} />
      <ChangePasswordModal open={showChangePw} onClose={() => setShowChangePw(false)} onSubmit={handleChangePassword} loading={changePwLoading} error={changePwError} />
      <CommandPalette pages={NAV_ITEMS.map(item => ({ ...item, keywords: '' }))} />
    </div>
    </>
  );
}
