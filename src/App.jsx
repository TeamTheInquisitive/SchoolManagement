import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Provider, useSelector } from 'react-redux';
import { store } from './store';
import LoginPage from './pages/auth/LoginPage';
import AdminLayout from './components/layout/AdminLayout';
import DashboardPage from './pages/dashboard/DashboardPage';
import StudentsPage from './pages/students/StudentsPage';
import StudentDetailsPage from './pages/students/StudentDetailsPage';
import ClassStudentsPage from './pages/students/ClassStudentsPage';
import TeachersPage from './pages/teachers/TeachersPage';
import TeacherDetailsPage from './pages/teachers/TeacherDetailsPage';
import TeacherPrivilegesPage from './pages/teachers/TeacherPrivilegesPage';
import LeaveManagementPage from './pages/leaves/LeaveManagementPage';
import ExaminationsPage from './pages/examinations/ExaminationsPage';
import LibraryPage from './pages/library/LibraryPage';
import FeeManagementPage from './pages/fees/FeeManagementPage';
import TransportPage from './pages/transport/TransportPage';
import PayrollPage from './pages/payroll/PayrollPage';
import NotificationsPage from './pages/notifications/NotificationsPage';
import TimetablePage from './pages/timetable/TimetablePage';
import SettingsPage from './pages/settings/SettingsPage';
import AnalyticsPage from './pages/analytics/AnalyticsPage';
import MentoringPage from './pages/mentoring/MentoringPage';
import CredentialsPage from './pages/credentials/CredentialsPage';
import AttendancePage from './pages/attendance/AttendancePage';
import NewAdmissionPage from './pages/admissions/NewAdmissionPage';
import GeneratorsPage from './pages/generators/GeneratorsPage';

function NotFoundPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
      <h1 className="text-6xl font-bold text-slate-300 mb-4">404</h1>
      <p className="text-lg text-slate-600 mb-2">Page Not Found</p>
      <p className="text-sm text-slate-400">You don't have access to this page or it doesn't exist.</p>
    </div>
  );
}

function ProtectedRoute({ children, allowedRoles }) {
  const { user } = useSelector(s => s.auth);
  const location = useLocation();
  if (!user) return <Navigate to="/admin/login" state={{ from: location.pathname + location.search }} replace />;
  if (allowedRoles && !allowedRoles.includes(user.role)) return <Navigate to="/admin/login" replace />;
  return children;
}

function ModuleRoute({ module, children }) {
  const { user } = useSelector(s => s.auth);
  if (user?.allowed_modules && !user.allowed_modules.includes(module)) {
    return <NotFoundPage />;
  }
  return children;
}

const MODULE_TO_PATH = {
  dashboard: 'dashboard', students: 'students', admissions: 'admissions',
  staff: 'staff', timetable: 'timetable', attendance: 'attendance',
  examinations: 'examinations', fees: 'fees', transport: 'transport',
  leaves: 'leaves', mentoring: 'mentoring', notifications: 'notifications',
  library: 'library', settings: 'settings',
};

function AdminIndex() {
  const { user } = useSelector(s => s.auth);
  if (user?.allowed_modules && user.allowed_modules.length > 0) {
    const firstModule = user.allowed_modules[0];
    return <Navigate to={MODULE_TO_PATH[firstModule] || 'dashboard'} replace />;
  }
  return <Navigate to="dashboard" replace />;
}

export default function App() {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <Routes>
          <Route path="/admin/login" element={<LoginPage />} />
          <Route path="/admin" element={<ProtectedRoute allowedRoles={['admin', 'super_admin']}><AdminLayout /></ProtectedRoute>}>
            <Route index element={<AdminIndex />} />
            <Route path="dashboard" element={<ModuleRoute module="dashboard"><DashboardPage /></ModuleRoute>} />
            <Route path="students" element={<ModuleRoute module="students"><StudentsPage /></ModuleRoute>} />
            <Route path="admissions" element={<ModuleRoute module="admissions"><NewAdmissionPage /></ModuleRoute>} />
            <Route path="students/:className/:sectionName" element={<ModuleRoute module="students"><ClassStudentsPage /></ModuleRoute>} />
            <Route path="students/:className/:sectionName/:studentId" element={<ModuleRoute module="students"><ClassStudentsPage /></ModuleRoute>} />
            <Route path="students/:id" element={<ModuleRoute module="students"><StudentDetailsPage /></ModuleRoute>} />
            <Route path="staff" element={<ModuleRoute module="staff"><TeachersPage /></ModuleRoute>} />
            <Route path="staff/:id" element={<ModuleRoute module="staff"><TeacherDetailsPage /></ModuleRoute>} />
            <Route path="teacher-privileges" element={<ModuleRoute module="staff"><TeacherPrivilegesPage /></ModuleRoute>} />
            <Route path="leaves" element={<ModuleRoute module="leaves"><LeaveManagementPage /></ModuleRoute>} />
            <Route path="examinations" element={<ModuleRoute module="examinations"><ExaminationsPage /></ModuleRoute>} />
            <Route path="library" element={<ModuleRoute module="library"><LibraryPage /></ModuleRoute>} />
            <Route path="fees" element={<ModuleRoute module="fees"><FeeManagementPage /></ModuleRoute>} />
            <Route path="transport" element={<ModuleRoute module="transport"><TransportPage /></ModuleRoute>} />
            <Route path="staff-and-payroll" element={<Navigate to="/admin/payroll" replace />} />
            <Route path="payroll" element={<ModuleRoute module="staff"><PayrollPage /></ModuleRoute>} />
            <Route path="timetable" element={<ModuleRoute module="timetable"><TimetablePage /></ModuleRoute>} />
            <Route path="timetable/:className/:sectionName" element={<ModuleRoute module="timetable"><TimetablePage /></ModuleRoute>} />
            <Route path="notifications" element={<ModuleRoute module="notifications"><NotificationsPage /></ModuleRoute>} />
            <Route path="analytics" element={<ModuleRoute module="dashboard"><AnalyticsPage /></ModuleRoute>} />
            <Route path="mentoring" element={<ModuleRoute module="mentoring"><MentoringPage /></ModuleRoute>} />
            <Route path="credentials" element={<ModuleRoute module="settings"><CredentialsPage /></ModuleRoute>} />
            <Route path="attendance" element={<ModuleRoute module="attendance"><AttendancePage /></ModuleRoute>} />
            <Route path="settings" element={<ModuleRoute module="settings"><SettingsPage /></ModuleRoute>} />
            <Route path="generators" element={<ModuleRoute module="settings"><GeneratorsPage /></ModuleRoute>} />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/admin/login" replace />} />
        </Routes>
      </BrowserRouter>
    </Provider>
  );
}
