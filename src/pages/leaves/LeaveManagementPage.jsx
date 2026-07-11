import { useState, useMemo } from 'react';
import { useDebounceValue } from 'usehooks-ts';
import { Clock, ThumbsUp, ThumbsDown, UserX, CheckCircle, XCircle, Eye, Plus, Calendar, ChevronLeft, ChevronRight } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { useLeaves, useApproveLeave, useRejectLeave, useLeaveBalances, useAllocateLeaves, useLeavePolicy, useLeaveCalendar } from '../../services/leaveService';
import api from '../../services/api';
import { ENDPOINTS } from '../../config/api';
import { Button, Badge, Modal, ConfirmDialog, SearchableSelect, useToast, useSortableData, Breadcrumb, HoverCard, usePagination, DataTable , AnimatedNumber } from 'school-erp-ui-shared';

const STATUS_TABS = [
  { key: 'Pending', label: 'Pending', color: 'bg-amber-500' },
  { key: 'Approved', label: 'Approved', color: 'bg-green-500' },
  { key: 'Rejected', label: 'Rejected', color: 'bg-red-500' },
  { key: '', label: 'All', color: 'bg-indigo-500' },
];

export default function LeaveManagementPage() {
  const toast = useToast();
  const [statusFilter, setStatusFilter] = useState('Pending');
  const [teacherFilter, setTeacherFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [viewLeave, setViewLeave] = useState(null);
  const [allocateOpen, setAllocateOpen] = useState(false);
  const [allocateForm, setAllocateForm] = useState({ staff_ids: [], leave_types: {} });
  const [balanceSearch, setBalanceSearch] = useState('');
  const [rejectData, setRejectData] = useState(null);
  const [rejectRemarks, setRejectRemarks] = useState('');
  const [approveData, setApproveData] = useState(null);
  const [approveRemarks, setApproveRemarks] = useState('');
  const [confirmAllocate, setConfirmAllocate] = useState(false);
  const [debouncedBalanceSearch] = useDebounceValue(balanceSearch, 300);
  const pagination = usePagination(20, "admin-leaves");

  const { data: leavesData, isLoading, isFetching, isError, refetch } = useLeaves({ ...pagination.params, status: statusFilter || undefined, search: teacherFilter || undefined, leave_type: typeFilter || undefined });
  const { data: balancesData } = useLeaveBalances();
  const { data: policyData } = useLeavePolicy();
  const { data: staffListData } = useQuery({ queryKey: ['staff-list'], queryFn: () => api.get(ENDPOINTS.staff.list, { params: { page_size: 200 } }).then(r => r.data).catch(() => ({ results: [] })) });
  const approveMutation = useApproveLeave();
  const rejectMutation = useRejectLeave();
  const allocateMutation = useAllocateLeaves();

  const leaves = leavesData?.results ?? [];
  const { sortedData, sortConfig, requestSort } = useSortableData(leaves);
  const summary = leavesData?.overall_summary ?? {};
  const balances = balancesData?.results ?? [];
  const policyLeaveTypes = policyData?.leave_types ?? [];

  if (isError) return <div className="text-center py-12"><p className="text-red-500 mb-2">Failed to load leave data</p><Button variant="secondary" onClick={refetch}>Retry</Button></div>;

  const kpis = [
    { label: 'Pending', value: summary.pending ?? 0, icon: Clock, color: 'text-amber-600', bg: 'bg-gradient-to-br from-amber-50 to-amber-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(245,158,11,0.3)]' },
    { label: 'Approved', value: summary.approved ?? 0, icon: ThumbsUp, color: 'text-green-600', bg: 'bg-gradient-to-br from-green-50 to-green-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(34,197,94,0.3)]' },
    { label: 'Rejected', value: summary.rejected ?? 0, icon: ThumbsDown, color: 'text-red-600', bg: 'bg-gradient-to-br from-red-50 to-red-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(239,68,68,0.3)]' },
    { label: 'On Leave Today', value: summary.on_leave_today ?? 0, icon: UserX, color: 'text-purple-600', bg: 'bg-gradient-to-br from-purple-50 to-purple-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(147,51,234,0.3)]' },
  ];

  const columns = [
    {
      key: 'teacher_name', label: 'Teacher', sortable: true,
      render: (l) => (
        <HoverCard content={
          <div>
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-purple-700 text-white flex items-center justify-center text-sm font-bold">{(l.teacher_name || '').slice(0, 2).toUpperCase()}</div>
              <div>
                <p className="text-sm font-bold text-slate-900">{l.teacher_name}</p>
                <p className="text-xs text-slate-500">{l.department || 'Teaching'}</p>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="bg-slate-50 rounded-lg p-2"><p className="text-xs text-slate-400">Type</p><p className="text-sm font-bold text-blue-600">{(l.leave_type || '').replace(' Leave', '')}</p></div>
              <div className="bg-slate-50 rounded-lg p-2"><p className="text-xs text-slate-400">Days</p><p className="text-sm font-bold text-slate-900">{l.days || 0}</p></div>
              <div className="bg-slate-50 rounded-lg p-2"><p className="text-xs text-slate-400">Status</p><p className={`text-sm font-bold ${l.status === 'Approved' ? 'text-emerald-600' : l.status === 'Rejected' ? 'text-red-600' : 'text-amber-600'}`}>{l.status}</p></div>
            </div>
          </div>
        }>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-purple-600 text-white flex items-center justify-center text-xs font-semibold">{(l.teacher_name || '').slice(0, 2).toUpperCase()}</div>
            <div><p className="text-sm font-semibold text-slate-800 cursor-pointer hover:text-primary-600 transition-colors">{l.teacher_name}</p><p className="text-[10px] text-slate-400">{l.department || 'Teaching'}</p></div>
          </div>
        </HoverCard>
      ),
    },
    { key: 'leave_type', label: 'Type', render: (l) => (l.leave_type || '').replace(' Leave', '') },
    { key: 'from_date', label: 'From', sortable: true },
    { key: 'to_date', label: 'To' },
    { key: 'days', label: 'Days', sortable: true, render: (l) => <span className="font-semibold">{l.days}</span> },
    { key: 'reason', label: 'Reason', render: (l) => (
      <div className="max-w-[200px]">
        <span className="truncate block text-sm text-slate-900">{l.reason}</span>
        {l.remarks && (
          <span className="truncate block text-[11px] text-red-500 mt-0.5" title={l.remarks}>Remarks: {l.remarks}</span>
        )}
      </div>
    )},
    { key: 'status', label: 'Status', sortable: true, render: (l) => <Badge status={l.status} /> },
    {
      key: 'actions', label: 'Actions',
      render: (l) => (
        <div className="flex gap-1">
          <button onClick={() => setViewLeave(l)} className="p-1 hover:bg-slate-100 rounded" title="View"><Eye className="w-4 h-4 text-slate-500" /></button>
          {l.status === 'Pending' && (
            <>
              <button onClick={() => { setApproveData(l); setApproveRemarks(''); }} className="p-1 hover:bg-green-50 rounded" title="Approve"><CheckCircle className="w-4 h-4 text-green-600" /></button>
              <button onClick={() => { setRejectData({ id: l.id, teacher_name: l.teacher_name, currentStatus: l.status }); setRejectRemarks(''); }} className="p-1 hover:bg-red-50 rounded" title="Reject"><XCircle className="w-4 h-4 text-red-500" /></button>
            </>
          )}
          {l.status === 'Approved' && (
            <button onClick={() => { setRejectData({ id: l.id, teacher_name: l.teacher_name, currentStatus: l.status }); setRejectRemarks(''); }} className="p-1 hover:bg-red-50 rounded" title="Revert & Reject"><XCircle className="w-4 h-4 text-red-500" /></button>
          )}
          {l.status === 'Rejected' && (
            <button onClick={() => { setApproveData(l); setApproveRemarks(''); }} className="p-1 hover:bg-green-50 rounded" title="Revert & Approve"><CheckCircle className="w-4 h-4 text-green-600" /></button>
          )}
        </div>
      ),
    },
  ];

  return (
    <div>
      <Breadcrumb items={[{ label: 'Dashboard', href: '/admin/dashboard' }, { label: 'Leave Management' }]} />
      <div className="flex justify-between items-center mb-6"><div><h1 className="text-2xl md:text-3xl font-bold text-slate-900">Teacher Leave Management</h1><p className="text-sm text-slate-500 mt-1">Review, approve or reject teacher leave requests</p></div><Button variant="primary" icon={Plus} onClick={() => setAllocateOpen(true)}>Allocate Leaves</Button></div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mb-4">
        {kpis.map(k => (
          <div key={k.label} className={`bg-white border border-slate-200 rounded-xl p-4 md:p-5 flex items-center gap-3 md:gap-4 transition-all duration-200 hover:-translate-y-1 ${k.glow} cursor-default group`}>
            <div className={`${k.bg} p-2.5 md:p-3 rounded-xl transition-transform duration-200 group-hover:scale-110`}><k.icon className={`w-5 h-5 ${k.color}`} /></div>
            <div><p className="text-xs text-slate-500 font-medium">{k.label}</p><p className="text-xl md:text-2xl font-bold text-slate-900 mt-0.5"><AnimatedNumber value={k.value} id={k.label} /></p></div>
          </div>
        ))}
      </div>

      {/* Leave Calendar */}
      <LeaveCalendarSection />

      {/* Status Tabs */}
      <div className="flex gap-2 mb-4">
        {STATUS_TABS.map(tab => {
          const count = tab.key === 'Pending' ? summary.pending : tab.key === 'Approved' ? summary.approved : tab.key === 'Rejected' ? summary.rejected : summary.total_applications;
          const isActive = statusFilter === tab.key;
          return (
            <button key={tab.key} onClick={() => { setStatusFilter(tab.key); pagination.reset(); }} className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${isActive ? `${tab.color} text-white` : 'border border-slate-200 text-slate-500 hover:bg-slate-50'}`}>
              {tab.label} ({count ?? 0})
            </button>
          );
        })}
      </div>

      <DataTable
        columns={columns}
        data={sortedData}
        loading={isFetching}
        emptyMessage={`No ${statusFilter || ''} leave applications found`}
        headerTitle="Applications"
        filters={[
          { key: 'teacher', value: teacherFilter, onChange: (v) => { setTeacherFilter(v); pagination.reset(); }, options: [{ value: '', label: 'All Teachers' }, ...[...new Set(leaves.map(l => l.teacher_name).filter(Boolean))].map(t => ({ value: t, label: t }))] },
          { key: 'type', value: typeFilter, onChange: (v) => { setTypeFilter(v); pagination.reset(); }, options: [{ value: '', label: 'All Types' }, ...policyLeaveTypes.map(lt => ({ value: lt.type, label: lt.display_name || lt.type.replace(' Leave', '') }))] },
        ]}
        sortConfig={sortConfig}
        onSort={requestSort}
        page={pagination.page}
        totalPages={leavesData?.total_pages || 1}
        totalCount={leavesData?.count || 0}
        pageSize={pagination.pageSize}
        onPageChange={(p) => pagination.setPage(p)}
        onPageSizeChange={pagination.setPageSize}
        className="mb-4"
      />

      {/* Balances */}
      {balances.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-xl p-4 md:p-5 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-semibold text-slate-900">Teacher Leave Balances</h3>
            <div className="flex items-center gap-3">
              <input
                type="text"
                value={balanceSearch}
                onChange={e => setBalanceSearch(e.target.value)}
                placeholder="Search teacher..."
                className="border border-slate-300 rounded-lg px-3 py-1.5 text-sm w-48 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
              <span className="text-xs text-slate-400">{balances.filter(b => !debouncedBalanceSearch || (b.teacher_name || '').toLowerCase().includes(debouncedBalanceSearch.toLowerCase())).length} teachers</span>
            </div>
          </div>
          <div className="overflow-x-auto rounded-xl border border-slate-200">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="py-3 px-4 text-left text-xs font-semibold text-slate-500 uppercase">Teacher</th>
                  {(() => {
                    const balanceColors = ['bg-blue-500', 'bg-amber-500', 'bg-purple-500', 'bg-emerald-500', 'bg-pink-500', 'bg-indigo-500'];
                    const colKeys = policyLeaveTypes.length > 0
                      ? policyLeaveTypes.map(lt => ({ key: lt.type.toLowerCase().replace(' leave', '').replace(' ', '_'), label: lt.display_name || lt.type.replace(' Leave', '') }))
                      : [{ key: 'casual', label: 'Casual' }, { key: 'sick', label: 'Sick' }, { key: 'annual', label: 'Annual' }];
                    return colKeys.map((col, idx) => (
                      <th key={col.key} className="py-3 px-3 text-center text-xs font-semibold text-slate-500 uppercase">
                        <div className="flex items-center justify-center gap-1.5"><span className={`w-2 h-2 rounded-full ${balanceColors[idx % balanceColors.length]}`} />{col.label}</div>
                      </th>
                    ));
                  })()}
                  <th className="py-3 px-3 text-center text-xs font-semibold text-slate-500 uppercase">
                    <div className="flex items-center justify-center gap-1.5"><span className="w-2 h-2 rounded-full bg-slate-500" />Total</div>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {balances.filter(b => !debouncedBalanceSearch || (b.teacher_name || '').toLowerCase().includes(debouncedBalanceSearch.toLowerCase())).map(b => {
                  const balanceColors = ['bg-blue-500', 'bg-amber-500', 'bg-purple-500', 'bg-emerald-500', 'bg-pink-500', 'bg-indigo-500'];
                  const colKeys = policyLeaveTypes.length > 0
                    ? policyLeaveTypes.map(lt => lt.type.toLowerCase().replace(' leave', '').replace(' ', '_'))
                    : ['casual', 'sick', 'annual'];
                  let totalUsed = 0;
                  let totalAlloc = 0;
                  colKeys.forEach(key => {
                    totalUsed += Number(b[key]?.availed) || 0;
                    totalAlloc += Number(b[key]?.total) || 0;
                  });
                  const totalPct = totalAlloc > 0 ? (totalUsed / totalAlloc) * 100 : 0;
                  return (
                    <tr key={b.teacher_id || b.teacher_name} className="hover:bg-primary-50/30 transition-colors duration-150">
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-indigo-700 text-white flex items-center justify-center text-xs font-bold shadow-sm">{(b.teacher_name || '').slice(0, 2).toUpperCase()}</div>
                          <div>
                            <p className="text-sm font-semibold text-slate-900">{b.teacher_name}</p>
                            <p className="text-[10px] text-slate-400">{b.department || 'Teaching'}</p>
                          </div>
                        </div>
                      </td>
                      {colKeys.map((key, idx) => (
                        <td key={key} className="py-3 px-3"><BalanceCell data={b[key]} color={balanceColors[idx % balanceColors.length]} /></td>
                      ))}
                      <td className="py-3 px-3">
                        <div className="flex flex-col items-center gap-1">
                          <span className={`text-base font-bold ${totalPct > 80 ? 'text-red-600' : totalPct > 50 ? 'text-amber-600' : 'text-slate-900'}`}>{totalUsed}<span className="text-xs text-slate-400 font-medium">/{totalAlloc}</span></span>
                          <div className="flex items-center gap-2">
                            <div className="w-20 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                              <div className={`h-full rounded-full transition-all duration-500 ${totalPct > 80 ? 'bg-red-500' : totalPct > 50 ? 'bg-amber-500' : 'bg-emerald-500'}`} style={{ width: `${totalPct}%` }} />
                            </div>
                            <span className={`text-[11px] font-medium ${totalPct > 80 ? 'text-red-500' : totalPct > 50 ? 'text-amber-500' : 'text-emerald-500'}`}>{totalPct.toFixed(0)}%</span>
                          </div>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Allocate Leaves Modal */}
      <Modal open={allocateOpen} onClose={() => setAllocateOpen(false)} title="Allocate Leaves to Employees" size="lg">
        <div className="space-y-5">
          {/* Employee Selection */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-slate-700">Select Employees</label>
              <span className="text-xs text-primary-600 font-medium">{allocateForm.staff_ids.length} selected</span>
            </div>
            <div className="border border-slate-200 rounded-xl overflow-hidden">
              <label className="flex items-center gap-3 px-4 py-2.5 bg-slate-50 border-b border-slate-200 cursor-pointer hover:bg-slate-100 transition-colors">
                <input type="checkbox" checked={allocateForm.staff_ids.length === ((staffListData?.results || []).length) && (staffListData?.results || []).length > 0} onChange={e => setAllocateForm({...allocateForm, staff_ids: e.target.checked ? (staffListData?.results || []).map(t => t.id) : []})} className="w-4 h-4 rounded border-slate-300 text-primary-600" />
                <span className="text-sm font-semibold text-slate-800">Select All Employees</span>
                <span className="text-xs text-slate-400 ml-auto">{(staffListData?.results || []).length} total</span>
              </label>
              <div className="max-h-48 overflow-y-auto divide-y divide-slate-50">
                {(staffListData?.results || []).map(t => (
                  <label key={t.id} className={`flex items-center gap-3 px-4 py-2.5 cursor-pointer transition-colors ${allocateForm.staff_ids.includes(t.id) ? 'bg-primary-50/50' : 'hover:bg-slate-50'}`}>
                    <input type="checkbox" checked={allocateForm.staff_ids.includes(t.id)} onChange={e => setAllocateForm({...allocateForm, staff_ids: e.target.checked ? [...allocateForm.staff_ids, t.id] : allocateForm.staff_ids.filter(id => id !== t.id)})} className="w-4 h-4 rounded border-slate-300 text-primary-600" />
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-indigo-700 text-white flex items-center justify-center text-xs font-bold">{(t.full_name || '').slice(0, 2).toUpperCase()}</div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-slate-800">{t.full_name}</p>
                      <p className="text-xs text-slate-400">{t.department || 'Staff'} • {t.employee_id}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          </div>

          {/* Leave Types */}
          <div>
            <label className="text-sm font-medium text-slate-700 mb-3 block">Leave Allocation (Days per Year)</label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {policyLeaveTypes.length > 0 ? policyLeaveTypes.map((lt, idx) => {
                const colorStyles = [
                  { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-700', ring: 'focus:ring-blue-400' },
                  { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700', ring: 'focus:ring-red-400' },
                  { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-700', ring: 'focus:ring-green-400' },
                  { bg: 'bg-purple-50', border: 'border-purple-200', text: 'text-purple-700', ring: 'focus:ring-purple-400' },
                  { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', ring: 'focus:ring-amber-400' },
                  { bg: 'bg-indigo-50', border: 'border-indigo-200', text: 'text-indigo-700', ring: 'focus:ring-indigo-400' },
                ];
                const cs = colorStyles[idx % colorStyles.length];
                return (
                  <div key={lt.type} className={`${cs.bg} border ${cs.border} rounded-xl p-3`}>
                    <p className={`text-xs font-medium ${cs.text} mb-1.5`}>{lt.display_name || lt.type}</p>
                    <input type="number" value={allocateForm.leave_types[lt.type] ?? lt.total_per_year} onChange={e => setAllocateForm({...allocateForm, leave_types: {...allocateForm.leave_types, [lt.type]: Number(e.target.value)}})} className={`w-full border ${cs.border} rounded-lg px-3 py-2 text-sm text-center font-semibold bg-white focus:ring-2 ${cs.ring} focus:outline-none`} />
                  </div>
                );
              }) : (
                <>
                  <div className="bg-blue-50 border border-blue-200 rounded-xl p-3">
                    <p className="text-xs font-medium text-blue-700 mb-1.5">Casual Leave</p>
                    <input type="number" value={allocateForm.leave_types['Casual Leave'] ?? 12} onChange={e => setAllocateForm({...allocateForm, leave_types: {...allocateForm.leave_types, 'Casual Leave': Number(e.target.value)}})} className="w-full border border-blue-200 rounded-lg px-3 py-2 text-sm text-center font-semibold bg-white focus:ring-2 focus:ring-blue-400 focus:outline-none" />
                  </div>
                  <div className="bg-red-50 border border-red-200 rounded-xl p-3">
                    <p className="text-xs font-medium text-red-700 mb-1.5">Sick Leave</p>
                    <input type="number" value={allocateForm.leave_types['Sick Leave'] ?? 10} onChange={e => setAllocateForm({...allocateForm, leave_types: {...allocateForm.leave_types, 'Sick Leave': Number(e.target.value)}})} className="w-full border border-red-200 rounded-lg px-3 py-2 text-sm text-center font-semibold bg-white focus:ring-2 focus:ring-blue-400 focus:outline-none" />
                  </div>
                  <div className="bg-green-50 border border-green-200 rounded-xl p-3">
                    <p className="text-xs font-medium text-green-700 mb-1.5">Annual Leave</p>
                    <input type="number" value={allocateForm.leave_types['Annual Leave'] ?? 15} onChange={e => setAllocateForm({...allocateForm, leave_types: {...allocateForm.leave_types, 'Annual Leave': Number(e.target.value)}})} className="w-full border border-green-200 rounded-lg px-3 py-2 text-sm text-center font-semibold bg-white focus:ring-2 focus:ring-blue-400 focus:outline-none" />
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
        <div className="flex justify-end gap-2 mt-5 pt-4 border-t border-slate-100">
          <Button variant="ghost" onClick={() => setAllocateOpen(false)}>Cancel</Button>
          <Button variant="primary" disabled={allocateForm.staff_ids.length === 0 || allocateMutation.isPending} onClick={() => setConfirmAllocate(true)}>{allocateMutation.isPending ? 'Allocating...' : `Allocate to ${allocateForm.staff_ids.length} Employee(s)`}</Button>
        </div>
      </Modal>

      {/* Allocate Leaves Confirmation */}
      <ConfirmDialog
        open={confirmAllocate}
        title="Confirm Leave Allocation"
        message={`Are you sure you want to allocate leaves to ${allocateForm.staff_ids.length} employee(s)? This will set or reset their leave balances for the selected leave types.`}
        onConfirm={() => {
          const leave_types = {};
          if (policyLeaveTypes.length > 0) {
            policyLeaveTypes.forEach(lt => {
              const val = allocateForm.leave_types[lt.type] ?? lt.total_per_year;
              if (val > 0) leave_types[lt.type] = val;
            });
          } else {
            if ((allocateForm.leave_types['Casual Leave'] ?? 12) > 0) leave_types['Casual Leave'] = allocateForm.leave_types['Casual Leave'] ?? 12;
            if ((allocateForm.leave_types['Sick Leave'] ?? 10) > 0) leave_types['Sick Leave'] = allocateForm.leave_types['Sick Leave'] ?? 10;
            if ((allocateForm.leave_types['Annual Leave'] ?? 15) > 0) leave_types['Annual Leave'] = allocateForm.leave_types['Annual Leave'] ?? 15;
          }
          allocateMutation.mutate({ staff_ids: allocateForm.staff_ids, leave_types }, {
            onSuccess: () => { setConfirmAllocate(false); setAllocateOpen(false); setAllocateForm({ staff_ids: [], leave_types: {} }); toast.success('Leaves allocated successfully'); },
            onError: (err) => { setConfirmAllocate(false); toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to allocate leaves'); },
          });
        }}
        onClose={() => setConfirmAllocate(false)}
        loading={allocateMutation.isPending}
      />

      {/* View Leave Detail Modal */}
      <Modal open={!!viewLeave} onClose={() => setViewLeave(null)} title="Leave Application Details">
        {viewLeave && (
          <div className="space-y-3">
            <div className="flex items-center gap-3 pb-3 border-b border-slate-100">
              <div className="w-10 h-10 rounded-full bg-purple-600 text-white flex items-center justify-center text-sm font-semibold">{(viewLeave.teacher_name || '').slice(0, 2).toUpperCase()}</div>
              <div><p className="font-semibold text-slate-800">{viewLeave.teacher_name}</p><p className="text-xs text-slate-500">{viewLeave.department || 'Teaching'}</p></div>
              <Badge status={viewLeave.status} />
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div><p className="text-xs text-slate-500">Leave Type</p><p className="font-medium">{viewLeave.leave_type}</p></div>
              <div><p className="text-xs text-slate-500">Duration</p><p className="font-medium">{viewLeave.days} day(s)</p></div>
              <div><p className="text-xs text-slate-500">From</p><p className="font-medium">{viewLeave.from_date}</p></div>
              <div><p className="text-xs text-slate-500">To</p><p className="font-medium">{viewLeave.to_date}</p></div>
              <div className="col-span-2"><p className="text-xs text-slate-500">Reason</p><p className="font-medium">{viewLeave.reason || 'No reason provided'}</p></div>
              {viewLeave.applied_on && <div><p className="text-xs text-slate-500">Applied On</p><p className="font-medium">{viewLeave.applied_on}</p></div>}
              {viewLeave.approved_by && <div><p className="text-xs text-slate-500">Approved By</p><p className="font-medium">{viewLeave.approved_by}</p></div>}
              {viewLeave.approved_on && <div><p className="text-xs text-slate-500">Approved On</p><p className="font-medium">{new Date(viewLeave.approved_on).toLocaleDateString()}</p></div>}
              {viewLeave.rejected_by && <div><p className="text-xs text-slate-500">Rejected By</p><p className="font-medium">{viewLeave.rejected_by}</p></div>}
              {viewLeave.rejected_on && <div><p className="text-xs text-slate-500">Rejected On</p><p className="font-medium">{new Date(viewLeave.rejected_on).toLocaleDateString()}</p></div>}
            </div>
            {viewLeave.remarks && (
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-3">
                <p className="text-xs text-slate-500 mb-1">Remarks</p>
                <p className="text-sm font-medium text-slate-700">{viewLeave.remarks}</p>
              </div>
            )}
            {viewLeave.status !== 'Cancelled' && (
              <div className="flex gap-2 pt-3 border-t border-slate-100">
                {viewLeave.status === 'Pending' && (
                  <>
                    <Button variant="primary" onClick={() => { setApproveData(viewLeave); setApproveRemarks(''); setViewLeave(null); }}>Approve</Button>
                    <Button variant="ghost" className="!text-red-600 hover:!bg-red-50" onClick={() => { setRejectData({ id: viewLeave.id, teacher_name: viewLeave.teacher_name, currentStatus: viewLeave.status }); setRejectRemarks(''); setViewLeave(null); }}>Reject</Button>
                  </>
                )}
                {viewLeave.status === 'Approved' && (
                  <Button variant="ghost" className="!text-red-600 hover:!bg-red-50" onClick={() => { setRejectData({ id: viewLeave.id, teacher_name: viewLeave.teacher_name, currentStatus: viewLeave.status }); setRejectRemarks(''); setViewLeave(null); }}>Revert &amp; Reject</Button>
                )}
                {viewLeave.status === 'Rejected' && (
                  <Button variant="primary" onClick={() => { setApproveData(viewLeave); setApproveRemarks(''); setViewLeave(null); }}>Revert &amp; Approve</Button>
                )}
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* Approve Leave Confirmation */}
      <Modal open={!!approveData} onClose={() => setApproveData(null)} title="Approve Leave Request">
        {approveData && (
          <div className="space-y-4">
            <p className="text-sm text-slate-600">
              {approveData.status === 'Rejected'
                ? <>Reverting rejection and approving leave for <span className="font-semibold text-slate-800">{approveData.teacher_name}</span>.</>
                : <>Approving leave request from <span className="font-semibold text-slate-800">{approveData.teacher_name}</span>.</>
              }
            </p>
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-sm">
              <div className="grid grid-cols-2 gap-2">
                <div><span className="text-xs text-slate-500">Type:</span> <span className="font-medium">{approveData.leave_type}</span></div>
                <div><span className="text-xs text-slate-500">Days:</span> <span className="font-medium">{approveData.days}</span></div>
                <div><span className="text-xs text-slate-500">From:</span> <span className="font-medium">{approveData.from_date}</span></div>
                <div><span className="text-xs text-slate-500">To:</span> <span className="font-medium">{approveData.to_date}</span></div>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1.5 block">Remarks <span className="text-xs text-slate-400 font-normal">(optional)</span></label>
              <textarea
                value={approveRemarks}
                onChange={e => setApproveRemarks(e.target.value)}
                placeholder="Add any remarks for approval..."
                className="w-full border border-slate-300 rounded-lg px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400 min-h-[80px]"
              />
            </div>
            <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
              <Button variant="ghost" onClick={() => setApproveData(null)}>Cancel</Button>
              <Button
                variant="primary"
                disabled={approveMutation.isPending}
                onClick={() => {
                  approveMutation.mutate({ id: approveData.id, data: { remarks: approveRemarks.trim() || undefined } }, {
                    onSuccess: () => { setApproveData(null); setApproveRemarks(''); toast.success('Leave approved'); },
                    onError: (err) => toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to approve'),
                  });
                }}
              >
                {approveMutation.isPending ? 'Approving...' : 'Approve Leave'}
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Reject Leave Remarks Modal */}
      <Modal open={!!rejectData} onClose={() => setRejectData(null)} title={rejectData?.currentStatus === 'Approved' ? 'Revert & Reject Leave' : 'Reject Leave Request'}>
        {rejectData && (
          <div className="space-y-4">
            <p className="text-sm text-slate-600">
              {rejectData.currentStatus === 'Approved'
                ? <>Reverting approval and rejecting leave for <span className="font-semibold text-slate-800">{rejectData.teacher_name}</span>. Please provide a reason.</>
                : <>Rejecting leave request for <span className="font-semibold text-slate-800">{rejectData.teacher_name}</span>. Please provide a reason.</>
              }
            </p>
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1.5 block">Rejection Remarks *</label>
              <textarea
                value={rejectRemarks}
                onChange={e => setRejectRemarks(e.target.value)}
                placeholder="Enter reason for rejection..."
                className="w-full border border-slate-300 rounded-lg px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400 min-h-[100px]"
              />
            </div>
            <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
              <Button variant="ghost" onClick={() => setRejectData(null)}>Cancel</Button>
              <Button
                variant="primary"
                className="!bg-red-600 hover:!bg-red-700"
                disabled={!rejectRemarks.trim() || rejectMutation.isPending}
                onClick={() => {
                  rejectMutation.mutate({ id: rejectData.id, data: { remarks: rejectRemarks.trim() } }, {
                    onSuccess: () => { setRejectData(null); setRejectRemarks(''); toast.success('Leave rejected'); },
                    onError: (err) => toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to reject'),
                  });
                }}
              >
                {rejectMutation.isPending ? 'Rejecting...' : 'Reject Leave'}
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}

function BalanceCell({ data, color }) {
  const used = data ? Number(data.availed || data.used) : 0;
  const total = data ? Number(data.total || data.allocated) : 0;
  const pct = total > 0 ? (used / total) * 100 : 0;
  return (
    <div className="flex flex-col items-center gap-1">
      <span className={`text-base font-bold ${pct > 75 ? 'text-red-600' : 'text-slate-900'}`}>{used}<span className="text-xs text-slate-400 font-medium">/{total}</span></span>
      <div className="w-20 h-1.5 bg-slate-100 rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all duration-500 ${pct > 75 ? 'bg-red-500' : color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const DAYS_SHORT = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

function LeaveCalendarSection() {
  const [showCalendar, setShowCalendar] = useState(false);
  const [viewYear, setViewYear] = useState(new Date().getFullYear());
  const [viewMonth, setViewMonth] = useState(new Date().getMonth());
  const [hoveredDate, setHoveredDate] = useState(null);

  const fromDate = `${viewYear}-${String(viewMonth + 1).padStart(2, '0')}-01`;
  const lastDay = new Date(viewYear, viewMonth + 1, 0).getDate();
  const toDate = `${viewYear}-${String(viewMonth + 1).padStart(2, '0')}-${lastDay}`;

  const { data: calendarData } = useLeaveCalendar({ from_date: fromDate, to_date: toDate });
  const leavesByDate = calendarData?.leaves_by_date || {};
  const conflictDates = calendarData?.conflict_dates || [];

  const firstDayOfMonth = new Date(viewYear, viewMonth, 1).getDay();
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const prevMonth = () => {
    if (viewMonth === 0) { setViewMonth(11); setViewYear(viewYear - 1); }
    else setViewMonth(viewMonth - 1);
  };
  const nextMonth = () => {
    if (viewMonth === 11) { setViewMonth(0); setViewYear(viewYear + 1); }
    else setViewMonth(viewMonth + 1);
  };

  return (
    <div className="mb-4">
      <button
        onClick={() => setShowCalendar(!showCalendar)}
        className="flex items-center gap-2 text-sm font-medium text-primary-600 hover:text-primary-700 mb-3 transition-colors"
      >
        <Calendar size={16} />
        {showCalendar ? 'Hide Calendar View' : 'Show Calendar View'}
      </button>

      {showCalendar && (
        <div className="bg-white border border-slate-200 rounded-xl p-5 mb-4 transition-all duration-200">
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <button onClick={prevMonth} className="p-2 hover:bg-slate-100 rounded-lg transition-colors">
              <ChevronLeft size={16} className="text-slate-600" />
            </button>
            <h3 className="text-base font-semibold text-slate-900">{MONTHS[viewMonth]} {viewYear}</h3>
            <button onClick={nextMonth} className="p-2 hover:bg-slate-100 rounded-lg transition-colors">
              <ChevronRight size={16} className="text-slate-600" />
            </button>
          </div>

          {/* Day Headers */}
          <div className="grid grid-cols-7 mb-1">
            {DAYS_SHORT.map(d => (
              <div key={d} className="text-center text-xs font-semibold text-slate-400 py-2">{d}</div>
            ))}
          </div>

          {/* Calendar Grid */}
          <div className="grid grid-cols-7 gap-1">
            {Array.from({ length: firstDayOfMonth }, (_, i) => <div key={`e-${i}`} />)}
            {Array.from({ length: lastDay }, (_, i) => {
              const day = i + 1;
              const dateKey = `${viewYear}-${String(viewMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
              const leaves = leavesByDate[dateKey] || [];
              const isConflict = conflictDates.includes(dateKey);
              const isToday = today.getFullYear() === viewYear && today.getMonth() === viewMonth && today.getDate() === day;
              const isWeekend = new Date(viewYear, viewMonth, day).getDay() === 0;
              const hasLeaves = leaves.length > 0;

              return (
                <div
                  key={day}
                  onMouseEnter={() => setHoveredDate(hasLeaves ? dateKey : null)}
                  onMouseLeave={() => setHoveredDate(null)}
                  className={`relative min-h-[52px] p-1.5 rounded-lg border transition-all duration-100 ${
                    isConflict ? 'bg-red-50 border-red-200' :
                    hasLeaves ? 'bg-amber-50 border-amber-200' :
                    isToday ? 'bg-primary-50 border-primary-200' :
                    isWeekend ? 'bg-slate-50 border-slate-100' :
                    'bg-white border-slate-100 hover:border-slate-200'
                  }`}
                >
                  <span className={`text-xs font-medium ${isToday ? 'text-primary-700' : isWeekend ? 'text-slate-400' : 'text-slate-700'}`}>{day}</span>
                  {hasLeaves && (
                    <div className="mt-0.5">
                      {leaves.length <= 2 ? (
                        leaves.map((l, idx) => (
                          <p key={idx} className="text-[9px] text-amber-700 truncate leading-tight">{l.teacher_name?.split(' ')[0]}</p>
                        ))
                      ) : (
                        <>
                          <p className="text-[9px] text-amber-700 truncate leading-tight">{leaves[0].teacher_name?.split(' ')[0]}</p>
                          <p className="text-[9px] text-red-600 font-medium">+{leaves.length - 1} more</p>
                        </>
                      )}
                    </div>
                  )}

                  {/* Hover tooltip */}
                  {hoveredDate === dateKey && leaves.length > 0 && (
                    <div className="absolute z-20 top-full left-1/2 -translate-x-1/2 mt-1 bg-white border border-slate-200 rounded-lg shadow-lg p-3 min-w-[180px]">
                      <p className="text-xs font-semibold text-slate-700 mb-2">{new Date(dateKey).toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' })}</p>
                      <div className="space-y-1.5">
                        {leaves.map((l, idx) => (
                          <div key={idx} className="flex items-center gap-2">
                            <div className="w-5 h-5 rounded-full bg-purple-100 text-purple-700 flex items-center justify-center text-[8px] font-bold flex-shrink-0">{(l.teacher_name || '').slice(0, 1)}</div>
                            <div>
                              <p className="text-xs font-medium text-slate-800">{l.teacher_name}</p>
                              <p className="text-[10px] text-slate-400">{l.leave_type}{l.is_half_day ? ' (Half)' : ''}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Legend */}
          <div className="flex items-center gap-4 mt-4 pt-3 border-t border-slate-100">
            <div className="flex items-center gap-1.5"><div className="w-3 h-3 rounded bg-amber-100 border border-amber-200" /><span className="text-[10px] text-slate-500">On Leave</span></div>
            <div className="flex items-center gap-1.5"><div className="w-3 h-3 rounded bg-red-100 border border-red-200" /><span className="text-[10px] text-slate-500">Multiple (Conflict)</span></div>
            <div className="flex items-center gap-1.5"><div className="w-3 h-3 rounded bg-primary-100 border border-primary-200" /><span className="text-[10px] text-slate-500">Today</span></div>
            <span className="ml-auto text-[10px] text-slate-400">{calendarData?.total_leave_days_this_month || 0} total leave days this month</span>
          </div>
        </div>
      )}
    </div>
  );
}
