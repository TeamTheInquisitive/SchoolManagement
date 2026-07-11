// ─── Status Chip Styles ─────────────────────────────────────────────────────
export const STATUS_STYLES = {
  Active: { bgcolor: '#dcfce7', color: '#16a34a' },
  active: { bgcolor: '#dcfce7', color: '#16a34a' },
  Operational: { bgcolor: '#dcfce7', color: '#16a34a' },
  Available: { bgcolor: '#f1f5f9', color: '#475569' },
  Paid: { bgcolor: '#dcfce7', color: '#16a34a' },
  Approved: { bgcolor: '#dcfce7', color: '#16a34a' },
  Generated: { bgcolor: '#dcfce7', color: '#16a34a' },
  Returned: { bgcolor: '#dcfce7', color: '#16a34a' },
  Pending: { bgcolor: '#fef3c7', color: '#d97706' },
  partial: { bgcolor: '#fef3c7', color: '#d97706' },
  Maintenance: { bgcolor: '#fef3c7', color: '#d97706' },
  Issued: { bgcolor: '#fef3c7', color: '#d97706' },
  Inactive: { bgcolor: '#f1f5f9', color: '#64748b' },
  Rejected: { bgcolor: '#fee2e2', color: '#dc2626' },
  Overdue: { bgcolor: '#fee2e2', color: '#dc2626' },
  overdue: { bgcolor: '#fee2e2', color: '#dc2626' },
  'Out-Of-Order': { bgcolor: '#fee2e2', color: '#dc2626' },
  Cancelled: { bgcolor: '#f1f5f9', color: '#64748b' },
  Disbursed: { bgcolor: '#dbeafe', color: '#2563eb' },
  paid: { bgcolor: '#dcfce7', color: '#16a34a' },
  pending: { bgcolor: '#f1f5f9', color: '#64748b' },
};

// ─── Dropdown Options ────────────────────────────────────────────────────────
export const CLASS_OPTIONS = ['8', '9', '10', '11', '12'];
export const SECTION_OPTIONS = ['A', 'B', 'C'];
export const GENDER_OPTIONS = [
  { value: 'Male', label: 'Male' },
  { value: 'Female', label: 'Female' },
  { value: 'Other', label: 'Other' },
];
export const EMPLOYMENT_TYPES = [
  { value: 'Full-Time', label: 'Full-Time' },
  { value: 'Part-Time', label: 'Part-Time' },
  { value: 'Contract', label: 'Contract' },
];
export const DEPARTMENTS = [
  { value: 'Teaching', label: 'Teaching' },
  { value: 'Administration', label: 'Administration' },
  { value: 'Accounts', label: 'Accounts' },
  { value: 'Transport', label: 'Transport' },
  { value: 'Maintenance', label: 'Maintenance' },
  { value: 'Others', label: 'Others' },
];
export const LEAVE_STATUSES = ['Pending', 'Approved', 'Rejected'];
export const FEE_STATUSES = ['paid', 'partial', 'pending', 'overdue'];
export const VEHICLE_TYPES = [
  { value: 'Bus', label: 'Bus' },
  { value: 'Mini-Bus', label: 'Mini-Bus' },
  { value: 'Van', label: 'Van' },
];
export const FUEL_TYPES = [
  { value: 'Diesel', label: 'Diesel' },
  { value: 'Petrol', label: 'Petrol' },
  { value: 'CNG', label: 'CNG' },
  { value: 'Electric', label: 'Electric' },
];
export const VEHICLE_STATUSES = [
  { value: 'Operational', label: 'Operational' },
  { value: 'Maintenance', label: 'Maintenance' },
  { value: 'Out-Of-Order', label: 'Out-Of-Order' },
];
export const SHIFT_OPTIONS = [
  { value: 'Morning', label: 'Morning' },
  { value: 'Afternoon', label: 'Afternoon' },
  { value: 'Evening', label: 'Evening' },
];
export const LICENSE_TYPES = [
  { value: 'Heavy Vehicle', label: 'Heavy Vehicle' },
  { value: 'Light Vehicle', label: 'Light Vehicle' },
  { value: 'Transport', label: 'Transport' },
];
export const EXAM_TYPES = [
  { value: 'Mid-Term', label: 'Mid-Term' },
  { value: 'Final', label: 'Final' },
  { value: 'Unit Test', label: 'Unit Test' },
  { value: 'Quarterly', label: 'Quarterly' },
];
export const BOOK_CATEGORIES = [
  { value: 'Mathematics', label: 'Mathematics' },
  { value: 'Physics', label: 'Physics' },
  { value: 'Chemistry', label: 'Chemistry' },
  { value: 'English', label: 'English' },
  { value: 'Biology', label: 'Biology' },
  { value: 'History', label: 'History' },
  { value: 'Computer Science', label: 'Computer Science' },
];

