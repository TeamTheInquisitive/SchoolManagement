import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Users, DollarSign, Clock, CreditCard, FileText, Banknote, TrendingUp } from 'lucide-react';
import { useDebounceValue } from 'usehooks-ts';
import api from '../../services/api';
import { ENDPOINTS } from '../../config/api';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button, Modal, ConfirmDialog, Tabs, SearchableSelect, useToast, Breadcrumb, Pagination, usePagination, useTabState, DatePicker } from 'school-erp-ui-shared';
import { useStaff, useCreateStaff, useUpdateStaff, useDeleteStaff } from '../../services/staffService';
import { fetchNextId } from '../../services/settingsService';
import { usePayroll, useSalaryAdvances, useApproveSalaryAdvance, useRejectSalaryAdvance } from '../../services/payrollService';
import { useLeaves, useApproveLeave, useRejectLeave } from '../../services/leaveService';
import { DEPARTMENTS, EMPLOYMENT_TYPES, GENDER_OPTIONS } from '../../constants.jsx';
import StaffDirectoryTab from './StaffDirectoryTab';
import PayrollTab from './PayrollTab';
import LeaveTab from './LeaveTab';
import AdvancesTab from './AdvancesTab';

const phoneRegex = /^[6-9]\d{9}$/;
const pincodeRegex = /^\d{6}$/;

const staffSchema = z.object({
  employee_id: z.string().min(1, 'Required'),
  full_name: z.string().min(1, 'Full name is required'),
  email: z.string().email('Invalid email'),
  phone: z.string().regex(phoneRegex, '10 digits starting with 6-9').optional().or(z.literal('')),
  department: z.string().optional(),
  designation: z.string().optional(),
  employment_type: z.string().optional(),
  joining_date: z.string().optional().refine(val => {
    if (!val) return true;
    return val <= new Date().toISOString().split('T')[0];
  }, { message: 'Joining date cannot be in the future' }),
  salary: z.coerce.number().min(0, 'Salary must be 0 or more').optional().or(z.literal('')),
  is_teacher: z.boolean().default(false),
  gender: z.string().optional(),
  date_of_birth: z.string().optional(),
  qualification: z.string().optional(),
  experience_years: z.coerce.number().min(0).optional().or(z.literal('')),
  address_line1: z.string().optional(),
  city: z.string().optional(),
  state: z.string().optional(),
  pincode: z.string().regex(pincodeRegex, 'Must be 6 digits').optional().or(z.literal('')),
  blood_group: z.string().optional(),
  emergency_contact_name: z.string().optional(),
  emergency_contact_phone: z.string().regex(phoneRegex, '10 digits starting with 6-9').optional().or(z.literal('')),
  // Salary structure
  basic_salary: z.coerce.number().min(0).optional().or(z.literal('')),
  hra: z.coerce.number().min(0).optional().or(z.literal('')),
  da: z.coerce.number().min(0).optional().or(z.literal('')),
  ta: z.coerce.number().min(0).optional().or(z.literal('')),
  other_allowances: z.coerce.number().min(0).optional().or(z.literal('')),
  pf_deduction: z.coerce.number().min(0).optional().or(z.literal('')),
  tax_deduction: z.coerce.number().min(0).optional().or(z.literal('')),
  other_deductions: z.coerce.number().min(0).optional().or(z.literal('')),
  // Banking
  bank_name: z.string().optional(),
  bank_account_number: z.string().optional(),
  bank_ifsc: z.string().optional(),
  pan_number: z.string().regex(/^[A-Z]{5}[0-9]{4}[A-Z]$/, 'PAN must be in format: ABCDE1234F').optional().or(z.literal('')),
});

