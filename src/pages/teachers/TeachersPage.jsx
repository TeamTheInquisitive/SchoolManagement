import { useState, useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { Plus, Eye, Pencil, Trash2, Download, Upload, Users, CheckCircle, GraduationCap, Copy, Check } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useDebounceValue } from 'usehooks-ts';
import { useTeachers, useCreateTeacher, useUpdateTeacher, useDeleteTeacher } from '../../services/teacherService';
import { useSchoolProfile, useSubjects } from '../../services/settingsService';
import { fetchNextId } from '../../services/settingsService';
import { Button, Modal, ConfirmDialog, SearchableSelect, useToast, exportStyledExcel, useSortableData, Breadcrumb, usePagination, DataTable, DatePicker } from 'school-erp-ui-shared';
import { DEPARTMENTS, EMPLOYMENT_TYPES, GENDER_OPTIONS } from '../../constants.jsx';
import { downloadBulkTemplate } from '../../utils/bulkTemplateExport';
import { getSchoolInfo } from '../../utils/getSchoolInfo';
import BulkImportModal from '../../components/BulkImportModal';
import api from '../../services/api';
import { ENDPOINTS } from '../../config/api';

const phoneRegex = /^[6-9]\d{9}$/;

const teacherSchema = z.object({
  // Personal Details
  employee_id: z.string().min(1, 'Required'),
  full_name: z.string().min(1, 'Required'),
  email: z.string().email('Invalid email'),
  phone: z.string().regex(phoneRegex, '10 digits starting with 6-9').optional().or(z.literal('')),
  gender: z.string().optional(),
  date_of_birth: z.string().optional().refine(val => {
    if (!val) return true;
    return val <= new Date().toISOString().split('T')[0];
  }, { message: 'Date of birth must be in the past' }),
  address: z.string().optional(),
  emergency_contact_name: z.string().optional(),
  emergency_contact_phone: z.string().regex(phoneRegex, '10 digits starting with 6-9').optional().or(z.literal('')),
  emergency_contact_relationship: z.string().optional(),
  // Professional Details
  department: z.string().optional(),
  designation: z.string().optional(),
  primary_subject: z.string().optional(),
  subjects: z.string().optional(),
  qualification: z.string().optional(),
  employment_type: z.string().optional(),
  joining_date: z.string().optional(),
  max_workload_hours: z.coerce.number().min(0).optional().or(z.literal('')),
  // Salary Structure
  basic_salary: z.preprocess(v => v === '' ? undefined : Number(v), z.number().min(1, 'Basic salary is required')),
  hra: z.preprocess(v => v === '' ? undefined : Number(v), z.number().min(0).optional()),
  da: z.preprocess(v => v === '' ? undefined : Number(v), z.number().min(0).optional()),
  ta: z.preprocess(v => v === '' ? undefined : Number(v), z.number().min(0).optional()),
  other_allowances: z.preprocess(v => v === '' ? undefined : Number(v), z.number().min(0).optional()),
  pf_deduction: z.preprocess(v => v === '' ? undefined : Number(v), z.number().min(0).optional()),
  tax_deduction: z.preprocess(v => v === '' ? undefined : Number(v), z.number().min(0).optional()),
  other_deductions: z.preprocess(v => v === '' ? undefined : Number(v), z.number().min(0).optional()),
  bank_name: z.string().optional(),
  account_number: z.string().optional(),
  ifsc_code: z.string().optional(),
  pan_number: z.string().regex(/^[A-Z]{5}[0-9]{4}[A-Z]$/, 'PAN must be in format: ABCDE1234F').optional().or(z.literal('')),
});

const STEPS_CREATE = [
  { id: 'personal', label: 'Personal Details', icon: '1' },
  { id: 'professional', label: 'Professional Details', icon: '2' },
  { id: 'salary', label: 'Salary Structure', icon: '3' },
];

const STEPS_EDIT = [
  { id: 'personal', label: 'Personal Details', icon: '1' },
  { id: 'professional', label: 'Professional Details', icon: '2' },
];