// ─── Dashboard Quick Actions ─────────────────────────────────────────────────
export const QUICK_ACTIONS = [
  { label: 'Exams', desc: '3 scheduled', icon: null, color: '#dbeafe', path: '/admin/examinations' },
  { label: 'Transport', desc: 'Fleet management', icon: null, color: '#fce7f3', path: '/admin/transport' },
  { label: 'Payroll', desc: 'Manage staff', icon: null, color: '#fef3c7', path: '/admin/payroll' },
  { label: 'Notifications', desc: 'Send messages', icon: null, color: '#ede9fe', path: '/admin/notifications' },
  { label: 'Timetable', desc: 'Schedule classes', icon: null, color: '#f3e8ff', path: '/admin/timetable' },
  { label: 'Student Details', desc: 'View profiles', icon: null, color: '#dcfce7', path: '/admin/students' },
  { label: 'Fee Management', desc: 'Track payments', icon: null, color: '#dbeafe', path: '/admin/fees' },
  { label: 'Mentoring', desc: 'Student mentoring', icon: null, color: '#ecfdf5', path: '/admin/mentoring' },
];

// ─── Notification Templates ──────────────────────────────────────────────────
export const NOTIFICATION_TEMPLATES = [
  { title: 'Fee Payment Reminder', message: 'Dear Parent/Guardian, This is a reminder that the school fee payment for this term is due. Please process the payment at your earliest convenience. Thank you, School Administration', recipients: ['parents'] },
  { title: 'PTM Notification', message: "Dear Parent/Guardian, Parent-Teacher Meeting (PTM) is scheduled for [Date] at [Time]. Your presence is requested to discuss your child's academic progress. Regards, School...", recipients: ['parents', 'teaching_staff'] },
  { title: 'Holiday Announcement', message: 'Dear All, This is to inform you that the school will remain closed on [Date] due to [Reason]. Regular classes will resume on [Date]. Stay safe, School Administration', recipients: ['all'] },
  { title: 'Exam Schedule', message: 'Dear Students/Parents, The examination schedule for [Term/Semester] has been published. Please check the school portal for detailed timing and subjects. Best wishes, Examination...', recipients: ['students', 'parents'] },
  { title: 'Event Invitation', message: 'Dear All, You are cordially invited to [Event Name] on [Date] at [Time]. Your participation would be greatly appreciated. Warm regards, Event Committee', recipients: ['all'] },
];

// ─── Notification Recipient Groups ───────────────────────────────────────────
export const RECIPIENT_GROUPS = [
  { id: 'teaching_staff', label: 'Teachers', description: 'All teaching staff', color: 'bg-blue-50 border-blue-200 text-blue-700' },
  { id: 'non_teaching_staff', label: 'Non-Teaching Staff', description: 'Admin & support', color: 'bg-purple-50 border-purple-200 text-purple-700' },
  { id: 'transport', label: 'Transport', description: 'Drivers & helpers', color: 'bg-amber-50 border-amber-200 text-amber-700' },
  { id: 'students', label: 'Students', description: 'All enrolled students', color: 'bg-emerald-50 border-emerald-200 text-emerald-700' },
  { id: 'parents', label: 'Parents', description: 'Guardians & parents', color: 'bg-pink-50 border-pink-200 text-pink-700' },
  { id: 'all', label: 'Everyone', description: 'All users', color: 'bg-slate-50 border-slate-200 text-slate-700' },
];

// ─── Timetable ───────────────────────────────────────────────────────────────
export const WORKING_DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
export const PERIOD_LABELS = ['Period 1', 'Period 2', 'Period 3', 'Period 4', 'Period 5', 'Period 6'];

// ─── Pagination ──────────────────────────────────────────────────────────────
export const DEFAULT_PAGE_SIZE = 20;
export const MAX_PAGE_SIZE = 100;
