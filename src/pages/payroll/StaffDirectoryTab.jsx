import { useState } from 'react';
import { Plus, Pencil, Trash2, History, Calendar, Download } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Button, Badge, Modal, SearchableSelect, useSortableData, DataTable, PrintHeader, useToast } from 'school-erp-ui-shared';
import { useSchoolProfile } from '../../services/settingsService';
import { generatePayslipPdf } from '../../utils/payslipPdf';
import SalarySlipView from './SalarySlipView';
import { downloadBulkTemplate } from '../../utils/bulkTemplateExport';
import { DEPARTMENTS, EMPLOYMENT_TYPES, GENDER_OPTIONS } from '../../constants.jsx';
import api from '../../services/api';
import { ENDPOINTS } from '../../config/api';

export default function StaffDirectoryTab({ staff, search, setSearch, deptFilter, setDeptFilter, statusFilter, setStatusFilter, onAdd, onEdit, onDelete, pagination, staffData, loading }) {
  const toast = useToast();
  const [historyStaff, setHistoryStaff] = useState(null);
  const navigate = useNavigate();
  const filteredStaff = staff;
  const { sortedData, sortConfig, requestSort } = useSortableData(filteredStaff);
  const { data: schoolData } = useSchoolProfile();

  const handleDownloadTemplate = async () => {
    await downloadBulkTemplate({
      filename: 'Bulk_Staff_Upload',
      schoolName: schoolData?.school_name || '',
      schoolCode: schoolData?.school_code || '',
      sheetName: 'Staff Data',
      columns: [
        // Personal Information
        { header: 'Employee ID', key: 'employee_id', mandatory: true, description: 'Unique employee ID (auto-generated if left blank)' },
        { header: 'Full Name', key: 'full_name', mandatory: true, description: 'Staff full name' },
        { header: 'Email', key: 'email', mandatory: true, description: 'Email address (used for login)' },
        { header: 'Phone', key: 'phone', description: '10-digit mobile number' },
        { header: 'Gender', key: 'gender', dropdown: GENDER_OPTIONS.map(g => g.value), description: 'Male, Female, or Other' },
        { header: 'Date of Birth', key: 'date_of_birth', description: 'Format: YYYY-MM-DD' },
        { header: 'Blood Group', key: 'blood_group', dropdown: ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'], description: 'Blood group' },
        { header: 'Address', key: 'address_line1', description: 'Full address' },
        { header: 'City', key: 'city', description: 'City' },
        { header: 'State', key: 'state', description: 'State' },
        { header: 'Pincode', key: 'pincode', description: '6-digit pincode' },
        // Professional Information
        { header: 'Department', key: 'department', mandatory: true, dropdown: DEPARTMENTS.map(d => d.value), description: 'Teaching, Administration, Accounts, etc.' },
        { header: 'Designation', key: 'designation', description: 'Job title / designation' },
        { header: 'Employment Type', key: 'employment_type', dropdown: EMPLOYMENT_TYPES.map(t => t.value), description: 'Full-Time, Part-Time, or Contract' },
        { header: 'Joining Date', key: 'joining_date', description: 'Format: YYYY-MM-DD' },
        { header: 'Qualification', key: 'qualification', description: 'Highest qualification (e.g., B.Ed, M.Sc)' },
        { header: 'Experience (Years)', key: 'experience_years', description: 'Total years of experience' },
        { header: 'Is Teacher', key: 'is_teacher', dropdown: ['Yes', 'No'], description: 'Yes if this staff member teaches classes' },
        // Salary - Earnings
        { header: 'Basic Salary', key: 'basic_salary', description: 'Monthly basic salary in ₹' },
        { header: 'HRA', key: 'hra', description: 'House Rent Allowance in ₹' },
        { header: 'DA', key: 'da', description: 'Dearness Allowance in ₹' },
        { header: 'TA', key: 'ta', description: 'Travel Allowance in ₹' },
        { header: 'Other Allowances', key: 'other_allowances', description: 'Any other monthly allowances in ₹' },
        // Salary - Deductions
        { header: 'PF Deduction', key: 'pf_deduction', description: 'Provident Fund deduction in ₹' },
        { header: 'Tax Deduction (TDS)', key: 'tax_deduction', description: 'TDS / Income tax deduction in ₹' },
        { header: 'Other Deductions', key: 'other_deductions', description: 'Any other monthly deductions in ₹' },
        // Bank Details
        { header: 'Bank Name', key: 'bank_name', description: 'Bank name for salary credit' },
        { header: 'Account Number', key: 'bank_account_number', description: 'Bank account number' },
        { header: 'IFSC Code', key: 'bank_ifsc', description: 'Bank branch IFSC code' },
        { header: 'PAN Number', key: 'pan_number', description: 'PAN card number (e.g., ABCDE1234F)' },
        // Emergency Contact
        { header: 'Emergency Contact Name', key: 'emergency_contact_name', description: 'Emergency contact person name' },
        { header: 'Emergency Contact Phone', key: 'emergency_contact_phone', description: 'Emergency contact phone number' },
        { header: 'Emergency Contact Relationship', key: 'emergency_contact_relationship', dropdown: ['Father', 'Mother', 'Spouse', 'Sibling', 'Friend', 'Other'], description: 'Relationship with emergency contact' },
      ],
    });
    toast.success('Template downloaded');
  };

  const columns = [
    {
      key: 'full_name', label: 'Employee', sortable: true,
      render: (s) => (
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-indigo-700 text-white flex items-center justify-center text-xs font-semibold shadow-sm">{(s.full_name || '').slice(0, 2).toUpperCase()}</div>
          <div><p className={`font-semibold text-slate-800 ${s.is_teacher ? 'cursor-pointer hover:text-primary-600 hover:underline' : ''}`} onClick={() => s.is_teacher && navigate(`/admin/staff/${s.id}`)}>{s.full_name}</p><p className="text-[10px] text-slate-400">{s.employee_id}</p></div>
        </div>
      ),
    },
    {
      key: 'department', label: 'Department', sortable: true,
      render: (s) => (
        <div><p className="text-slate-800">{s.department || ''}</p><p className="text-[10px] text-slate-500">{s.designation || ''}</p></div>
      ),
    },
    {
      key: 'contact', label: 'Contact',
      render: (s) => <div className="text-slate-500"><p>{s.email || ''}</p><p>{s.phone || ''}</p></div>,
    },
    {
      key: 'salary', label: 'Salary',
      render: (s) => {
        const sal = (Number(s.basic_salary || 0) + Number(s.hra || 0) + Number(s.da || 0) + Number(s.ta || 0) + Number(s.other_allowances || 0)) || Number(s.salary || 0);
        return <div><p className="font-medium text-slate-800">{'₹'}{sal.toLocaleString()}</p><p className="text-[10px] text-slate-400">per month</p></div>;
      },
    },
    {
      key: 'employment', label: 'Employment',
      render: (s) => <div><p className="text-slate-800">{s.employment_type || '-'}</p><p className="text-[10px] text-slate-500">Joined: {s.joining_date || '-'}</p></div>,
    },
    {
      key: 'status', label: 'Status',
      render: (s) => <Badge status={s.status || 'Active'} />,
    },
    {
      key: 'actions', label: 'Actions',
      render: (s) => (
        <div className="flex gap-1">
          <button className="p-1.5 hover:bg-slate-100 rounded-lg transition-all duration-150 active:scale-[0.97]" onClick={() => onEdit(s)} title="Edit"><Pencil className="w-4 h-4 text-slate-500" /></button>
          <button className="p-1.5 hover:bg-blue-50 rounded-lg transition-all duration-150 active:scale-[0.97]" onClick={() => setHistoryStaff(s)} title="Salary History"><History className="w-4 h-4 text-blue-500" /></button>
          <button className="p-1.5 hover:bg-red-50 rounded-lg transition-all duration-150 active:scale-[0.97]" onClick={() => onDelete(s.id)} title="Delete"><Trash2 className="w-4 h-4 text-red-500" /></button>
        </div>
      ),
    },
  ];

  return (
    <div>
      <DataTable
        columns={columns}
        data={sortedData}
        loading={loading || false}
        emptyMessage="No staff found"
        emptyIcon={Plus}
        headerTitle="Staff Directory"
        search={{ value: search, onChange: setSearch, placeholder: 'Search by name, ID, or email...' }}
        filters={[
          { key: 'department', value: deptFilter, onChange: setDeptFilter, options: [{ value: '', label: 'All Departments' }, { value: 'Teaching', label: 'Teaching' }, { value: 'Administration', label: 'Administration' }, { value: 'Accounts', label: 'Accounts' }, { value: 'Transport', label: 'Transport' }] },
          { key: 'status', value: statusFilter, onChange: setStatusFilter, options: [{ value: '', label: 'All Status' }, { value: 'Active', label: 'Active' }, { value: 'Inactive', label: 'Inactive' }] },
        ]}
        sortConfig={sortConfig}
        onSort={requestSort}
        page={pagination?.page}
        totalPages={staffData?.total_pages || 1}
        totalCount={staffData?.count || 0}
        pageSize={pagination?.pageSize}
        onPageChange={pagination ? (p) => pagination.setPage(p) : undefined}
        onPageSizeChange={pagination.setPageSize}
      />

      {/* Salary History Modal */}
      <Modal open={!!historyStaff} onClose={() => setHistoryStaff(null)} title="Complete Salary History & Financial Details" size="3xl">
        {historyStaff && <SalaryHistoryView staff={historyStaff} />}
      </Modal>

    </div>
  );
}

function SalaryHistoryView({ staff }) {
  const [filterYear, setFilterYear] = useState(String(new Date().getFullYear()));
  const [filterMonth, setFilterMonth] = useState(String(new Date().getMonth() || 12));
  const [filterStatus, setFilterStatus] = useState('');
  const [viewSlip, setViewSlip] = useState(null);

  const { data: payrollData } = useQuery({
    queryKey: ['staff-payroll-history', staff.id],
    queryFn: () => api.get(ENDPOINTS.payroll.staffPayslips(staff.id)).then(r => r.data),
    enabled: !!staff.id,
  });

  const allPayslips = payrollData?.results || [];
  const payslips = allPayslips.filter(p => {
    if (filterYear && String(p.year) !== filterYear) return false;
    if (filterMonth && String(p.month) !== filterMonth) return false;
    if (filterStatus && p.status !== filterStatus) return false;
    return true;
  });

  const totalPaid = payslips.reduce((s, p) => s + Number(p.paid_amount || 0), 0);
  const totalEarnings = payslips.reduce((s, p) => s + Number(p.net_salary || 0), 0);
  const paidCount = payslips.filter(p => p.status === 'Paid').length;
  const pendingCount = payslips.filter(p => p.status !== 'Paid').length;
  const sal = Number(staff.basic_salary || 0) + Number(staff.hra || 0) + Number(staff.da || 0) + Number(staff.ta || 0) + Number(staff.other_allowances || 0);
  const fmt = (v) => `₹${Number(v || 0).toLocaleString()}`;
  const MONTHS = ['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const currentYear = new Date().getFullYear();
  const years = [...new Set([currentYear, currentYear - 1, ...allPayslips.map(p => p.year).filter(Boolean)])].sort().reverse();

  return (
    <div className="space-y-4">
      {/* Salary Slip — same "Payslip" modal as the Payroll tab */}
      <Modal open={!!viewSlip} onClose={() => setViewSlip(null)} title="Payslip" size="3xl">
        {viewSlip && <SalarySlipView staff={{ ...staff, ...viewSlip }} onClose={() => setViewSlip(null)} />}
      </Modal>
      {/* Staff Header */}
      <div className="flex items-center gap-3 pb-3 border-b border-slate-100">
        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-500 to-indigo-700 text-white flex items-center justify-center text-sm font-bold">{(staff.full_name || '').slice(0, 2).toUpperCase()}</div>
        <div className="flex-1">
          <p className="text-base font-bold text-slate-900">{staff.full_name}</p>
          <p className="text-xs text-slate-500">{staff.employee_id} • {staff.designation || staff.department || 'Staff'} • {staff.department || 'Teaching'}</p>
        </div>
        <Badge status={staff.status || 'Active'} />
      </div>

      {/* Quick Info */}
      <div className="grid grid-cols-3 gap-3">
        <div className="bg-slate-50 rounded-lg p-3 text-center"><p className="text-[10px] text-slate-400">Current Salary</p><p className="text-base font-bold text-slate-900">{fmt(sal || staff.salary)}</p></div>
        <div className="bg-slate-50 rounded-lg p-3 text-center"><p className="text-[10px] text-slate-400">Join Date</p><p className="text-base font-bold text-slate-900">{staff.joining_date || '-'}</p></div>
        <div className="bg-slate-50 rounded-lg p-3 text-center"><p className="text-[10px] text-slate-400">Employment Type</p><p className="text-base font-bold text-slate-900">{staff.employment_type || '-'}</p></div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-end gap-3">
        <div><label className="text-xs text-slate-500 mb-1 block">Filter by Year</label><SearchableSelect value={filterYear} onChange={setFilterYear} options={[{ value: '', label: 'All Years' }, ...years.map(y => ({ value: String(y), label: String(y) }))]} placeholder="All Years" /></div>
        <div><label className="text-xs text-slate-500 mb-1 block">Filter by Month</label><SearchableSelect value={filterMonth} onChange={setFilterMonth} options={[{ value: '', label: 'All Months' }, ...MONTHS.slice(1).map((m, i) => ({ value: String(i + 1), label: m }))]} placeholder="All Months" /></div>
        <div><label className="text-xs text-slate-500 mb-1 block">Filter by Status</label><SearchableSelect value={filterStatus} onChange={setFilterStatus} options={[{ value: '', label: 'All Status' }, { value: 'Paid', label: 'Paid' }, { value: 'Unpaid', label: 'Unpaid' }, { value: 'Partially Paid', label: 'Partially Paid' }]} placeholder="All Status" /></div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-3">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-2.5 text-center"><p className="text-[10px] text-blue-600">Total Records</p><p className="text-lg font-bold text-blue-700">{payslips.length}</p></div>
        <div className="bg-green-50 border border-green-200 rounded-lg p-2.5 text-center"><p className="text-[10px] text-green-600">Paid</p><p className="text-lg font-bold text-green-700">{paidCount}</p><p className="text-[10px] text-green-600">{fmt(totalPaid)}</p></div>
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-2.5 text-center"><p className="text-[10px] text-amber-600">Pending</p><p className="text-lg font-bold text-amber-700">{pendingCount}</p><p className="text-[10px] text-amber-600">{fmt(totalEarnings - totalPaid)}</p></div>
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-center"><p className="text-[10px] text-slate-500">Total Credited</p><p className="text-lg font-bold text-slate-900">{fmt(totalPaid)}</p></div>
      </div>

      {/* Monthly Records */}
      <div>
        <p className="text-sm font-semibold text-slate-800 mb-2 flex items-center gap-1.5"><Calendar className="w-4 h-4 text-slate-500" /> Monthly Salary Records ({payslips.length} records)</p>
        {payslips.length > 0 ? (
          <div className="space-y-3 max-h-64 overflow-y-auto pr-1">
            {payslips.map((p, i) => {
              const gross = Number(p.basic_salary || 0) + Number(p.hra || 0) + Number(p.da || 0) + Number(p.transport_allowance || 0);
              const ded = Number(p.deductions || 0);
              const net = Number(p.net_salary || 0);
              return (
                <div key={p.id || i} className="border border-slate-200 rounded-xl overflow-hidden hover:border-slate-300 hover:shadow-sm transition-all">
                  {/* Card Header */}
                  <div className="flex justify-between items-center px-4 py-3 bg-slate-50 border-b border-slate-100">
                    <div>
                      <p className="text-sm font-bold text-slate-900">{MONTHS[p.month] || `Month ${p.month}`} {p.year}</p>
                      <p className="text-[10px] text-slate-400">{p.paid_on ? `Payment Date: ${p.paid_on}` : 'Payment pending'}</p>
                    </div>
                    <Badge status={p.status} />
                  </div>
                  {/* Summary Row */}
                  <div className="grid grid-cols-4 divide-x divide-slate-100 border-b border-slate-100">
                    <div className="p-3 text-center"><p className="text-[10px] text-slate-400 mb-0.5">Gross Earnings</p><p className="text-sm font-bold text-slate-800">{fmt(gross || p.allowances)}</p></div>
                    <div className="p-3 text-center"><p className="text-[10px] text-slate-400 mb-0.5">Deductions</p><p className="text-sm font-bold text-red-600">-{fmt(ded)}</p></div>
                    <div className="p-3 text-center"><p className="text-[10px] text-slate-400 mb-0.5">Net Salary</p><p className="text-sm font-bold text-slate-800">{fmt(net)}</p></div>
                    <div className="p-3 text-center"><p className="text-[10px] text-slate-400 mb-0.5">Paid</p><p className="text-sm font-bold text-green-700">{fmt(p.paid_amount || 0)}</p>{Number(p.paid_amount || 0) < net && <p className="text-[9px] text-amber-600">Remaining: {fmt(net - Number(p.paid_amount || 0))}</p>}</div>
                  </div>
                  {/* Breakdown */}
                  <div className="grid grid-cols-2 divide-x divide-slate-100 px-4 py-3">
                    <div className="pr-4">
                      <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wide mb-1.5">Earnings Breakdown</p>
                      <div className="space-y-1 text-xs">
                        <div className="flex justify-between"><span className="text-slate-500">Base Pay</span><span className="font-medium text-slate-700">{fmt(p.basic_salary)}</span></div>
                        <div className="flex justify-between"><span className="text-slate-500">HRA</span><span className="font-medium text-slate-700">{fmt(p.hra)}</span></div>
                        <div className="flex justify-between"><span className="text-slate-500">DA</span><span className="font-medium text-slate-700">{fmt(p.da)}</span></div>
                        <div className="flex justify-between"><span className="text-slate-500">Transport</span><span className="font-medium text-slate-700">{fmt(p.transport_allowance)}</span></div>
                      </div>
                    </div>
                    <div className="pl-4">
                      <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wide mb-1.5">Deductions Breakdown</p>
                      <div className="space-y-1 text-xs">
                        <div className="flex justify-between"><span className="text-slate-500">PF</span><span className="font-medium text-slate-700">{fmt(ded)}</span></div>
                      </div>
                    </div>
                  </div>
                  {/* Footer */}
                  <div className="flex items-center justify-between px-4 py-2.5 bg-slate-50 border-t border-slate-100">
                    <p className="text-xs text-slate-500 flex items-center gap-1"><Calendar className="w-3 h-3" /> Attendance: <span className="font-medium">{p.working_days || p.attendance_days || 26}/{p.total_days || 26} days</span></p>
                    {p.notes && <p className="text-xs text-amber-600 mt-1 italic">📝 {p.notes}</p>}
                    {p.payment_history?.length > 0 && (
                      <div className="mt-2 border-t border-slate-100 pt-2">
                        <p className="text-[10px] font-semibold text-slate-500 mb-1">Payment History</p>
                        {p.payment_history.map((ph, idx) => (
                          <div key={idx} className="flex items-center justify-between text-xs py-0.5">
                            <span className="text-slate-600">{ph.date} {ph.method && `• ${ph.method}`}</span>
                            <span className="font-medium text-green-700">{fmt(ph.amount)}</span>
                          </div>
                        ))}
                      </div>
                    )}
                    <button onClick={() => setViewSlip({...staff, basic_salary: p.basic_salary, hra: p.hra, da: p.da, ta: p.transport_allowance, other_allowances: 0, pf_deduction: ded, tax_deduction: 0, other_deductions: 0, month: p.month, year: p.year, paid_on: p.paid_on})} className="text-xs font-medium text-primary-600 bg-primary-50 border border-primary-200 px-3 py-1 rounded-lg hover:bg-primary-100 transition-colors">👁 View Slip</button>
                  </div>
                </div>
              );
            })}
          </div>
        ) : <p className="text-sm text-slate-400 text-center py-4">No payroll records found</p>}
      </div>

      {/* Lifetime Summary */}
      <div className="grid grid-cols-2 gap-3 pt-3 border-t border-slate-100">
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4"><p className="text-xs text-blue-600 mb-1">Lifetime Earnings 📈</p><p className="text-xl font-bold text-blue-700">{fmt(totalEarnings)}</p><p className="text-[10px] text-blue-500">Total gross salary across all months</p></div>
        <div className="bg-green-50 border border-green-200 rounded-xl p-4"><p className="text-xs text-green-600 mb-1">Net Amount Credited 💰</p><p className="text-xl font-bold text-green-700">{fmt(totalPaid)}</p><p className="text-[10px] text-green-500">Successfully paid to bank account</p></div>
      </div>
    </div>
  );
}

