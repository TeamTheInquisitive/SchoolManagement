import { useState } from 'react';
import { useDebounceValue } from 'usehooks-ts';
import { Download, DollarSign, CheckCircle, AlertCircle, TrendingUp, Send, History, Receipt, Printer, Clock, Eye, CreditCard, Pencil, Trash2 } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { useFees, useRecordPayment, useBulkRecordPayment, useSendReminder, useBulkApplyLateFees, useGenerateDue, useCreateFeeRecord, useUpdateFeeRecord, useDeleteFeeRecord, exportFeeCsv } from '../../services/feeService';
import { useClassSectionFilter } from '../../hooks/useClassSectionFilter';
import api from '../../services/api';
import { ENDPOINTS } from '../../config/api';
import { Button, Badge, Modal, SearchableSelect, useToast, exportToCsv, generateFeeReceipt, useSortableData, Breadcrumb, HoverCard, usePagination, DataTable, DatePicker , AnimatedNumber } from 'school-erp-ui-shared';

export default function FeeManagementPage() {
  const toast = useToast();
  const [search, setSearch] = useState('');
  const [debouncedSearch] = useDebounceValue(search, 300);
  const [statusFilter, setStatusFilter] = useState('');
  const { selectedClass: classFilter, selectedSection: sectionFilter, setSelectedClass: setClassFilter, setSelectedSection: setSectionFilter, classOptions, sectionOptions } = useClassSectionFilter();
  const [paymentDialog, setPaymentDialog] = useState(null);
  const [paymentAmount, setPaymentAmount] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('Online');
  const [paymentRemarks, setPaymentRemarks] = useState('');
  const [selectedIds, setSelectedIds] = useState([]);
  const [historyFee, setHistoryFee] = useState(null);
  const [viewFeeStudent, setViewFeeStudent] = useState(null);
  const [receiptFee, setReceiptFee] = useState(null);
  const [receiptPayment, setReceiptPayment] = useState(null);
  const pagination = usePagination(20, "admin-fees");

  const { data: feesData, isLoading, isFetching, isError, refetch } = useFees({ ...pagination.params, search: debouncedSearch || undefined, status: statusFilter || undefined, class_name: classFilter || undefined, section: sectionFilter || undefined });
  const recordPaymentMutation = useRecordPayment();
  const sendReminderMutation = useSendReminder();
  const bulkLateFeeMutation = useBulkApplyLateFees();
  const generateDueMutation = useGenerateDue();
  const [generateDueDialog, setGenerateDueDialog] = useState(false);
  const [confirmLateFee, setConfirmLateFee] = useState(false);

  const fees = Array.isArray(feesData?.results) ? feesData.results : [];
  const { sortedData, sortConfig, requestSort } = useSortableData(fees);
  const summary = feesData?.summary || {};
  const totalFees = Math.round(Number(summary.total_fees || 0) || fees.reduce((s, f) => s + Number(f.total_amount || 0), 0));
  const collected = Math.round(Number(summary.collected || 0) || fees.reduce((s, f) => s + Number(f.paid || 0), 0));
  const pending = Math.round(Number(summary.pending || 0) || totalFees - collected);
  const collectionRate = summary.collection_rate ?? (totalFees > 0 ? ((collected / totalFees) * 100).toFixed(1) : '0.0');

  const handleRecordPayment = () => {
    if (!paymentDialog || !paymentAmount) return;
    const data = { amount: Number(paymentAmount), payment_method: paymentMethod };
    if (paymentRemarks.trim()) data.reference = paymentRemarks.trim();
    if (!paymentDialog?.id) { toast.error('No fee record selected'); setPaymentDialog(null); return; }
    recordPaymentMutation.mutate({ id: paymentDialog.id, data }, { onSuccess: () => { setPaymentDialog(null); setPaymentAmount(''); setPaymentMethod('Online'); setPaymentRemarks(''); toast.success('Payment recorded successfully'); }, onError: (err) => { toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to record payment'); } });
  };

  const handleExportCsv = async () => {
    try {
      const blob = await exportFeeCsv();
      const url = URL.createObjectURL(new Blob([blob]));
      const a = document.createElement('a');
      a.href = url;
      a.download = 'fee-records.csv';
      a.click();
      URL.revokeObjectURL(url);
      toast.success('CSV exported successfully');
    } catch {
      const headers = ['Student', 'Class', 'Section', 'Fee Type', 'Total', 'Paid', 'Pending', 'Due Date', 'Status'];
      const rows = fees.map(f => [f.student_name, f.class_name, f.section, f.fee_type, f.total_amount, f.paid_amount, f.pending_amount, f.due_date, f.status]);
      exportToCsv('fee-records', headers, rows);
      toast.success('CSV exported successfully');
    }
  };

  if (isError) return <div><div className="mb-6"><h1 className="text-2xl font-bold text-slate-800">Fee Management</h1></div><div className="text-center py-8 text-slate-400">Failed to load fee data. Please try again.</div></div>;

  const kpis = [
    { label: 'Total Fees', value: `₹${totalFees.toLocaleString()}`, icon: DollarSign, color: 'text-emerald-600', bg: 'bg-gradient-to-br from-emerald-50 to-emerald-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(16,185,129,0.3)]' },
    { label: 'Collected', value: `₹${collected.toLocaleString()}`, icon: CheckCircle, color: 'text-green-600', bg: 'bg-gradient-to-br from-green-50 to-green-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(34,197,94,0.3)]' },
    { label: 'Pending', value: `₹${pending.toLocaleString()}`, icon: AlertCircle, color: 'text-red-600', bg: 'bg-gradient-to-br from-red-50 to-red-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(239,68,68,0.3)]' },
    { label: 'Collection Rate', value: `${collectionRate}%`, icon: TrendingUp, color: 'text-purple-600', bg: 'bg-gradient-to-br from-purple-50 to-purple-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(147,51,234,0.3)]' },
  ];

  const checkboxClass = "w-5 h-5 rounded-md border-2 border-slate-300 text-primary-500 appearance-none cursor-pointer transition-all duration-200 checked:bg-primary-500 checked:border-primary-500 checked:bg-[url('data:image/svg+xml,%3Csvg%20viewBox%3D%220%200%2016%2016%22%20fill%3D%22white%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cpath%20d%3D%22M12.207%204.793a1%201%200%20010%201.414l-5%205a1%201%200%2001-1.414%200l-2-2a1%201%200%20011.414-1.414L6.5%209.086l4.293-4.293a1%201%200%20011.414%200z%22%2F%3E%3C%2Fsvg%3E')] checked:bg-center checked:bg-no-repeat hover:border-primary-400 hover:shadow-sm focus:ring-2 focus:ring-primary-500/30 focus:ring-offset-1";

  const columns = [
    {
      key: 'checkbox', label: '',
      render: (f) => f.status !== 'paid' ? <input type="checkbox" checked={selectedIds.includes(f.student_id)} onChange={e => setSelectedIds(e.target.checked ? [...selectedIds, f.student_id] : selectedIds.filter(id => id !== f.student_id))} className={checkboxClass} /> : null,
    },
    {
      key: 'student_name', label: 'Student', sortable: true,
      render: (f) => (
        <HoverCard content={
          <div>
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-indigo-700 text-white flex items-center justify-center text-sm font-bold">{(f.student_name || '').slice(0, 2).toUpperCase()}</div>
              <div>
                <p className="text-sm font-bold text-slate-900">{f.student_name}</p>
                <p className="text-xs text-slate-500">{f.class_name ? `Class ${f.class_name}` : ''}{f.roll_number ? ` • Roll: ${f.roll_number}` : ''}</p>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="bg-slate-50 rounded-lg p-2"><p className="text-xs text-slate-400">Total Fee</p><p className="text-sm font-bold text-slate-900">{'₹'}{(f.total_amount || 0).toLocaleString()}</p></div>
              <div className="bg-slate-50 rounded-lg p-2"><p className="text-xs text-slate-400">Paid</p><p className="text-sm font-bold text-emerald-600">{'₹'}{(f.total_paid || 0).toLocaleString()}</p></div>
              <div className="bg-slate-50 rounded-lg p-2"><p className="text-xs text-slate-400">Pending</p><p className="text-sm font-bold text-red-600">{'₹'}{(f.total_pending || 0).toLocaleString()}</p></div>
            </div>
          </div>
        }>
          <a href={`/admin/students/${f.student_id}`} className="font-medium text-primary-600 hover:text-primary-700 hover:underline transition-colors">{f.student_name || ''}</a>
        </HoverCard>
      ),
    },
    { key: 'class_name', label: 'Class', render: (f) => <span className="text-slate-500">{f.class_name || ''}{f.section ? `-${f.section}` : ''}</span> },
    { key: 'components_count', label: 'Components', render: (f) => <span className="text-slate-500">{f.components_count || 0} items</span> },
    { key: 'total_amount', label: 'Total', sortable: true, render: (f) => `₹${(f.total_amount || 0).toLocaleString()}` },
    { key: 'total_paid', label: 'Paid', render: (f) => {
      const paidPct = (f.total_amount || 0) > 0 ? ((f.total_paid || 0) / (f.total_amount || 1)) * 100 : 0;
      return (
        <div>
          <span>{`₹${(f.total_paid || 0).toLocaleString()}`}</span>
          <div className="w-16 h-1.5 bg-slate-100 rounded-full overflow-hidden mt-1">
            <div className={`h-full rounded-full ${paidPct >= 100 ? 'bg-emerald-500' : paidPct >= 50 ? 'bg-blue-500' : 'bg-amber-500'}`} style={{ width: `${Math.min(paidPct, 100)}%` }} />
          </div>
        </div>
      );
    } },
    { key: 'total_pending', label: 'Pending', render: (f) => <span className={(f.total_pending || 0) > 0 ? 'text-red-600' : 'text-green-600'}>{'₹'}{(f.total_pending || 0).toLocaleString()}</span> },
    { key: 'status', label: 'Status', sortable: true, render: (f) => <Badge status={f.status || 'pending'} /> },
    {
      key: 'actions', label: 'Actions',
      render: (f) => (
        <div className="flex gap-1">
          <button onClick={() => setViewFeeStudent(f)} className="p-1.5 rounded-lg text-slate-400 hover:text-blue-600 hover:bg-blue-50 transition-all duration-150 active:scale-[0.97]" title="View Details"><Eye size={15} /></button>
          {f.status !== 'Paid' && Number(f.total_pending || 0) > 0 && <Button variant="primary" size="sm" onClick={() => setViewFeeStudent(f)}>Record</Button>}
          <button onClick={() => setHistoryFee(f)} className="p-1.5 rounded-lg text-slate-400 hover:text-amber-600 hover:bg-amber-50 transition-all duration-150 active:scale-[0.97]" title="Payment History"><History size={15} /></button>
          <button onClick={() => setReceiptFee(f)} className="p-1.5 rounded-lg text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 transition-all duration-150 active:scale-[0.97]" title="View Receipt"><Receipt size={15} /></button>
        </div>
      ),
    },
  ];

  return (
    <div>
      <Breadcrumb items={[{ label: 'Dashboard', href: '/admin/dashboard' }, { label: 'Fee Management' }]} />
      <div className="flex justify-between items-center mb-6">
        <div><h1 className="text-2xl md:text-3xl font-bold text-slate-900">Fee Management</h1><p className="text-sm text-slate-500 mt-1">Track and manage student fee payments</p></div>
        <div className="flex gap-2">
          <Button variant="secondary" icon={Send} onClick={() => sendReminderMutation.mutate(selectedIds.length > 0 ? { target_group: 'Selected', student_ids: selectedIds, message: 'This is a reminder that your fee payment is overdue. Please clear the dues at the earliest.', send_via: 'in_app' } : { target_group: 'Overdue', message: 'This is a reminder that your fee payment is overdue. Please clear the dues at the earliest.', send_via: 'in_app' }, { onSuccess: () => { setSelectedIds([]); toast.success('Reminders sent successfully'); }, onError: (err) => { toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to send reminders'); } })}>{selectedIds.length > 0 ? `Send Reminder (${selectedIds.length})` : 'Send Reminders (All Overdue)'}</Button>
          {/* <Button variant="secondary" disabled={selectedIds.length === 0} onClick={() => setGenerateDueDialog(true)}>{selectedIds.length > 0 ? `Generate Due (${selectedIds.length})` : 'Generate Due'}</Button> */}
          <Button variant="secondary" onClick={() => setConfirmLateFee(true)}>Apply Late Fee</Button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mb-4">
        {kpis.map(k => (
          <div key={k.label} className={`bg-white border border-slate-200 rounded-xl p-4 md:p-5 flex items-center gap-3 md:gap-4 transition-all duration-200 hover:-translate-y-1 ${k.glow} cursor-default group`}>
            <div className={`${k.bg} p-2.5 md:p-3 rounded-xl transition-transform duration-200 group-hover:scale-110`}><k.icon className={`w-5 h-5 ${k.color}`} /></div>
            <div><p className="text-xs text-slate-500 font-medium">{k.label}</p><p className="text-xl md:text-2xl font-bold text-slate-900 mt-0.5"><AnimatedNumber value={k.value} id={k.label} /></p></div>
          </div>
        ))}
      </div>

      <DataTable
        columns={columns}
        data={sortedData}
        loading={isFetching}
        emptyMessage="No fee records found. Try adjusting your filters."
        emptyIcon={DollarSign}
        headerTitle="Fee Records"
        headerCount={feesData?.count || 0}
        headerExtra={<Button variant="secondary" size="sm" icon={Download} onClick={handleExportCsv}>Export CSV</Button>}
        search={{ value: search, onChange: (v) => { setSearch(v); pagination.reset(); }, placeholder: 'Search fee records...' }}
        filters={[
          { key: 'status', value: statusFilter, onChange: (v) => { setStatusFilter(v); pagination.reset(); }, options: [{ value: '', label: 'All Status' }, { value: 'paid', label: 'Paid' }, { value: 'partial', label: 'Partial' }, { value: 'pending', label: 'Pending' }, { value: 'overdue', label: 'Overdue' }] },
          { key: 'class', value: classFilter, onChange: (v) => { setClassFilter(v); pagination.reset(); }, options: classOptions },
          { key: 'section', value: sectionFilter, onChange: (v) => { setSectionFilter(v); pagination.reset(); }, options: sectionOptions },
        ]}
        sortConfig={sortConfig}
        onSort={requestSort}
        page={pagination.page}
        totalPages={feesData?.total_pages || 1}
        totalCount={feesData?.count || 0}
        pageSize={pagination.pageSize}
        onPageChange={(p) => pagination.setPage(p)}
        onPageSizeChange={pagination.setPageSize}
      />

      {/* Payment Modal */}
      <Modal open={!!paymentDialog} onClose={() => { setPaymentDialog(null); setPaymentAmount(''); setPaymentMethod('Online'); setPaymentRemarks(''); }} title="Record Payment">
        {paymentDialog && (
          <div className="space-y-4">
            {/* Student Info */}
            <div className="bg-slate-50 rounded-xl p-4 grid grid-cols-2 gap-3">
              <div><p className="text-[11px] text-slate-400">Student</p><p className="text-sm font-semibold text-slate-900">{paymentDialog.student_name}</p></div>
              <div><p className="text-[11px] text-slate-400">Class & Section</p><p className="text-sm font-semibold text-slate-900">{paymentDialog.class_name}{paymentDialog.section ? `-${paymentDialog.section}` : ''}</p></div>
              <div><p className="text-[11px] text-slate-400">Total Amount</p><p className="text-sm font-bold text-slate-900">₹{(paymentDialog.total_amount || 0).toLocaleString()}</p></div>
              <div><p className="text-[11px] text-slate-400">Pending Amount</p><p className="text-sm font-bold text-red-600">₹{(paymentDialog.pending_amount || 0).toLocaleString()}</p></div>
            </div>

            {/* Amount */}
            {(() => {
              const maxPayable = Number(paymentDialog.pending_amount || 0) || (Number(paymentDialog.total_amount || 0) - Number(paymentDialog.paid_amount || 0));
              return (
                <div>
                  <label className="text-sm font-medium text-slate-700 mb-1.5 block">Payment Amount *</label>
                  <input type="number" value={paymentAmount} onChange={e => { if (e.target.value === '' || Number(e.target.value) <= maxPayable) setPaymentAmount(e.target.value); }} className="w-full border border-slate-300 rounded-lg px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400" placeholder="Enter amount" />
                  <p className="text-xs text-slate-400 mt-1">Maximum: ₹{maxPayable.toLocaleString()}</p>
                </div>
              );
            })()}

            {/* Payment Method */}
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1.5 block">Payment Method</label>
              <div className="flex gap-2">
                {['Online', 'Cash', 'Cheque', 'UPI', 'Bank Transfer'].map(m => (
                  <button key={m} onClick={() => setPaymentMethod(m)} className={`px-3 py-1.5 text-xs font-medium rounded-lg border transition-all duration-150 ${paymentMethod === m ? 'bg-primary-50 border-primary-300 text-primary-700' : 'border-slate-200 text-slate-500 hover:border-slate-300'}`}>{m}</button>
                ))}
              </div>
            </div>

            {/* Remarks */}
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1.5 block">Remarks (optional)</label>
              <textarea value={paymentRemarks} onChange={e => setPaymentRemarks(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400 min-h-[70px]" placeholder="e.g. Cheque No. 123456, Paid for Term 2..." />
            </div>
          </div>
        )}
        <div className="flex justify-end gap-2 mt-5 pt-4 border-t border-slate-100">
          <Button variant="ghost" onClick={() => { setPaymentDialog(null); setPaymentAmount(''); setPaymentMethod('Online'); setPaymentRemarks(''); }}>Cancel</Button>
          <Button variant="primary" onClick={handleRecordPayment} disabled={!paymentAmount || Number(paymentAmount) <= 0} loading={recordPaymentMutation.isPending}>Record Payment</Button>
        </div>
      </Modal>

      {/* Payment History Modal */}
      <Modal open={!!historyFee} onClose={() => setHistoryFee(null)} title="Payment History" size="lg">
        {historyFee && <PaymentHistoryModal fee={historyFee} onViewReceipt={(payment) => { setReceiptPayment(payment); setReceiptFee(historyFee); setHistoryFee(null); }} />}
      </Modal>

      {/* Receipt Modal */}
      <Modal open={!!receiptFee} onClose={() => { setReceiptFee(null); setReceiptPayment(null); }} title="Fee Receipt" size="md">
        {receiptFee && <ReceiptModal fee={receiptFee} payment={receiptPayment} />}
      </Modal>

      {/* Generate Due Modal */}
      <Modal open={generateDueDialog} onClose={() => setGenerateDueDialog(false)} title="Generate Fee Due" size="md">
        {generateDueDialog && <GenerateDueForm onClose={() => { setGenerateDueDialog(false); setSelectedIds([]); }} generateDueMutation={generateDueMutation} toast={toast} studentIds={selectedIds} studentCount={selectedIds.length} />}
      </Modal>

      {/* View Fee Details Modal */}
      <Modal open={!!viewFeeStudent} onClose={() => { setViewFeeStudent(null); refetch(); }} title={`Fee Details - ${viewFeeStudent?.student_name || ''}`} size="3xl">
        {viewFeeStudent && <StudentFeeDetailView studentId={viewFeeStudent.student_id} />}
      </Modal>

      {/* Bulk Late Fee Confirmation Modal */}
      <Modal open={confirmLateFee} onClose={() => setConfirmLateFee(false)} title="Confirm Apply Late Fee">
        <div className="space-y-4">
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
            <p className="text-sm text-amber-800">
              Apply late fee penalty to <span className="font-semibold">{fees.filter(f => f.status === 'overdue' || f.status === 'Overdue').length || 'all'}</span> students with overdue payments?
            </p>
          </div>
          <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
            <Button variant="ghost" onClick={() => setConfirmLateFee(false)}>Cancel</Button>
            <Button
              variant="primary"
              disabled={bulkLateFeeMutation.isPending}
              onClick={() => {
                bulkLateFeeMutation.mutate({ penalty_type: 'fixed', amount: 100, apply_to: 'all_overdue' }, {
                  onSuccess: () => { setConfirmLateFee(false); toast.success('Late fees applied successfully'); },
                  onError: (err) => { setConfirmLateFee(false); toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to apply late fees'); },
                });
              }}
            >
              {bulkLateFeeMutation.isPending ? 'Applying...' : 'Confirm Apply Late Fee'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

function StudentFeeDetailView({ studentId }) {
  const toast = useToast();
  const [payingFee, setPayingFee] = useState(null);
  const [payAmount, setPayAmount] = useState('');
  const [payMethod, setPayMethod] = useState('Cash');
  const [payRemarks, setPayRemarks] = useState('');
  const [bulkPayMode, setBulkPayMode] = useState(false);
  const [bulkAmount, setBulkAmount] = useState('');
  const [bulkMethod, setBulkMethod] = useState('Cash');
  const [bulkRemarks, setBulkRemarks] = useState('');
  const [addFeeMode, setAddFeeMode] = useState(false);
  const [newFee, setNewFee] = useState({ fee_type: '', fee_category: 'academic', total_amount: '', due_date: '', description: '' });
  const [addFeeErrors, setAddFeeErrors] = useState({});
  const recordPaymentMutation = useRecordPayment();
  const bulkRecordPaymentMutation = useBulkRecordPayment();
  const createFeeRecordMutation = useCreateFeeRecord();
  const updateFeeRecordMutation = useUpdateFeeRecord();
  const deleteFeeRecordMutation = useDeleteFeeRecord();
  const [editingFee, setEditingFee] = useState(null);
  const [editAmount, setEditAmount] = useState('');
  const [deletingFee, setDeletingFee] = useState(null);

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['student-fee-detail', studentId],
    queryFn: () => api.get(ENDPOINTS.fees.student(studentId)).then(r => r.data),
    enabled: !!studentId,
  });

  if (isLoading) return <div className="py-8 text-center text-slate-400">Loading...</div>;

  const records = data?.records || [];
  const totalAmount = records.reduce((s, r) => s + Number(r.total_amount || 0), 0);
  const totalPaid = records.reduce((s, r) => s + Number(r.paid || 0), 0);
  const totalPending = records.reduce((s, r) => s + Number(r.pending || 0), 0);
  const pendingRecords = records.filter(r => r.status?.toLowerCase() !== 'paid' && Number(r.pending || 0) > 0);

  const handleRecordPayment = () => {
    if (!payingFee || !payAmount) return;
    const payData = { amount: Number(payAmount), payment_method: payMethod };
    if (payRemarks.trim()) payData.reference = payRemarks.trim();
    recordPaymentMutation.mutate({ id: payingFee.id, data: payData }, {
      onSuccess: () => { setPayingFee(null); setPayAmount(''); setPayRemarks(''); toast.success('Payment recorded successfully'); refetch(); },
      onError: (err) => { toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to record payment'); },
    });
  };

  const handleBulkPayment = () => {
    if (!bulkAmount || Number(bulkAmount) <= 0) return;
    const payData = { amount: Number(bulkAmount), payment_method: bulkMethod };
    if (bulkRemarks.trim()) payData.reference = bulkRemarks.trim();
    bulkRecordPaymentMutation.mutate({ studentId, data: payData }, {
      onSuccess: (res) => {
        toast.success(res?.message || `Payment recorded for ${res?.components_paid || 0} component(s)`);
        setBulkPayMode(false);
        setBulkAmount('');
        setBulkRemarks('');
        refetch();
      },
      onError: (err) => { toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to record payment'); },
    });
  };

  const handleAddFee = () => {
    const errs = {};
    if (!newFee.fee_type.trim()) errs.fee_type = 'Fee type is required';
    if (!newFee.total_amount || Number(newFee.total_amount) <= 0) errs.total_amount = 'Amount must be greater than 0';
    if (!newFee.due_date) errs.due_date = 'Due date is required';
    setAddFeeErrors(errs);
    if (Object.keys(errs).length > 0) return;

    const payload = {
      student_id: studentId,
      fee_type: newFee.fee_type.trim(),
      fee_category: newFee.fee_category || 'academic',
      total_amount: Number(newFee.total_amount),
      due_date: newFee.due_date,
    };
    if (newFee.description.trim()) payload.description = newFee.description.trim();

    createFeeRecordMutation.mutate(payload, {
      onSuccess: () => {
        toast.success('Fee component added successfully');
        setAddFeeMode(false);
        setNewFee({ fee_type: '', fee_category: 'academic', total_amount: '', due_date: '', description: '' });
        setAddFeeErrors({});
        refetch();
      },
      onError: (err) => {
        toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to add fee component');
      },
    });
  };

  // Compute distribution preview
  const getDistributionPreview = (amount) => {
    const numAmount = Number(amount) || 0;
    if (numAmount <= 0) return [];
    let remaining = numAmount;
    return pendingRecords.map(r => {
      const componentPending = Number(r.pending || 0);
      const allocated = Math.min(remaining, componentPending);
      remaining -= allocated;
      return { ...r, allocated, willBePaid: allocated >= componentPending };
    }).filter(r => r.allocated > 0);
  };

  const distributionPreview = bulkPayMode ? getDistributionPreview(bulkAmount) : [];

  const PAYMENT_METHODS = [
    { value: 'Cash', label: 'Cash' },
    { value: 'Online', label: 'Online' },
    { value: 'UPI', label: 'UPI' },
    { value: 'Cheque', label: 'Cheque' },
    { value: 'Bank Transfer', label: 'Bank Transfer' },
  ];

  return (
    <div className="space-y-5">
      {/* Summary Cards */}
      <div className="grid grid-cols-3 gap-3">
        <div className="bg-white border border-slate-200 rounded-xl p-4 text-center">
          <p className="text-xs text-slate-400 font-medium">Total Fee</p>
          <p className="text-xl md:text-2xl font-bold text-slate-900 mt-1">₹{totalAmount.toLocaleString()}</p>
        </div>
        <div className="bg-white border border-emerald-200 rounded-xl p-4 text-center">
          <p className="text-xs text-emerald-500 font-medium">Paid</p>
          <p className="text-xl md:text-2xl font-bold text-emerald-600 mt-1">₹{totalPaid.toLocaleString()}</p>
        </div>
        <div className="bg-white border border-red-200 rounded-xl p-4 text-center">
          <p className="text-xs text-red-400 font-medium">Pending</p>
          <p className="text-xl md:text-2xl font-bold text-red-600 mt-1">₹{totalPending.toLocaleString()}</p>
        </div>
      </div>

      {/* Add Fee Component Button */}
      {!addFeeMode && (
        <div className="flex justify-end">
          <Button variant="secondary" size="sm" onClick={() => setAddFeeMode(true)}>+ Add Fee Component</Button>
        </div>
      )}

      {/* Add Fee Component Form */}
      {addFeeMode && (
        <div className="bg-white border border-slate-200 rounded-xl p-5 space-y-4 shadow-sm">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-semibold text-slate-900">Add Fee Component</h3>
            <button onClick={() => { setAddFeeMode(false); setAddFeeErrors({}); setNewFee({ fee_type: '', fee_category: 'academic', total_amount: '', due_date: '', description: '' }); }} className="text-slate-400 hover:text-slate-600 text-sm font-medium transition-colors">Cancel</button>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1.5 block">Fee Type *</label>
              <input type="text" value={newFee.fee_type} onChange={e => { setNewFee(f => ({ ...f, fee_type: e.target.value })); if (addFeeErrors.fee_type) setAddFeeErrors(er => ({ ...er, fee_type: '' })); }} placeholder="e.g. Tuition Fee, Lab Fee, Transport Fee..." className={`w-full border rounded-lg px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400 ${addFeeErrors.fee_type ? 'border-red-400' : 'border-slate-300'}`} />
              {addFeeErrors.fee_type && <p className="text-xs text-red-500 mt-0.5">{addFeeErrors.fee_type}</p>}
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1.5 block">Category</label>
              <select value={newFee.fee_category} onChange={e => setNewFee(f => ({ ...f, fee_category: e.target.value }))} className="w-full border border-slate-300 rounded-lg px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400">
                <option value="academic">Academic</option>
                <option value="transport">Transport</option>
                <option value="hostel">Hostel</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1.5 block">Amount *</label>
              <input type="number" value={newFee.total_amount} onChange={e => { setNewFee(f => ({ ...f, total_amount: e.target.value })); if (addFeeErrors.total_amount) setAddFeeErrors(er => ({ ...er, total_amount: '' })); }} placeholder="e.g. 5000" className={`w-full border rounded-lg px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400 ${addFeeErrors.total_amount ? 'border-red-400' : 'border-slate-300'}`} />
              {addFeeErrors.total_amount && <p className="text-xs text-red-500 mt-0.5">{addFeeErrors.total_amount}</p>}
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1.5 block">Due Date *</label>
              <DatePicker value={newFee.due_date} onChange={(v) => { setNewFee(f => ({ ...f, due_date: v })); if (addFeeErrors.due_date) setAddFeeErrors(er => ({ ...er, due_date: '' })); }} />
              {addFeeErrors.due_date && <p className="text-xs text-red-500 mt-0.5">{addFeeErrors.due_date}</p>}
            </div>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700 mb-1.5 block">Description <span className="text-slate-400 font-normal">(optional)</span></label>
            <input type="text" value={newFee.description} onChange={e => setNewFee(f => ({ ...f, description: e.target.value }))} placeholder="e.g. Additional lab fee for science stream" className="w-full border border-slate-300 rounded-lg px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400" />
          </div>
          <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
            <Button variant="ghost" onClick={() => { setAddFeeMode(false); setAddFeeErrors({}); setNewFee({ fee_type: '', fee_category: 'academic', total_amount: '', due_date: '', description: '' }); }}>Cancel</Button>
            <Button variant="primary" onClick={handleAddFee} loading={createFeeRecordMutation.isPending} disabled={!newFee.fee_type.trim() || !newFee.total_amount || !newFee.due_date}>Add Fee Component</Button>
          </div>
        </div>
      )}

      {/* All Paid Success */}
      {totalPending <= 0 && totalPaid > 0 && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-5 text-center">
          <div className="w-12 h-12 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-2">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6 text-emerald-600"><path fillRule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zm13.36-1.814a.75.75 0 10-1.22-.872l-3.236 4.53L9.53 12.22a.75.75 0 00-1.06 1.06l2.25 2.25a.75.75 0 001.14-.094l3.75-5.25z" clipRule="evenodd" /></svg>
          </div>
          <p className="text-sm font-semibold text-emerald-800">All Fees Paid</p>
          <p className="text-xs text-emerald-600 mt-0.5">Total paid: ₹{totalPaid.toLocaleString()}</p>
        </div>
      )}

      {/* Record Payment CTA */}
      {totalPending > 0 && !bulkPayMode && (
        <div className="bg-gradient-to-r from-primary-50 to-indigo-50 border border-primary-200 rounded-xl p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
              <CreditCard size={18} className="text-primary-600" />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-800">Record Payment</p>
              <p className="text-xs text-slate-500">Pay all or partial across {pendingRecords.length} pending component{pendingRecords.length !== 1 ? 's' : ''}</p>
            </div>
          </div>
          <Button variant="primary" onClick={() => { setBulkPayMode(true); setBulkAmount(String(totalPending)); }}>
            Record Payment
          </Button>
        </div>
      )}

      {/* Bulk Payment Panel */}
      {bulkPayMode && (
        <div className="bg-white border border-slate-200 rounded-xl p-5 space-y-5 shadow-sm">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-semibold text-slate-900 flex items-center gap-2">
              <CreditCard size={18} className="text-primary-600" />
              Record Payment
            </h3>
            <button onClick={() => setBulkPayMode(false)} className="text-slate-400 hover:text-slate-600 text-sm font-medium transition-colors">Cancel</button>
          </div>

          {/* Amount Input */}
          <div>
            <label className="text-sm font-medium text-slate-700 mb-2 block">Payment Amount</label>
            <div className="relative">
              <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-sm font-medium">₹</span>
              <input
                type="number"
                value={bulkAmount}
                onChange={e => { if (e.target.value === '' || Number(e.target.value) <= totalPending) setBulkAmount(e.target.value); }}
                className="w-full border border-slate-300 rounded-xl pl-8 pr-4 py-3 text-lg font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400"
                placeholder="0"
              />
            </div>
            <div className="flex items-center justify-between mt-2">
              <p className="text-xs text-slate-400">Maximum payable: ₹{totalPending.toLocaleString()}</p>
              {Number(bulkAmount) > 0 && Number(bulkAmount) < totalPending && (
                <button onClick={() => setBulkAmount(String(totalPending))} className="text-xs text-primary-600 hover:text-primary-700 font-medium transition-colors">Pay Full Amount</button>
              )}
            </div>
          </div>

          {/* Payment Method Chips */}
          <div>
            <label className="text-sm font-medium text-slate-700 mb-2 block">Payment Method</label>
            <div className="flex flex-wrap gap-2">
              {PAYMENT_METHODS.map(m => (
                <button
                  key={m.value}
                  onClick={() => setBulkMethod(m.value)}
                  className={`px-4 py-2 rounded-full border text-sm font-medium cursor-pointer transition-all duration-200 ${
                    bulkMethod === m.value
                      ? 'bg-primary-100 border-primary-400 text-primary-700 shadow-sm'
                      : 'border-slate-200 text-slate-600 hover:border-slate-300 hover:bg-slate-50'
                  }`}
                >
                  {m.label}
                </button>
              ))}
            </div>
          </div>

          {/* Reference/Transaction Number */}
          <div>
            <label className="text-sm font-medium text-slate-700 mb-2 block">Reference / Transaction No. <span className="text-slate-400 font-normal">(optional)</span></label>
            <input
              type="text"
              value={bulkRemarks}
              onChange={e => setBulkRemarks(e.target.value)}
              placeholder="e.g. TXN-123456, Cheque No. 789012"
              className="w-full border border-slate-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400"
            />
          </div>

          {/* Distribution Preview */}
          {distributionPreview.length > 0 && (
            <div>
              <label className="text-sm font-medium text-slate-700 mb-2 block">Payment Distribution</label>
              <div className="bg-slate-50 rounded-xl border border-slate-200 overflow-hidden">
                <div className="divide-y divide-slate-100">
                  {distributionPreview.map((r, i) => (
                    <div key={r.id || i} className="flex items-center justify-between px-4 py-2.5">
                      <div className="flex items-center gap-2">
                        {r.willBePaid ? (
                          <CheckCircle size={14} className="text-emerald-500" />
                        ) : (
                          <div className="w-3.5 h-3.5 rounded-full border-2 border-amber-400" />
                        )}
                        <span className="text-sm text-slate-700">{r.fee_type}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-xs text-slate-400">Due: ₹{Number(r.pending || 0).toLocaleString()}</span>
                        <span className={`text-sm font-semibold ${r.willBePaid ? 'text-emerald-600' : 'text-amber-600'}`}>
                          ₹{r.allocated.toLocaleString()}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="bg-slate-100 px-4 py-2.5 flex items-center justify-between border-t border-slate-200">
                  <span className="text-sm font-medium text-slate-600">Total</span>
                  <span className="text-sm font-bold text-slate-900">₹{Number(bulkAmount || 0).toLocaleString()}</span>
                </div>
              </div>
            </div>
          )}

          {/* Submit */}
          <div className="flex items-center justify-between pt-2 border-t border-slate-100">
            <div className="text-sm text-slate-500">
              {distributionPreview.length > 0 && (
                <span>Paying <span className="font-medium text-slate-700">{distributionPreview.length}</span> of {pendingRecords.length} components</span>
              )}
            </div>
            <div className="flex gap-2">
              <Button variant="ghost" onClick={() => setBulkPayMode(false)}>Cancel</Button>
              <Button
                variant="primary"
                onClick={handleBulkPayment}
                loading={bulkRecordPaymentMutation.isPending}
                disabled={!bulkAmount || Number(bulkAmount) <= 0}
              >
                Record Payment
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Fee Components Table */}
      <div className="rounded-xl border border-slate-200 overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200">
              <th className="text-left px-4 py-2.5 text-xs font-semibold text-slate-500">Fee Type</th>
              <th className="text-left px-4 py-2.5 text-xs font-semibold text-slate-500">Category</th>
              <th className="text-right px-4 py-2.5 text-xs font-semibold text-slate-500">Amount</th>
              <th className="text-right px-4 py-2.5 text-xs font-semibold text-slate-500">Paid</th>
              <th className="text-right px-4 py-2.5 text-xs font-semibold text-slate-500">Pending</th>
              <th className="text-left px-4 py-2.5 text-xs font-semibold text-slate-500">Status</th>
              <th className="text-left px-4 py-2.5 text-xs font-semibold text-slate-500">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {records.map((r, i) => (
              <tr key={r.id || i} className="hover:bg-slate-50/50">
                <td className="px-4 py-3 font-medium text-slate-800">{r.fee_type}</td>
                <td className="px-4 py-3 text-slate-500 capitalize">{r.fee_category}</td>
                <td className="px-4 py-3 text-right">₹{Number(r.total_amount || 0).toLocaleString()}</td>
                <td className="px-4 py-3 text-right text-green-600">₹{Number(r.paid || 0).toLocaleString()}</td>
                <td className="px-4 py-3 text-right text-red-600">₹{Number(r.pending || 0).toLocaleString()}</td>
                <td className="px-4 py-3"><Badge status={r.status} /></td>
                <td className="px-4 py-3">
                  <div className="flex gap-1">
                    {r.status?.toLowerCase() !== 'paid' && Number(r.pending || 0) > 0 && <Button size="sm" variant="primary" onClick={() => { setPayingFee(r); setPayAmount(String(Number(r.pending || 0))); }}>Pay</Button>}
                    {r.status?.toLowerCase() !== 'paid' && <button onClick={() => { setEditingFee(r); setEditAmount(String(Number(r.total_amount || 0))); }} className="p-1.5 rounded-lg text-slate-400 hover:text-primary-600 hover:bg-primary-50 transition-colors active:scale-[0.97]" title="Edit Amount"><Pencil size={14} /></button>}
                    {Number(r.paid || 0) === 0 && <button onClick={() => setDeletingFee(r)} className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors active:scale-[0.97]" title="Delete"><Trash2 size={14} /></button>}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Edit Fee Amount */}
      {editingFee && (
        <div className="bg-white border border-amber-200 rounded-xl p-5 space-y-4 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold text-slate-800">Edit Amount: <span className="text-primary-700">{editingFee.fee_type}</span></p>
            <button onClick={() => setEditingFee(null)} className="text-slate-400 hover:text-slate-600 text-sm font-medium transition-colors">Cancel</button>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-slate-50 rounded-lg p-2.5 text-center border border-slate-200"><p className="text-[10px] text-slate-400">Current Amount</p><p className="text-sm font-bold text-slate-900">₹{Number(editingFee.total_amount || 0).toLocaleString()}</p></div>
            <div className="bg-emerald-50 rounded-lg p-2.5 text-center border border-emerald-200"><p className="text-[10px] text-slate-400">Paid</p><p className="text-sm font-bold text-emerald-600">₹{Number(editingFee.paid || 0).toLocaleString()}</p></div>
            <div className="bg-red-50 rounded-lg p-2.5 text-center border border-red-200"><p className="text-[10px] text-slate-400">Pending</p><p className="text-sm font-bold text-red-600">₹{Number(editingFee.pending || 0).toLocaleString()}</p></div>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700 mb-2 block">New Total Amount</label>
            <div className="relative">
              <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-sm font-medium">₹</span>
              <input type="number" value={editAmount} onChange={e => setEditAmount(e.target.value)} className="w-full border border-slate-300 rounded-xl pl-8 pr-4 py-2.5 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400" />
            </div>
            {Number(editAmount) < Number(editingFee.paid || 0) && <p className="text-xs text-red-500 mt-1">Amount cannot be less than already paid (₹{Number(editingFee.paid || 0).toLocaleString()})</p>}
          </div>
          <div className="flex gap-2 pt-2 border-t border-slate-100 justify-end">
            <Button variant="ghost" onClick={() => setEditingFee(null)}>Cancel</Button>
            <Button variant="primary" onClick={() => {
              const newAmount = Number(editAmount);
              if (newAmount < Number(editingFee.paid || 0)) { toast.error('Amount cannot be less than already paid'); return; }
              updateFeeRecordMutation.mutate({ id: editingFee.id, data: { total_amount: newAmount } }, {
                onSuccess: () => { setEditingFee(null); toast.success('Fee amount updated'); refetch(); },
                onError: (err) => toast.error(err.response?.data?.error || 'Failed to update'),
              });
            }} disabled={!editAmount || Number(editAmount) <= 0 || Number(editAmount) < Number(editingFee.paid || 0)} loading={updateFeeRecordMutation.isPending}>Update Amount</Button>
          </div>
        </div>
      )}

      {/* Delete Fee Confirmation */}
      {deletingFee && (
        <div className="bg-white border border-red-200 rounded-xl p-5 space-y-3 shadow-sm">
          <p className="text-sm font-semibold text-red-800">Delete "{deletingFee.fee_type}" (₹{Number(deletingFee.total_amount || 0).toLocaleString()})?</p>
          <p className="text-xs text-slate-500">This will permanently remove this fee component. This action cannot be undone.</p>
          <div className="flex gap-2 justify-end">
            <Button variant="ghost" onClick={() => setDeletingFee(null)}>Cancel</Button>
            <Button variant="primary" className="!bg-red-600 hover:!bg-red-700" onClick={() => {
              deleteFeeRecordMutation.mutate(deletingFee.id, {
                onSuccess: () => { setDeletingFee(null); toast.success('Fee component deleted'); refetch(); },
                onError: (err) => toast.error(err.response?.data?.error || 'Failed to delete'),
              });
            }} loading={deleteFeeRecordMutation.isPending}>Delete</Button>
          </div>
        </div>
      )}

      {/* Individual Component Payment Form */}
      {payingFee && (
        <div className="bg-white border border-primary-200 rounded-xl p-5 space-y-4 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold text-slate-800">Record Payment for: <span className="text-primary-700">{payingFee.fee_type}</span></p>
            <button onClick={() => setPayingFee(null)} className="text-slate-400 hover:text-slate-600 text-sm font-medium transition-colors">Cancel</button>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-slate-50 rounded-lg p-2.5 text-center border border-slate-200"><p className="text-[10px] text-slate-400">Total Fee</p><p className="text-sm font-bold text-slate-900">₹{Number(payingFee.total_amount || 0).toLocaleString()}</p></div>
            <div className="bg-emerald-50 rounded-lg p-2.5 text-center border border-emerald-200"><p className="text-[10px] text-slate-400">Paid</p><p className="text-sm font-bold text-emerald-600">₹{Number(payingFee.paid || 0).toLocaleString()}</p></div>
            <div className="bg-red-50 rounded-lg p-2.5 text-center border border-red-200"><p className="text-[10px] text-slate-400">Remaining</p><p className="text-sm font-bold text-red-600">₹{Number(payingFee.pending || 0).toLocaleString()}</p></div>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700 mb-2 block">Amount</label>
            <div className="relative">
              <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-sm font-medium">₹</span>
              <input type="number" value={payAmount} onChange={e => { if (e.target.value === '' || Number(e.target.value) <= Number(payingFee.pending || 0)) setPayAmount(e.target.value); }} className="w-full border border-slate-300 rounded-xl pl-8 pr-4 py-2.5 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400" />
            </div>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700 mb-2 block">Payment Method</label>
            <div className="flex flex-wrap gap-2">
              {PAYMENT_METHODS.map(m => (
                <button
                  key={m.value}
                  onClick={() => setPayMethod(m.value)}
                  className={`px-4 py-2 rounded-full border text-sm font-medium cursor-pointer transition-all duration-200 ${
                    payMethod === m.value
                      ? 'bg-primary-100 border-primary-400 text-primary-700 shadow-sm'
                      : 'border-slate-200 text-slate-600 hover:border-slate-300 hover:bg-slate-50'
                  }`}
                >
                  {m.label}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700 mb-2 block">Reference <span className="text-slate-400 font-normal">(optional)</span></label>
            <input type="text" value={payRemarks || ''} onChange={e => setPayRemarks(e.target.value)} placeholder="e.g. Cheque No. 123456" className="w-full border border-slate-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400" />
          </div>
          <div className="flex gap-2 pt-2 border-t border-slate-100 justify-end">
            <Button variant="ghost" onClick={() => setPayingFee(null)}>Cancel</Button>
            <Button variant="primary" onClick={handleRecordPayment} loading={recordPaymentMutation.isPending} disabled={!payAmount || Number(payAmount) <= 0}>Record Payment</Button>
          </div>
        </div>
      )}
    </div>
  );
}

function PaymentHistoryModal({ fee, onViewReceipt }) {
  const { data, isLoading } = useQuery({
    queryKey: ['fee-history', fee.student_id],
    queryFn: () => api.get(`/admin/students/${fee.student_id}/fee-history`).then(r => r.data).catch(() => null),
    enabled: !!fee.student_id,
  });

  const displayPayments = data?.payments || [];
  const totalPaid = Number(fee.total_paid || fee.paid_amount || 0);
  const totalAmount = Number(fee.total_amount || 0);
  const pct = totalAmount > 0 ? (totalPaid / totalAmount) * 100 : 0;

  return (
    <div>
      {/* Summary Header */}
      <div className="bg-gradient-to-br from-slate-50 to-slate-100/80 rounded-xl p-5 mb-5">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-500 to-indigo-700 text-white flex items-center justify-center text-sm font-bold shadow-sm">
            {(fee.student_name || '').slice(0, 2).toUpperCase()}
          </div>
          <div>
            <p className="text-base font-bold text-slate-900">{fee.student_name}</p>
            <p className="text-xs text-slate-500">Class {fee.class_name} • {fee.fee_type || 'Tuition Fee'}</p>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-3 mb-4">
          <div className="bg-white rounded-xl p-3 text-center border border-slate-200">
            <p className="text-xs text-slate-500">Total Fee</p>
            <p className="text-lg font-bold text-slate-900">₹{totalAmount.toLocaleString()}</p>
          </div>
          <div className="bg-white rounded-xl p-3 text-center border border-emerald-200">
            <p className="text-xs text-slate-500">Paid</p>
            <p className="text-lg font-bold text-emerald-600">₹{totalPaid.toLocaleString()}</p>
          </div>
          <div className="bg-white rounded-xl p-3 text-center border border-red-200">
            <p className="text-xs text-slate-500">Pending</p>
            <p className="text-lg font-bold text-red-600">₹{(totalAmount - totalPaid).toLocaleString()}</p>
          </div>
        </div>
        {/* Progress Bar */}
        <div>
          <div className="flex justify-between items-center mb-1.5">
            <span className="text-xs text-slate-500">Payment Progress</span>
            <span className={`text-xs font-semibold ${pct >= 100 ? 'text-emerald-600' : pct > 50 ? 'text-blue-600' : 'text-amber-600'}`}>{pct.toFixed(0)}%</span>
          </div>
          <div className="w-full h-3 bg-white border border-slate-200 rounded-full overflow-hidden">
            <div className={`h-full rounded-full transition-all duration-700 ${pct >= 100 ? 'bg-emerald-500' : pct > 50 ? 'bg-blue-500' : 'bg-amber-500'}`} style={{ width: `${Math.min(pct, 100)}%` }} />
          </div>
        </div>
      </div>

      {/* Payment Timeline */}
      <h4 className="text-sm font-semibold text-slate-900 mb-3 flex items-center gap-2">
        <Clock size={14} className="text-slate-400" /> Payment Timeline
      </h4>
      {isLoading ? (
        <div className="space-y-3">{[1, 2, 3].map(i => <div key={i} className="h-16 bg-slate-100 rounded-xl animate-pulse" />)}</div>
      ) : displayPayments.length > 0 ? (
        <div className="space-y-3">
          {displayPayments.map((p, i) => (
            <div key={p.id || i} className="flex items-start gap-3 p-3 bg-white border border-slate-200 rounded-xl transition-all duration-150 hover:shadow-sm hover:border-slate-300">
              <div className={`w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 ${p.status === 'Paid' || p.status === 'paid' ? 'bg-emerald-100' : 'bg-amber-100'}`}>
                <CheckCircle size={16} className={p.status === 'Paid' || p.status === 'paid' ? 'text-emerald-600' : 'text-amber-600'} />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-semibold text-slate-900">₹{(p.amount || 0).toLocaleString()}</p>
                  <div className="flex items-center gap-2">
                    <Badge status={p.status || 'Paid'}>{p.status || 'Paid'}</Badge>
                    <button
                      onClick={() => onViewReceipt && onViewReceipt(p)}
                      className="flex items-center gap-1 px-2.5 py-1.5 text-[11px] font-medium text-primary-600 bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors duration-150"
                      title="View Receipt"
                    >
                      <Receipt size={12} /> Receipt
                    </button>
                  </div>
                </div>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="text-xs text-slate-500">{p.date || p.payment_date || p.paid_on}</span>
                  <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${(p.method || p.payment_method || 'Online') === 'Online' ? 'bg-blue-100 text-blue-700' : (p.method || p.payment_method) === 'Cheque' ? 'bg-amber-100 text-amber-700' : (p.method || p.payment_method) === 'Cash' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-600'}`}>{p.method || p.payment_method || 'Online'}</span>
                </div>
                {p.reference && <p className="text-[11px] text-slate-400 mt-0.5">Ref: {p.reference}</p>}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 bg-slate-50 rounded-xl">
          <DollarSign size={24} className="text-slate-300 mx-auto mb-2" />
          <p className="text-sm text-slate-400">No payment records found</p>
        </div>
      )}

      {/* Due Date */}
      {fee.due_date && (
        <div className="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between">
          <span className="text-xs text-slate-500">Due Date</span>
          <span className="text-sm font-medium text-slate-900">{fee.due_date}</span>
        </div>
      )}
    </div>
  );
}

function ReceiptModal({ fee, payment }) {
  const { data, isLoading } = useQuery({
    queryKey: ['fee-receipt', fee.student_id || fee.id],
    queryFn: () => api.get(ENDPOINTS.fees.studentReceipt(fee.student_id || fee.id)).then(r => r.data).catch(() => null),
    enabled: !!(fee.student_id || fee.id),
  });

  const receipt = { ...(data || {}), ...(payment || {}) };
  const schoolName = data?.school_name || receipt.school_name || 'School ERP';

  // Get latest payment from receipt data
  const payments = data?.payments || [];
  const latestPayment = payments.length > 0 ? payments[payments.length - 1] : null;

  const paidAmount = payment?.amount || latestPayment?.amount || receipt.amount_paid || receipt.total_amount_paid || fee.total_paid || 0;
  const receiptDate = payment?.date || payment?.payment_date || latestPayment?.payment_date || latestPayment?.date || receipt.payment_date || new Date().toISOString().split('T')[0];
  const receiptRef = payment?.reference || latestPayment?.reference || receipt.receipt_number || `RCP-${(fee.student_id || fee.id || '').slice(0, 8)}`;
  const receiptMethod = payment?.method || payment?.payment_method || latestPayment?.method || latestPayment?.payment_method || receipt.payment_method || 'Cash';

  const handlePrint = () => {
    generateFeeReceipt({
      student: { name: fee.student_name, full_name: fee.student_name, class_name: fee.class_name },
      payment: { amount: paidAmount, date: receiptDate, status: 'Paid', method: receiptMethod, ref: receiptRef },
      schoolName,
    });
  };

  if (isLoading) return <div className="text-center py-8 text-slate-400">Loading receipt...</div>;

  return (
    <div>
      {/* Receipt Card */}
      <div className="border-2 border-dashed border-slate-200 rounded-xl p-6 bg-white">
        {/* Header */}
        <div className="text-center mb-5 pb-4 border-b border-slate-200">
          <h2 className="text-lg font-bold text-slate-900">{schoolName}</h2>
          <p className="text-xs text-slate-500 mt-0.5">Fee Payment Receipt</p>
        </div>

        {/* Receipt Details */}
        <div className="grid grid-cols-2 gap-4 mb-5">
          <div>
            <p className="text-[11px] text-slate-400 uppercase tracking-wider">Receipt No</p>
            <p className="text-sm font-semibold text-slate-900">{receiptRef}</p>
          </div>
          <div className="text-right">
            <p className="text-[11px] text-slate-400 uppercase tracking-wider">Date</p>
            <p className="text-sm font-semibold text-slate-900">{receiptDate}</p>
          </div>
        </div>

        <div className="bg-slate-50 rounded-xl p-4 mb-5 space-y-2.5">
          <div className="flex justify-between">
            <span className="text-xs text-slate-500">Student Name</span>
            <span className="text-sm font-medium text-slate-900">{fee.student_name}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-xs text-slate-500">Class</span>
            <span className="text-sm font-medium text-slate-900">{fee.class_name}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-xs text-slate-500">Fee Type</span>
            <span className="text-sm font-medium text-slate-900">{fee.fee_type || 'Tuition Fee'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-xs text-slate-500">Payment Method</span>
            <span className="text-sm font-medium text-slate-900">{receiptMethod}</span>
          </div>
        </div>

        {/* Amount */}
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 text-center mb-5">
          <p className="text-xs text-emerald-600 font-medium">Amount Paid</p>
          <p className="text-3xl font-bold text-emerald-700 mt-1">₹{Number(paidAmount).toLocaleString()}</p>
        </div>

        {/* Status */}
        <div className="flex items-center justify-center gap-2">
          <CheckCircle size={16} className="text-emerald-500" />
          <span className="text-sm font-medium text-emerald-600">Payment Confirmed</span>
        </div>

        {/* Latest Transaction */}
        {latestPayment && !payment && (
          <div className="mt-5 pt-4 border-t border-slate-200">
            <p className="text-[11px] text-slate-400 uppercase tracking-wider mb-2">Latest Transaction</p>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 space-y-1.5">
              <div className="flex justify-between">
                <span className="text-xs text-slate-500">Fee Type</span>
                <span className="text-sm font-medium text-slate-900">{latestPayment.fee_type}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-xs text-slate-500">Amount</span>
                <span className="text-sm font-bold text-emerald-700">₹{Number(latestPayment.amount).toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-xs text-slate-500">Date</span>
                <span className="text-sm font-medium text-slate-900">{latestPayment.payment_date}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-xs text-slate-500">Method</span>
                <span className="text-sm font-medium text-slate-900">{latestPayment.method}</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Print Button */}
      <div className="flex justify-center mt-5">
        <Button variant="primary" size="lg" icon={Printer} onClick={handlePrint}>Print Receipt</Button>
      </div>
    </div>
  );
}

const FEE_TYPE_OPTIONS = [
  { value: 'Tuition Fee', label: 'Tuition Fee' },
  { value: 'Lab Fee', label: 'Lab Fee' },
  { value: 'Library Fee', label: 'Library Fee' },
  { value: 'Transport Fee', label: 'Transport Fee' },
  { value: 'Exam Fee', label: 'Exam Fee' },
];

function GenerateDueForm({ onClose, generateDueMutation, toast, studentIds = [], studentCount = 0 }) {
  const [form, setForm] = useState({ fee_type: '', amount: '', due_date: '' });
  const [errors, setErrors] = useState({});

  const validate = () => {
    const errs = {};
    if (!form.fee_type.trim()) errs.fee_type = 'Fee type is required';
    if (!form.amount || Number(form.amount) <= 0) errs.amount = 'Amount must be greater than 0';
    if (!form.due_date) errs.due_date = 'Due date is required';
    const today = new Date().toISOString().split('T')[0];
    if (form.due_date && form.due_date <= today) errs.due_date = 'Due date must be in the future';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = () => {
    if (!validate()) return;
    generateDueMutation.mutate(
      { student_ids: studentIds, fee_type: form.fee_type.trim(), amount: Number(form.amount), due_date: form.due_date },
      {
        onSuccess: (res) => { toast.success(res?.message || `Fee dues generated for ${studentCount} student(s)`); onClose(); },
        onError: (err) => { toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to generate dues'); },
      }
    );
  };

  return (
    <div>
      <div className="space-y-4">
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-blue-100 flex items-center justify-center shrink-0">
            <span className="text-sm font-bold text-blue-700">{studentCount}</span>
          </div>
          <div>
            <p className="text-sm font-medium text-blue-800">Generate fee for {studentCount} selected student{studentCount !== 1 ? 's' : ''}</p>
            <p className="text-xs text-blue-600 mt-0.5">A pending fee entry will be created for each selected student.</p>
          </div>
        </div>
        <div>
          <label className="text-sm font-medium text-slate-700 mb-1.5 block">Fee Type *</label>
          <input type="text" value={form.fee_type} onChange={e => { setForm(f => ({ ...f, fee_type: e.target.value })); if (errors.fee_type) setErrors(er => ({ ...er, fee_type: '' })); }} placeholder="e.g. Tuition Fee, Lab Fee, Transport Fee..." className={`w-full border rounded-lg px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400 ${errors.fee_type ? 'border-red-400' : 'border-slate-300'}`} />
          {errors.fee_type && <p className="text-xs text-red-500 mt-0.5">{errors.fee_type}</p>}
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-slate-700 mb-1.5 block">Amount (₹) *</label>
            <input type="text" inputMode="numeric" value={form.amount} onChange={e => { const val = e.target.value.replace(/[^0-9.]/g, ''); setForm(f => ({ ...f, amount: val })); if (errors.amount) setErrors(er => ({ ...er, amount: '' })); }} placeholder="e.g. 5000" className={`w-full border rounded-lg px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400 ${errors.amount ? 'border-red-400' : 'border-slate-300'}`} />
            {errors.amount && <p className="text-xs text-red-500 mt-0.5">{errors.amount}</p>}
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700 mb-1.5 block">Due Date *</label>
            <DatePicker value={form.due_date} onChange={(v) => { setForm(f => ({ ...f, due_date: v })); if (errors.due_date) setErrors(er => ({ ...er, due_date: '' })); }} />
            {errors.due_date && <p className="text-xs text-red-500 mt-0.5">{errors.due_date}</p>}
          </div>
        </div>
      </div>
      <div className="flex justify-end gap-2 mt-5 pt-4 border-t border-slate-100">
        <Button variant="ghost" onClick={onClose}>Cancel</Button>
        <Button variant="primary" loading={generateDueMutation.isPending} disabled={!form.fee_type.trim() || !form.amount || !form.due_date} onClick={handleSubmit}>
          Generate Fee Dues
        </Button>
      </div>
    </div>
  );
}