export default function StaffPage() {
  const toast = useToast();
  const staffTabs = [
    { id: 'directory', label: 'Staff Directory', icon: Users },
    { id: 'payroll', label: 'Payroll', icon: CreditCard },
    { id: 'leave', label: 'Leave', icon: FileText },
    { id: 'advances', label: 'Advances (Coming Soon)', icon: Banknote },
  ];
  const [tab, setTab] = useTabState(staffTabs);
  const [search, setSearch] = useState('');
  const [debouncedSearch] = useDebounceValue(search, 300);
  const [deptFilter, setDeptFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingStaff, setEditingStaff] = useState(null);
  const [deleteId, setDeleteId] = useState(null);
  const [formStep, setFormStep] = useState(0);
  const pagination = usePagination(20, "admin-staff");

  const { data: staffData, isFetching: staffFetching, isLoading: staffLoading } = useStaff({ ...pagination.params, search: debouncedSearch || undefined, department: deptFilter || undefined, status: statusFilter || undefined });
  const { data: payrollData } = usePayroll();
  const { data: payrollHistoryData } = useQuery({ queryKey: ['payroll-history'], queryFn: () => api.get(ENDPOINTS.payroll.history).then(r => r.data) });
  const { data: leavesData } = useLeaves({ status: 'Pending' });
  const { data: advancesData } = useSalaryAdvances({ status: 'Pending' });

  const createStaffMutation = useCreateStaff();
  const updateStaffMutation = useUpdateStaff();
  const deleteStaffMutation = useDeleteStaff();
  const approveLeave = useApproveLeave();
  const rejectLeave = useRejectLeave();
  const approveAdvance = useApproveSalaryAdvance();
  const rejectAdvance = useRejectSalaryAdvance();

  const { register, handleSubmit, reset, watch, setValue, trigger, formState: { errors, isDirty } } = useForm({ resolver: zodResolver(staffSchema) });

  const staff = Array.isArray(staffData?.results) ? staffData.results : [];
  const payroll = Array.isArray(payrollData?.results) ? payrollData.results : [];
  const leaves = Array.isArray(leavesData?.results) ? leavesData.results : [];
  const advances = Array.isArray(advancesData?.results) ? advancesData.results : [];

  const totalStaff = staffData?.count || staff.length;
  const payrollHistory = payrollHistoryData?.history || [];
  const annualPayroll = payrollHistory.reduce((s, h) => s + Number(h.total_salary || 0), 0);
  const annualPaid = payrollHistory.reduce((s, h) => s + Number(h.total_paid || 0), 0);
  const annualPending = annualPayroll - annualPaid;

  const clean = (d) => Object.fromEntries(Object.entries(d).filter(([, v]) => v !== '' && v !== undefined));

  const defaultValues = { employee_id: '', full_name: '', email: '', phone: '', department: '', designation: '', employment_type: '', joining_date: '', salary: '', is_teacher: false, gender: '', date_of_birth: '', qualification: '', experience_years: '', address_line1: '', city: '', state: '', pincode: '', blood_group: '', emergency_contact_name: '', emergency_contact_phone: '', basic_salary: '', hra: '', da: '', ta: '', other_allowances: '', pf_deduction: '', tax_deduction: '', other_deductions: '', bank_name: '', bank_account_number: '', bank_ifsc: '', pan_number: '' };

  const openAdd = async () => { setEditingStaff(null); reset(defaultValues); setFormStep(0); try { const res = await fetchNextId('staff'); if (res.enabled && res.id) setValue('employee_id', res.id); } catch {} setDialogOpen(true); };
  const openEdit = (s) => {
    setEditingStaff(s);
    reset({
      employee_id: s.employee_id || '', full_name: s.full_name || '', email: s.email || '', phone: s.phone || '', department: s.department || '', designation: s.designation || '', employment_type: s.employment_type || '', joining_date: s.joining_date || '', salary: s.salary || '', is_teacher: s.is_teacher || false, gender: s.gender || '', date_of_birth: s.date_of_birth || '', qualification: s.qualification || '', experience_years: s.experience_years || '', address_line1: s.address_line1 || '', city: s.city || '', state: s.state || '', pincode: s.pincode || '', blood_group: s.blood_group || '', emergency_contact_name: s.emergency_contact_name || '', emergency_contact_phone: s.emergency_contact_phone || '',
      basic_salary: s.basic_salary || '', hra: s.hra || '', da: s.da || '', ta: s.ta || '', other_allowances: s.other_allowances || '', pf_deduction: s.pf_deduction || '', tax_deduction: s.tax_deduction || '', other_deductions: s.other_deductions || '',
      bank_name: s.bank_name || '', bank_account_number: s.bank_account_number || '', bank_ifsc: s.bank_ifsc || '', pan_number: s.pan_number || '',
    });
    setFormStep(2);
    setDialogOpen(true);
  };

  const onSubmit = (data) => {
    const payload = clean(data);
    const cb = { onSuccess: () => { setDialogOpen(false); reset(); setFormStep(0); toast.success('Staff member saved successfully'); }, onError: (err) => { toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to save staff member'); } };
    editingStaff ? updateStaffMutation.mutate({ id: editingStaff.id, data: payload }, cb) : createStaffMutation.mutate(payload, cb);
  };

  const kpis = [
    { label: 'Total Staff', value: totalStaff, icon: Users, color: 'text-blue-600', bg: 'bg-gradient-to-br from-blue-50 to-blue-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(59,130,246,0.3)]' },
    { label: 'Annual Payroll', value: `₹${annualPayroll.toLocaleString()}`, icon: TrendingUp, color: 'text-emerald-600', bg: 'bg-gradient-to-br from-emerald-50 to-emerald-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(16,185,129,0.3)]' },
    { label: 'Annual Disbursed', value: `₹${annualPaid.toLocaleString()}`, icon: DollarSign, color: 'text-green-600', bg: 'bg-gradient-to-br from-green-50 to-green-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(34,197,94,0.3)]' },
    { label: 'Annual Pending', value: `₹${annualPending.toLocaleString()}`, icon: Clock, color: 'text-amber-600', bg: 'bg-gradient-to-br from-amber-50 to-amber-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(245,158,11,0.3)]' },
  ];

  const isSaving = createStaffMutation.isPending || updateStaffMutation.isPending;

  return (
    <div>
      <Breadcrumb items={[{ label: 'Dashboard', href: '/admin/dashboard' }, { label: 'Staff' }]} />
      <div className="mb-6"><h1 className="text-2xl md:text-3xl font-bold text-slate-900">Staff & Payroll Management</h1><p className="text-sm text-slate-500 mt-1">Manage staff directory, payroll, leaves, and salary advances</p></div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mb-4">
        {kpis.map(k => (<div key={k.label} className={`bg-white border border-slate-200 rounded-xl p-4 md:p-5 flex items-center gap-3 md:gap-4 transition-all duration-200 hover:-translate-y-1 ${k.glow} cursor-default group`}><div className={`${k.bg} p-2.5 md:p-3 rounded-xl transition-transform duration-200 group-hover:scale-110`}><k.icon className={`w-5 h-5 ${k.color}`} /></div><div><p className="text-xs text-slate-500 font-medium">{k.label}</p><p className="text-xl font-bold text-slate-900 mt-0.5">{k.value}</p></div></div>))}
      </div>

      <div className="mb-4">
        <Tabs tabs={staffTabs} active={tab} onChange={(i) => { if (i === 3) return; setTab(i); }} />
      </div>

      {tab === 0 && <StaffDirectoryTab staff={staff} search={search} setSearch={(v) => { setSearch(v); pagination.reset(); }} deptFilter={deptFilter} setDeptFilter={(v) => { setDeptFilter(v); pagination.reset(); }} statusFilter={statusFilter} setStatusFilter={(v) => { setStatusFilter(v); pagination.reset(); }} onAdd={openAdd} onEdit={openEdit} onDelete={(id) => setDeleteId(id)} pagination={pagination} staffData={staffData} loading={staffFetching} />}
      {tab === 1 && <PayrollTab />}
      {tab === 2 && <LeaveTab leaves={leaves} onApprove={(id) => approveLeave.mutate({ id, data: {} })} onReject={(id) => rejectLeave.mutate({ id, data: { remarks: 'Rejected by admin' } })} />}

      <Modal open={dialogOpen} onClose={() => { setDialogOpen(false); setEditingStaff(null); setFormStep(0); }} title={editingStaff ? 'Edit Staff Member' : 'Add Staff Member'} size="3xl">
        <StaffFormWizard
          register={register}
          errors={errors}
          watch={watch}
          setValue={setValue}
          trigger={trigger}
          formStep={formStep}
          setFormStep={setFormStep}
          onSubmit={handleSubmit(onSubmit)}
          onCancel={() => { setDialogOpen(false); setEditingStaff(null); setFormStep(0); }}
          isSaving={isSaving}
          isEditing={!!editingStaff}
          isDirty={isDirty}
          submitError={createStaffMutation.isError ? (createStaffMutation.error?.response?.data?.error || createStaffMutation.error?.response?.data?.detail) : updateStaffMutation.isError ? (updateStaffMutation.error?.response?.data?.error || updateStaffMutation.error?.response?.data?.detail) : null}
          toast={toast}
        />
      </Modal>

      <ConfirmDialog open={!!deleteId} onClose={() => setDeleteId(null)} onConfirm={() => deleteStaffMutation.mutate(deleteId, { onSuccess: () => setDeleteId(null) })} loading={deleteStaffMutation.isPending} message="Are you sure you want to delete this staff member? This action cannot be undone." />
    </div>
  );
}

const STEPS = [
  { id: 'personal', label: 'Personal Information', icon: '1' },
  { id: 'professional', label: 'Professional Info', icon: '2' },
  { id: 'salary', label: 'Salary Structure', icon: '3' },
];

function StaffFormWizard({ register, errors, watch, setValue, trigger, formStep, setFormStep, onSubmit, onCancel, isSaving, isEditing, isDirty, submitError, toast }) {
  const inp = (err) => `w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400 ${err ? 'border-red-400' : 'border-slate-300'}`;
  const Err = ({ e }) => e ? <p className="text-xs text-red-500 mt-0.5">{e.message}</p> : null;

  const handleNext = async () => {
    if (formStep === 0) {
      const valid = await trigger(['employee_id', 'full_name', 'email']);
      if (!valid) return;
    }
    setFormStep(formStep + 1);
  };

  const salaryOnlyMode = isEditing && formStep === 2;

  return (
    <div>
      {/* Stepper - hide in salary-only edit mode */}
      {!salaryOnlyMode && (
      <div className="flex items-center justify-between mb-6 px-2">
        {STEPS.map((step, i) => (
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
            {i < STEPS.length - 1 && <div className={`flex-1 h-0.5 mx-3 rounded ${i < formStep ? 'bg-emerald-300' : 'bg-slate-200'}`} />}
          </div>
        ))}
      </div>
      )}

      <div>
        {/* Step 1: Personal Information */}
        {formStep === 0 && (
          <div className="space-y-4 max-h-[55vh] overflow-y-auto pr-1 pb-4">
            <div className="grid grid-cols-2 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Employee ID *</label><input {...register('employee_id')} className={inp(errors.employee_id)} /><Err e={errors.employee_id} /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Full Name *</label><input {...register('full_name')} className={inp(errors.full_name)} /><Err e={errors.full_name} /></div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Email *</label><input {...register('email')} className={inp(errors.email)} /><Err e={errors.email} /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Phone</label><input {...register('phone')} maxLength={10} placeholder="9876543210" className={inp(errors.phone)} /><Err e={errors.phone} /></div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Gender</label><SearchableSelect value={watch('gender')} onChange={(val) => setValue('gender', val, { shouldDirty: true })} options={[{ value: '', label: 'Select' }, ...GENDER_OPTIONS]} placeholder="Select Gender..." /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Date of Birth</label><DatePicker value={watch('date_of_birth')} onChange={(v) => setValue('date_of_birth', v, { shouldDirty: true })} /></div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Blood Group</label><SearchableSelect value={watch('blood_group')} onChange={(val) => setValue('blood_group', val, { shouldDirty: true })} options={['A+','A-','B+','B-','O+','O-','AB+','AB-'].map(b => ({ value: b, label: b }))} placeholder="Select Blood Group..." /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Address</label><input {...register('address_line1')} className={inp()} /></div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">City</label><input {...register('city')} className={inp()} /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">State</label><input {...register('state')} className={inp()} /></div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Pincode</label><input {...register('pincode')} maxLength={6} placeholder="560001" className={inp(errors.pincode)} /><Err e={errors.pincode} /></div>
              <div></div>
            </div>
          </div>
        )}

        {/* Step 2: Professional Information */}
        {formStep === 1 && (
          <div className="space-y-4 max-h-[55vh] overflow-y-auto pr-1 pb-4">
            <div className="grid grid-cols-2 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Department</label><SearchableSelect value={watch('department')} onChange={(val) => setValue('department', val, { shouldDirty: true })} options={DEPARTMENTS} placeholder="Select Department..." /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Designation</label><input {...register('designation')} className={inp()} /></div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Employment Type</label><SearchableSelect value={watch('employment_type')} onChange={(val) => setValue('employment_type', val, { shouldDirty: true })} options={[{ value: '', label: 'Select' }, ...EMPLOYMENT_TYPES]} placeholder="Select Employment Type..." /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Joining Date</label><DatePicker value={watch('joining_date')} onChange={(v) => setValue('joining_date', v, { shouldDirty: true })} /><Err e={errors.joining_date} /></div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Qualification</label><input {...register('qualification')} className={inp()} /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Experience (years)</label><input type="number" {...register('experience_years')} className={inp()} /></div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-end gap-2 pb-1"><label className="flex items-center gap-2 text-sm"><input type="checkbox" {...register('is_teacher')} className="rounded border-slate-300" /> Is Teacher</label></div>
            </div>
          </div>
        )}

        {/* Step 3: Salary Structure */}
        {formStep === 2 && (
          <div className="space-y-4 max-h-[55vh] overflow-y-auto pr-1 pb-4">
            <h4 className="text-sm font-semibold text-slate-700 border-b border-slate-100 pb-2">Earnings</h4>
            <div className="grid grid-cols-2 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Basic Salary (₹)</label><input type="number" {...register('basic_salary')} className={inp()} />{watch('basic_salary') !== '' && Number(watch('basic_salary')) === 0 && <p className="text-xs text-amber-500 mt-0.5">Salary is set to ₹0</p>}</div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">HRA (₹)</label><input type="number" {...register('hra')} className={inp()} /></div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">DA (₹)</label><input type="number" {...register('da')} className={inp()} /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">TA (₹)</label><input type="number" {...register('ta')} className={inp()} /></div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Other Allowances (₹)</label><input type="number" {...register('other_allowances')} className={inp()} /></div>
              <div></div>
            </div>

            <h4 className="text-sm font-semibold text-slate-700 border-b border-slate-100 pb-2 pt-2">Deductions</h4>
            <div className="grid grid-cols-2 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">PF Deduction (₹)</label><input type="number" {...register('pf_deduction')} className={inp()} /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Tax Deduction (₹)</label><input type="number" {...register('tax_deduction')} className={inp()} /></div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Other Deductions (₹)</label><input type="number" {...register('other_deductions')} className={inp()} /></div>
              <div></div>
            </div>

            <StaffSalarySummary watch={watch} />

            <h4 className="text-sm font-semibold text-slate-700 border-b border-slate-100 pb-2 pt-2">Bank Details</h4>
            <div className="grid grid-cols-2 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Bank Name</label><input {...register('bank_name')} className={inp()} /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Account Number</label><input {...register('bank_account_number')} className={inp()} /></div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">IFSC Code</label><input {...register('bank_ifsc')} className={inp()} /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">PAN Number</label><input {...register('pan_number')} className={inp(errors.pan_number)} placeholder="e.g. ABCDE1234F" /><Err e={errors.pan_number} /></div>
            </div>
          </div>
        )}
      </div>

      {submitError && <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg mt-3">{submitError}</p>}

      {/* Navigation */}
      <div className="flex justify-between mt-4 pt-3 border-t border-slate-100">
        <div>
          {formStep > 0 && !salaryOnlyMode && <Button variant="ghost" onClick={() => setFormStep(formStep - 1)}>Previous</Button>}
        </div>
        <div className="flex gap-2">
          <Button variant="ghost" onClick={onCancel}>Cancel</Button>
          {formStep < STEPS.length - 1 ? (
            <Button variant="primary" onClick={handleNext}>Next</Button>
          ) : (
            <Button variant="primary" onClick={onSubmit} disabled={isSaving || (isEditing && !isDirty)}>{isSaving ? 'Saving...' : isEditing ? 'Update' : 'Add Staff'}</Button>
          )}
        </div>
      </div>
    </div>
  );
}

function StaffSalarySummary({ watch }) {
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
    <div className="border-t border-slate-100 pt-4 mt-2">
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
