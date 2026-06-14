import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Provider, useSelector } from 'react-redux';
import { store } from './store';
import LoginPage from './pages/auth/LoginPage';
import AdminLayout from './components/layout/AdminLayout';
import DashboardPage from './pages/dashboard/DashboardPage';
import StudentsPage from './pages/students/StudentsPage';
import StudentDetailsPage from './pages/students/StudentDetailsPage';
import TeachersPage from './pages/teachers/TeachersPage';
import TeacherDetailsPage from './pages/teachers/TeacherDetailsPage';
import TeacherPrivilegesPage from './pages/teachers/TeacherPrivilegesPage';
import LeaveManagementPage from './pages/leaves/LeaveManagementPage';
import ExaminationsPage from './pages/examinations/ExaminationsPage';
import LibraryPage from './pages/library/LibraryPage';
import FeeManagementPage from './pages/fees/FeeManagementPage';
import TransportPage from './pages/transport/TransportPage';
import PayrollPage from './pages/payroll/PayrollPage';
import StaffPage from './pages/staff/StaffPage';
import NotificationsPage from './pages/notifications/NotificationsPage';
import TimetablePage from './pages/timetable/TimetablePage';
import SettingsPage from './pages/settings/SettingsPage';
import AnalyticsPage from './pages/analytics/AnalyticsPage';
import MentoringPage from './pages/mentoring/MentoringPage';
import CredentialsPage from './pages/credentials/CredentialsPage';
import AttendancePage from './pages/attendance/AttendancePage';
import NewAdmissionPage from './pages/admissions/NewAdmissionPage';

function ProtectedRoute({ children, allowedRoles }) {
  const { user } = useSelector(s => s.auth);
  if (!user) return <Navigate to="/admin/login" replace />;
  if (allowedRoles && !allowedRoles.includes(user.role)) return <Navigate to="/admin/login" replace />;
  return children;
}

export default function App() {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <Routes>
          <Route path="/admin/login" element={<LoginPage />} />
          <Route path="/admin" element={<ProtectedRoute allowedRoles={['admin', 'super_admin']}><AdminLayout /></ProtectedRoute>}>
            <Route index element={<Navigate to="dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="students" element={<StudentsPage />} />
            <Route path="admissions" element={<NewAdmissionPage />} />
            <Route path="students/:id" element={<StudentDetailsPage />} />
            <Route path="teachers" element={<TeachersPage />} />
            <Route path="teachers/:id" element={<TeacherDetailsPage />} />
            <Route path="teacher-privileges" element={<TeacherPrivilegesPage />} />
            <Route path="leaves" element={<LeaveManagementPage />} />
            <Route path="examinations" element={<ExaminationsPage />} />
            <Route path="library" element={<LibraryPage />} />
            <Route path="fees" element={<FeeManagementPage />} />
            <Route path="transport" element={<TransportPage />} />
            <Route path="staff" element={<StaffPage />} />
            <Route path="payroll" element={<PayrollPage />} />
            <Route path="timetable" element={<TimetablePage />} />
            <Route path="timetable/:className/:sectionName" element={<TimetablePage />} />
            <Route path="notifications" element={<NotificationsPage />} />
            <Route path="analytics" element={<AnalyticsPage />} />
            <Route path="mentoring" element={<MentoringPage />} />
            <Route path="credentials" element={<CredentialsPage />} />
            <Route path="attendance" element={<AttendancePage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/admin/login" replace />} />
        </Routes>
      </BrowserRouter>
    </Provider>
  );
}
