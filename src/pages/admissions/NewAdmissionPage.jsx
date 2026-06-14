import { useState } from 'react';
import { useDebounceValue } from 'usehooks-ts';
import { Plus, Users, CheckCircle, Clock, IndianRupee, Eye, Calendar, FileText, ArrowRight, User, Phone, Mail, MapPin, School, Banknote, XCircle } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useStudents, useCreateStudent, useUpdateStudent } from '../../services/studentService';
import { useFeeStructures, useAcademicYears, useAcademicYear } from '../../services/settingsService';
import { useClassSectionFilter } from '../../hooks/useClassSectionFilter';
import { Button, Badge, Modal, SearchableSelect, Tabs, ConfirmDialog, useToast, Breadcrumb, usePagination, DataTable, useTabState, DatePicker, DateRangePicker , AnimatedNumber } from 'school-erp-ui-shared';
import { GENDER_OPTIONS } from '../../constants.jsx';
import { fetchNextId } from '../../services/settingsService';

const ADMISSION_STATUS = 'Admission Pending';

const phoneRegex = /^[6-9]\d{9}$/;

const admissionSchema = z.object({
  full_name: z.string().min(1, 'Student name is required'),
  date_of_birth: z.string().optional(),
  gender: z.string().optional(),
  phone: z.string().regex(phoneRegex, '10 digits starting with 6-9').optional().or(z.literal('')),
  email: z.string().email('Invalid email').optional().or(z.literal('')),
  address: z.string().optional(),
  previous_school: z.string().optional(),
  student_type: z.string().optional(),
  parent_name: z.string().min(1, 'Parent/Guardian name is required'),
  parent_phone: z.string().regex(phoneRegex, '10 digits starting with 6-9'),
  parent_email: z.string().email('Invalid email').optional().or(z.literal('')),
  parent_relationship: z.string().optional(),
  parent_occupation: z.string().optional(),
  parent_address: z.string().optional(),
  class_name: z.string().min(1, 'Class is required'),
  section: z.string().optional(),
  concession: z.string().optional(),
  token_advance: z.string().optional(),
  token_payment_method: z.string().optional(),
  remarks: z.string().optional(),
});

