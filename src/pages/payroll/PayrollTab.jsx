import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { RefreshCw, CheckCircle, Undo2, FileText, CircleDashed, History, Trash2, Download, TrendingUp, TrendingDown, ArrowUpRight, ArrowDownRight, BarChart3 } from 'lucide-react';
import { Button, Badge, Modal, ConfirmDialog, useToast, PrintHeader } from 'school-erp-ui-shared';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { usePayroll, useRunPayroll, useUpdatePayslip, useRecordPayment, useMarkAllPaid, useUndoAllPaid, useDeletePayroll } from '../../services/payrollService';
import { useSchoolProfile } from '../../services/settingsService';
import { generatePayslipPdf } from '../../utils/payslipPdf';
import SalarySlipView from './SalarySlipView';
import api from '../../services/api';
import { ENDPOINTS } from '../../config/api';

const MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];
const PAYMENT_METHODS = ['Cash', 'Online', 'UPI', 'Cheque', 'Bank Transfer'];

export default function PayrollTab() {
  const toast = useToast();
  const now = new Date();
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [year, setYear] = useState(now.getFullYear());
  const [showRunModal, setShowRunModal] = useState(false);
  const [confirmAction, setConfirmAction] = useState(null); // { title, message, onConfirm }
  const [runMonth, setRunMonth] = useState(now.getMonth() + 1);
  const [runYear, setRunYear] = useState(now.getFullYear());
  const [runWorkingDays, setRunWorkingDays] = useState('26');
  const [editModal, setEditModal] = useState(null);
  const [editData, setEditData] = useState({});
  const [payModal, setPayModal] = useState(null);
  const [payAmount, setPayAmount] = useState('');
  const [payMethod, setPayMethod] = useState('Online');
  const [slipView, setSlipView] = useState(null);
  const [payHistoryView, setPayHistoryView] = useState(null);
  const [showHistory, setShowHistory] = useState(false);

  const [showComparison, setShowComparison] = useState(false);

  const { data: payrollData, isLoading } = usePayroll({ month, year });
  const { data: schoolProfile } = useSchoolProfile();

  // Previous month calculation
  const prevMonth = month === 1 ? 12 : month - 1;
  const prevYear = month === 1 ? year - 1 : year;
  const { data: prevPayrollData } = usePayroll({ month: prevMonth, year: prevYear });

  // Fetch history for trend chart
  const { data: historyData } = useQuery({
    queryKey: ['payroll-history'],
    queryFn: () => api.get(ENDPOINTS.payroll.history).then(r => r.data),
    enabled: showComparison,
  });

  const runPayroll = useRunPayroll();
  const updatePayslip = useUpdatePayslip();
  const recordPayment = useRecordPayment();
  const markAllPaid = useMarkAllPaid();
  const undoAllPaid = useUndoAllPaid();
  const deletePayroll = useDeletePayroll();

  const payslips = payrollData?.results || [];
  const prevPayslips = prevPayrollData?.results || [];
  const totalGross = payslips.reduce((s, p) => s + Number(p.basic_salary || 0) + Number(p.allowances || 0), 0);
  const totalDeductions = payslips.reduce((s, p) => s + Number(p.deductions || 0), 0);
  const totalNet = payslips.reduce((s, p) => s + Number(p.net_salary || 0), 0);
  const totalDisbursed = payslips.reduce((s, p) => s + Number(p.paid_amount || 0), 0);
  const totalPending = totalNet - totalDisbursed;

  const handleRunPayroll = () => {
    // Check if payroll already exists for selected month
    if (runMonth === month && runYear === year && payslips.length > 0) {
      toast.error(`Payroll for ${MONTHS[runMonth - 1]} ${runYear} has already been generated.`);
      return;
    }
    runPayroll.mutate({ month: runMonth, year: runYear, working_days: Number(runWorkingDays) || 26 }, {
      onSuccess: () => { setShowRunModal(false); setMonth(runMonth); setYear(runYear); toast.success('Payroll processed successfully'); },
      onError: (err) => toast.error(err.response?.data?.error || `Payroll for ${MONTHS[runMonth - 1]} ${runYear} has already been generated.`),
    });
  };

  const openEdit = (p) => {
    const basic = Number(p.basic_salary) || 0;
    const hra = Number(p.hra) || 0;
    const da = Number(p.da) || 0;
    const ta = Number(p.transport_allowance) || 0;
    const totalAllow = Number(p.allowances) || 0;
    const otherAllow = Math.max(0, totalAllow - hra - da - ta);
    const breakup = p.deduction_breakup || {};
    const pf = Number(breakup.pf) || 0;
    const taxDeduction = (Number(breakup.professional_tax) || 0) + (Number(breakup.tds) || 0);
    const totalDed = Number(p.deductions) || 0;
    const otherDed = Math.max(0, totalDed - pf - taxDeduction);
    const net = Number(p.net_salary) || 0;
    setEditData({ basic_salary: basic, hra, da, transport_allowance: ta, other_allowances: otherAllow, pf_deduction: pf, professional_tax: taxDeduction, other_deductions: otherDed, net_salary: net });
    setEditModal(p);
  };

  const handleEditChange = (field, value) => {
    const updated = { ...editData, [field]: Number(value) || 0 };
    const earnings = updated.basic_salary + updated.hra + updated.da + updated.transport_allowance + updated.other_allowances;
    const deductions = updated.pf_deduction + updated.professional_tax + updated.other_deductions;
    updated.total_deductions = deductions;
    updated.net_salary = earnings - deductions;
    setEditData(updated);
  };

  const saveEdit = () => {
    updatePayslip.mutate({ id: editModal.id, data: editData }, {
      onSuccess: () => { setEditModal(null); toast.success('Payslip updated'); },
      onError: (err) => toast.error(err.response?.data?.error || 'Failed to update'),
    });
  };

  const openPay = (p) => {
    setPayAmount(String(Number(p.net_salary) - Number(p.paid_amount || 0)));
    setPayMethod('Online');
    setPayModal(p);
  };

  const handlePay = () => {
    recordPayment.mutate({ id: payModal.id, data: { amount: Number(payAmount), payment_method: payMethod } }, {
      onSuccess: () => { setPayModal(null); toast.success('Payment recorded'); },
      onError: (err) => toast.error(err.response?.data?.error || 'Failed to record payment'),
    });
  };

  const handleMarkAllPaid = () => {
    markAllPaid.mutate({ month, year }, {
      onSuccess: (res) => toast.success(res.message || 'All marked as paid'),
      onError: (err) => toast.error(err.response?.data?.error || 'Failed'),
    });
  };

  const handleUndoAllPaid = () => {
    const paidSlips = payslips.filter(p => p.status === 'Paid');
    if (!paidSlips.length) return;
    setConfirmAction({ title: 'Undo All Payments', message: `Are you sure you want to undo payment for ${paidSlips.length} employee(s) for ${MONTHS[month - 1]} ${year}? This will reset their status to Unpaid.`, onConfirm: () => {
      undoAllPaid.mutate({ month, year }, {
        onSuccess: (res) => toast.success(res.message || 'All payments undone'),
        onError: (err) => toast.error(err.response?.data?.error || 'Failed to undo'),
      });
    }});
  };

  const fmt = (v) => `₹${Number(v || 0).toLocaleString()}`;

  return (
    <div>
      {/* Controls */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-slate-700 flex items-center gap-2">
            <button onClick={() => { if (month === 1) { setMonth(12); setYear(year - 1); } else setMonth(month - 1); }} className="p-1 hover:bg-slate-100 rounded">←</button>
            {MONTHS[month - 1]} {year}
            <button onClick={() => { if (month === 12) { setMonth(1); setYear(year + 1); } else setMonth(month + 1); }} className="p-1 hover:bg-slate-100 rounded">→</button>
          </span>
        </div>
        <div className="flex items-center gap-2">
          {payslips.length > 0 && <button className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-lg bg-red-50 text-red-600 border border-red-200 hover:bg-red-100 transition-colors" onClick={() => setConfirmAction({ title: 'Delete Payroll', message: `Are you sure you want to delete the entire payroll for ${MONTHS[month - 1]} ${year}? This will remove all ${payslips.length} payslip(s). This action cannot be undone.`, onConfirm: () => { deletePayroll.mutate({ month, year }, { onSuccess: (res) => toast.success(res.message || 'Payroll deleted'), onError: (err) => toast.error(err.response?.data?.error || 'Failed to delete') }); } })}><Trash2 className="w-4 h-4" /> Delete Payroll</button>}
          {payslips.length > 0 && payslips.some(p => p.status === 'Paid') && <button className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-lg bg-amber-50 text-amber-600 border border-amber-200 hover:bg-amber-100 transition-colors" onClick={handleUndoAllPaid}><Undo2 className="w-4 h-4" /> Undo All Paid</button>}
          {payslips.length > 0 && payslips.some(p => p.status !== 'Paid') && <button className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-lg bg-green-50 text-green-700 border border-green-200 hover:bg-green-100 transition-colors" onClick={() => setConfirmAction({ title: 'Mark All as Paid', message: `Are you sure you want to mark all ${payslips.length} employee(s) as paid for ${MONTHS[month - 1]} ${year}?`, onConfirm: handleMarkAllPaid })} disabled={markAllPaid.isPending}><CheckCircle className="w-4 h-4" /> Mark All Paid</button>}
          <Button variant="primary" size="sm" icon={RefreshCw} onClick={() => setShowRunModal(true)}>Process Payroll</Button>
          <button className={`flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-lg border transition-colors ${showComparison ? 'bg-indigo-100 text-indigo-700 border-indigo-300' : 'bg-indigo-50 text-indigo-600 border-indigo-200 hover:bg-indigo-100'}`} onClick={() => setShowComparison(!showComparison)}><BarChart3 className="w-4 h-4" /> Comparison</button>
          <button className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-lg bg-indigo-50 text-indigo-600 border border-indigo-200 hover:bg-indigo-100 transition-colors" onClick={() => setShowHistory(true)}><History className="w-4 h-4" /> History</button>
        </div>
      </div>

      {/* Stats */}
      {payslips.length > 0 && (
        <div className="grid grid-cols-5 gap-3 mb-4">
          <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-3"><p className="text-xs text-indigo-600">Employees</p><p className="text-lg font-bold text-indigo-900">{payslips.length}</p><p className="text-[10px] text-indigo-500">{MONTHS[month - 1]} {year}</p></div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3"><p className="text-xs text-blue-600">Gross Salary</p><p className="text-lg font-bold text-blue-900">{fmt(totalGross)}</p><p className="text-[10px] text-blue-500">Deductions: {fmt(totalDeductions)}</p></div>
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-3"><p className="text-xs text-slate-500">Net Payable</p><p className="text-lg font-bold text-slate-900">{fmt(totalNet)}</p></div>
          <div className="bg-green-50 border border-green-200 rounded-lg p-3"><p className="text-xs text-green-600">Disbursed</p><p className="text-lg font-bold text-green-700">{fmt(totalDisbursed)}</p></div>
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-3"><p className="text-xs text-amber-600">Pending</p><p className="text-lg font-bold text-amber-700">{fmt(totalPending)}</p></div>
        </div>
      )}

      {/* Month-over-Month Comparison */}
      {showComparison && <PayrollComparison currentPayslips={payslips} prevPayslips={prevPayslips} month={month} year={year} prevMonth={prevMonth} prevYear={prevYear} historyData={historyData} />}

      {/* Table */}
      {isLoading ? <p className="text-sm text-slate-500">Loading...</p> : payslips.length === 0 ? (
        <div className="text-center py-12 text-slate-500"><p>No payroll records for {MONTHS[month - 1]} {year}.</p><p className="text-xs mt-1">Click "Process Payroll" to generate.</p></div>
      ) : (
        <div className="overflow-x-auto border border-slate-200 rounded-lg">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>{['Employee','Gross Salary','Deductions','Net Salary','Paid','Remaining','Status','Actions'].map(h => <th key={h} className="px-3 py-2.5 text-left text-xs font-semibold text-slate-600">{h}</th>)}</tr>
            </thead>
            <tbody>
              {payslips.map(p => {
                const gross = Number(p.basic_salary || 0) + Number(p.allowances || 0);
                const deductions = Number(p.deductions || 0);
                const net = Number(p.net_salary || 0);
                const remaining = net - Number(p.paid_amount || 0);
                return (
                  <tr key={p.id} className="border-b border-slate-100 hover:bg-slate-50">
                    <td className="px-3 py-2.5 font-medium text-slate-800">{p.employee_name}</td>
                    <td className="px-3 py-2.5 text-green-700">{fmt(gross)}</td>
                    <td className="px-3 py-2.5 text-red-600">{fmt(deductions)}</td>
                    <td className="px-3 py-2.5 font-bold">{fmt(net)}</td>
                    <td className="px-3 py-2.5 text-green-700">{fmt(p.paid_amount)}</td>
                    <td className="px-3 py-2.5 text-amber-700">{fmt(remaining)}</td>
                    <td className="px-3 py-2.5"><Badge status={p.status} /></td>
                    <td className="px-3 py-2.5">
                      <div className="flex gap-2">
                        {p.status !== 'Paid' && <Button size="sm" variant="secondary" onClick={() => openEdit(p)}>Edit</Button>}
                        {p.status !== 'Paid' && <Button size="sm" variant="primary" onClick={() => openPay(p)}>Pay</Button>}
                        {Number(p.paid_amount || 0) > 0 && <Button size="sm" variant="ghost" icon={History} onClick={() => setPayHistoryView(p)} title="Payment History" />}
                        <Button size="sm" variant="ghost" icon={FileText} onClick={() => setSlipView(p)} title="View Payslip" />
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Process Payroll Modal */}
      <Modal open={showRunModal} onClose={() => setShowRunModal(false)} title="Process Payroll" size="sm">
        <div className="space-y-4">
          <div><label className="text-xs font-medium text-slate-600 mb-1 block">Year</label><select value={runYear} onChange={e => setRunYear(Number(e.target.value))} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">{[now.getFullYear() - 1, now.getFullYear(), now.getFullYear() + 1].map(y => <option key={y} value={y}>{y}</option>)}</select></div>
          <div><label className="text-xs font-medium text-slate-600 mb-1 block">Month</label><select value={runMonth} onChange={e => setRunMonth(Number(e.target.value))} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">{MONTHS.map((m, i) => <option key={i} value={i + 1}>{m}</option>)}</select></div>
          <div><label className="text-xs font-medium text-slate-600 mb-1 block">Working Days</label><input type="number" value={runWorkingDays} onChange={e => setRunWorkingDays(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" min={1} max={31} /><p className="text-[10px] text-slate-400 mt-1">Total days in month - Approved leaves - Holidays</p></div>
          <div className="flex justify-end gap-2 pt-2"><Button variant="ghost" onClick={() => setShowRunModal(false)}>Cancel</Button><Button variant="primary" onClick={handleRunPayroll} disabled={runPayroll.isPending}>{runPayroll.isPending ? 'Processing...' : 'Process'}</Button></div>
        </div>
      </Modal>

      {/* Edit Payslip Modal */}
      <Modal open={!!editModal} onClose={() => setEditModal(null)} title={`Edit Salary - ${editModal?.employee_name || ''}`} size="lg">
        {editModal && (
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-3 mb-3">
              <div className="bg-green-50 rounded-lg p-3 text-center"><p className="text-xs text-slate-400">Gross Earnings</p><p className="text-lg font-bold text-green-700">{fmt(editData.basic_salary + editData.hra + editData.da + editData.transport_allowance + editData.other_allowances)}</p></div>
              <div className="bg-red-50 rounded-lg p-3 text-center"><p className="text-xs text-slate-400">Total Deductions</p><p className="text-lg font-bold text-red-600">{fmt(editData.pf_deduction + editData.professional_tax + editData.other_deductions)}</p></div>
              <div className="bg-blue-50 rounded-lg p-3 text-center"><p className="text-xs text-slate-400">Net Salary</p><p className="text-lg font-bold text-blue-700">{fmt(editData.net_salary)}</p></div>
            </div>
            <p className="text-xs text-slate-500 font-medium uppercase">Earnings</p>
            <div className="grid grid-cols-3 gap-3">
              <div><label className="text-xs text-slate-600 mb-1 block">Basic Salary (₹)</label><input type="number" value={editData.basic_salary} onChange={e => handleEditChange('basic_salary', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></div>
              <div><label className="text-xs text-slate-600 mb-1 block">HRA (₹)</label><input type="number" value={editData.hra} onChange={e => handleEditChange('hra', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></div>
              <div><label className="text-xs text-slate-600 mb-1 block">DA (₹)</label><input type="number" value={editData.da} onChange={e => handleEditChange('da', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></div>
              <div><label className="text-xs text-slate-600 mb-1 block">TA (₹)</label><input type="number" value={editData.transport_allowance} onChange={e => handleEditChange('transport_allowance', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></div>
              <div><label className="text-xs text-slate-600 mb-1 block">Other Allowances (₹)</label><input type="number" value={editData.other_allowances} onChange={e => handleEditChange('other_allowances', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></div>
            </div>
            <p className="text-xs text-slate-500 font-medium uppercase mt-3">Deductions</p>
            <div className="grid grid-cols-3 gap-3">
              <div><label className="text-xs text-slate-600 mb-1 block">PF Deduction (₹)</label><input type="number" value={editData.pf_deduction} onChange={e => handleEditChange('pf_deduction', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></div>
              <div><label className="text-xs text-slate-600 mb-1 block">Tax Deduction (₹)</label><input type="number" value={editData.professional_tax} onChange={e => handleEditChange('professional_tax', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></div>
              <div><label className="text-xs text-slate-600 mb-1 block">Other Deductions (₹)</label><input type="number" value={editData.other_deductions} onChange={e => handleEditChange('other_deductions', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></div>
            </div>
            <div><label className="text-xs text-slate-600 mb-1 block">Notes <span className="text-slate-400 font-normal">(reason for changes)</span></label><textarea value={editData.notes || ''} onChange={e => setEditData(d => ({ ...d, notes: e.target.value }))} rows={2} placeholder="e.g. Adjusted HRA for Q2, deducted advance..." className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm resize-none" /></div>
            <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
              <Button variant="ghost" onClick={() => setEditModal(null)}>Cancel</Button>
              <Button variant="primary" onClick={saveEdit} disabled={updatePayslip.isPending}>{updatePayslip.isPending ? 'Saving...' : 'Save Changes'}</Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Pay Modal */}
      <Modal open={!!payModal} onClose={() => setPayModal(null)} title={`Record Payment - ${payModal?.employee_name || ''}`} size="md">
        {payModal && (
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-3">
              <div className="bg-slate-50 rounded-lg p-3 text-center"><p className="text-xs text-slate-400">Net Salary</p><p className="text-lg font-bold text-slate-900">{fmt(payModal.net_salary)}</p></div>
              <div className="bg-green-50 rounded-lg p-3 text-center"><p className="text-xs text-slate-400">Paid</p><p className="text-lg font-bold text-green-700">{fmt(payModal.paid_amount)}</p></div>
              <div className="bg-amber-50 rounded-lg p-3 text-center"><p className="text-xs text-slate-400">Remaining</p><p className="text-lg font-bold text-amber-700">{fmt(Number(payModal.net_salary) - Number(payModal.paid_amount || 0))}</p></div>
            </div>
            <div><label className="text-xs text-slate-600 mb-1 block">Amount (₹)</label><input type="number" value={payAmount} onChange={e => setPayAmount(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></div>
            <div>
              <label className="text-xs text-slate-600 mb-1.5 block">Payment Method</label>
              <div className="flex gap-2 flex-wrap">
                {PAYMENT_METHODS.map(m => (
                  <button key={m} onClick={() => setPayMethod(m)} className={`px-3 py-1.5 rounded-lg text-sm font-medium border transition-all ${payMethod === m ? 'bg-primary-100 border-primary-400 text-primary-700' : 'border-slate-200 text-slate-600 hover:border-slate-300'}`}>{m}</button>
                ))}
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
              <Button variant="ghost" onClick={() => setPayModal(null)}>Cancel</Button>
              <Button variant="primary" onClick={handlePay} disabled={recordPayment.isPending || !payAmount}>{recordPayment.isPending ? 'Recording...' : 'Record Payment'}</Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Payslip View Modal */}
      <Modal open={!!slipView} onClose={() => setSlipView(null)} title="Payslip" size="3xl">
        {slipView && (() => {
          const pf = Number(slipView.deduction_breakup?.provident_fund || 0);
          const tax = Number(slipView.deduction_breakup?.professional_tax || 0);
          const totalDed = Number(slipView.deductions || 0);
          const otherDed = Math.max(0, totalDed - pf - tax);
          const otherAllow = Math.max(0, Number(slipView.allowances || 0) - Number(slipView.hra || 0) - Number(slipView.da || 0) - Number(slipView.transport_allowance || 0));
          const slip = {
            full_name: slipView.employee_name,
            employee_id: slipView.employee_id,
            designation: slipView.designation,
            department: slipView.department,
            month: slipView.month,
            year: slipView.year,
            basic_salary: slipView.basic_salary,
            hra: slipView.hra,
            da: slipView.da,
            ta: slipView.transport_allowance,
            other_allowances: otherAllow,
            pf_deduction: pf,
            tax_deduction: tax,
            other_deductions: otherDed,
            paid_on: slipView.paid_on,
            working_days: slipView.working_days,
            total_days: slipView.total_days,
            payment_method: slipView.payment_method,
            reference: slipView.reference,
          };
          return <SalarySlipView staff={slip} onClose={() => setSlipView(null)} />;
        })()}
      </Modal>

      {/* Payment History Modal */}
      <Modal open={!!payHistoryView} onClose={() => setPayHistoryView(null)} title={`Payment History — ${payHistoryView?.employee_name || ''}`} size="3xl">
        {payHistoryView && (
          <div>
            <div className="grid grid-cols-3 gap-3 mb-4">
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-center">
                <p className="text-[10px] text-slate-500 uppercase">Net Salary</p>
                <p className="text-base font-bold text-slate-900">{fmt(payHistoryView.net_salary)}</p>
              </div>
              <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-center">
                <p className="text-[10px] text-green-600 uppercase">Total Paid</p>
                <p className="text-base font-bold text-green-700">{fmt(payHistoryView.paid_amount)}</p>
              </div>
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-center">
                <p className="text-[10px] text-amber-600 uppercase">Remaining</p>
                <p className="text-base font-bold text-amber-700">{fmt(Number(payHistoryView.net_salary) - Number(payHistoryView.paid_amount || 0))}</p>
              </div>
            </div>
            {/* Payment History */}
            <p className="text-xs font-semibold text-slate-600 mb-2">Payments</p>
            {(() => {
              const history = payHistoryView.payment_history || [];
              if (history.length === 0) {
                return <p className="text-sm text-slate-400 text-center py-3 mb-4 bg-slate-50 rounded-lg">No payment records yet{payHistoryView.paid_on ? `. Marked as paid on ${payHistoryView.paid_on}` : ''}</p>;
              }
              const runningTotal = history.reduce((acc, ph) => {
                acc.push((acc.length > 0 ? acc[acc.length - 1] : 0) + Number(ph.amount));
                return acc;
              }, []);
              return (
                <div className="border border-slate-200 rounded-lg overflow-hidden mb-4">
                  <table className="w-full text-sm">
                    <thead className="bg-slate-50 border-b border-slate-200">
                      <tr>
                        <th className="text-left px-4 py-2 text-xs font-semibold text-slate-500">#</th>
                        <th className="text-left px-4 py-2 text-xs font-semibold text-slate-500">Date</th>
                        <th className="text-left px-4 py-2 text-xs font-semibold text-slate-500">Method</th>
                        <th className="text-right px-4 py-2 text-xs font-semibold text-slate-500">Amount</th>
                        <th className="text-right px-4 py-2 text-xs font-semibold text-slate-500">Running Total</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {history.map((ph, idx) => (
                        <tr key={idx} className="hover:bg-slate-50/50">
                          <td className="px-4 py-2.5 text-slate-400">{idx + 1}</td>
                          <td className="px-4 py-2.5 text-slate-700">{ph.date ? new Date(ph.date + 'T00:00:00').toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : '—'}</td>
                          <td className="px-4 py-2.5"><span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${ph.method === 'Bank Transfer' ? 'bg-blue-50 text-blue-700' : ph.method === 'UPI' ? 'bg-purple-50 text-purple-700' : ph.method === 'Cash' ? 'bg-emerald-50 text-emerald-700' : ph.method === 'Bulk' ? 'bg-slate-100 text-slate-600' : 'bg-slate-100 text-slate-600'}`}>{ph.method || '—'}</span></td>
                          <td className="px-4 py-2.5 text-right font-semibold text-green-700">{fmt(ph.amount)}</td>
                          <td className="px-4 py-2.5 text-right text-xs text-slate-500">{fmt(runningTotal[idx])}</td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot>
                      <tr className="bg-slate-50 border-t border-slate-200">
                        <td colSpan={3} className="px-4 py-2.5 text-xs font-semibold text-slate-600">Total ({history.length} payment{history.length !== 1 ? 's' : ''})</td>
                        <td className="px-4 py-2.5 text-right font-bold text-green-700">{fmt(history.reduce((s, ph) => s + Number(ph.amount), 0))}</td>
                        <td></td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              );
            })()}

            {/* Edit History */}
            {payHistoryView.edit_history?.length > 0 && (
              <>
                <p className="text-xs font-semibold text-slate-600 mb-2">Edit History</p>
                <div className="space-y-2">
                  {payHistoryView.edit_history.map((edit, idx) => (
                    <div key={idx} className="border border-slate-200 rounded-lg p-3 bg-slate-50/50">
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="text-xs font-medium text-slate-700">{edit.date || '—'}</span>
                        {edit.notes && <span className="text-[10px] text-amber-600 italic">{edit.notes}</span>}
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {Object.entries(edit.changes || {}).map(([field, val]) => (
                          <span key={field} className="text-[10px] px-2 py-0.5 rounded bg-white border border-slate-200 text-slate-600">
                            {field.replace(/_/g, ' ')}: <span className="text-red-500 line-through">{fmt(val.old)}</span> → <span className="text-green-600 font-medium">{fmt(val.new)}</span>
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        )}
      </Modal>

      {/* Confirmation Dialog */}
      <ConfirmDialog
        open={!!confirmAction}
        onClose={() => setConfirmAction(null)}
        onConfirm={() => { confirmAction?.onConfirm(); setConfirmAction(null); }}
        title={confirmAction?.title || 'Confirm'}
        message={confirmAction?.message || 'Are you sure?'}
        confirmText="Confirm"
      />

      {/* Payroll History Modal */}
      {showHistory && <PayrollHistoryModal onClose={() => setShowHistory(false)} />}
    </div>
  );
}

function PayrollComparison({ currentPayslips, prevPayslips, month, year, prevMonth, prevYear, historyData }) {
  const MONTH_NAMES = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  const MONTH_SHORT = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const fmt = (v) => `₹${Number(v || 0).toLocaleString('en-IN')}`;

  const currentTotal = currentPayslips.reduce((s, p) => s + Number(p.net_salary || 0), 0);
  const prevTotal = prevPayslips.reduce((s, p) => s + Number(p.net_salary || 0), 0);
  const currentStaffCount = currentPayslips.length;
  const prevStaffCount = prevPayslips.length;

  // Identify new joiners and staff who left (by employee_id or employee_name)
  const currentIds = new Set(currentPayslips.map(p => p.employee_id || p.employee_name));
  const prevIds = new Set(prevPayslips.map(p => p.employee_id || p.employee_name));
  const newJoiners = currentPayslips.filter(p => !prevIds.has(p.employee_id || p.employee_name));
  const staffLeft = prevPayslips.filter(p => !currentIds.has(p.employee_id || p.employee_name));

  const salaryDelta = currentTotal - prevTotal;
  const salaryDeltaPercent = prevTotal > 0 ? ((salaryDelta / prevTotal) * 100).toFixed(1) : 0;

  // Build trend chart data from history
  const history = historyData?.history || [];
  const trendData = useMemo(() => {
    if (history.length === 0) return [];
    return history
      .slice()
      .sort((a, b) => (a.year * 12 + a.month) - (b.year * 12 + b.month))
      .map(h => ({
        period: `${MONTH_SHORT[h.month - 1]} ${h.year}`,
        total_salary: Number(h.total_salary || 0),
        total_paid: Number(h.total_paid || 0),
        staff: h.total_staff || 0,
      }));
  }, [history]);

  const hasEnoughData = currentPayslips.length > 0 || prevPayslips.length > 0;

  if (!hasEnoughData) {
    return (
      <div className="mb-4 bg-slate-50 border border-slate-200 rounded-xl p-6 text-center">
        <BarChart3 className="w-8 h-8 text-slate-300 mx-auto mb-2" />
        <p className="text-sm text-slate-500 font-medium">Not enough data for comparison</p>
        <p className="text-xs text-slate-400 mt-1">Process payroll for at least one month to see comparisons.</p>
      </div>
    );
  }

  return (
    <div className="mb-4 bg-white border border-slate-200 rounded-xl overflow-hidden">
      {/* Header */}
      <div className="px-5 py-3 bg-slate-50 border-b border-slate-200">
        <h4 className="text-sm font-semibold text-slate-800 flex items-center gap-2">
          <BarChart3 size={16} className="text-indigo-500" />
          Month-over-Month Comparison
        </h4>
      </div>

      <div className="p-5">
        {/* Two-column comparison cards */}
        <div className="grid grid-cols-2 gap-4 mb-5">
          {/* Current Month */}
          <div className="bg-indigo-50/50 border border-indigo-100 rounded-xl p-4">
            <p className="text-xs font-semibold text-indigo-600 uppercase tracking-wide mb-3">{MONTH_NAMES[month - 1]} {year} (Current)</p>
            <div className="space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-600">Total Net Salary</span>
                <span className="text-sm font-bold text-slate-900">{fmt(currentTotal)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-600">Staff Paid</span>
                <span className="text-sm font-bold text-slate-900">{currentStaffCount}</span>
              </div>
              {newJoiners.length > 0 && (
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-600">New Joiners</span>
                  <span className="text-sm font-medium text-green-600">+{newJoiners.length}</span>
                </div>
              )}
            </div>
          </div>

          {/* Previous Month */}
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">{MONTH_NAMES[prevMonth - 1]} {prevYear} (Previous)</p>
            {prevPayslips.length === 0 ? (
              <p className="text-xs text-slate-400 italic">No payroll data available</p>
            ) : (
              <div className="space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-600">Total Net Salary</span>
                  <span className="text-sm font-bold text-slate-900">{fmt(prevTotal)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-600">Staff Paid</span>
                  <span className="text-sm font-bold text-slate-900">{prevStaffCount}</span>
                </div>
                {staffLeft.length > 0 && (
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-600">Staff Left</span>
                    <span className="text-sm font-medium text-red-600">-{staffLeft.length}</span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Delta indicators */}
        {prevPayslips.length > 0 && (
          <div className="grid grid-cols-3 gap-3 mb-5">
            <div className={`flex items-center gap-2 p-3 rounded-lg border ${salaryDelta >= 0 ? 'bg-red-50/50 border-red-100' : 'bg-green-50/50 border-green-100'}`}>
              {salaryDelta >= 0 ? <ArrowUpRight size={16} className="text-red-500" /> : <ArrowDownRight size={16} className="text-green-500" />}
              <div>
                <p className="text-[10px] text-slate-500 uppercase">Salary Change</p>
                <p className={`text-sm font-bold ${salaryDelta >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                  {salaryDelta >= 0 ? '+' : ''}{fmt(salaryDelta)} ({salaryDelta >= 0 ? '+' : ''}{salaryDeltaPercent}%)
                </p>
              </div>
            </div>
            <div className={`flex items-center gap-2 p-3 rounded-lg border ${newJoiners.length > 0 ? 'bg-green-50/50 border-green-100' : 'bg-slate-50 border-slate-200'}`}>
              {newJoiners.length > 0 ? <TrendingUp size={16} className="text-green-500" /> : <span className="w-4 h-4" />}
              <div>
                <p className="text-[10px] text-slate-500 uppercase">New Joiners</p>
                <p className="text-sm font-bold text-slate-800">{newJoiners.length} staff</p>
              </div>
            </div>
            <div className={`flex items-center gap-2 p-3 rounded-lg border ${staffLeft.length > 0 ? 'bg-amber-50/50 border-amber-100' : 'bg-slate-50 border-slate-200'}`}>
              {staffLeft.length > 0 ? <TrendingDown size={16} className="text-amber-500" /> : <span className="w-4 h-4" />}
              <div>
                <p className="text-[10px] text-slate-500 uppercase">Staff Left</p>
                <p className="text-sm font-bold text-slate-800">{staffLeft.length} staff</p>
              </div>
            </div>
          </div>
        )}

        {/* Trend chart from history */}
        {trendData.length >= 2 && (
          <div>
            <p className="text-xs font-semibold text-slate-600 mb-3">Salary Trend (All Months)</p>
            <div className="h-48 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={trendData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="period" tick={{ fontSize: 10, fill: '#64748b' }} />
                  <YAxis tick={{ fontSize: 10, fill: '#64748b' }} tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`} />
                  <Tooltip
                    contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e2e8f0' }}
                    formatter={(value, name) => [`₹${Number(value).toLocaleString('en-IN')}`, name === 'total_salary' ? 'Net Salary' : 'Paid']}
                    labelStyle={{ fontWeight: 600 }}
                  />
                  <Legend
                    wrapperStyle={{ fontSize: 11 }}
                    formatter={(value) => value === 'total_salary' ? 'Net Salary' : 'Disbursed'}
                  />
                  <Bar dataKey="total_salary" fill="#6366f1" radius={[3, 3, 0, 0]} name="total_salary" />
                  <Bar dataKey="total_paid" fill="#22c55e" radius={[3, 3, 0, 0]} name="total_paid" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* New joiner / left staff details */}
        {(newJoiners.length > 0 || staffLeft.length > 0) && prevPayslips.length > 0 && (
          <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-slate-100">
            {newJoiners.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-green-700 mb-2">New Joiners This Month</p>
                <div className="space-y-1">
                  {newJoiners.slice(0, 5).map((p, i) => (
                    <div key={i} className="flex items-center justify-between text-xs px-2 py-1.5 bg-green-50 rounded">
                      <span className="text-slate-700">{p.employee_name}</span>
                      <span className="text-green-600 font-medium">{fmt(p.net_salary)}</span>
                    </div>
                  ))}
                  {newJoiners.length > 5 && <p className="text-[10px] text-slate-400 pl-2">+{newJoiners.length - 5} more</p>}
                </div>
              </div>
            )}
            {staffLeft.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-red-700 mb-2">Staff Left (in previous, not in current)</p>
                <div className="space-y-1">
                  {staffLeft.slice(0, 5).map((p, i) => (
                    <div key={i} className="flex items-center justify-between text-xs px-2 py-1.5 bg-red-50 rounded">
                      <span className="text-slate-700">{p.employee_name}</span>
                      <span className="text-red-600 font-medium">{fmt(p.net_salary)}</span>
                    </div>
                  ))}
                  {staffLeft.length > 5 && <p className="text-[10px] text-slate-400 pl-2">+{staffLeft.length - 5} more</p>}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function PayrollHistoryModal({ onClose }) {
  const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const { data } = useQuery({
    queryKey: ['payroll-history'],
    queryFn: () => api.get(ENDPOINTS.payroll.history).then(r => r.data),
  });
  const history = data?.history || [];
  const fmt = (v) => `₹${Number(v || 0).toLocaleString('en-IN')}`;

  const totalSalary = history.reduce((s, h) => s + Number(h.total_salary || 0), 0);
  const totalPaid = history.reduce((s, h) => s + Number(h.total_paid || 0), 0);
  const totalPending = totalSalary - totalPaid;
  const monthsProcessed = history.length;
  const allPaidMonths = history.filter(h => h.paid_count === h.total_staff).length;

  return (
    <Modal open onClose={onClose} title="Payroll History — Academic Year" size="full">
      <div className="max-h-[75vh] overflow-y-auto overflow-x-auto">
        {history.length === 0 ? (
          <p className="text-center text-slate-500 py-8">No payroll history found.</p>
        ) : (<>
          <div className="grid grid-cols-5 gap-3 mb-5">
            <div className="bg-indigo-50 border border-indigo-200 rounded-xl p-4 text-center">
              <p className="text-[10px] font-medium text-indigo-600 uppercase">Months Processed</p>
              <p className="text-xl font-bold text-indigo-900">{monthsProcessed}</p>
              <p className="text-[10px] text-indigo-500">{allPaidMonths} fully paid</p>
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-center">
              <p className="text-[10px] font-medium text-blue-600 uppercase">Total Payroll (Year)</p>
              <p className="text-xl font-bold text-blue-900">{fmt(totalSalary)}</p>
            </div>
            <div className="bg-green-50 border border-green-200 rounded-xl p-4 text-center">
              <p className="text-[10px] font-medium text-green-600 uppercase">Total Disbursed</p>
              <p className="text-xl font-bold text-green-700">{fmt(totalPaid)}</p>
              <p className="text-[10px] text-green-500">{totalSalary > 0 ? Math.round(totalPaid / totalSalary * 100) : 0}% of total</p>
            </div>
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-center">
              <p className="text-[10px] font-medium text-amber-600 uppercase">Total Pending</p>
              <p className="text-xl font-bold text-amber-700">{fmt(totalPending)}</p>
              <p className="text-[10px] text-amber-500">{totalSalary > 0 ? Math.round(totalPending / totalSalary * 100) : 0}% of total</p>
            </div>
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-center">
              <p className="text-[10px] font-medium text-slate-500 uppercase">Avg Monthly Cost</p>
              <p className="text-xl font-bold text-slate-900">{fmt(monthsProcessed > 0 ? Math.round(totalSalary / monthsProcessed) : 0)}</p>
            </div>
          </div>
          <table className="w-full text-sm">
            <thead className="bg-slate-50 sticky top-0">
              <tr>
                <th className="text-left px-3 py-2 font-medium text-slate-600">Period</th>
                <th className="text-center px-3 py-2 font-medium text-slate-600">Staff</th>
                <th className="text-right px-3 py-2 font-medium text-slate-600">Total Salary</th>
                <th className="text-right px-3 py-2 font-medium text-slate-600">Total Paid</th>
                <th className="text-center px-3 py-2 font-medium text-slate-600">Status</th>
                <th className="text-right px-3 py-2 font-medium text-slate-600">Processed On</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {history.map((h, i) => {
                const allPaid = h.paid_count === h.total_staff;
                const pending = h.total_salary - h.total_paid;
                return (
                  <tr key={i} className="hover:bg-slate-50">
                    <td className="px-3 py-2.5 font-medium text-slate-800">{MONTHS[h.month - 1]} {h.year}</td>
                    <td className="px-3 py-2.5 text-center">{h.total_staff}</td>
                    <td className="px-3 py-2.5 text-right">{fmt(h.total_salary)}</td>
                    <td className="px-3 py-2.5 text-right text-green-700 font-medium">{fmt(h.total_paid)}</td>
                    <td className="px-3 py-2.5 text-center">
                      {allPaid ? <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">All Paid</span> : <span className="text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full">Pending: {fmt(pending)}</span>}
                    </td>
                    <td className="px-3 py-2.5 text-right text-slate-500 text-xs">{h.processed_on ? new Date(h.processed_on).toLocaleDateString('en-IN') : '-'}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </>)}
      </div>
    </Modal>
  );
}
