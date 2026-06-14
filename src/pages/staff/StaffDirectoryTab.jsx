import { useState } from 'react';
import { Plus, Pencil, Trash2, History, Calendar } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Button, Badge, Modal, SearchableSelect, useSortableData, DataTable, PrintHeader } from 'school-erp-ui-shared';
import { useSchoolProfile } from '../../services/settingsService';
import api from '../../services/api';
import { ENDPOINTS } from '../../config/api';

export default function StaffDirectoryTab({ staff, search, setSearch, deptFilter, setDeptFilter, statusFilter, setStatusFilter, onAdd, onEdit, onDelete, pagination, staffData, loading }) {
  const [historyStaff, setHistoryStaff] = useState(null);
  const navigate = useNavigate();
  const filteredStaff = staff;
  const { sortedData, sortConfig, requestSort } = useSortableData(filteredStaff);

  const columns = [
    {
      key: 'full_name', label: 'Employee', sortable: true,
      render: (s) => (
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-indigo-700 text-white flex items-center justify-center text-xs font-semibold shadow-sm">{(s.full_name || '').slice(0, 2).toUpperCase()}</div>
          <div><p className={`font-semibold text-slate-800 ${s.is_teacher ? 'cursor-pointer hover:text-primary-600 hover:underline' : ''}`} onClick={() => s.is_teacher && navigate(`/admin/teachers/${s.id}`)}>{s.full_name}</p><p className="text-[10px] text-slate-400">{s.employee_id}</p></div>
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
        headerExtra={<Button variant="primary" size="sm" icon={Plus} onClick={onAdd}>Add Staff Member</Button>}
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

  if (viewSlip) {
    return <SalarySlipView staff={{...staff, ...viewSlip}} onClose={() => setViewSlip(null)} />;
  }

  return (
    <div className="space-y-4">
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

function SalarySlipView({ staff, onClose }) {
  const { data: schoolData } = useSchoolProfile();
  const basic = Number(staff.basic_salary || 0);
  const hra = Number(staff.hra || 0);
  const da = Number(staff.da || 0);
  const ta = Number(staff.ta || 0);
  const otherAllow = Number(staff.other_allowances || 0);
  const pf = Number(staff.pf_deduction || 0);
  const tax = Number(staff.tax_deduction || 0);
  const otherDed = Number(staff.other_deductions || 0);
  const grossEarnings = basic + hra + da + ta + otherAllow;
  const totalDeductions = pf + tax + otherDed;
  const netPayable = grossEarnings - totalDeductions;
  const fmt = (v) => `₹${Number(v || 0).toLocaleString()}`;

  const handleDownloadPdf = () => {
    const content = document.getElementById('salary-slip-content');
    if (content) {
      const printWindow = window.open('', '_blank');
      printWindow.document.write(`<html><head><title>Salary Slip - ${staff.full_name}</title><style>body{font-family:sans-serif;padding:40px;max-width:700px;margin:0 auto;} table{width:100%;border-collapse:collapse;} td,th{padding:8px 12px;text-align:left;} .right{text-align:right;} .bold{font-weight:bold;} .green{color:#16a34a;} .red{color:#dc2626;} hr{margin:12px 0;border:none;border-top:1px solid #e2e8f0;} .header{text-align:center;border-bottom:2px solid #1e293b;padding-bottom:16px;margin-bottom:20px;} .header h1{margin:0;font-size:20px;text-transform:uppercase;letter-spacing:1px;} .header p{margin:4px 0;font-size:11px;color:#64748b;} .doc-title{text-align:center;margin:16px 0;padding-top:12px;border-top:1px solid #e2e8f0;font-size:13px;font-weight:bold;text-transform:uppercase;letter-spacing:1px;}</style></head><body>`);
      printWindow.document.write(`<div class="header"><h1>${schoolData?.name || 'School'}</h1>${schoolData?.affiliation ? `<p>${schoolData.affiliation}</p>` : ''}${schoolData?.address ? `<p>${schoolData.address}</p>` : ''}<p>${[schoolData?.phone, schoolData?.email].filter(Boolean).join(' • ')}</p><div class="doc-title">Salary Slip</div></div>`);
      printWindow.document.write(`<p><strong>${staff.full_name}</strong><br/>${staff.employee_id} • ${staff.designation || staff.department || 'Staff'}</p><hr/>`);
      printWindow.document.write(`<h4>Earnings</h4><table><tr><td>Base Pay</td><td class="right">${fmt(basic)}</td></tr><tr><td>HRA</td><td class="right">${fmt(hra)}</td></tr><tr><td>DA</td><td class="right">${fmt(da)}</td></tr><tr><td>Transport Allowance</td><td class="right">${fmt(ta)}</td></tr><tr><td>Other Allowances</td><td class="right">${fmt(otherAllow)}</td></tr><tr class="bold"><td>Gross Earnings</td><td class="right green">${fmt(grossEarnings)}</td></tr></table>`);
      printWindow.document.write(`<hr/><h4>Deductions</h4><table><tr><td>Provident Fund</td><td class="right">${fmt(pf)}</td></tr><tr><td>Professional Tax</td><td class="right">${fmt(tax)}</td></tr><tr><td>Other Deductions</td><td class="right">${fmt(otherDed)}</td></tr><tr class="bold"><td>Total Deductions</td><td class="right red">${fmt(totalDeductions)}</td></tr></table>`);
      printWindow.document.write(`<hr/><table><tr class="bold"><td style="font-size:18px">Net Payable</td><td class="right green" style="font-size:18px">${fmt(netPayable)}</td></tr></table>`);
      printWindow.document.write(`</body></html>`);
      printWindow.document.close();
      printWindow.print();
    }
  };

  return (
    <div id="salary-slip-content">
      <PrintHeader school={schoolData} title="Salary Slip" subtitle={`${staff.month_name || 'Current'} ${staff.year || new Date().getFullYear()}`} />
      {/* Staff Info */}
      <div className="pb-3 border-b border-slate-100 mb-4">
        <p className="text-lg font-bold text-slate-900">{staff.full_name}</p>
        <p className="text-xs text-slate-500">{staff.employee_id} • {staff.designation || staff.department || 'Staff'}</p>
        <p className="text-xs text-slate-500">{staff.department || 'Teaching'}</p>
        <div className="grid grid-cols-3 gap-3 mt-3 pt-3 border-t border-slate-50">
          <div><p className="text-[10px] text-slate-400">Period</p><p className="text-xs font-semibold text-slate-700">{staff.month_name || (staff.month ? ['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][staff.month] : 'Current')} {staff.year || new Date().getFullYear()}</p></div>
          <div><p className="text-[10px] text-slate-400">Payment Date</p><p className="text-xs font-semibold text-slate-700">{staff.paid_on || '-'}</p></div>
          <div><p className="text-[10px] text-slate-400">Working Days</p><p className="text-xs font-semibold text-slate-700">{staff.working_days || 26}/{staff.total_days || 30}</p></div>
        </div>
      </div>

      {/* Earnings */}
      <div className="mb-4">
        <p className="text-sm font-bold text-slate-800 mb-2">Earnings</p>
        <div className="space-y-1.5">
          <div className="flex justify-between text-sm"><span className="text-slate-600">Base Pay</span><span className="text-slate-800">{fmt(basic)}</span></div>
          <div className="flex justify-between text-sm"><span className="text-slate-600">HRA</span><span className="text-slate-800">{fmt(hra)}</span></div>
          <div className="flex justify-between text-sm"><span className="text-slate-600">DA</span><span className="text-slate-800">{fmt(da)}</span></div>
          <div className="flex justify-between text-sm"><span className="text-slate-600">Transport Allowance</span><span className="text-slate-800">{fmt(ta)}</span></div>
          <div className="flex justify-between text-sm"><span className="text-slate-600">Other Allowances</span><span className="text-slate-800">{fmt(otherAllow)}</span></div>
          <div className="flex justify-between text-sm font-bold pt-1 border-t border-slate-100"><span className="text-slate-800">Gross Earnings</span><span className="text-green-600">{fmt(grossEarnings)}</span></div>
        </div>
      </div>

      {/* Deductions */}
      <div className="mb-4">
        <p className="text-sm font-bold text-slate-800 mb-2">Deductions</p>
        <div className="space-y-1.5">
          <div className="flex justify-between text-sm"><span className="text-slate-600">Provident Fund</span><span className="text-slate-800">{fmt(pf)}</span></div>
          <div className="flex justify-between text-sm"><span className="text-slate-600">Professional Tax</span><span className="text-slate-800">{fmt(tax)}</span></div>
          <div className="flex justify-between text-sm"><span className="text-slate-600">Other Deductions</span><span className="text-slate-800">{fmt(otherDed)}</span></div>
          <div className="flex justify-between text-sm font-bold pt-1 border-t border-slate-100"><span className="text-slate-800">Total Deductions</span><span className="text-red-600">{fmt(totalDeductions)}</span></div>
        </div>
      </div>

      {/* Net Payable */}
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 mb-4">
        <div className="flex justify-between items-center">
          <p className="text-base font-bold text-slate-800">Net Payable</p>
          <p className="text-2xl font-bold text-green-600">{fmt(netPayable)}</p>
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-2 pt-3 border-t border-slate-100">
        <Button variant="primary" className="flex-1" onClick={handleDownloadPdf}>⬇ Download PDF</Button>
        <Button variant="ghost" onClick={onClose}>Close</Button>
      </div>
    </div>
  );
}