export default function NewAdmissionPage() {
  const toast = useToast();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [viewStudent, setViewStudent] = useState(null);
  const [formStep, setFormStep] = useState(0);
  const admissionTabs = [{ id: 'pending', label: 'Pending', icon: Clock }, { id: 'admitted', label: 'Admitted', icon: CheckCircle }, { id: 'rejected', label: 'Rejected', icon: XCircle }];
  const [activeTab, setActiveTab] = useTabState(admissionTabs);
  const { selectedClass: filterClass, selectedSection: filterSection, setSelectedClass: setFilterClass, setSelectedSection: setFilterSection, classOptions, sectionOptions, classes: allClasses } = useClassSectionFilter();
  const { data: academicYearData } = useAcademicYear();
  const { data: academicYearsData } = useAcademicYears();
  const [selectedYear, setSelectedYear] = useState('');
  const [filterDateFrom, setFilterDateFrom] = useState('');
  const [filterDateTo, setFilterDateTo] = useState('');
  const pagination = usePagination(20, 'admin-admissions');
  const [search, setSearch] = useState('');
  const [debouncedSearch] = useDebounceValue(search, 300);

  const currentYear = selectedYear || academicYearData?.current || '';

  const tabStatuses = [ADMISSION_STATUS, 'Active', 'Rejected'];
  const currentStatus = tabStatuses[activeTab];

  const { data: studentsData, isFetching } = useStudents({
    ...pagination.params,
    status: currentStatus,
    search: debouncedSearch || undefined,
    class_name: filterClass || undefined,
    section: filterSection || undefined,
    date_from: filterDateFrom || undefined,
    date_to: filterDateTo || undefined,
  });

  // Fetch counts for each tab
  const { data: pendingData } = useStudents({ page: 1, page_size: 1, status: ADMISSION_STATUS });
  const { data: admittedData } = useStudents({ page: 1, page_size: 1, status: 'Active' });
  const { data: rejectedData } = useStudents({ page: 1, page_size: 1, status: 'Rejected' });

  const admissions = studentsData?.results ?? [];
  const createMutation = useCreateStudent();
  const updateMutation = useUpdateStudent();
  const [confirmAction, setConfirmAction] = useState(null);

  const pendingCount = pendingData?.count || 0;
  const admittedCount = admittedData?.count || 0;
  const rejectedCount = rejectedData?.count || 0;

  const stats = {
    total: pendingCount + admittedCount + rejectedCount,
    admitted: admittedCount,
    pending: pendingCount,
    rejected: rejectedCount,
  };

  const displayTabs = [
    { id: 'pending', label: `Pending (${pendingCount})`, icon: Clock },
    { id: 'admitted', label: `Admitted (${admittedCount})`, icon: CheckCircle },
    { id: 'rejected', label: `Rejected (${rejectedCount})`, icon: XCircle },
  ];

  const handleAdmit = (student) => {
    setConfirmAction({ type: 'admit', student });
  };

  const handleReject = (student) => {
    setConfirmAction({ type: 'reject', student });
  };

  const executeAction = () => {
    if (!confirmAction) return;
    const { type, student } = confirmAction;
    const status = type === 'admit' ? 'Active' : 'Rejected';
    updateMutation.mutate({ id: student.id, data: { status } }, {
      onSuccess: () => {
        toast.success(type === 'admit' ? `${student.full_name} admitted successfully` : 'Application rejected');
        setConfirmAction(null);
      },
      onError: (err) => {
        toast.error(err.response?.data?.detail || `Failed to ${type} student`);
        setConfirmAction(null);
      },
    });
  };

  const kpis = [
    { label: 'Total Applications', value: stats.total, icon: Users, color: 'text-blue-600', bg: 'bg-gradient-to-br from-blue-50 to-blue-100', border: 'border-blue-100' },
    { label: 'Admitted', value: stats.admitted, icon: CheckCircle, color: 'text-emerald-600', bg: 'bg-gradient-to-br from-emerald-50 to-emerald-100', border: 'border-emerald-100' },
    { label: 'Pending', value: stats.pending, icon: Clock, color: 'text-amber-600', bg: 'bg-gradient-to-br from-amber-50 to-amber-100', border: 'border-amber-100' },
    { label: 'Rejected', value: stats.rejected, icon: XCircle, color: 'text-red-600', bg: 'bg-gradient-to-br from-red-50 to-red-100', border: 'border-red-100' },
  ];

  const daysAgo = (dateStr) => {
    if (!dateStr) return null;
    const diff = Math.floor((new Date() - new Date(dateStr)) / 86400000);
    if (diff === 0) return 'Today';
    if (diff === 1) return '1 day ago';
    return `${diff} days ago`;
  };

  const classBreakdown = admissions.reduce((acc, s) => {
    const cls = s.class_name || 'Unknown';
    acc[cls] = (acc[cls] || 0) + 1;
    return acc;
  }, {});

  const columns = [
    { key: 'roll_number', label: 'Application No', sortable: true },
    { key: 'full_name', label: 'Student Name', sortable: true, render: (s) => (
      <div className="flex items-center gap-2">
        <div className="w-7 h-7 rounded-full bg-gradient-to-br from-indigo-500 to-indigo-700 text-white flex items-center justify-center text-xs font-semibold">{(s.full_name || '').slice(0, 2).toUpperCase()}</div>
        <div>
          <span className="font-medium text-slate-800">{s.full_name}</span>
          {s.admission_date && (s.status === ADMISSION_STATUS || s.status === 'Rejected') && (() => {
            const days = Math.floor((new Date() - new Date(s.admission_date)) / 86400000);
            return days > 7 ? <p className="text-[9px] text-amber-600 font-medium">{daysAgo(s.admission_date)}</p> : <p className="text-[9px] text-slate-400">{daysAgo(s.admission_date)}</p>;
          })()}
        </div>
      </div>
    )},
    { key: 'class_name', label: 'Class Applied', render: (s) => <span>{s.class_name} {s.section && `- ${s.section}`}</span> },
    { key: 'parent_name', label: 'Parent Name', render: (s) => <span className="text-slate-600">{s.parent_name || '—'}</span> },
    { key: 'phone', label: 'Phone', render: (s) => <span className="text-slate-500">{s.parent_phone || s.phone || '—'}</span> },
    { key: 'token_advance', label: 'Token', render: (s) => (
      <span className={`font-medium ${s.token_advance > 0 ? 'text-emerald-700' : 'text-slate-400'}`}>
        {s.token_advance > 0 ? `₹${Number(s.token_advance).toLocaleString()}` : '—'}
      </span>
    )},
    { key: 'status', label: 'Status', render: (s) => <Badge status={s.status === ADMISSION_STATUS ? 'Pending' : s.status} /> },
    { key: 'actions', label: 'Actions', render: (s) => (
      <div className="flex gap-1">
        <button onClick={(e) => { e.stopPropagation(); setViewStudent(s); }} className="p-1.5 hover:bg-slate-100 rounded-lg transition-all duration-150" title="View details">
          <Eye className="w-4 h-4 text-slate-500" />
        </button>
        {s.status === ADMISSION_STATUS && (
          <>
            <button onClick={(e) => { e.stopPropagation(); handleAdmit(s); }} className="px-2 py-1 text-xs bg-emerald-50 text-emerald-700 rounded hover:bg-emerald-100 font-medium">Admit</button>
            <button onClick={(e) => { e.stopPropagation(); handleReject(s); }} className="px-2 py-1 text-xs bg-red-50 text-red-700 rounded hover:bg-red-100 font-medium">Reject</button>
          </>
        )}
        {s.status === 'Rejected' && (
          <button onClick={(e) => { e.stopPropagation(); handleAdmit(s); }} className="px-2 py-1 text-xs bg-emerald-50 text-emerald-700 rounded hover:bg-emerald-100 font-medium">Re-Approve</button>
        )}
      </div>
    )},
  ];

  const yearOptions = (Array.isArray(academicYearsData) ? academicYearsData : academicYearsData?.academic_years || []).map(y => ({ value: y.name || y.year || y, label: y.name || y.year || y }));

  return (
    <div>
      <Breadcrumb items={[{ label: 'Dashboard', href: '/admin/dashboard' }, { label: 'New Admissions' }]} />
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900">New Admissions</h1>
          <p className="text-sm text-slate-500 mt-1">Track and manage new student admissions for the academic year</p>
        </div>
        <div className="flex items-center gap-3">
          {yearOptions.length > 1 && (
            <div className="w-44">
              <SearchableSelect value={currentYear} onChange={setSelectedYear} options={yearOptions} placeholder="Academic Year" />
            </div>
          )}
          <Button variant="primary" icon={Plus} onClick={() => { setFormStep(0); setDialogOpen(true); }}>New Admission</Button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mb-6">
        {kpis.map(k => (
          <div key={k.label} className={`bg-white border ${k.border} rounded-xl p-4 flex items-center gap-3 transition-all duration-200 hover:-translate-y-1 cursor-default`}>
            <div className={`${k.bg} p-2.5 rounded-xl`}><k.icon className={`w-5 h-5 ${k.color}`} /></div>
            <div><p className="text-xs text-slate-500 font-medium">{k.label}</p><p className="text-xl md:text-2xl font-bold text-slate-900"><AnimatedNumber value={k.value} id={k.label} /></p></div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <Tabs tabs={displayTabs} active={activeTab} onChange={(i) => { setActiveTab(i); pagination.reset(); setSearch(''); setFilterClass(''); setFilterSection(''); setFilterDateFrom(''); setFilterDateTo(''); }} className="mb-4" />

      {/* Date Range Filter */}
      <div className="mb-4">
        <DateRangePicker
          label="Filter by Date"
          startValue={filterDateFrom}
          endValue={filterDateTo}
          onChange={(start, end) => { setFilterDateFrom(start); setFilterDateTo(end); pagination.reset(); }}
          placeholder="Select date range"
        />
      </div>

      {/* Class Breakdown */}
      {Object.keys(classBreakdown).length > 0 && (
        <div className="flex items-center gap-2 mb-3 flex-wrap">
          <span className="text-[10px] font-semibold text-slate-400 uppercase">By Class:</span>
          {Object.entries(classBreakdown).sort(([a], [b]) => a.localeCompare(b, undefined, { numeric: true })).map(([cls, count]) => (
            <span key={cls} className="text-[11px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full font-medium">
              Class {cls} <span className="text-slate-800 font-bold">{count}</span>
            </span>
          ))}
        </div>
      )}

      <DataTable
        columns={columns}
        data={admissions}
        loading={isFetching}
        emptyMessage={activeTab === 0 ? "No pending applications. Click 'New Admission' to add one." : activeTab === 1 ? 'No admitted students yet.' : 'No rejected applications.'}
        emptyIcon={activeTab === 0 ? Clock : activeTab === 1 ? CheckCircle : XCircle}
        headerTitle={activeTab === 0 ? 'Pending Applications' : activeTab === 1 ? 'Admitted Students' : 'Rejected Applications'}
        headerCount={studentsData?.count || 0}
        search={{ value: search, onChange: (v) => { setSearch(v); pagination.reset(); }, placeholder: 'Search by name or application no...' }}
        filters={[
          { key: 'class', value: filterClass, onChange: (v) => { setFilterClass(v); pagination.reset(); }, options: classOptions },
          { key: 'section', value: filterSection, onChange: (v) => { setFilterSection(v); pagination.reset(); }, options: sectionOptions },
        ]}
        page={pagination.page}
        totalPages={studentsData?.total_pages || 1}
        totalCount={studentsData?.count || 0}
        pageSize={pagination.pageSize}
        onPageChange={(p) => pagination.setPage(p)}
        onPageSizeChange={pagination.setPageSize}
      />

      {/* New Admission Form Modal */}
      <Modal open={dialogOpen} onClose={() => { setDialogOpen(false); setFormStep(0); }} title="New Admission" size="3xl">
        <AdmissionFormWizard
          formStep={formStep}
          setFormStep={setFormStep}
          classOptions={classOptions}
          allClasses={allClasses}
          onCancel={() => { setDialogOpen(false); setFormStep(0); }}
          onSuccess={() => { setDialogOpen(false); setFormStep(0); toast.success('Admission application created successfully'); }}
          onError={(msg) => toast.error(msg)}
          createMutation={createMutation}
        />
      </Modal>

      {/* View Admission Details Modal */}
      <Modal open={!!viewStudent} onClose={() => setViewStudent(null)} title="Admission Details" size="2xl">
        {viewStudent && <AdmissionViewPanel student={viewStudent} onClose={() => setViewStudent(null)} onAdmit={() => { handleAdmit(viewStudent); setViewStudent(null); }} onReject={() => { handleReject(viewStudent); setViewStudent(null); }} />}
      </Modal>

      {/* Admit Confirmation */}
      {confirmAction?.type === 'admit' && (
        <Modal open onClose={() => setConfirmAction(null)} title="Confirm Admission" size="md" persistent={false}>
          <div className="space-y-4">
            <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 flex items-start gap-3">
              <CheckCircle className="w-6 h-6 text-emerald-500 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm font-semibold text-emerald-900">Approve this admission?</p>
                <p className="text-xs text-emerald-700 mt-1">This will change the student's status from <span className="font-medium">Pending</span> to <span className="font-medium">Active</span>. They will appear in the class roster and fee records will be generated.</p>
              </div>
            </div>
            <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-indigo-700 text-white flex items-center justify-center text-sm font-bold flex-shrink-0">
                  {(confirmAction.student.full_name || '').slice(0, 2).toUpperCase()}
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-900">{confirmAction.student.full_name}</p>
                  <p className="text-xs text-slate-500">Class {confirmAction.student.class_name}{confirmAction.student.section ? ` - ${confirmAction.student.section}` : ''} • {confirmAction.student.roll_number}</p>
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
              <Button variant="ghost" onClick={() => setConfirmAction(null)}>Cancel</Button>
              <Button variant="primary" onClick={executeAction} disabled={updateMutation.isPending}>
                {updateMutation.isPending ? 'Admitting...' : 'Confirm Admission'}
              </Button>
            </div>
          </div>
        </Modal>
      )}

      {/* Reject Confirmation */}
      {confirmAction?.type === 'reject' && (
        <Modal open onClose={() => setConfirmAction(null)} title="Reject Application" size="md" persistent={false}>
          <div className="space-y-4">
            <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3">
              <svg className="w-6 h-6 text-red-500 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
              <div>
                <p className="text-sm font-semibold text-red-900">Reject this application?</p>
                <p className="text-xs text-red-700 mt-1">This will mark the admission application as <span className="font-medium">Rejected</span>. The student will not be enrolled. This action can be reversed later if needed.</p>
              </div>
            </div>
            <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-indigo-700 text-white flex items-center justify-center text-sm font-bold flex-shrink-0">
                  {(confirmAction.student.full_name || '').slice(0, 2).toUpperCase()}
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-900">{confirmAction.student.full_name}</p>
                  <p className="text-xs text-slate-500">Class {confirmAction.student.class_name}{confirmAction.student.section ? ` - ${confirmAction.student.section}` : ''} • {confirmAction.student.roll_number}</p>
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
              <Button variant="ghost" onClick={() => setConfirmAction(null)}>Cancel</Button>
              <Button variant="primary" onClick={executeAction} disabled={updateMutation.isPending} className="bg-red-600 hover:bg-red-700 border-red-600">
                {updateMutation.isPending ? 'Rejecting...' : 'Reject Application'}
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}

// ─── Admission View Panel ────────────────────────────────────────────────────
function AdmissionViewPanel({ student, onClose, onAdmit, onReject }) {
  const s = student;
  const InfoRow = ({ icon: Icon, label, value }) => (
    <div className="flex items-start gap-3 py-2">
      <Icon className="w-4 h-4 text-slate-400 mt-0.5 flex-shrink-0" />
      <div>
        <p className="text-xs text-slate-500">{label}</p>
        <p className="text-sm font-medium text-slate-800">{value || '—'}</p>
      </div>
    </div>
  );

  return (
    <div className="space-y-5">
      {/* Status Timeline */}
      <div className="flex items-center gap-0 mb-5">
        {[
          { label: 'Applied', done: true },
          { label: 'Reviewed', done: s.status !== 'Admission Pending' },
          { label: s.status === 'Rejected' ? 'Rejected' : 'Admitted', done: s.status === 'Active' || s.status === 'Rejected' },
        ].map((step, i, arr) => (
          <div key={step.label} className="flex items-center flex-1">
            <div className="flex flex-col items-center">
              <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${step.done ? (step.label === 'Rejected' ? 'bg-red-500 text-white' : 'bg-emerald-500 text-white') : 'bg-slate-200 text-slate-400'}`}>
                {step.done ? '✓' : i + 1}
              </div>
              <span className={`text-[10px] mt-1 ${step.done ? 'text-slate-700 font-medium' : 'text-slate-400'}`}>{step.label}</span>
            </div>
            {i < arr.length - 1 && <div className={`flex-1 h-0.5 mx-2 ${step.done ? 'bg-emerald-400' : 'bg-slate-200'}`} />}
          </div>
        ))}
      </div>

      {/* Student Info */}
      <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-indigo-700 text-white flex items-center justify-center text-sm font-bold">{(s.full_name || '').slice(0, 2).toUpperCase()}</div>
          <div>
            <h3 className="font-semibold text-slate-900">{s.full_name}</h3>
            <p className="text-xs text-slate-500">Application: {s.roll_number}</p>
          </div>
          <div className="ml-auto"><Badge status={s.status === ADMISSION_STATUS ? 'Pending' : s.status} /></div>
        </div>
        <div className="grid grid-cols-2 gap-x-6">
          <InfoRow icon={Calendar} label="Date of Birth" value={s.date_of_birth} />
          <InfoRow icon={User} label="Gender" value={s.gender} />
          <InfoRow icon={Phone} label="Phone" value={s.phone} />
          <InfoRow icon={Mail} label="Email" value={s.email} />
          <InfoRow icon={MapPin} label="Address" value={s.address} />
          <InfoRow icon={School} label="Previous School" value={s.previous_school} />
        </div>
      </div>

      {/* Parent Info */}
      <div className="bg-blue-50/50 rounded-xl p-4 border border-blue-100">
        <h4 className="text-sm font-semibold text-slate-700 mb-2">Parent / Guardian</h4>
        <div className="grid grid-cols-2 gap-x-6">
          <InfoRow icon={User} label="Name" value={s.parent_name} />
          <InfoRow icon={User} label="Relationship" value={s.parent_relationship} />
          <InfoRow icon={Phone} label="Phone" value={s.parent_phone} />
          <InfoRow icon={Mail} label="Email" value={s.parent_email} />
          <InfoRow icon={FileText} label="Occupation" value={s.parent_occupation} />
        </div>
      </div>

      {/* Academic & Fee Info */}
      <div className="bg-emerald-50/50 rounded-xl p-4 border border-emerald-100">
        <h4 className="text-sm font-semibold text-slate-700 mb-2">Academic & Fees</h4>
        <div className="grid grid-cols-2 gap-x-6">
          <InfoRow icon={School} label="Class Applied" value={`${s.class_name} ${s.section ? `- ${s.section}` : ''}`} />
          <InfoRow icon={User} label="Student Type" value={s.student_type} />
          <InfoRow icon={Banknote} label="Token Advance" value={s.token_advance ? `₹${Number(s.token_advance).toLocaleString()} (${s.token_payment_method || 'Cash'})` : 'None'} />
          <InfoRow icon={IndianRupee} label="Concession" value={s.concessions ? `₹${Object.values(s.concessions).reduce((sum, v) => sum + Number(v), 0).toLocaleString()}` : 'None'} />
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
        <Button variant="ghost" onClick={onClose}>Close</Button>
        {s.status === ADMISSION_STATUS && (
          <>
            <Button variant="secondary" onClick={onReject} className="text-red-600 border-red-200 hover:bg-red-50">Reject</Button>
            <Button variant="primary" onClick={onAdmit}>Admit Student</Button>
          </>
        )}
        {s.status === 'Rejected' && (
          <Button variant="primary" onClick={onAdmit}>Re-Approve & Admit</Button>
        )}
      </div>
    </div>
  );
}

// ─── Multi-Step Form Wizard ──────────────────────────────────────────────────
const STEPS = [
  { id: 'student', label: 'Student Details', icon: '1' },
  { id: 'parent', label: 'Parent/Guardian', icon: '2' },
  { id: 'academic', label: 'Class & Fees', icon: '3' },
  { id: 'summary', label: 'Review & Submit', icon: '4' },
];

const PAYMENT_METHODS = ['Cash', 'Online', 'UPI', 'Cheque', 'Card', 'Bank Transfer'];

function AdmissionFormWizard({ formStep, setFormStep, classOptions = [], allClasses = [], onCancel, onSuccess, onError, createMutation }) {
  const { register, handleSubmit, watch, setValue, trigger, formState: { errors }, getValues } = useForm({
    resolver: zodResolver(admissionSchema),
    defaultValues: {
      student_type: '',
      gender: '',
      class_name: '',
      section: '',
      parent_relationship: 'Father',
      token_payment_method: 'Cash',
      concession: '',
      token_advance: '',
    },
  });
  const { data: feeData } = useFeeStructures();
  const structures = feeData?.structures || [];
  const classSections = feeData?.class_sections || [];
  const selectedClass = watch('class_name');
  const selectedSection = watch('section');
  const matchedClass = allClasses.find(c => c.name === selectedClass);
  const matchedClassSection = classSections.find(cs => cs.class_id === matchedClass?.id && cs.display_name?.endsWith(`- ${selectedSection}`));
  const generalFees = structures.filter(fs => !fs.class_id && !fs.class_section_id);
  const classWideFees = structures.filter(fs => fs.class_id === matchedClass?.id && !fs.class_section_id);
  const sectionFees = matchedClassSection ? structures.filter(fs => fs.class_section_id === matchedClassSection.id) : [];
  const applicableFees = [...generalFees, ...classWideFees, ...sectionFees];
  const totalFee = applicableFees.reduce((s, f) => s + (Number(f.amount) || 0), 0);
  const [feeConcessions, setFeeConcessions] = useState({});
  const totalConcession = Object.values(feeConcessions).reduce((s, v) => s + (Number(v) || 0), 0);
  const netFee = Math.max(0, totalFee - totalConcession);
  const concessionAmt = totalConcession;

  const inp = (err) => `w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400 ${err ? 'border-red-400' : 'border-slate-300'}`;

  const handleNext = async () => {
    if (formStep === 0) {
      const valid = await trigger(['full_name', 'phone', 'email']);
      if (!valid) return;
    }
    if (formStep === 1) {
      const valid = await trigger(['parent_name', 'parent_phone', 'parent_email']);
      if (!valid) return;
    }
    if (formStep === 2) {
      const valid = await trigger(['class_name']);
      if (!valid) return;
    }
    setFormStep(formStep + 1);
  };

  const onSubmit = async (data) => {
    // Generate application number
    let rollNumber = `ADM-${Date.now().toString(36).toUpperCase()}`;
    try { const res = await fetchNextId('student'); if (res.enabled && res.id) rollNumber = res.id; } catch {}

    const payload = {
      roll_number: rollNumber,
      full_name: data.full_name,
      email: data.email || undefined,
      phone: data.phone || undefined,
      class_name: data.class_name,
      section: data.section || 'A',
      date_of_birth: data.date_of_birth || undefined,
      gender: data.gender || undefined,
      student_type: data.student_type || undefined,
      address: data.address || undefined,
      parent_name: data.parent_name || undefined,
      parent_phone: data.parent_phone || undefined,
      parent_email: data.parent_email || undefined,
      parent_relationship: data.parent_relationship || undefined,
      parent_occupation: data.parent_occupation || undefined,
      previous_school: data.previous_school || undefined,
      token_advance: data.token_advance ? Number(data.token_advance) : undefined,
      token_payment_method: data.token_payment_method || undefined,
      status: ADMISSION_STATUS,
      concessions: totalConcession > 0 ? Object.fromEntries(Object.entries(feeConcessions).filter(([, v]) => Number(v) > 0)) : undefined,
    };
    // Remove undefined values
    const cleanPayload = Object.fromEntries(Object.entries(payload).filter(([, v]) => v !== undefined));

    createMutation.mutate(cleanPayload, {
      onSuccess: () => onSuccess(),
      onError: (err) => onError(err.response?.data?.error || err.response?.data?.detail || 'Failed to create admission'),
    });
  };

  return (
    <div>
      {/* Stepper */}
      <div className="flex items-center justify-between mb-6 px-2">
        {STEPS.map((step, i) => (
          <div key={step.id} className="flex items-center flex-1">
            <div className="flex items-center gap-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-200 ${
                i < formStep ? 'bg-emerald-500 text-white' : i === formStep ? 'bg-primary-600 text-white shadow-md shadow-primary-200' : 'bg-slate-100 text-slate-400'
              }`}>{i < formStep ? '✓' : step.icon}</div>
              <span className={`text-xs font-medium hidden sm:inline ${i === formStep ? 'text-primary-700' : i < formStep ? 'text-emerald-600' : 'text-slate-400'}`}>{step.label}</span>
            </div>
            {i < STEPS.length - 1 && <div className={`flex-1 h-0.5 mx-2 rounded ${i < formStep ? 'bg-emerald-300' : 'bg-slate-200'}`} />}
          </div>
        ))}
      </div>

      {/* Step 1: Student Details */}
      {formStep === 0 && (
        <div className="space-y-4 max-h-[55vh] overflow-y-auto pr-1 pb-4">
          <div className="bg-slate-50 rounded-xl p-3 border border-slate-100 mb-2">
            <p className="text-xs text-slate-500">Enter the student's personal information. Fields marked with * are required.</p>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Student Name *</label>
              <input {...register('full_name')} className={inp(errors.full_name)} placeholder="Full name of the student" />
              {errors.full_name && <p className="text-xs text-red-500 mt-0.5">{errors.full_name.message}</p>}
            </div>
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Date of Birth</label>
              <DatePicker value={watch('date_of_birth')} onChange={(v) => setValue('date_of_birth', v, { shouldDirty: true })} />
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Gender</label>
              <SearchableSelect value={watch('gender')} onChange={(v) => setValue('gender', v)} options={[{ value: '', label: 'Select' }, ...GENDER_OPTIONS]} placeholder="Select..." />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Phone</label>
              <input {...register('phone')} maxLength={10} placeholder="9876543210" className={inp(errors.phone)} />
              {errors.phone && <p className="text-xs text-red-500 mt-0.5">{errors.phone.message}</p>}
            </div>
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Email</label>
              <input {...register('email')} className={inp(errors.email)} placeholder="student@email.com" />
              {errors.email && <p className="text-xs text-red-500 mt-0.5">{errors.email.message}</p>}
            </div>
          </div>
          <div>
            <label className="text-xs font-medium text-slate-600 mb-1 block">Address</label>
            <input {...register('address')} className={inp()} placeholder="Full residential address" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Previous School</label>
              <input {...register('previous_school')} className={inp()} placeholder="Name of previous school" />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Student Type</label>
              <SearchableSelect value={watch('student_type')} onChange={(v) => setValue('student_type', v)} options={[{ value: '', label: 'Select' }, { value: 'Day Scholar', label: 'Day Scholar' }, { value: 'Hosteller', label: 'Hosteller' }]} placeholder="Select..." />
            </div>
          </div>
        </div>
      )}

      {/* Step 2: Parent/Guardian Details */}
      {formStep === 1 && (
        <div className="space-y-4 max-h-[55vh] overflow-y-auto pr-1 pb-4">
          <div className="bg-slate-50 rounded-xl p-3 border border-slate-100 mb-2">
            <p className="text-xs text-slate-500">Enter the parent or guardian details. This will be used for communication and fee receipts.</p>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Parent/Guardian Name *</label>
              <input {...register('parent_name')} className={inp(errors.parent_name)} placeholder="Full name" />
              {errors.parent_name && <p className="text-xs text-red-500 mt-0.5">{errors.parent_name.message}</p>}
            </div>
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Relationship</label>
              <SearchableSelect value={watch('parent_relationship')} onChange={(v) => setValue('parent_relationship', v)} options={[{ value: 'Father', label: 'Father' }, { value: 'Mother', label: 'Mother' }, { value: 'Guardian', label: 'Guardian' }]} placeholder="Select..." />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Phone *</label>
              <input {...register('parent_phone')} maxLength={10} placeholder="9876543210" className={inp(errors.parent_phone)} />
              {errors.parent_phone && <p className="text-xs text-red-500 mt-0.5">{errors.parent_phone.message}</p>}
            </div>
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Email</label>
              <input {...register('parent_email')} className={inp(errors.parent_email)} placeholder="parent@email.com" />
              {errors.parent_email && <p className="text-xs text-red-500 mt-0.5">{errors.parent_email.message}</p>}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Occupation</label>
              <input {...register('parent_occupation')} className={inp()} placeholder="e.g. Engineer, Doctor, Business" />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Parent Address</label>
              <input {...register('parent_address')} className={inp()} placeholder="Same as student if left blank" />
            </div>
          </div>
        </div>
      )}

      {/* Step 3: Class, Fee & Token Advance */}
      {formStep === 2 && (
        <div className="space-y-4 max-h-[55vh] overflow-y-auto pr-1 pb-4">
          {/* Class Selection */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Class Applied *</label>
              <SearchableSelect value={watch('class_name')} onChange={(v) => { setValue('class_name', v, { shouldValidate: true }); setValue('section', ''); }} options={classOptions.filter(o => o.value)} placeholder="Select Class..." />
              {errors.class_name && <p className="text-xs text-red-500 mt-0.5">{errors.class_name.message}</p>}
            </div>
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Section Preference</label>
              <SearchableSelect value={watch('section')} onChange={(v) => setValue('section', v)} options={(() => { const cls = allClasses.find(c => c.name === watch('class_name')); return cls?.sections?.length ? cls.sections.map(s => ({ value: s.section_name, label: s.section_name })) : []; })()} placeholder="Select..." />
            </div>
          </div>

          {/* Fee Structure Display with Concession */}
          {applicableFees.length > 0 && (
            <div className="rounded-xl border border-slate-200 overflow-hidden">
              <div className="bg-blue-50 px-4 py-2.5 border-b border-blue-100 flex items-center justify-between">
                <p className="text-xs text-blue-700 font-medium">Fee Structure for {selectedClass ? `Class ${selectedClass}` : 'selected class'}{selectedSection ? ` - ${selectedSection}` : ''}</p>
                <span className="text-xs text-blue-500">({applicableFees.length} components)</span>
              </div>
              <table className="w-full text-sm">
                <thead><tr className="bg-slate-50 border-b border-slate-200">
                  <th className="text-left px-4 py-2 text-xs font-semibold text-slate-500">Fee Type</th>
                  <th className="text-left px-4 py-2 text-xs font-semibold text-slate-500">Frequency</th>
                  <th className="text-right px-4 py-2 text-xs font-semibold text-slate-500">Amount</th>
                  <th className="text-right px-4 py-2 text-xs font-semibold text-slate-500">Concession</th>
                  <th className="text-right px-4 py-2 text-xs font-semibold text-slate-500">Net Amount</th>
                </tr></thead>
                <tbody className="divide-y divide-slate-100">
                  {applicableFees.map((f, i) => {
                    const amt = Number(f.amount) || 0;
                    const disc = Number(feeConcessions[f.id]) || 0;
                    const net = Math.max(0, amt - disc);
                    return (
                      <tr key={f.id || i} className="hover:bg-slate-50/50">
                        <td className="px-4 py-2.5">
                          <p className="font-medium text-slate-800">{f.fee_type}</p>
                          <p className="text-[11px] text-slate-400 capitalize">{f.fee_category}</p>
                        </td>
                        <td className="px-4 py-2.5 text-slate-500 capitalize">{f.frequency}</td>
                        <td className="px-4 py-2.5 text-right font-medium text-slate-700">₹{amt.toLocaleString()}</td>
                        <td className="px-4 py-2.5 text-right">
                          <input type="number" min="0" max={amt} value={feeConcessions[f.id] || ''} onChange={(e) => setFeeConcessions(prev => ({ ...prev, [f.id]: e.target.value }))} placeholder="0" className="w-24 text-right border border-slate-200 rounded-lg px-2.5 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent hover:border-slate-300 transition-colors" />
                        </td>
                        <td className="px-4 py-2.5 text-right font-bold text-emerald-700">₹{net.toLocaleString()}</td>
                      </tr>
                    );
                  })}
                </tbody>
                <tfoot>
                  <tr className="bg-emerald-50 border-t border-emerald-200">
                    <td colSpan={2} className="px-4 py-2.5 font-semibold text-slate-700">Total</td>
                    <td className="px-4 py-2.5 text-right font-semibold text-slate-500">₹{totalFee.toLocaleString()}</td>
                    <td className="px-4 py-2.5 text-right font-semibold text-red-500">-₹{totalConcession.toLocaleString()}</td>
                    <td className="px-4 py-2.5 text-right font-bold text-emerald-700">₹{netFee.toLocaleString()}</td>
                  </tr>
                </tfoot>
              </table>
            </div>
          )}

          {!selectedClass && (
            <div className="text-center py-6 text-slate-400 border border-dashed border-slate-200 rounded-xl">
              <School className="w-8 h-8 mx-auto mb-2 text-slate-300" />
              <p className="text-sm">Select a class to view applicable fee structure</p>
            </div>
          )}

          {/* Token Advance */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Token Advance (₹)</label>
              <input type="number" {...register('token_advance')} placeholder="0" min="0" className={inp()} />
            </div>
          </div>

          {/* Payment Method Chips */}
          <div>
            <label className="text-xs font-medium text-slate-600 mb-2 block">Payment Method</label>
            <div className="flex flex-wrap gap-2">
              {PAYMENT_METHODS.map(method => (
                <button
                  key={method}
                  type="button"
                  onClick={() => setValue('token_payment_method', method)}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-all duration-150 ${
                    watch('token_payment_method') === method
                      ? 'bg-primary-600 text-white border-primary-600 shadow-sm'
                      : 'bg-white text-slate-600 border-slate-200 hover:border-primary-300 hover:text-primary-700'
                  }`}
                >
                  {method}
                </button>
              ))}
            </div>
          </div>

          {/* Remarks */}
          <div>
            <label className="text-xs font-medium text-slate-600 mb-1 block">Remarks</label>
            <input {...register('remarks')} className={inp()} placeholder="Any additional notes about this admission..." />
          </div>
        </div>
      )}

      {/* Step 4: Summary / Review */}
      {formStep === 3 && (
        <div className="space-y-4 max-h-[55vh] overflow-y-auto pr-1 pb-4">
          <div className="bg-emerald-50 rounded-xl p-3 border border-emerald-100 mb-2">
            <p className="text-xs text-emerald-700 font-medium">Please review all details before submitting the admission application.</p>
          </div>

          {/* Student Summary */}
          <div className="rounded-xl border border-slate-200 overflow-hidden">
            <div className="bg-slate-50 px-4 py-2 border-b border-slate-200 flex items-center gap-2">
              <User className="w-3.5 h-3.5 text-slate-500" />
              <span className="text-xs font-semibold text-slate-600 uppercase">Student Details</span>
            </div>
            <div className="p-4 grid grid-cols-2 gap-x-6 gap-y-2">
              <SummaryField label="Name" value={watch('full_name')} />
              <SummaryField label="Date of Birth" value={watch('date_of_birth')} />
              <SummaryField label="Gender" value={watch('gender')} />
              <SummaryField label="Phone" value={watch('phone')} />
              <SummaryField label="Email" value={watch('email')} />
              <SummaryField label="Student Type" value={watch('student_type')} />
              <SummaryField label="Address" value={watch('address')} full />
              <SummaryField label="Previous School" value={watch('previous_school')} />
            </div>
          </div>

          {/* Parent Summary */}
          <div className="rounded-xl border border-slate-200 overflow-hidden">
            <div className="bg-slate-50 px-4 py-2 border-b border-slate-200 flex items-center gap-2">
              <Users className="w-3.5 h-3.5 text-slate-500" />
              <span className="text-xs font-semibold text-slate-600 uppercase">Parent / Guardian</span>
            </div>
            <div className="p-4 grid grid-cols-2 gap-x-6 gap-y-2">
              <SummaryField label="Name" value={watch('parent_name')} />
              <SummaryField label="Relationship" value={watch('parent_relationship')} />
              <SummaryField label="Phone" value={watch('parent_phone')} />
              <SummaryField label="Email" value={watch('parent_email')} />
              <SummaryField label="Occupation" value={watch('parent_occupation')} />
            </div>
          </div>

          {/* Academic & Fee Summary */}
          <div className="rounded-xl border border-slate-200 overflow-hidden">
            <div className="bg-slate-50 px-4 py-2 border-b border-slate-200 flex items-center gap-2">
              <School className="w-3.5 h-3.5 text-slate-500" />
              <span className="text-xs font-semibold text-slate-600 uppercase">Academic & Fees</span>
            </div>
            <div className="p-4">
              <div className="grid grid-cols-2 gap-x-6 gap-y-2 mb-3">
                <SummaryField label="Class Applied" value={`${watch('class_name')} ${watch('section') ? `- ${watch('section')}` : ''}`} />
                <SummaryField label="Total Applicable Fee" value={totalFee > 0 ? `₹${totalFee.toLocaleString()}` : 'N/A'} />
                <SummaryField label="Concession" value={concessionAmt > 0 ? `₹${concessionAmt.toLocaleString()}` : 'None'} />
                <SummaryField label="Net Fee" value={totalFee > 0 ? `₹${netFee.toLocaleString()}` : 'N/A'} highlight />
              </div>
              {(Number(watch('token_advance')) > 0) && (
                <div className="mt-3 pt-3 border-t border-slate-100">
                  <div className="flex items-center gap-3">
                    <div className="bg-purple-50 border border-purple-200 rounded-lg px-3 py-2 flex items-center gap-2">
                      <Banknote className="w-4 h-4 text-purple-600" />
                      <div>
                        <p className="text-xs text-purple-500">Token Advance</p>
                        <p className="text-sm font-bold text-purple-800">₹{Number(watch('token_advance')).toLocaleString()}</p>
                      </div>
                    </div>
                    <div className="bg-slate-50 border border-slate-200 rounded-lg px-3 py-2">
                      <p className="text-xs text-slate-500">Payment Method</p>
                      <p className="text-sm font-medium text-slate-800">{watch('token_payment_method') || 'Cash'}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Navigation */}
      <div className="flex items-center justify-between mt-6 pt-4 border-t border-slate-100">
        <Button variant="ghost" onClick={onCancel}>Cancel</Button>
        <div className="flex items-center gap-2">
          {formStep > 0 && <Button variant="secondary" onClick={() => setFormStep(formStep - 1)}>Previous</Button>}
          {formStep < STEPS.length - 1 ? (
            <Button type="button" variant="primary" onClick={handleNext}>
              {formStep === 2 ? 'Review' : 'Next'} <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          ) : (
            <Button variant="primary" onClick={handleSubmit(onSubmit)} disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Submitting...' : 'Submit Application'}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── Summary Field Component ─────────────────────────────────────────────────
function SummaryField({ label, value, full, highlight }) {
  return (
    <div className={full ? 'col-span-2' : ''}>
      <p className="text-xs text-slate-500">{label}</p>
      <p className={`text-sm font-medium ${highlight ? 'text-emerald-700' : 'text-slate-800'}`}>{value || '—'}</p>
    </div>
  );
}
