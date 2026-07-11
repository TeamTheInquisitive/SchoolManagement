import { useState, useEffect } from 'react';
import { Users, GraduationCap, Calendar, DollarSign, CheckCircle, XCircle, ArrowRight, BookOpen, Bus, Bell, ClipboardList, Clock, CreditCard, UserCheck, Heart, AlertTriangle, FileText, UserPlus, Cake, Send } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, Legend } from 'recharts';
import { useNavigate } from 'react-router-dom';
import { useDashboardStats, useAttendanceTrends, useFeeCollectionStatus, useStudentDistribution, useLeaveOverview, useLowAttendance, useBirthdays } from '../../services/dashboardService';
import { useAcademicYear } from '../../services/settingsService';
import { useApproveLeave, useRejectLeave } from '../../services/leaveService';
import { useCreateNotification } from '../../services/notificationService';
import { QUICK_ACTIONS } from '../../constants.jsx';
import { SkeletonDashboard, useToast, ErrorBoundary, AnimatedNumber, ConfirmDialog, Modal, Button, Badge } from 'school-erp-ui-shared';


const QUICK_ACTION_ICONS = {
  'Exams': ClipboardList,
  'Library': BookOpen,
  'Transport': Bus,
  'Payroll': CreditCard,
  'Notifications': Bell,
  'Timetable': Clock,
  'Student Details': UserCheck,
  'Fee Management': DollarSign,
  'Mentoring': Heart,
};