export default function TeachersPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const toast = useToast();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [debouncedSearch] = useDebounceValue(search, 300);
  const [filterDept, setFilterDept] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingTeacher, setEditingTeacher] = useState(null);
  const [deleteId, setDeleteId] = useState(null);
  const [formStep, setFormStep] = useState(0);
  const [bulkImportOpen, setBulkImportOpen] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [copied, setCopied] = useState(null);
  const pagination = usePagination(20, "admin-teachers");

  const { data: teachersData, isLoading, isFetching } = useTeachers({ ...pagination.params, search: debouncedSearch || undefined, department: filterDept || undefined, status: filterStatus || undefined });
  const { data: schoolProfile } = useSchoolProfile();
  const { data: subjectsData } = useSubjects();
  const subjectOptions = (Array.isArray(subjectsData) ? subjectsData : subjectsData?.subjects || []).map(s => ({ value: s.name, label: s.name }));
  const createTeacher = useCreateTeacher();
  const updateTeacher = useUpdateTeacher();
  const deleteTeacher = useDeleteTeacher();
  const { register, handleSubmit, reset, watch, setValue, trigger, formState: { errors, isDirty } } = useForm({ resolver: zodResolver(teacherSchema) });

  const teachers = (teachersData?.results || teachersData) ?? [];

  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(null), 1500);
  };

  // Ctrl+S / Cmd+S keyboard shortcut for form submission
  useEffect(() => {
    const handler = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        if (dialogOpen) {
          handleFormSubmit();
        }
      }
    };
    if (dialogOpen) {
      document.addEventListener('keydown', handler);
      return () => document.removeEventListener('keydown', handler);
    }
  }, [dialogOpen]);

  // Handle ?edit=ID from teacher detail page
  useEffect(() => {
    const editId = searchParams.get('edit');
    if (editId && teachers.length > 0) {
      const t = teachers.find(x => x.id === editId);
      if (t) {
        setEditingTeacher(t);
        reset({ employee_id: t.employee_id || '', full_name: t.user?.full_name || '', email: t.user?.email || '', phone: t.user?.phone || '', subjects: (t.subjects || []).join(', '), primary_subject: t.primary_subject || '', qualification: t.qualification || '', joining_date: t.joining_date || '', max_workload_hours: t.max_workload_hours || '', department: t.department || '', designation: t.designation || '', gender: t.gender || '', employment_type: t.employment_type || '', date_of_birth: t.date_of_birth || '', address: t.address || '', emergency_contact_name: t.emergency_contact_name || '', emergency_contact_phone: t.emergency_contact_phone || '', emergency_contact_relationship: t.emergency_contact_relationship || '', basic_salary: t.basic_salary != null ? Math.round(t.basic_salary) : '', hra: t.hra != null ? Math.round(t.hra) : '', da: t.da != null ? Math.round(t.da) : '', ta: t.ta != null ? Math.round(t.ta) : '', other_allowances: t.other_allowances != null ? Math.round(t.other_allowances) : '', pf_deduction: t.pf_deduction != null ? Math.round(t.pf_deduction) : '', tax_deduction: t.tax_deduction != null ? Math.round(t.tax_deduction) : '', other_deductions: t.other_deductions != null ? Math.round(t.other_deductions) : '', bank_name: t.bank_name || '', account_number: t.account_number || '', ifsc_code: t.ifsc_code || '', pan_number: t.pan_number || '' });
        setFormStep(0);
        setDialogOpen(true);
        setSearchParams({});
      }
    }
  }, [teachers, searchParams]);
  const { sortedData, sortConfig, requestSort } = useSortableData(teachers);

  const onSubmit = (data) => {
    const payload = Object.fromEntries(Object.entries(data).filter(([, v]) => v !== '' && v !== undefined));
    if (payload.subjects) payload.subjects = payload.subjects.split(',').map(s => s.trim()).filter(Boolean);
    else payload.subjects = [];
    const cb = { onSuccess: () => { setDialogOpen(false); setEditingTeacher(null); setFormStep(0); reset(); toast.success(editingTeacher ? 'Teacher updated successfully' : 'Teacher added successfully'); }, onError: (err) => { toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to save teacher'); } };
    editingTeacher ? updateTeacher.mutate({ id: editingTeacher.id, data: payload }, cb) : createTeacher.mutate(payload, cb);
  };

  const handleFormSubmit = () => {
    handleSubmit(onSubmit, (validationErrors) => {
      const step0Fields = ['employee_id', 'full_name', 'email', 'phone', 'gender', 'date_of_birth', 'address', 'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship'];
      const step1Fields = ['department', 'designation', 'primary_subject', 'subjects', 'qualification', 'employment_type', 'joining_date', 'max_workload_hours'];
      const errorKeys = Object.keys(validationErrors);
      if (errorKeys.some(k => step0Fields.includes(k))) {
        setFormStep(0);
        toast.error('Please fix errors in Personal Details step');
      } else if (errorKeys.some(k => step1Fields.includes(k))) {
        setFormStep(1);
        toast.error('Please fix errors in Professional Details step');
      } else {
        toast.error('Please fix validation errors');
      }
    })();
  };

  const handleDownloadTemplate = async () => {
    await downloadBulkTemplate({
      filename: 'Bulk_Teacher_Upload',
      schoolName: schoolProfile?.school_name || '',
      schoolCode: schoolProfile?.school_code || '',
      sheetName: 'Teacher Data',
      columns: [
        { header: 'Employee ID', key: 'employee_id', mandatory: true, description: 'Unique employee identifier' },
        { header: 'Full Name', key: 'full_name', mandatory: true, description: 'Teacher full name' },
        { header: 'Email', key: 'email', mandatory: true, description: 'Email address (used for login)' },
        { header: 'Phone', key: 'phone', description: '10-digit mobile number' },
        { header: 'Gender', key: 'gender', dropdown: ['Male', 'Female', 'Other'], description: 'Male, Female, or Other' },
        { header: 'Date of Birth', key: 'date_of_birth', description: 'Format: YYYY-MM-DD' },
        { header: 'Address', key: 'address', description: 'Full address' },
        { header: 'Emergency Contact Name', key: 'emergency_contact_name', description: 'Emergency contact person name' },
        { header: 'Emergency Contact Phone', key: 'emergency_contact_phone', description: 'Emergency contact phone number' },
        { header: 'Emergency Contact Relationship', key: 'emergency_contact_relationship', dropdown: ['Father', 'Mother', 'Spouse', 'Sibling', 'Friend', 'Other'], description: 'Relationship with emergency contact' },
        { header: 'Department', key: 'department', dropdown: DEPARTMENTS.map(d => d.value), description: 'Teaching, Administration, Accounts, etc.' },
        { header: 'Designation', key: 'designation', description: 'e.g. Senior Teacher, HOD' },
        { header: 'Primary Subject', key: 'primary_subject', dropdown: subjectOptions.map(s => s.value), description: 'Main subject taught' },
        { header: 'Subjects', key: 'subjects', description: 'Comma separated list of subjects (e.g., Mathematics, Physics, Chemistry)' },
        { header: 'Qualification', key: 'qualification', description: 'e.g. M.Sc, B.Ed' },
        { header: 'Employment Type', key: 'employment_type', dropdown: EMPLOYMENT_TYPES.map(e => e.value), description: 'Full-Time, Part-Time, or Contract' },
        { header: 'Joining Date', key: 'joining_date', description: 'Format: YYYY-MM-DD' },
        { header: 'Max Workload Hours', key: 'max_workload_hours', description: 'Maximum teaching hours per week' },
        { header: 'Basic Salary', key: 'basic_salary', description: 'Monthly basic salary in ₹' },
        { header: 'HRA', key: 'hra', description: 'House Rent Allowance in ₹' },
        { header: 'DA', key: 'da', description: 'Dearness Allowance in ₹' },
        { header: 'TA', key: 'ta', description: 'Travel Allowance in ₹' },
        { header: 'Other Allowances', key: 'other_allowances', description: 'Any other monthly allowances in ₹' },
        { header: 'PF Deduction', key: 'pf_deduction', description: 'Provident Fund deduction in ₹' },
        { header: 'Tax Deduction (TDS)', key: 'tax_deduction', description: 'TDS / Income tax deduction in ₹' },
        { header: 'Other Deductions', key: 'other_deductions', description: 'Any other monthly deductions in ₹' },
        { header: 'Bank Name', key: 'bank_name', description: 'Bank name for salary credit' },
        { header: 'Account Number', key: 'account_number', description: 'Bank account number' },
        { header: 'IFSC Code', key: 'ifsc_code', description: 'Bank branch IFSC code' },
        { header: 'PAN Number', key: 'pan_number', description: 'PAN card number (e.g., ABCDE1234F)' },
      ],
      referenceData: [
        { title: 'Available Subjects', values: subjectOptions.map(s => s.value) },
      ],
    });
    toast.success('Template downloaded successfully');
  };

  const columns = [
    { key: 'employee_id', label: 'Employee ID', render: (t) => (
      <span className="inline-flex items-center gap-1">
        {t.employee_id}
        <button onClick={(e) => { e.stopPropagation(); copyToClipboard(t.employee_id, `emp-${t.id}`); }} className="text-gray-400 hover:text-gray-600 ml-1">
          {copied === `emp-${t.id}` ? <Check size={14} className="text-green-500" /> : <Copy size={14} />}
        </button>
      </span>
    )},
    {
      key: 'user.full_name', label: 'Name', sortable: true,
      render: (t) => (
        <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate(`/admin/staff/${t.id}`)}>
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-indigo-700 text-white flex items-center justify-center text-xs font-semibold shadow-sm">{(t.user?.full_name || '').slice(0, 2).toUpperCase()}</div>
          <span className="font-semibold text-purple-600 hover:underline">{t.user?.full_name}</span>
        </div>
      ),
    },
    { key: 'primary_subject', label: 'Subject', sortable: true, render: (t) => t.primary_subject || (t.subjects || []).join(', ') },
    { key: 'qualification', label: 'Qualification', render: (t) => <span className="text-slate-500">{t.qualification}</span> },
    { key: 'email', label: 'Email', render: (t) => <span className="text-slate-500">{t.user?.email}</span> },
    {
      key: 'workload', label: 'Workload',
      render: (t) => {
        const current = t.total_periods_per_week || t.workload_hours || 0;
        const max = t.max_workload_hours;
        const hasMax = max && max > 0;
        const pct = hasMax ? Math.min((current / max) * 100, 100) : 0;
        const isOverloaded = hasMax && current > max;
        const isNearMax = hasMax && pct > 90 && !isOverloaded;
        const barColor = isOverloaded ? 'bg-red-500' : pct > 90 ? 'bg-red-500' : pct >= 70 ? 'bg-amber-500' : 'bg-emerald-500';
        const badgeStyle = isOverloaded ? 'bg-red-100 text-red-700 border border-red-200' : isNearMax ? 'bg-amber-100 text-amber-700 border border-amber-200' : 'bg-amber-100 text-amber-600';
        return (
          <div className="min-w-[100px]">
            <div className="flex items-center gap-1.5">
              <span className={`text-xs font-medium px-2.5 py-0.5 rounded-full ${badgeStyle}`}>{current} periods</span>
              {isOverloaded && (
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-red-500 text-white animate-pulse" title="Exceeds max workload">OVER</span>
              )}
              {isNearMax && (
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-amber-500 text-white" title="Near max workload">HIGH</span>
              )}
            </div>
            {hasMax && (
              <div className="flex items-center gap-1.5 mt-1.5">
                <div className="flex-1 h-1.5 rounded-full bg-slate-100 overflow-hidden">
                  <div className={`h-full rounded-full ${barColor} transition-all duration-300`} style={{ width: `${Math.min(pct, 100)}%` }} />
                </div>
                <span className={`text-[10px] whitespace-nowrap ${isOverloaded ? 'text-red-600 font-semibold' : 'text-slate-500'}`}>{current}/{max} hrs</span>
              </div>
            )}
            {!hasMax && current > 0 && (
              <p className="text-[10px] text-slate-400 mt-0.5">No max set</p>
            )}
          </div>
        );
      },
    },
    {
      key: 'actions', label: 'Actions',
      render: (t) => (
        <div className="flex gap-1">
          <button onClick={(e) => { e.stopPropagation(); navigate(`/admin/staff/${t.id}`); }} className="p-1.5 hover:bg-slate-100 rounded-lg transition-all duration-150 active:scale-[0.97]"><Eye className="w-4 h-4 text-slate-500" /></button>
          <button onClick={(e) => { e.stopPropagation(); setEditingTeacher(t); reset({ employee_id: t.employee_id || '', full_name: t.user?.full_name || '', email: t.user?.email || '', phone: t.user?.phone || '', subjects: (t.subjects || []).join(', '), primary_subject: t.primary_subject || '', qualification: t.qualification || '', joining_date: t.joining_date || '', max_workload_hours: t.max_workload_hours || '', department: t.department || '', designation: t.designation || '', gender: t.gender || '', employment_type: t.employment_type || '', date_of_birth: t.date_of_birth || '', address: t.address || '', emergency_contact_name: t.emergency_contact_name || '', emergency_contact_phone: t.emergency_contact_phone || '', emergency_contact_relationship: t.emergency_contact_relationship || '', basic_salary: t.basic_salary != null ? Math.round(t.basic_salary) : '', hra: t.hra != null ? Math.round(t.hra) : '', da: t.da != null ? Math.round(t.da) : '', ta: t.ta != null ? Math.round(t.ta) : '', other_allowances: t.other_allowances != null ? Math.round(t.other_allowances) : '', pf_deduction: t.pf_deduction != null ? Math.round(t.pf_deduction) : '', tax_deduction: t.tax_deduction != null ? Math.round(t.tax_deduction) : '', other_deductions: t.other_deductions != null ? Math.round(t.other_deductions) : '', bank_name: t.bank_name || '', account_number: t.account_number || '', ifsc_code: t.ifsc_code || '', pan_number: t.pan_number || '' }); setFormStep(0); setDialogOpen(true); }} className="p-1.5 hover:bg-slate-100 rounded-lg transition-all duration-150 active:scale-[0.97]"><Pencil className="w-4 h-4 text-slate-500" /></button>
          <button onClick={(e) => { e.stopPropagation(); setDeleteId(t.id); }} className="p-1.5 hover:bg-red-50 rounded-lg transition-all duration-150 active:scale-[0.97]"><Trash2 className="w-4 h-4 text-red-500" /></button>
        </div>
      ),
    },
  ];

  const summary = teachersData?.summary || {};
  const totalTeachers = summary.total || teachersData?.count || 0;
  const activeTeachers = summary.active || teachers.filter(t => t.status !== 'Inactive').length;
  const totalDepartments = summary.departments || [...new Set(teachers.map(t => t.department).filter(Boolean))].length;

  const kpis = [
    { label: 'Total Staff', value: totalTeachers, icon: Users, color: 'text-blue-600', bg: 'bg-gradient-to-br from-blue-50 to-blue-100', border: 'border-blue-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(59,130,246,0.3)]' },
    { label: 'Active', value: activeTeachers, icon: CheckCircle, color: 'text-emerald-600', bg: 'bg-gradient-to-br from-emerald-50 to-emerald-100', border: 'border-emerald-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(16,185,129,0.3)]' },
    { label: 'Departments', value: totalDepartments, icon: GraduationCap, color: 'text-purple-600', bg: 'bg-gradient-to-br from-purple-50 to-purple-100', border: 'border-purple-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(147,51,234,0.3)]' },
  ];

  return (
    <div>
      <Breadcrumb items={[{ label: 'Dashboard', href: '/admin/dashboard' }, { label: 'Staff' }]} />
      <div className="flex justify-between items-center mb-6">
        <div><h1 className="text-2xl md:text-3xl font-bold text-slate-900">Staff Management</h1><p className="text-sm text-slate-500 mt-1">Manage staff records and workload</p></div>
        <div className="flex gap-2 flex-wrap">
          <Button variant="secondary" icon={Download} onClick={handleDownloadTemplate}>Download Template</Button>
          <Button variant="secondary" icon={Upload} onClick={() => setBulkImportOpen(true)}>Bulk Import</Button>
          <Button variant="primary" icon={Plus} onClick={async () => { setEditingTeacher(null); reset({ employee_id: '', full_name: '', email: '', phone: '', subjects: '', primary_subject: '', qualification: '', joining_date: '', max_workload_hours: '', department: 'Teaching', designation: '', gender: '', employment_type: '', date_of_birth: '', address: '', emergency_contact_name: '', emergency_contact_phone: '', emergency_contact_relationship: '' }); try { const res = await fetchNextId('teacher'); if (res.enabled && res.id) setValue('employee_id', res.id); } catch {} setFormStep(0); setDialogOpen(true); }}>Add Staff</Button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-3 md:gap-4 mb-6">
        {kpis.map(k => (
          <div key={k.label} className={`bg-white border ${k.border} rounded-xl p-4 md:p-5 flex items-center gap-3 md:gap-4 transition-all duration-200 hover:-translate-y-1 ${k.glow} cursor-default group`}>
            <div className={`${k.bg} p-2.5 md:p-3 rounded-xl transition-transform duration-200 group-hover:scale-110`}><k.icon className={`w-5 h-5 ${k.color}`} /></div>
            <div><p className="text-xs text-slate-500 font-medium">{k.label}</p><p className="text-xl md:text-2xl font-bold text-slate-900 mt-0.5">{k.value}</p></div>
          </div>
        ))}
      </div>

      <DataTable
        columns={columns}
        data={sortedData}
        loading={isFetching}
        emptyMessage={search ? 'No teachers found. Try a different search term.' : 'No teachers found'}
        emptyIcon={Eye}
        headerTitle="All Staff"
        headerCount={teachersData?.count || 0}
        headerExtra={
          <Button variant="secondary" size="sm" icon={Download} disabled={exporting} loading={exporting} onClick={async () => { if (exporting) return; setExporting(true); toast.info('Exporting all staff... Please wait.'); try { const { fetchAllPages } = await import('../../utils/exportAllPages'); const allTeachers = await fetchAllPages(ENDPOINTS.teachers.list, { ...(filterDept && { department: filterDept }), ...(filterStatus && { status: filterStatus }), ...(search && { search }) }, 100); const headers = ['Employee ID', 'Name', 'Subject', 'Qualification', 'Email', 'Department', 'Phone']; const rows = allTeachers.map(t => [t.employee_id, t.user?.full_name || t.full_name, t.primary_subject || (t.subjects || []).join(', '), t.qualification, t.user?.email || t.email, t.department, t.phone]); const fp = [filterDept && filterDept, filterStatus && filterStatus].filter(Boolean); const fn = fp.length > 0 ? `${fp.join('_')}_Staff` : 'All_Staff'; const fd = fp.length > 0 ? `Filters: ${[filterDept && `Department: ${filterDept}`, filterStatus && `Status: ${filterStatus}`].filter(Boolean).join(' | ')}` : ''; await exportStyledExcel({ filename: fn, schoolInfo: getSchoolInfo(schoolProfile), reportTitle: `Staff Directory${fd ? ` (${fd})` : ''}`, headers, rows }); toast.success(`Exported ${allTeachers.length} staff`); } catch { toast.error('Failed to export'); } setExporting(false); }}>{exporting ? 'Exporting...' : 'Export Excel'}</Button>
        }
        search={{ value: search, onChange: (v) => { setSearch(v); pagination.reset(); }, placeholder: 'Search by name or ID...' }}
        filters={[
          { key: 'department', value: filterDept, onChange: (v) => { setFilterDept(v); pagination.reset(); }, options: [{ value: '', label: 'All Departments' }, ...DEPARTMENTS] },
          { key: 'status', value: filterStatus, onChange: (v) => { setFilterStatus(v); pagination.reset(); }, options: [{ value: '', label: 'All Status' }, { value: 'Active', label: 'Active' }, { value: 'Inactive', label: 'Inactive' }] },
        ]}
        sortConfig={sortConfig}
        onSort={requestSort}
        page={pagination.page}
        totalPages={teachersData?.total_pages || 1}
        totalCount={teachersData?.count || 0}
        pageSize={pagination.pageSize}
        onPageChange={(p) => pagination.setPage(p)}
        onPageSizeChange={pagination.setPageSize}
      />

      <Modal open={dialogOpen} onClose={() => { setDialogOpen(false); setEditingTeacher(null); setFormStep(0); }} title={editingTeacher ? 'Edit Staff' : 'Add New Staff'} size="3xl">
        <TeacherFormWizard
          register={register}
          errors={errors}
          watch={watch}
          setValue={setValue}
          trigger={trigger}
          formStep={formStep}
          setFormStep={setFormStep}
          onSubmit={handleFormSubmit}
          onCancel={() => { setDialogOpen(false); setEditingTeacher(null); setFormStep(0); }}
          isSubmitting={createTeacher.isPending || updateTeacher.isPending}
          isEditing={!!editingTeacher}
          isDirty={isDirty}
          submitError={(createTeacher.isError || updateTeacher.isError) ? ((createTeacher.error || updateTeacher.error)?.response?.data?.error || (createTeacher.error || updateTeacher.error)?.response?.data?.detail || 'Failed to save teacher') : null}
          editingTeacher={editingTeacher}
          subjectOptions={subjectOptions}
        />
      </Modal>

      <ConfirmDialog open={!!deleteId} onClose={() => setDeleteId(null)} onConfirm={() => { const id = deleteId; setDeleteId(null); toast.undoable('Teacher deleted', () => deleteTeacher.mutate(id, { onError: (err) => { toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to delete teacher'); } }), () => toast.info('Delete cancelled')); }} loading={deleteTeacher.isPending} message="Are you sure you want to delete this teacher? You will have a few seconds to undo." />

      <BulkImportModal
        open={bulkImportOpen}
        onClose={() => setBulkImportOpen(false)}
        title="Bulk Import Teachers"
        columns={[
          { key: 'employee_id', header: 'Employee ID', mandatory: true },
          { key: 'full_name', header: 'Full Name', mandatory: true },
          { key: 'email', header: 'Email', mandatory: true },
          { key: 'phone', header: 'Phone' },
          { key: 'gender', header: 'Gender', dropdown: ['Male', 'Female', 'Other'] },
          { key: 'date_of_birth', header: 'Date of Birth' },
          { key: 'address', header: 'Address' },
          { key: 'emergency_contact_name', header: 'Emergency Contact Name' },
          { key: 'emergency_contact_phone', header: 'Emergency Contact Phone' },
          { key: 'emergency_contact_relationship', header: 'Emergency Contact Relationship', dropdown: ['Father', 'Mother', 'Spouse', 'Sibling', 'Friend', 'Other'] },
          { key: 'department', header: 'Department', dropdown: DEPARTMENTS.map(d => d.value) },
          { key: 'designation', header: 'Designation' },
          { key: 'primary_subject', header: 'Primary Subject', dropdown: subjectOptions.map(s => s.value) },
          { key: 'subjects', header: 'Subjects' },
          { key: 'qualification', header: 'Qualification' },
          { key: 'employment_type', header: 'Employment Type', dropdown: EMPLOYMENT_TYPES.map(e => e.value) },
          { key: 'joining_date', header: 'Joining Date' },
          { key: 'max_workload_hours', header: 'Max Workload Hours' },
          { key: 'basic_salary', header: 'Basic Salary' },
          { key: 'hra', header: 'HRA' },
          { key: 'da', header: 'DA' },
          { key: 'ta', header: 'TA' },
          { key: 'other_allowances', header: 'Other Allowances' },
          { key: 'pf_deduction', header: 'PF Deduction' },
          { key: 'tax_deduction', header: 'Tax Deduction (TDS)' },
          { key: 'other_deductions', header: 'Other Deductions' },
          { key: 'bank_name', header: 'Bank Name' },
          { key: 'account_number', header: 'Account Number' },
          { key: 'ifsc_code', header: 'IFSC Code' },
          { key: 'pan_number', header: 'PAN Number' },
        ]}
        onImport={async (rows) => {
          const validSubjectNames = subjectOptions.map(s => s.value.toLowerCase());
          const errors = [];
          const cleaned = rows.map((r, idx) => {
            const row = Object.fromEntries(Object.entries(r).filter(([, v]) => v !== ''));
            if (row.subjects) {
              const subjectList = row.subjects.split(',').map(s => s.trim()).filter(Boolean);
              const invalid = subjectList.filter(s => !validSubjectNames.includes(s.toLowerCase()));
              if (invalid.length) errors.push(`Row ${idx + 1}: Invalid subject(s) - ${invalid.join(', ')}`);
              row.subjects = subjectList;
            } else {
              row.subjects = [];
            }
            if (row.primary_subject && !validSubjectNames.includes(row.primary_subject.toLowerCase())) {
              errors.push(`Row ${idx + 1}: Invalid primary subject - ${row.primary_subject}`);
            }
            if (row.max_workload_hours) row.max_workload_hours = Number(row.max_workload_hours);
            if (row.basic_salary) row.basic_salary = Number(row.basic_salary);
            if (row.hra) row.hra = Number(row.hra);
            if (row.da) row.da = Number(row.da);
            if (row.ta) row.ta = Number(row.ta);
            if (row.other_allowances) row.other_allowances = Number(row.other_allowances);
            if (row.pf_deduction) row.pf_deduction = Number(row.pf_deduction);
            if (row.tax_deduction) row.tax_deduction = Number(row.tax_deduction);
            if (row.other_deductions) row.other_deductions = Number(row.other_deductions);
            return row;
          });
          if (errors.length) {
            toast.error(errors.slice(0, 3).join('\n') + (errors.length > 3 ? `\n...and ${errors.length - 3} more errors` : ''));
            throw new Error('Validation failed');
          }
          const res = await api.post(ENDPOINTS.teachers.bulkImport, { teachers: cleaned });
          queryClient.invalidateQueries({ queryKey: ['teachers'] });
          return res.data;
        }}
        dataStartRow={4}
      />
    </div>
  );
}

function TeacherFormWizard({ register, errors, watch, setValue, trigger, formStep, setFormStep, onSubmit, onCancel, isSubmitting, isEditing, isDirty, submitError, editingTeacher, subjectOptions }) {
  const inp = (err) => `w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400 ${err ? 'border-red-400' : 'border-slate-300'}`;
  const steps = isEditing ? STEPS_EDIT : STEPS_CREATE;

  const handleNext = async () => {
    if (formStep === 0) {
      const valid = await trigger(['employee_id', 'full_name', 'email']);
      if (!valid) return;
    }
    if (formStep === 1) {
      const valid = await trigger(['department']);
      if (!valid) return;
    }
    setFormStep(formStep + 1);
  };

  return (
    <div>
      {/* Stepper */}
      <div className="flex items-center justify-between mb-6 px-2">
        {steps.map((step, i) => (
          <div key={step.id} className="flex items-center flex-1">
            <div className="flex items-center gap-2.5">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-200 ${
                i < formStep ? 'bg-emerald-500 text-white' :
                i === formStep ? 'bg-primary-600 text-white shadow-md shadow-primary-200' :
                'bg-slate-100 text-slate-400'
              }`}>
                {i < formStep ? '✓' : step.icon}
              </div>
              <span className={`text-xs font-medium hidden sm:inline ${i === formStep ? 'text-primary-700' : i < formStep ? 'text-emerald-600' : 'text-slate-400'}`}>{step.label}</span>
            </div>
            {i < steps.length - 1 && <div className={`flex-1 h-0.5 mx-3 rounded ${i < formStep ? 'bg-emerald-300' : 'bg-slate-200'}`} />}
          </div>
        ))}
      </div>

      <div>
        {/* Step 1: Personal Details */}
        {formStep === 0 && (
          <div className="space-y-4 max-h-[55vh] overflow-y-auto pr-1">
            <div className="grid grid-cols-2 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Employee ID *</label><input {...register('employee_id')} className={inp(errors.employee_id)} />{errors.employee_id && <p className="text-xs text-red-500 mt-0.5">{errors.employee_id.message}</p>}</div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Full Name *</label><input {...register('full_name')} className={inp(errors.full_name)} />{errors.full_name && <p className="text-xs text-red-500 mt-0.5">{errors.full_name.message}</p>}</div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Email *</label><input {...register('email')} className={inp(errors.email)} />{errors.email && <p className="text-xs text-red-500 mt-0.5">{errors.email.message}</p>}</div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Phone</label><input {...register('phone')} maxLength={10} placeholder="9876543210" className={inp(errors.phone)} />{errors.phone && <p className="text-xs text-red-500 mt-0.5">{errors.phone.message}</p>}</div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Gender</label><SearchableSelect value={watch('gender')} onChange={(val) => setValue('gender', val, { shouldDirty: true })} options={[{ value: '', label: 'Select' }, ...GENDER_OPTIONS]} placeholder="Select Gender..." /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Date of Birth</label><DatePicker value={watch('date_of_birth')} onChange={(v) => setValue('date_of_birth', v, { shouldDirty: true })} />{errors.date_of_birth && <p className="text-xs text-red-500 mt-0.5">{errors.date_of_birth.message}</p>}</div>
            </div>
            <div><label className="text-xs font-medium text-slate-600 mb-1 block">Address</label><input {...register('address')} className={inp()} placeholder="Full address..." /></div>

            {/* Emergency Contact */}
            <div className="border-t border-slate-100 pt-4 mt-4">
              <p className="text-sm font-semibold text-slate-700 mb-3">Emergency Contact</p>
              <div className="grid grid-cols-3 gap-4">
                <div><label className="text-xs font-medium text-slate-600 mb-1 block">Contact Name</label><input {...register('emergency_contact_name')} className={inp()} placeholder="Name" /></div>
                <div><label className="text-xs font-medium text-slate-600 mb-1 block">Contact Phone</label><input {...register('emergency_contact_phone')} maxLength={10} placeholder="9876543210" className={inp(errors.emergency_contact_phone)} />{errors.emergency_contact_phone && <p className="text-xs text-red-500 mt-0.5">{errors.emergency_contact_phone.message}</p>}</div>
                <div><label className="text-xs font-medium text-slate-600 mb-1 block">Relationship</label><SearchableSelect value={watch('emergency_contact_relationship')} onChange={(val) => setValue('emergency_contact_relationship', val, { shouldDirty: true })} options={[{ value: 'Spouse', label: 'Spouse' }, { value: 'Parent', label: 'Parent' }, { value: 'Sibling', label: 'Sibling' }, { value: 'Friend', label: 'Friend' }, { value: 'Other', label: 'Other' }]} placeholder="Select..." /></div>
              </div>
            </div>
          </div>
        )}

        {/* Step 2: Professional Details */}
        {formStep === 1 && (
          <div className="space-y-4 max-h-[55vh] overflow-y-auto pr-1">
            <div className="bg-slate-50 rounded-xl p-4 border border-slate-100 mb-2">
              <p className="text-xs text-slate-500">Enter the professional and academic details for this teacher. Subjects should match those configured in your school setup.</p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Department</label><SearchableSelect value={watch('department')} onChange={(val) => { setValue('department', val, { shouldDirty: true }); if (val && val !== 'Teaching') { setValue('primary_subject', '', { shouldDirty: true }); setValue('subjects', '', { shouldDirty: true }); } }} options={DEPARTMENTS} placeholder="Select Department..." /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Designation</label><input {...register('designation')} className={inp()} placeholder="e.g. Senior Teacher" /></div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className={watch('department') && watch('department') !== 'Teaching' ? 'opacity-50 pointer-events-none' : ''}><label className="text-xs font-medium text-slate-600 mb-1 block">Primary Subject</label><SearchableSelect value={watch('primary_subject')} onChange={(val) => setValue('primary_subject', val, { shouldDirty: true })} options={subjectOptions} placeholder="Select Subject..." /></div>
              <div className={watch('department') && watch('department') !== 'Teaching' ? 'opacity-50 pointer-events-none' : ''}>
                <label className="text-xs font-medium text-slate-600 mb-1 block">Subjects</label>
                <SearchableSelect
                  value=""
                  onChange={(val) => {
                    if (!val) return;
                    const current = (watch('subjects') || '').split(',').map(v => v.trim()).filter(Boolean);
                    if (!current.includes(val)) {
                      setValue('subjects', [...current, val].join(', '), { shouldDirty: true });
                    }
                  }}
                  options={subjectOptions.filter(s => !(watch('subjects') || '').split(',').map(v => v.trim()).includes(s.value))}
                  placeholder="Search & select subjects..."
                />
                {(watch('subjects') || '').split(',').filter(v => v.trim()).length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {(watch('subjects') || '').split(',').map(v => v.trim()).filter(Boolean).map(s => (
                      <span key={s} className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-primary-50 text-primary-700 text-xs border border-primary-200">
                        {s}
                        <button type="button" onClick={() => { const updated = (watch('subjects') || '').split(',').map(v => v.trim()).filter(v => v && v !== s).join(', '); setValue('subjects', updated, { shouldDirty: true }); }} className="hover:text-red-500">×</button>
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Qualification</label><input {...register('qualification')} className={inp()} placeholder="e.g. M.Sc, B.Ed" /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Employment Type</label><SearchableSelect value={watch('employment_type')} onChange={(val) => setValue('employment_type', val, { shouldDirty: true })} options={[{ value: '', label: 'Select' }, ...EMPLOYMENT_TYPES]} placeholder="Select Employment Type..." /></div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Joining Date</label><DatePicker value={watch('joining_date')} onChange={(v) => setValue('joining_date', v, { shouldDirty: true })} />{watch('joining_date') && watch('joining_date') > new Date().toISOString().split('T')[0] && <p className="text-xs text-amber-500 mt-0.5">Joining date is in the future</p>}</div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Max Workload (hours/week)</label><input type="number" {...register('max_workload_hours')} min="0" className={inp()} placeholder="e.g. 30" /></div>
            </div>
          </div>
        )}

        {/* Step 3: Salary Structure (only for new staff) */}
        {!isEditing && formStep === 2 && (
          <div className="space-y-4 max-h-[55vh] overflow-y-auto pr-1">
            <p className="text-sm font-semibold text-slate-700 mb-2">Earnings</p>
            <div className="grid grid-cols-2 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Basic Salary *</label><input type="number" {...register('basic_salary')} className={inp(errors.basic_salary)} placeholder="e.g. 30000" />{errors.basic_salary && <p className="text-xs text-red-500 mt-0.5">{errors.basic_salary.message}</p>}</div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">HRA</label><input type="number" {...register('hra')} className={inp()} placeholder="e.g. 12000" /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">DA (Dearness Allowance)</label><input type="number" {...register('da')} className={inp()} placeholder="e.g. 5000" /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">TA (Travel Allowance)</label><input type="number" {...register('ta')} className={inp()} placeholder="e.g. 3000" /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Other Allowances</label><input type="number" {...register('other_allowances')} className={inp()} placeholder="e.g. 2000" /></div>
            </div>
            <div className="border-t border-slate-100 pt-4 mt-4">
              <p className="text-sm font-semibold text-slate-700 mb-2">Deductions</p>
              <div className="grid grid-cols-2 gap-4">
                <div><label className="text-xs font-medium text-slate-600 mb-1 block">PF Deduction</label><input type="number" {...register('pf_deduction')} className={inp()} placeholder="e.g. 1800" /></div>
                <div><label className="text-xs font-medium text-slate-600 mb-1 block">Tax Deduction</label><input type="number" {...register('tax_deduction')} className={inp()} placeholder="e.g. 2000" /></div>
                <div><label className="text-xs font-medium text-slate-600 mb-1 block">Other Deductions</label><input type="number" {...register('other_deductions')} className={inp()} placeholder="e.g. 500" /></div>
              </div>
            </div>
            <div className="border-t border-slate-100 pt-4 mt-4">
              <p className="text-sm font-semibold text-slate-700 mb-2">Bank Details</p>
              <div className="grid grid-cols-2 gap-4">
                <div><label className="text-xs font-medium text-slate-600 mb-1 block">Bank Name</label><input {...register('bank_name')} className={inp()} placeholder="e.g. State Bank of India" /></div>
                <div><label className="text-xs font-medium text-slate-600 mb-1 block">Account Number</label><input {...register('account_number')} className={inp()} placeholder="e.g. 1234567890" /></div>
                <div><label className="text-xs font-medium text-slate-600 mb-1 block">IFSC Code</label><input {...register('ifsc_code')} className={inp()} placeholder="e.g. SBIN0001234" /></div>
                <div><label className="text-xs font-medium text-slate-600 mb-1 block">PAN Number</label><input {...register('pan_number')} className={inp(errors.pan_number)} placeholder="e.g. ABCDE1234F" />{errors.pan_number && <p className="text-xs text-red-500 mt-0.5">{errors.pan_number.message}</p>}</div>
              </div>
            </div>
            <SalarySummary watch={watch} />
          </div>
        )}

        {/* Error */}
        {submitError && <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg mt-3">{submitError}</p>}

        {/* Navigation */}
        <div className="flex items-center justify-between mt-6 pt-4 border-t border-slate-100">
          <Button variant="ghost" onClick={onCancel}>Cancel</Button>
          <div className="flex items-center gap-2">
            {formStep > 0 && (
              <Button variant="secondary" onClick={() => setFormStep(formStep - 1)}>&larr; Previous</Button>
            )}
            {formStep < steps.length - 1 ? (
              <Button type="button" variant="primary" onClick={handleNext}>Next &rarr;</Button>
            ) : (
              <Button variant="primary" onClick={onSubmit} disabled={isSubmitting || (isEditing && !isDirty)}>
                {isSubmitting ? 'Saving...' : isEditing ? 'Update Teacher' : 'Add Teacher'}
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function SalarySummary({ watch }) {
  const basic = Number(watch('basic_salary')) || 0;
  const hra = Number(watch('hra')) || 0;
  const da = Number(watch('da')) || 0;
  const ta = Number(watch('ta')) || 0;
  const otherAllowances = Number(watch('other_allowances')) || 0;
  const pf = Number(watch('pf_deduction')) || 0;
  const tax = Number(watch('tax_deduction')) || 0;
  const otherDeductions = Number(watch('other_deductions')) || 0;

  const grossSalary = basic + hra + da + ta + otherAllowances;
  const grossDeductions = pf + tax + otherDeductions;
  const netSalary = grossSalary - grossDeductions;

  if (grossSalary === 0) return null;

  return (
    <div className="border-t border-slate-100 pt-4 mt-4">
      <p className="text-sm font-semibold text-slate-700 mb-3">Salary Summary</p>
      <div className="grid grid-cols-3 gap-3">
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-3 text-center">
          <p className="text-[10px] font-medium text-emerald-600 uppercase">Gross Salary</p>
          <p className="text-lg font-bold text-emerald-700">₹{grossSalary.toLocaleString()}</p>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-xl p-3 text-center">
          <p className="text-[10px] font-medium text-red-600 uppercase">Gross Deductions</p>
          <p className="text-lg font-bold text-red-700">₹{grossDeductions.toLocaleString()}</p>
        </div>
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-3 text-center">
          <p className="text-[10px] font-medium text-blue-600 uppercase">Net Salary</p>
          <p className="text-lg font-bold text-blue-700">₹{netSalary.toLocaleString()}</p>
        </div>
      </div>
    </div>
  );
}
