import { CheckCircle, XCircle } from 'lucide-react';
import { Badge, DataTable } from 'school-erp-ui-shared';

export default function AdvancesTab({ advances, onApprove, onReject }) {
  const columns = [
    { key: 'employee_name', label: 'Employee', render: (a) => <span className="font-medium text-slate-800">{a.employee_name || a.staff_name || ''}</span> },
    { key: 'amount', label: 'Amount', render: (a) => <span className="font-semibold text-slate-800">{'₹'}{Number(a.amount || 0).toLocaleString()}</span> },
    { key: 'reason', label: 'Reason', render: (a) => <span className="text-slate-500">{a.reason || ''}</span> },
    { key: 'requested_date', label: 'Requested On', render: (a) => <span className="text-slate-500">{a.requested_date || a.created_at || ''}</span> },
    { key: 'status', label: 'Status', render: (a) => <Badge status={a.status || 'Pending'} /> },
    {
      key: 'actions', label: 'Actions',
      render: (a) => a.status === 'Pending' ? (
        <div className="flex gap-1">
          <button onClick={() => onApprove(a.id)} className="p-1.5 hover:bg-green-50 rounded-lg transition-all duration-150 active:scale-[0.97]"><CheckCircle className="w-4 h-4 text-green-600" /></button>
          <button onClick={() => onReject(a.id)} className="p-1.5 hover:bg-red-50 rounded-lg transition-all duration-150 active:scale-[0.97]"><XCircle className="w-4 h-4 text-red-500" /></button>
        </div>
      ) : null,
    },
  ];

  return (
    <DataTable
      columns={columns}
      data={advances}
      loading={false}
      emptyMessage="No pending advance requests"
      emptyIcon={CheckCircle}
      headerTitle="Pending Salary Advance Requests"
    />
  );
}