export default function DashboardPage() {
  const navigate = useNavigate();
  const toast = useToast();
  const { data: stats, isLoading } = useDashboardStats();
  const { data: attendanceTrends } = useAttendanceTrends();
  const { data: feeCollection } = useFeeCollectionStatus();
  const { data: studentDistribution } = useStudentDistribution();
  const { data: leaveOverview } = useLeaveOverview();
  const { data: lowAttendanceData } = useLowAttendance();
  const { data: academicYearData } = useAcademicYear();
  const { data: birthdaysData } = useBirthdays();

  const todayBirthdays = birthdaysData?.today || [];
  const upcomingBirthdays = birthdaysData?.upcoming || [];

  if (isLoading) return <SkeletonDashboard />;

  const attendanceData = attendanceTrends?.data || attendanceTrends?.results || (Array.isArray(attendanceTrends) ? attendanceTrends : []);
  const feeData = feeCollection?.data || feeCollection?.results || (Array.isArray(feeCollection) ? feeCollection : []);
  const classDistribution = (studentDistribution?.data || studentDistribution?.results || (Array.isArray(studentDistribution) ? studentDistribution : [])).map(d => ({ ...d, name: d.class_name || d.name }));
  const leave = leaveOverview ?? {};
  const lowAttendance = (lowAttendanceData?.data || lowAttendanceData?.results || (Array.isArray(lowAttendanceData) ? lowAttendanceData : [])).map(s => ({ ...s, class: s.class_section || s.class, attendance: s.attendance_percentage != null ? `${s.attendance_percentage}%` : s.attendance }));

  const kpis = [
    { label: 'Total Students', value: stats?.total_students ?? 0, icon: Users, color: 'text-blue-600', bg: 'bg-gradient-to-br from-blue-50 to-blue-100', border: 'border-blue-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(59,130,246,0.3)]' },
    { label: 'Total Teachers', value: stats?.total_teachers ?? 0, icon: GraduationCap, color: 'text-emerald-600', bg: 'bg-gradient-to-br from-emerald-50 to-emerald-100', border: 'border-emerald-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(16,185,129,0.3)]' },
    { label: 'Active Classes', value: stats?.active_classes ?? 0, icon: Calendar, color: 'text-amber-600', bg: 'bg-gradient-to-br from-amber-50 to-amber-100', border: 'border-amber-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(245,158,11,0.3)]' },
    { label: 'Fee Collection', value: `${stats?.fee_collection_percentage ?? 0}%`, icon: DollarSign, color: 'text-purple-600', bg: 'bg-gradient-to-br from-purple-50 to-purple-100', border: 'border-purple-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(147,51,234,0.3)]' },
  ];

  return (
    <div>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900">Dashboard Overview</h1>
          <p className="text-sm text-slate-500 mt-0.5">Welcome to your admin command center</p>
        </div>
        <span className="text-sm text-slate-500 bg-white border border-slate-200 rounded-full px-4 py-1.5 shadow-soft hidden md:inline-block">Academic Year {academicYearData?.current || academicYearData?.name || '—'}</span>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mb-6">
        {kpis.map((k) => (
          <div
            key={k.label}
            className={`bg-white border ${k.border} rounded-xl p-4 md:p-5 flex items-center gap-3 md:gap-4 transition-all duration-200 hover:-translate-y-1 ${k.glow} cursor-default group`}
          >
            <div className={`${k.bg} p-2.5 md:p-3 rounded-xl transition-transform duration-200 group-hover:scale-110`}>
              <k.icon size={20} className={k.color} />
            </div>
            <div>
              <p className="text-xs text-slate-500 font-medium">{k.label}</p>
              <p className="text-xl md:text-2xl font-bold text-slate-900 mt-0.5">{typeof k.value === 'string' && isNaN(parseInt(k.value)) ? k.value : <AnimatedNumber value={k.value} id={k.label} />}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Leave Overview */}
      <LeaveOverviewCard leave={leave} onManage={() => navigate('/admin/leaves')} toast={toast} />

      {/* Quick Actions */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-3">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {QUICK_ACTIONS.map(a => {
            const Icon = QUICK_ACTION_ICONS[a.label];
            return (
              <div
                key={a.label}
                onClick={() => navigate(a.path)}
                className="bg-white border border-slate-200 rounded-xl p-3 md:p-4 flex items-center gap-3 cursor-pointer transition-all duration-200 hover:-translate-y-0.5 hover:shadow-soft-lg hover:border-slate-300 active:translate-y-0 active:shadow-soft group"
              >
                <div
                  className="w-10 h-10 md:w-11 md:h-11 rounded-lg flex items-center justify-center transition-transform duration-200 group-hover:scale-110"
                  style={{ backgroundColor: a.color }}
                >
                  {Icon ? <Icon size={20} className="text-slate-700" /> : null}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-slate-800 group-hover:text-primary-600 transition-colors duration-150">{a.label}</p>
                  <p className="text-xs text-slate-500">{a.desc}</p>
                </div>
                <ArrowRight size={16} className="text-slate-300 opacity-0 -translate-x-2 transition-all duration-200 group-hover:opacity-100 group-hover:translate-x-0 hidden md:block" />
              </div>
            );
          })}
        </div>
      </div>

      {/* Charts */}
      <ErrorBoundary>
      <div className="grid grid-cols-1 md:grid-cols-12 gap-4 mb-6">
        <div className="md:col-span-7 bg-white border border-slate-200 rounded-xl p-4 md:p-5 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300">
          <h3 className="text-base font-semibold text-slate-900 mb-4">Attendance Trends</h3>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={attendanceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="month" tick={{ fontSize: 12, fill: '#64748b' }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 12, fill: '#64748b' }} />
              <Tooltip contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 4px 20px -4px rgba(0,0,0,0.1)' }} />
              <Line type="monotone" dataKey="value" stroke="#0ea5e9" strokeWidth={2.5} dot={{ r: 4, fill: '#0ea5e9', strokeWidth: 2, stroke: '#fff' }} activeDot={{ r: 6, fill: '#0ea5e9', stroke: '#e0f2fe', strokeWidth: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="md:col-span-5 bg-white border border-slate-200 rounded-xl p-4 md:p-5 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300">
          <h3 className="text-base font-semibold text-slate-900 mb-4">Fee Collection Status</h3>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={feeData} cx="50%" cy="50%" outerRadius={75} innerRadius={45} dataKey="value" labelLine={false}>
                {feeData.map((entry) => <Cell key={entry.name} fill={entry.color} />)}
              </Pie>
              <Tooltip contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 4px 20px -4px rgba(0,0,0,0.1)' }} formatter={(value, name) => {const total = feeData.reduce((a, d) => a + d.value, 0); return [`${value} (${total > 0 ? Math.round(value/total*100) : 0}%)`, name];}} />
              <Legend verticalAlign="bottom" height={36} iconType="circle" formatter={(value) => <span className="text-xs text-slate-600">{value}</span>} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
      </ErrorBoundary>

      {/* Distribution + Alerts */}
      <ErrorBoundary>
      <div className="grid grid-cols-1 md:grid-cols-12 gap-4 mb-6">
        <div className="md:col-span-7 bg-white border border-slate-200 rounded-xl p-4 md:p-5 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-semibold text-slate-900">Student Distribution by Class</h3>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-sm bg-blue-500" />
                <span className="text-xs text-slate-500">Male</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-sm bg-pink-500" />
                <span className="text-xs text-slate-500">Female</span>
              </div>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={classDistribution} barGap={4} barCategoryGap="20%">
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 8px 30px -4px rgba(0,0,0,0.12)', padding: '10px 14px' }}
                cursor={{ fill: 'rgba(148, 163, 184, 0.08)', radius: 8 }}
                labelStyle={{ fontWeight: 600, color: '#1e293b', marginBottom: 4 }}
              />
              <Bar dataKey="male" fill="url(#maleGradient)" name="Male" radius={[8, 8, 0, 0]} maxBarSize={32} />
              <Bar dataKey="female" fill="url(#femaleGradient)" name="Female" radius={[8, 8, 0, 0]} maxBarSize={32} />
              <defs>
                <linearGradient id="maleGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#60a5fa" />
                  <stop offset="100%" stopColor="#3b82f6" />
                </linearGradient>
                <linearGradient id="femaleGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#f472b6" />
                  <stop offset="100%" stopColor="#ec4899" />
                </linearGradient>
              </defs>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="md:col-span-5 bg-white border border-slate-200 rounded-xl p-4 md:p-5 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300">
          <div className="flex items-center gap-2 mb-4">
            <span className="w-2 h-2 rounded-full bg-danger-500 animate-pulse" />
            <h3 className="text-base font-semibold text-slate-900">Low Attendance Alerts</h3>
          </div>
          {lowAttendance.length === 0 ? (
            <div className="text-center py-8">
              <div className="w-12 h-12 rounded-full bg-emerald-50 flex items-center justify-center mx-auto mb-2">
                <CheckCircle size={20} className="text-emerald-400" />
              </div>
              <p className="text-sm font-medium text-slate-600">All good!</p>
              <p className="text-xs text-slate-400 mt-0.5">No attendance alerts at this time</p>
            </div>
          ) : (
            <div className="space-y-0">
              {lowAttendance.map((s, i) => (
                <div key={i} onClick={() => s.student_id && navigate(`/admin/students/${s.student_id}`)} className={`flex justify-between items-center py-3 transition-colors duration-150 hover:bg-slate-50 rounded-lg px-2 -mx-2 cursor-pointer ${i < lowAttendance.length - 1 ? 'border-b border-slate-100' : ''}`}>
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-purple-700 text-white flex items-center justify-center text-xs font-semibold">{(s.name || '').slice(0, 2).toUpperCase()}</div>
                    <div>
                      <p className="text-sm font-medium text-slate-800">{s.name}</p>
                      <p className="text-xs text-slate-500">Class {s.class}</p>
                    </div>
                  </div>
                  <span className="text-xs font-medium px-2.5 py-0.5 rounded-full bg-danger-100 text-danger-600">{s.attendance}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      </ErrorBoundary>

      {/* Pending Actions */}
      {(leave.pending_requests > 0 || stats?.pending_admissions > 0 || stats?.fee_overdue_count > 0) && (
        <div className="bg-white border border-slate-200 rounded-xl p-4 md:p-5 mb-6 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300">
          <h3 className="text-base font-semibold text-slate-900 mb-3">Needs Your Attention</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {[
              { label: 'Leave Approvals', value: leave.pending_requests ?? 0, icon: FileText, color: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-100', path: '/admin/leaves' },
              { label: 'Admission Requests', value: stats?.pending_admissions ?? 0, icon: UserPlus, color: 'text-blue-600', bg: 'bg-blue-50', border: 'border-blue-100', path: '/admin/admissions' },
              { label: 'Fee Overdue', value: stats?.fee_overdue_count ?? 0, icon: AlertTriangle, color: 'text-red-600', bg: 'bg-red-50', border: 'border-red-100', path: '/admin/fees' },
            ].filter(item => item.value > 0).map(item => (
              <div key={item.label} onClick={() => navigate(item.path)} className={`flex items-center gap-3 p-3.5 rounded-xl border ${item.border} ${item.bg} cursor-pointer transition-all duration-150 hover:-translate-y-0.5 hover:shadow-sm group`}>
                <div className="w-10 h-10 rounded-lg bg-white flex items-center justify-center flex-shrink-0 shadow-sm">
                  <item.icon size={18} className={item.color} />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-semibold text-slate-800">{item.label}</p>
                  <p className="text-xs text-slate-500">requires action</p>
                </div>
                <span className={`text-xl font-bold ${item.color}`}>{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Birthdays */}
      <BirthdayWidget todayBirthdays={todayBirthdays} upcomingBirthdays={upcomingBirthdays} toast={toast} />
    </div>
  );
}

function LeaveOverviewCard({ leave, onManage, toast }) {
  const approveLeave = useApproveLeave();
  const rejectLeave = useRejectLeave();
  const [confirmAction, setConfirmAction] = useState(null);

  const handleApprove = (req) => {
    setConfirmAction({ type: 'approve', id: req.id, name: req.teacher_name || req.staff_name || 'this teacher' });
  };

  const handleReject = (req) => {
    setConfirmAction({ type: 'reject', id: req.id, name: req.teacher_name || req.staff_name || 'this teacher' });
  };

  const confirmLeaveAction = () => {
    if (!confirmAction) return;
    if (confirmAction.type === 'approve') {
      approveLeave.mutate({ id: confirmAction.id, data: {} }, {
        onSuccess: () => { toast.success('Leave approved successfully'); setConfirmAction(null); },
        onError: (err) => { toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to approve leave'); setConfirmAction(null); },
      });
    } else {
      rejectLeave.mutate({ id: confirmAction.id, data: {} }, {
        onSuccess: () => { toast.success('Leave rejected successfully'); setConfirmAction(null); },
        onError: (err) => { toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to reject leave'); setConfirmAction(null); },
      });
    }
  };
  const stats = [
    { label: 'Pending', value: leave.pending_requests ?? 0, gradient: 'from-amber-50 to-amber-100', color: '#d97706', icon: Clock },
    { label: 'Approved', value: leave.approved ?? 0, gradient: 'from-emerald-50 to-emerald-100', color: '#16a34a', icon: CheckCircle },
    { label: 'On Leave Today', value: leave.on_leave_today ?? 0, gradient: 'from-indigo-50 to-indigo-100', color: '#4f46e5', icon: Users },
    { label: 'Upcoming', value: leave.upcoming_leaves ?? 0, gradient: 'from-blue-50 to-blue-100', color: '#2563eb', icon: Calendar },
  ];
  const pending = Array.isArray(leave.pending_approvals) ? leave.pending_approvals : [];

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 md:p-5 mb-6 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-base font-semibold text-slate-900">Teacher Leave Overview</h3>
        <button onClick={onManage} className="text-sm text-primary-600 font-medium hover:text-primary-700 transition-colors duration-150 flex items-center gap-1 group">
          Manage Leaves
          <ArrowRight size={16} className="transition-transform duration-200 group-hover:translate-x-0.5" />
        </button>
      </div>
      {stats.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          {stats.map(s => {
            const Icon = s.icon;
            return (
              <div key={s.label} className={`bg-gradient-to-br ${s.gradient} rounded-xl p-3 md:p-4 text-center transition-all duration-200 hover:-translate-y-0.5 hover:shadow-sm group`}>
                <div className="flex justify-center mb-1">
                  <Icon size={16} className="transition-transform duration-200 group-hover:scale-110" style={{ color: s.color }} />
                </div>
                <p className="text-xl md:text-2xl font-bold" style={{ color: s.color }}>{s.value}</p>
                <p className="text-xs text-slate-600 mt-0.5">{s.label}</p>
              </div>
            );
          })}
        </div>
      )}
      {pending.length > 0 && (
        <>
          <p className="text-sm font-semibold text-slate-900 mb-3">Pending Approvals</p>
          <div className="space-y-0">
            {pending.map((req, i) => {
              const displayName = req.employee_name || req.name || req.teacher_name || req.full_name || 'Unknown';
              const leaveType = req.type || req.leave_type || '';
              const duration = req.duration || (req.days ? `${req.days} day(s)` : req.duration_days ? `${req.duration_days} day(s)` : '');
              const dateRange = req.dates || (req.from_date && req.to_date ? `${req.from_date} → ${req.to_date}` : '');
              const details = [leaveType, duration, dateRange].filter(Boolean).join(' • ');
              return (
                <div key={req.id || i} className={`flex justify-between items-center py-3 transition-colors duration-150 hover:bg-slate-50 rounded-lg px-2 -mx-2 ${i < pending.length - 1 ? 'border-b border-slate-100' : ''}`}>
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 text-white flex items-center justify-center text-xs font-semibold">{displayName.slice(0, 2).toUpperCase()}</div>
                    <div>
                      <p className="text-sm font-medium text-slate-800">{displayName}</p>
                      {details && <p className="text-xs text-slate-500">{details}</p>}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => handleApprove(req)} className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium bg-success-500 text-white rounded-lg transition-all duration-150 hover:bg-success-600 hover:shadow-glow-success active:scale-[0.97]">
                      <CheckCircle size={14} /> Approve
                    </button>
                    <button onClick={() => handleReject(req)} className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium border border-danger-500/30 text-danger-600 rounded-lg transition-all duration-150 hover:bg-danger-50 hover:border-danger-500/50 active:scale-[0.97]">
                      <XCircle size={14} /> Reject
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}
      <ConfirmDialog
        open={!!confirmAction}
        onClose={() => setConfirmAction(null)}
        onConfirm={confirmLeaveAction}
        loading={approveLeave.isPending || rejectLeave.isPending}
        title={confirmAction?.type === 'approve' ? 'Approve Leave' : 'Reject Leave'}
        message={`Are you sure you want to ${confirmAction?.type} the leave request from ${confirmAction?.name}?`}
        confirmText={confirmAction?.type === 'approve' ? 'Approve' : 'Reject'}
      />
    </div>
  );
}

function BirthdayWidget({ todayBirthdays, upcomingBirthdays, toast }) {
  const [wishDialog, setWishDialog] = useState({ open: false, person: null });
  const [wishMessage, setWishMessage] = useState('');
  const createNotification = useCreateNotification();

  const allBirthdays = [
    ...todayBirthdays.map(b => ({ ...b, isToday: true })),
    ...upcomingBirthdays.map(b => ({ ...b, isToday: false })),
  ];

  const openWishDialog = (person) => {
    const name = person.name || person.full_name || 'there';
    setWishMessage(`Happy Birthday, ${name}! Wishing you a wonderful day filled with joy and happiness.`);
    setWishDialog({ open: true, person });
  };

  const handleSendWish = () => {
    const person = wishDialog.person;
    createNotification.mutate({
      title: 'Birthday Wishes',
      message: wishMessage,
      type: 'birthday',
      recipients: person.role === 'teacher' || person.role === 'staff'
        ? { teachers: [person.id] }
        : { students: [person.id] },
    }, {
      onSuccess: () => {
        toast.success('Birthday wishes sent successfully!');
        setWishDialog({ open: false, person: null });
        setWishMessage('');
      },
      onError: (err) => {
        toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to send wishes');
      },
    });
  };

  return (
    <>
      <div className="bg-white border border-pink-200 rounded-xl p-4 md:p-5 mt-6 transition-all duration-200 hover:shadow-soft-lg">
        <div className="flex items-center gap-3 mb-4">
          <div className="bg-gradient-to-br from-pink-100 to-pink-200 p-2.5 rounded-xl">
            <Cake size={20} className="text-pink-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-900">Upcoming Birthdays</h2>
            <p className="text-xs text-slate-500">Today + next 7 days</p>
          </div>
        </div>

        {allBirthdays.length === 0 ? (
          <div className="text-center py-8">
            <div className="w-12 h-12 rounded-full bg-slate-50 flex items-center justify-center mx-auto mb-2">
              <Cake size={20} className="text-slate-300" />
            </div>
            <p className="text-sm text-slate-400">No upcoming birthdays</p>
          </div>
        ) : (
          <div className="space-y-0">
            {allBirthdays.map((b, i) => {
              const displayName = b.name || b.full_name || 'Unknown';
              const initials = displayName.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase();
              const role = b.role === 'teacher' || b.role === 'staff' ? 'Teacher' : 'Student';
              const dateStr = b.date ? new Date(b.date + 'T00:00:00').toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) : '';
              return (
                <div key={i} className={`flex items-center justify-between py-3 ${i < allBirthdays.length - 1 ? 'border-b border-slate-100' : ''}`}>
                  <div className="flex items-center gap-3">
                    <div className={`w-9 h-9 rounded-full flex items-center justify-center text-xs font-bold text-white ${b.isToday ? 'bg-gradient-to-br from-pink-400 to-pink-600' : 'bg-gradient-to-br from-slate-400 to-slate-600'}`}>
                      {initials}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-medium text-slate-800">{displayName}</p>
                        {b.isToday && (
                          <Badge variant="pink" size="sm">Today</Badge>
                        )}
                      </div>
                      <p className="text-xs text-slate-500">{role} {dateStr ? `• ${dateStr}` : ''}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => openWishDialog(b)}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-pink-600 border border-pink-200 rounded-lg hover:bg-pink-50 transition-all duration-150 active:scale-[0.97]"
                  >
                    <Send size={12} /> Send Wishes
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Send Wishes Dialog */}
      <Modal open={wishDialog.open} onClose={() => setWishDialog({ open: false, person: null })} title="Send Birthday Wishes">
        <div className="p-4 space-y-4">
          <div className="flex items-center gap-3 bg-pink-50 border border-pink-100 rounded-xl p-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-pink-400 to-pink-600 text-white flex items-center justify-center text-sm font-bold">
              {(wishDialog.person?.name || wishDialog.person?.full_name || '').split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()}
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-800">{wishDialog.person?.name || wishDialog.person?.full_name}</p>
              <p className="text-xs text-pink-600">{wishDialog.person?.role === 'teacher' || wishDialog.person?.role === 'staff' ? 'Teacher' : 'Student'}</p>
            </div>
          </div>
          <div>
            <label className="text-xs font-medium text-slate-600 mb-1.5 block">Message</label>
            <textarea
              value={wishMessage}
              onChange={e => setWishMessage(e.target.value)}
              rows={4}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent transition-all duration-150 hover:border-slate-400 resize-none"
            />
          </div>
        </div>
        <div className="flex justify-end gap-2 px-4 pb-4">
          <Button variant="ghost" onClick={() => setWishDialog({ open: false, person: null })}>Cancel</Button>
          <Button variant="primary" onClick={handleSendWish} loading={createNotification.isPending}>
            <Send size={14} className="mr-1.5" /> Send Wishes
          </Button>
        </div>
      </Modal>
    </>
  );
}
